import argparse
import sys
import json
import time
import subprocess
import os
from .session import XuexitongSession
from .auth import XuexitongAuth
from .api import XuexitongClient
from .ai_solver import AISolver
from .sign import XuexitongSign

def main():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--json", action="store_true", help="强制以 JSON 机器可读格式输出（方便 AI Agent 消费）")

    parser = argparse.ArgumentParser(
        prog="xuexitong",
        parents=[common_parser],
        description="学习通 CLI 自动化工具（支持逆向协议直接运行 + DeepSeek AI 答题推理 + 全类型签到）"
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="可用子命令")

    auth_parser = subparsers.add_parser("auth", parents=[common_parser], help="身份验证与登录管理")
    auth_parser.add_argument("--status", action="store_true", help="检查当前登录状态")
    auth_parser.add_argument("--qrcode", action="store_true", help="获取终端扫码登录二维码")
    auth_parser.add_argument("--poll", action="store_true", help="获取二维码并持续轮询等待扫码完成")
    auth_parser.add_argument("--cookie", type=str, help="直接注入 Cookie 字符串登录")
    auth_parser.add_argument("--logout", action="store_true", help="退出登录并清空凭据")

    course_parser = subparsers.add_parser("course", parents=[common_parser], help="课程管理与进度查询")
    course_parser.add_argument("--list", action="store_true", help="列出已加入的所有课程")
    course_parser.add_argument("--chapters", type=str, metavar="COURSE_ID", help="获取指定课程的章节结构与任务点")
    course_parser.add_argument("--clazz-id", type=str, default="", help="班级 ID (配合 --chapters)")

    play_parser = subparsers.add_parser("play", parents=[common_parser], help="视频任务点原速守护/心跳上报")
    play_parser.add_argument("--clazz-id", required=True, help="班级 ID")
    play_parser.add_argument("--job-id", required=True, help="任务点 Job ID")
    play_parser.add_argument("--object-id", required=True, help="视频 Object ID")
    play_parser.add_argument("--duration", type=float, required=True, help="视频总时长 (秒)")
    play_parser.add_argument("--simulate", action="store_true", help="仅单次发包测试，不进行完整物理挂机")
    play_parser.add_argument("--speed", type=float, default=1.0, help="挂机时钟步进速率 (默认 1.0 原速)")

    quiz_parser = subparsers.add_parser("quiz", parents=[common_parser], help="章节测验与 AI 自动作答")
    quiz_parser.add_argument("--solve", type=str, metavar="JSON_FILE_OR_STR", help="输入题目 JSON 进行 AI 解答")
    quiz_parser.add_argument("--api-key", type=str, help="大模型 API Key")

    sign_parser = subparsers.add_parser("sign", parents=[common_parser], help="班级签到（支持普通/手势/定位/签到码/二维码）")
    sign_parser.add_argument("--list", action="store_true", help="列出正在进行中的签到活动")
    sign_parser.add_argument("--course-id", type=str, help="课程 ID")
    sign_parser.add_argument("--clazz-id", type=str, help="班级 ID")
    sign_parser.add_argument("--active-id", type=str, help="活动 activeId")
    sign_parser.add_argument("--type", choices=["general", "location", "code", "qrcode", "photo"], default="general", help="签到类型")
    sign_parser.add_argument("--address", type=str, default="教学楼", help="位置签到地址名")
    sign_parser.add_argument("--lat", type=float, default=34.757975, help="纬度 (默认学校坐标)")
    sign_parser.add_argument("--lng", type=float, default=113.665412, help="经度 (默认学校坐标)")
    sign_parser.add_argument("--code", type=str, help="签到码/手势轨迹")
    sign_parser.add_argument("--enc", type=str, help="二维码动态盐值 enc")

    args = parser.parse_args()

    sm = XuexitongSession()
    client = XuexitongClient(sm)
    auth = XuexitongAuth(sm)
    signer = XuexitongSign(sm)

    result = {}

    if args.subcommand == "auth":
        if args.status:
            logged_in = sm.is_logged_in()
            result = {
                "logged_in": logged_in,
                "user_info": sm.user_info,
                "cookies_present": bool(sm.session.cookies)
            }
            if not args.json:
                print(f"登录状态: {'已登录' if logged_in else '未登录'}")
                if logged_in and sm.user_info:
                    print(f"用户信息: {sm.user_info}")
        elif args.cookie:
            ok = auth.login_by_cookie_str(args.cookie)
            result = {"success": ok, "message": "Cookie 注入成功" if ok else "Cookie 无效或已过期"}
            if not args.json:
                print("Cookie 已载入，状态:", "有效" if ok else "无效")
        elif args.qrcode or args.poll:
            qr_info = auth.get_login_qrcode()
            uuid = qr_info["uuid"]
            enc = qr_info["enc"]
            local_qr = qr_info.get("local_qr_path")
            html_path = qr_info.get("html_path")
            result = qr_info
            
            if not args.json:
                print("\n" + "=" * 50)
                print("请使用手机学习通 App 扫码登录：")
                print(f"📸 二维码已存至桌面: {local_qr}")
                print("=" * 50 + "\n")
                # 自动弹窗
                try:
                    if html_path and os.path.exists(html_path):
                        subprocess.run(["open", html_path], check=False)
                        print("💡 已自动为您打开本地二维码网页窗口！")
                except Exception:
                    pass

            if args.poll:
                if not args.json:
                    print("等待手机端扫码中...")
                start_t = time.time()
                fail_times = 0
                while time.time() - start_t < 180:
                    status_info = auth.check_qrcode_status(uuid, enc)
                    if not args.json:
                        sys.stdout.write(f"\r[{time.strftime('%H:%M:%S')}] 状态: {status_info['message']}   ")
                        sys.stdout.flush()
                    if status_info["status"] == "success":
                        result = {"success": True, "message": "登录成功"}
                        if not args.json:
                            print("\n🎉 登录成功！已保存凭据。")
                        break
                    elif status_info["status"] == "expired":
                        fail_times += 1
                        if fail_times >= 5:
                            result = {"success": False, "message": "二维码已失效"}
                            if not args.json:
                                print("\n二维码已失效。")
                            break
                    time.sleep(2)
        elif args.logout:
            sm.logout()
            result = {"success": True, "message": "已成功退出并清空会话凭据"}
            if not args.json:
                print("已登出并清除本地 Session。")
        else:
            auth_parser.print_help()
            sys.exit(0)

    elif args.subcommand == "course":
        if args.list:
            if not sm.is_logged_in():
                result = {"error": "未登录，请先执行 xuexitong auth 登录"}
                if not args.json:
                    print("错误: 未登录")
                sys.exit(1)
            courses = client.get_course_list()
            result = {"courses": courses, "total": len(courses)}
            if not args.json:
                print(f"共找到 {len(courses)} 门课程:")
                for c in courses:
                    print(f" - [{c['course_id']}] {c['title']} (班级: {c['clazz_id']})")
        elif args.chapters:
            chapters = client.get_course_chapters(args.chapters, args.clazz_id)
            result = {"chapters": chapters, "total": len(chapters)}
            if not args.json:
                print(f"共检索到 {len(chapters)} 个章节节点:")
                for ch in chapters:
                    print(f" - [{ch['chapter_id']}] {ch['title']}")
        else:
            course_parser.print_help()
            sys.exit(0)

    elif args.subcommand == "play":
        if args.simulate:
            res = client.report_video_progress(
                clazz_id=args.clazz_id,
                jobid=args.job_id,
                object_id=args.object_id,
                duration=args.duration,
                playing_time=args.duration,
                clip_time="0",
                is_drag=0
            )
            result = {"simulate": True, "response": res}
            if not args.json:
                print("心跳上报测试完成，服务器响应:", res)
        else:
            step = 30 * args.speed
            cur_time = 0
            if not args.json:
                print(f"开始原速守护视频进度上报 (总长 {args.duration}s, 步进 {step}s)...")
            while cur_time < args.duration:
                cur_time = min(cur_time + step, args.duration)
                res = client.report_video_progress(
                    clazz_id=args.clazz_id,
                    jobid=args.job_id,
                    object_id=args.object_id,
                    duration=args.duration,
                    playing_time=cur_time,
                    clip_time="0"
                )
                if not args.json:
                    print(f"[{time.strftime('%H:%M:%S')}] 进度: {cur_time:.1f}/{args.duration:.1f}s -> 上报状态: {res.get('isPassed', False)}")
                if cur_time < args.duration:
                    time.sleep(30)
            result = {"completed": True, "total_reported": args.duration}

    elif args.subcommand == "quiz":
        if args.solve:
            try:
                if args.solve.strip().startswith("[") or args.solve.strip().startswith("{"):
                    q_data = json.loads(args.solve)
                else:
                    with open(args.solve, 'r', encoding='utf-8') as f:
                        q_data = json.load(f)
                if isinstance(q_data, dict):
                    q_data = q_data.get("questions", [])
            except Exception as e:
                result = {"error": f"题目数据解析失败: {str(e)}"}
                if args.json:
                    print(json.dumps(result, ensure_ascii=False))
                else:
                    print("题目数据不是合法的 JSON:", e)
                sys.exit(1)

            solver = AISolver(api_key=args.api_key)
            try:
                answers = solver.solve_quiz(q_data)
                result = {"answers": answers}
                if not args.json:
                    print("AI 解题成功:")
                    for a in answers:
                        print(f" 题号 {a['id']}: 选项 {''.join(a['letters'])}")
            except Exception as e:
                result = {"error": str(e)}
                if not args.json:
                    print("解题失败:", e)
        else:
            quiz_parser.print_help()
            sys.exit(0)

    elif args.subcommand == "sign":
        if args.list:
            if not args.course_id or not args.clazz_id:
                result = {"error": "查看活动必须指定 --course-id 和 --clazz-id"}
                if not args.json:
                    print("错误: 缺少 --course-id 和 --clazz-id")
                sys.exit(1)
            signs = signer.get_active_signs(args.course_id, args.clazz_id)
            result = {"signs": signs, "total": len(signs)}
            if not args.json:
                print(f"当前班级共发现 {len(signs)} 个正在进行中的签到活动:")
                for s in signs:
                    print(f" - [{s['active_id']}] {s['name']} (类型: {s['other_id']}, 发起时间: {s['start_time']})")
        elif args.active_id:
            if args.type == "general":
                res = signer.sign_general(args.active_id)
            elif args.type == "location":
                res = signer.sign_location(args.active_id, address=args.address, lat=args.lat, lng=args.lng)
            elif args.type == "code":
                if not args.code:
                    res = {"success": False, "message": "签到码类型必须指定 --code 参数"}
                else:
                    res = signer.sign_code(args.active_id, args.code)
            elif args.type == "qrcode":
                res = signer.sign_qrcode(args.active_id, enc=args.enc or "")
            elif args.type == "photo":
                res = signer.sign_photo(args.active_id)
            else:
                res = {"success": False, "message": "不支持的签到类型"}

            result = res
            if not args.json:
                status_icon = "✅" if res.get("success") else "❌"
                print(f"{status_icon} 签到结果: {res.get('message')}")
        else:
            sign_parser.print_help()
            sys.exit(0)

    else:
        parser.print_help()
        sys.exit(0)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
