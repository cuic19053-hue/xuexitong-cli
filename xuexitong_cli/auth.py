import re
import os
import tempfile
import time
import requests
from .session import XuexitongSession

class XuexitongAuth:
    def __init__(self, session_manager: XuexitongSession):
        self.sm = session_manager
        self.session = session_manager.session

    def get_login_qrcode(self):
        """
        获取扫码登录二维码及唯一 uuid 和 enc 参数（对齐超星 passport2 最新 getauthstatus/v2 协议）
        为避免浏览器防盗链触发 403 forbidden，直接将图片二进制流持久化下载到本地 /tmp 供系统打开
        """
        login_url = "https://passport2.chaoxing.com/login?loginType=4"
        resp = self.session.get(login_url, timeout=10)
        
        uuid_match = re.search(r'value="([a-f0-9]+)"\s+id="uuid"', resp.text)
        enc_match = re.search(r'value="([a-f0-9]+)"\s+id="enc"', resp.text)
        
        if not uuid_match or not enc_match:
            raise RuntimeError("未能从超星登录页解析到 uuid / enc 字段")

        uuid = uuid_match.group(1)
        enc = enc_match.group(1)
        
        qr_img_url = f"https://passport2.chaoxing.com/createqr?uuid={uuid}&fid=-1"
        
        # 直接下载二维码图片数据，规避浏览器直接打开触发的 403 防盗链重定向
        img_resp = requests.get(qr_img_url, timeout=10)
        local_qr_path = os.path.join(tempfile.gettempdir(), f"xuexitong_qr_{uuid[:8]}.png")
        with open(local_qr_path, "wb") as f:
            f.write(img_resp.content)

        return {
            "uuid": uuid,
            "enc": enc,
            "qr_img_url": qr_img_url,
            "local_qr_path": local_qr_path
        }

    def check_qrcode_status(self, uuid: str, enc: str):
        """
        轮询扫码状态：
        'status': False, 'mes': '未登录', 'type': '3' -> 等待扫码
        'status': False, 'mes': '扫码成功', 'type': '4' -> 已扫码，请在手机确认
        'status': True, 'mes': '验证通过' -> 登录成功
        """
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
            return {"status": "expired", "message": "二维码已失效，请重新生成"}
        else:
            return {"status": "waiting", "message": mes or "状态检测中"}

    def login_by_cookie_str(self, cookie_str: str):
        """
        支持直接从控制台/浏览器抓包粘贴 Cookie 字符串登录
        格式：UID=xxx; _d=yyy; vc3=zzz
        """
        for item in cookie_str.split(";"):
            item = item.strip()
            if not item:
                continue
            if "=" in item:
                k, v = item.split("=", 1)
                self.session.cookies.set(k.strip(), v.strip(), domain=".chaoxing.com")
        self.sm.save()
        return self.sm.is_logged_in()
