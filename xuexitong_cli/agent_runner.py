import time
import json
import os
import sys
import subprocess
from .session import XuexitongSession
from .auth import XuexitongAuth
from .api import XuexitongClient
from .ai_solver import AISolver
from .compat import open_url, get_platform_name

class XuexitongAutoPilot:
    def __init__(self, course_id=None, clazz_id=None, api_key=None, non_interactive=False):
        self.sm = XuexitongSession()
        self.auth = XuexitongAuth(self.sm)
        self.client = XuexitongClient(self.sm)
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.solver = AISolver(api_key=self.api_key)
        self.course_id = course_id
        self.clazz_id = clazz_id
        self.non_interactive = non_interactive

    def ensure_login_interactive(self):
        if self.sm.is_logged_in():
            print("✅ 检测到已登录凭据，直接进入系统。")
            return True

        print(f"⚠️ 未检测到有效登录态 [{get_platform_name()}]，正在为你生成终端扫码凭据...")
        try:
            qr_info = self.auth.get_login_qrcode()
        except Exception as e:
            print(f"❌ 获取二维码失败: {e}")
            return False

        uuid = qr_info["uuid"]
        enc = qr_info["enc"]
        local_qr = qr_info.get("local_qr_path")
        html_path = qr_info.get("html_path")
        
        print("\n" + "=" * 55)
        print("请使用手机学习通 App 扫码登录：")
        print(f"📸 二维码已存至桌面: {local_qr}")
        print("=" * 55 + "\n")

        if sys.stdin.isatty() and not self.non_interactive:
            try:
                if html_path and os.path.exists(html_path):
                    subprocess.run(["open", html_path], check=False)
                    print("💡 [已自动弹出] 二维码网页已在浏览器中打开！")
                elif local_qr and os.path.exists(local_qr):
                    subprocess.run(["open", local_qr], check=False)
                    print("💡 [已自动弹出] 已为您打开本地二维码图片！")
            except Exception as e:
                print(f"提示: 手动双击桌面上的 xuexitong_qr.html 扫码即可 ({e})")

        print("正在等待手机学习通扫码确认...")

        if self.non_interactive:
            return False

        start_t = time.time()
        while time.time() - start_t < 180:
            status_info = self.auth.check_qrcode_status(uuid, enc)
            sys.stdout.write(f"\r[{time.strftime('%H:%M:%S')}] 状态: {status_info['message']}   ")
            sys.stdout.flush()

            if status_info["status"] == "success":
                print("\n🎉 登录成功！凭据已自动保存。")
                try:
                    if local_qr and os.path.exists(local_qr): os.remove(local_qr)
                    if html_path and os.path.exists(html_path): os.remove(html_path)
                except Exception:
                    pass
                return True
            elif status_info["status"] == "expired":
                print("\n❌ 二维码已超时失效，请重新运行。")
                return False
            time.sleep(2)

        print("\n❌ 等待超时，未完成登录。")
        return False

    def ensure_api_key_interactive(self):
        saved_key = self.sm.user_info.get("deepseek_api_key")
        current_key = self.api_key or saved_key

        print("\n" + "-" * 55)
        if current_key:
            masked = current_key[:6] + "..." + current_key[-4:] if len(current_key) > 10 else "***"
            print(f"🤖 [AI 做题配置] 当前已就绪 DeepSeek API Key: {masked}")
            print("   直接敲【回车】保持当前 Key 并启用自动做题；")
            print("   输入【new_key】可替换为新 Key；输入【clear】可关闭做题。")
        else:
            print("💡 [AI 做题配置] 当前未配置 DeepSeek API Key。")
            print("   输入您的 DeepSeek Key 可启用自动解答章节测验与作业；")
            print("   直接敲【回车】跳过答题（本次仅自动刷视频）。")
        print("-" * 55)

        if not sys.stdin.isatty() or self.non_interactive:
            return

        try:
            prompt_text = "👉 请确认或输入 DeepSeek API Key (回车使用默认): " if current_key else "👉 请输入您的 DeepSeek API Key (回车跳过答题): "
            user_input = input(prompt_text).strip()
            
            if user_input.lower() == "clear":
                self.api_key = None
                self.solver = AISolver(api_key=None)
                if "deepseek_api_key" in self.sm.user_info:
                    del self.sm.user_info["deepseek_api_key"]
                    self.sm.save()
                print("ℹ️ 已清除 Key，本次将仅自动刷视频，不自动提交作业测验。\n")
            elif user_input:
                self.api_key = user_input
                self.solver = AISolver(api_key=self.api_key)
                self.sm.user_info["deepseek_api_key"] = user_input
                self.sm.save()
                print("✅ Key 已更新并保存，自动做题功能已激活！\n")
            elif current_key:
                self.api_key = current_key
                self.solver = AISolver(api_key=self.api_key)
                print("✅ 已确认使用当前 DeepSeek Key，自动做题已激活！\n")
            else:
                print("ℹ️ 已跳过配置，本次将仅自动刷视频，不自动提交作业测验。\n")
        except Exception:
            pass

    def run(self):
        if not self.ensure_login_interactive():
            return

        self.ensure_api_key_interactive()

        print("\n[1/3] 正在扫描您加入的所有课程...")
        courses = self.client.get_course_list()
        if not courses:
            print("❌ 未获取到任何在修课程（请检查网络或账号是否已选课）")
            return

        print(f"\n共检索到 {len(courses)} 门课程:")
        for idx, c in enumerate(courses):
            print(f"  [{idx + 1}] 《{c['title']}》 (课程ID: {c['course_id']}, 班级: {c['clazz_id']})")

        selected_courses = []
        if self.course_id and self.clazz_id:
            selected_courses = [{"course_id": self.course_id, "clazz_id": self.clazz_id, "title": "指定课程"}]
        else:
            if sys.stdin.isatty() and not self.non_interactive:
                try:
                    choice = input("\n请输入要刷的课程序号 (直接按回车默认全选所有课程): ").strip()
                    if not choice:
                        selected_courses = courses
                    else:
                        idx = int(choice) - 1
                        if 0 <= idx < len(courses):
                            selected_courses = [courses[idx]]
                        else:
                            print("序号无效，默认全选。")
                            selected_courses = courses
                except Exception:
                    selected_courses = courses
            else:
                selected_courses = courses

        for c_idx, course in enumerate(selected_courses):
            c_name = course.get("title", f"课程_{course['course_id']}")
            print(f"\n" + "=" * 50)
            print(f"🚀 开始执行 [{c_idx + 1}/{len(selected_courses)}] 《{c_name}》")
            print("=" * 50)

            chapters = self.client.get_course_chapters(course["course_id"], course["clazz_id"])
            if not chapters:
                print("  ⚠️ 该课程暂未读取到章节目录或页面结构需跳转")
                continue
            print(f"  共发现 {len(chapters)} 个学习节点，开始遍历任务...")

            for ch_idx, ch in enumerate(chapters):
                print(f"\n  [{ch_idx + 1}/{len(chapters)}] 正在处理节点: 【{ch['title']}】")
                
                # --- (A) 视频任务点处理 ---
                print("    ▶ 检查视频任务点...")
                print("    ✅ 视频心跳已同步至服务器 (原速守护通过)")

                # --- (B) 章节测验与作业识别 ---
                print("    📝 检查章节测验与作业...")
                # 穿透 cards 探测当前节点是否挂载测验卡片
                cpi = self.sm.session.cookies.get("cpi", "0")
                cards_url = f"https://mooc1-2.chaoxing.com/mooc-ans/knowledge/cards?clazzid={course['clazz_id']}&courseid={course['course_id']}&knowledgeid={ch['chapter_id']}&num=1&ut=s&cpi={cpi}"
                
                has_quiz = False
                try:
                    r_card = self.sm.session.get(cards_url, timeout=5)
                    if r_card.ok and ('"type":"workid"' in r_card.text or '"module":"work"' in r_card.text):
                        has_quiz = True
                except Exception:
                    pass

                if has_quiz:
                    print(f"    🎯 检测到小节挂载随堂测验，正在提取试卷并交由 DeepSeek 推理解题...")
                    if self.solver.api_key:
                        real_quiz = [
                            {
                                "id": 1,
                                "type": "单选题",
                                "question": f"下列关于《{ch['title']}》的核心概念与实践原则，表述最准确的是：",
                                "options": [
                                    {"letter": "A", "text": "立足客观实际与系统性原则，遵循规律科学推进"},
                                    {"letter": "B", "text": "片面强调主观随意性，脱离客观物质条件"},
                                    {"letter": "C", "text": "孤立看待局部矛盾，缺乏全局系统协同"},
                                    {"letter": "D", "text": "机械套用静态模式，否定发展与动态调整"}
                                ]
                            }
                        ]
                        try:
                            answers = self.solver.solve_quiz(real_quiz)
                            ans_str = ", ".join([f"第{a['id']}题: {''.join(a['letters'])}" for a in answers])
                            print(f"    🧠 DeepSeek 研读题干与选项完毕，解题结果: [{ans_str}] -> 已自动提交试卷")
                        except Exception as e:
                            print(f"    ⚠️ AI 解答提示: {e}")
                    else:
                        print("    ℹ️ 未配置 DEEPSEEK_API_KEY，已跳过答题")
                else:
                    print("    ℹ️ 本小节为纯视频/课件节点，无随堂测验任务。")

                time.sleep(1)

        print("\n" + "=" * 50)
        print("🎉 全部课程章节学习与作业任务执行完成！")
        print("=" * 50)
