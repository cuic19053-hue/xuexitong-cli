import json
import os
import requests
from pathlib import Path

DEFAULT_SESSION_FILE = Path.home() / ".xuexitong_session.json"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
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
            except Exception:
                pass

    def save(self):
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "cookies": self.session.cookies.get_dict(),
            "user_info": self.user_info
        }
        self.session_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def is_logged_in(self):
        # 1. 如果本地连最基础的 UID / _uid / vc3 都没有，直接判定未登录
        if not (self.session.cookies.get("UID") or self.session.cookies.get("_uid")):
            return False

        # 2. 通过验证个人空间或课程中心判定登录态有效性
        try:
            resp = self.session.get("https://mooc1-2.chaoxing.com/visit/courses/study?isAjax=true", allow_redirects=False, timeout=8)
            if resp.status_code == 200 and ("courseItem" in resp.text or "courseName" in resp.text or "ulDiv" in resp.text):
                return True
            
            resp2 = self.session.get("https://i.chaoxing.com/base", allow_redirects=False, timeout=5)
            if resp2.status_code == 200 or (resp2.status_code == 302 and "passport" not in resp2.headers.get("Location", "")):
                return True
        except Exception:
            pass
        return False

    def logout(self):
        if self.session_file.exists():
            self.session_file.unlink()
        self.session.cookies.clear()
        self.user_info = {}
