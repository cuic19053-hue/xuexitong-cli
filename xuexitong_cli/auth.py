import re
import os
import time
import base64
import requests
from pathlib import Path
from .session import XuexitongSession

class XuexitongAuth:
    def __init__(self, session_manager: XuexitongSession):
        self.sm = session_manager
        self.session = session_manager.session

    def get_login_qrcode(self):
        """
        获取扫码登录二维码及唯一 uuid 和 enc 参数。
        必须严格按顺序：
        1. GET login 页面建立会话 Cookie
        2. 解析 uuid 与 enc
        3. 用【同一个 session】立即 GET 请求 createqr 激活二维码并获取二进制
        4. 生成桌面文件与 Base64 网页
        """
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://passport2.chaoxing.com/login?loginType=4"
        })
        login_url = "https://passport2.chaoxing.com/login?loginType=4"
        resp = self.session.get(login_url, timeout=10)
        
        uuid_match = re.search(r'value="([a-f0-9]+)"\s+id="uuid"', resp.text)
        enc_match = re.search(r'value="([a-f0-9]+)"\s+id="enc"', resp.text)
        
        if not uuid_match or not enc_match:
            raise RuntimeError("未能从超星登录页解析到 uuid / enc 字段")

        uuid = uuid_match.group(1)
        enc = enc_match.group(1)
        
        qr_img_url = f"https://passport2.chaoxing.com/createqr?uuid={uuid}&fid=-1"
        
        # 必须用同一个 session 请求，激活服务端二维码生命周期
        img_resp = self.session.get(qr_img_url, timeout=10)
        img_bytes = img_resp.content

        # 存放桌面
        desktop_dir = Path.home() / "Desktop"
        if not desktop_dir.exists():
            desktop_dir = Path.home()
        local_qr_path = str(desktop_dir / "xuexitong_qr.png")
        with open(local_qr_path, "wb") as f:
            f.write(img_bytes)

        # 生成无拦截 Base64 HTML 页面
        b64_data = base64.b64encode(img_bytes).decode('utf-8')
        html_path = str(desktop_dir / "xuexitong_qr.html")
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>超星学习通扫码登录</title>
<style>
body {{ display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh; font-family: -apple-system, sans-serif; background: #f7f9fa; }}
.card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }}
h2 {{ color: #1f2937; margin-bottom: 20px; }}
img {{ width: 260px; height: 260px; border: 1px solid #e5e7eb; border-radius: 8px; }}
p {{ color: #6b7280; font-size: 14px; margin-top: 15px; }}
</style>
</head>
<body>
<div class="card">
  <h2>请使用学习通 APP 扫码登录</h2>
  <img src="data:image/png;base64,{b64_data}" alt="二维码" />
  <p>扫码并在手机上点击允许登录后，回到终端即可自动继续！</p>
</div>
</body>
</html>
"""
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {
            "uuid": uuid,
            "enc": enc,
            "qr_img_url": qr_img_url,
            "local_qr_path": local_qr_path,
            "html_path": html_path
        }

    def check_qrcode_status(self, uuid: str, enc: str):
        url = "https://passport2.chaoxing.com/getauthstatus/v2"
        data = {
            "enc": enc,
            "uuid": uuid,
            "doubleFactorLogin": "0",
            "forbidotherlogin": "0"
        }
        headers = {
            "Referer": "https://passport2.chaoxing.com/login?loginType=4"
        }
        resp = self.session.post(url, data=data, headers=headers, timeout=10)
        try:
            res_json = resp.json()
        except Exception:
            return {"status": "error", "message": resp.text}

        if res_json.get("status") is True:
            self.sm.save()
            return {"status": "success", "message": "登录成功"}

        mes = res_json.get("mes", "")
        t = str(res_json.get("type", ""))
        if t == "3":
            return {"status": "waiting", "message": mes or "等待扫码"}
        elif t == "4":
            return {"status": "scanned", "message": mes or "已扫码，请在手机上点击确认"}
        elif t == "2":
            # 超星在初次轮询时偶尔由于网络延迟返回 type 2，此处做平滑重试
            return {"status": "retry", "message": mes or "状态同步中"}
        else:
            return {"status": "waiting", "message": mes or "状态检测中"}

    def login_by_cookie_str(self, cookie_str: str):
        for item in cookie_str.split(";"):
            item = item.strip()
            if not item:
                continue
            if "=" in item:
                k, v = item.split("=", 1)
                self.session.cookies.set(k.strip(), v.strip(), domain=".chaoxing.com")
        self.sm.save()
        return self.sm.is_logged_in()
