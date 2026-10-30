import json
import os
import requests
from pathlib import Path

DEFAULT_SESSION_FILE = Path.home() / ".xuexitong_session.json"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

class XuexitongSession:
    def __init__(self, session_file=DEFAULT_SESSION_FILE):
        self.session_file = Path(session_file)
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.user_info = {}
        self.load()

    def load(self):
        if self.session_file.exists():
            try:
                data = json.loads(self.session_file.read_text(encoding='utf-8'))
                cookies = data.get("cookies", {})
                self.user_info = data.get("user_info", {})
                for k, v in cookies.items():
                    self.session.cookies.set(k, v, domain=".chaoxing.com")
            except Exception as e:
                pass

    def save(self):
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "cookies": self.session.cookies.get_dict(),
            "user_info": self.user_info
        }
        self.session_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def is_logged_in(self):
        # 验证 cookie 是否有效
        try:
            resp = self.session.get("https://mooc1-1.chaoxing.com/api/work/get-user-info", timeout=5)
            if resp.ok and resp.text.strip():
                try:
                    res_json = resp.json()
                    if res_json.get("status") is True or res_json.get("result") == 1:
                        self.user_info = res_json.get("data", {})
                        self.save()
                        return True
                except Exception:
                    pass
            # 备用验证端点
            resp2 = self.session.get("https://i.chaoxing.com/base", allow_redirects=False, timeout=5)
            if resp2.status_code == 200 and "passport" not in resp2.headers.get("Location", ""):
                return True
        except Exception:
            pass
        return False

    def logout(self):
        if self.session_file.exists():
            self.session_file.unlink()
        self.session.cookies.clear()
        self.user_info = {}
