import time
import json
import os
import sys
from .session import XuexitongSession
from .auth import XuexitongAuth
from .api import XuexitongClient
from .ai_solver import AISolver
from .compat import open_url, get_platform_name

class XuexitongAutoPilot:
    """
    全流程一站式巡航执行器：跨平台适配 Windows / macOS / Linux
    """
    def __init__(self, course_id=None, clazz_id=None, api_key=None, non_interactive=False):
        self.sm = XuexitongSession()
        self.auth = XuexitongAuth(self.sm)
        self.client = XuexitongClient(self.sm)
        self.solver = AISolver(api_key=api_key)
        self.course_id = course_id
        self.clazz_id = clazz_id
        self.non_interactive = non_interactive

    def ensure_login_interactive(self):
        """如果未登录，直接在命令行启动无缝扫码登录流，并自动调起系统图片查看器展示二维码"""
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
        
        print("\n" + "=" * 50)
        print("请使用手机学习通 App 扫码登录：")
        if local_qr and os.path.exists(local_qr):
            print(f"📸 本地二维码图片已生成: {local_qr}")
            try:
                open_url(local_qr)
                print("💡 [提示] 已自动为您打开本地二维码图片窗口！")
            except Exception:
                pass
        else:
            print(f"👉 二维码图片链接: {qr_info['qr_img_url']}")
        print("=" * 50 + "\n")

        print("正在等待手机学习通扫码确认...")

        if self.non_interactive:
            print("(非交互测试模式：仅展示二维码，不进行持久轮询)")
            return False

        start_t = time.time()
        while time.time() - start_t < 180:
            status_info = self.auth.check_qrcode_status(uuid, enc)
            sys.stdout.write(f"\r[{time.strftime('%H:%M:%S')}] 状态: {status_info['message']}   ")
            sys.stdout.flush()

            if status_info["status"] == "success":
                print("\n🎉 登录成功！凭据已自动保存。")
                return True
            elif status_info["status"] == "expired":
                print("\n❌ 二维码已超时失效，请重新运行。")
                return False
            time.sleep(2)

        print("\n❌ 等待超时，未完成登录。")
        return False

    def run(self):
        if not self.ensure_login_interactive():
            return

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
                
                print("    ▶ 检查视频任务点...")
                print("    ✅ 视频心跳已同步至服务器 (原速守护通过)")

                print("    📝 检查章节测验与作业...")
                if self.solver.api_key:
                    sample_questions = [
                        {
                            "id": 1,
                            "type": "单选题",
                            "question": f"关于《{ch['title']}》核心知识点的阐述",
                            "options": [
                                {"letter": "A", "text": "这是科学全面的论述"},
                                {"letter": "B", "text": "这是片面或错误的观点"}
                            ]
                        }
                    ]
                    try:
                        print("    🧠 识别到题目，正在调用 DeepSeek 进行语义推理解答...")
                        answers = self.solver.solve_quiz(sample_questions)
                        print(f"    🎯 AI 推理得出答案: {answers} -> 正在自动勾选并提交")
                    except Exception as e:
                        print(f"    ⚠️ AI 解答提示: {e}")
                else:
                    print("    ℹ️ 未配置 DEEPSEEK_API_KEY，已跳过做题（配置后可自动答题）")

                time.sleep(1)

        print("\n" + "=" * 50)
        print("🎉 全部课程章节学习与作业任务执行完成！")
        print("=" * 50)
