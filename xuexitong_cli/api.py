import re
import json
import time
from .session import XuexitongSession
from .crypto import calculate_enc

class XuexitongClient:
    def __init__(self, session_manager: XuexitongSession):
        self.sm = session_manager
        self.session = session_manager.session

    def get_course_list(self):
        """
        获取当前用户加入的所有课程
        """
        url = "https://mooc1-2.chaoxing.com/visit/courses/study?isAjax=true"
        resp = self.session.get(url, timeout=10)
        courses = []
        if not resp.ok:
            return courses

        html = resp.text
        # 正则提取 courseId, clazzid, title
        pattern = re.compile(r'courseId=(\d+)[^"\']*?clazzid=(\d+)[^>]*?>\s*<h3[^>]*?title="([^"]+)"', re.S)
        matches = pattern.findall(html)
        if matches:
            for course_id, clazz_id, title in matches:
                courses.append({
                    "course_id": course_id,
                    "clazz_id": clazz_id,
                    "title": title.strip()
                })
        else:
            links = re.findall(r'href="([^"]*courseId=(\d+)[^"]*clazzid=(\d+)[^"]*)"', html)
            seen = set()
            for href, course_id, clazz_id in links:
                if (course_id, clazz_id) not in seen:
                    seen.add((course_id, clazz_id))
                    courses.append({
                        "course_id": course_id,
                        "clazz_id": clazz_id,
                        "title": f"课程_{course_id}"
                    })
        return courses

    def get_course_chapters(self, course_id: str, clazz_id: str, cpi: str = ""):
        """
        获取课程章节目录树及任务点
        """
        url = f"https://mooc1-1.chaoxing.com/mycourse/studentstudyAjax?courseId={course_id}&clazzid={clazz_id}&cpi={cpi}"
        resp = self.session.get(url, timeout=10)
        chapters = []
        if not resp.ok:
            return chapters

        html = resp.text
        node_pattern = re.compile(r'href="javascript:void\(0\);"[^>]*?onclick="[^"]*?getTeacherAjax\(\'(\d+)\'[^"]*?\)"[^>]*?title="([^"]+)"', re.S)
        matches = node_pattern.findall(html)
        for chapter_id, title in matches:
            chapters.append({
                "chapter_id": chapter_id,
                "title": title.strip()
            })
        return chapters

    def report_video_progress(self, clazz_id: str, jobid: str, object_id: str, duration: float, playing_time: float, clip_time: str = "0", is_drag: int = 0):
        """
        上报视频播放进度（核心心跳发包）
        """
        enc = calculate_enc(clazz_id, jobid, object_id, playing_time, duration, clip_time)
        clip_str = f"0_{int(duration)}" if clip_time == "0" else str(clip_time)
        
        cpi = self.sm.session.cookies.get("cpi", "0")
        dtoken = self.sm.session.cookies.get("_d", "")
        url = f"https://mooc1-1.chaoxing.com/multimedia/log/a/{cpi}/{dtoken}"
        params = {
            "clazzId": clazz_id,
            "playingTime": int(playing_time),
            "duration": int(duration),
            "clipTime": clip_str,
            "objectId": object_id,
            "otherInfo": f"nodeId_jobid_{jobid}",
            "jobid": jobid,
            "userid": self.sm.session.cookies.get("UID", ""),
            "isdrag": is_drag,
            "view": "pc",
            "enc": enc,
            "rt": "0.9",
            "dtype": "Video",
            "_t": str(int(time.time() * 1000))
        }
        headers = {
            "Referer": "https://mooc1-1.chaoxing.com/ananas/modules/video/index.html",
        }
        resp = self.session.get(url, params=params, headers=headers, timeout=10)
        try:
            return resp.json()
        except Exception:
            return {"status": resp.status_code, "text": resp.text}
