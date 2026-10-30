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
        # 解析标准 li.courseItem 节点
        lis = re.findall(r'<li[^>]*?class="[^"]*?courseItem[^"]*?".*?</li>', html, re.S)
        for li in lis:
            cid_match = re.search(r'name="courseId"\s+value="(\d+)"', li)
            clazz_match = re.search(r'name="classId"\s+value="(\d+)"', li)
            
            # 课程名称匹配规则
            name_match = (
                re.search(r'class="courseName"[^>]*?title="([^"]+)"', li) or
                re.search(r'class="courseName"[^>]*?>([^<]+)<', li) or
                re.search(r'<h3[^>]*?title="([^"]+)"', li) or
                re.search(r'title="([^"]+)"', li)
            )

            if cid_match and clazz_match:
                title = name_match.group(1).strip() if name_match else f"课程_{cid_match.group(1)}"
                if title in ["移动到", "退课"]:
                    # 备用从 a 标签提取
                    a_title = re.search(r'<a[^>]*?title="([^"]+)"[^>]*?>', li)
                    if a_title and a_title.group(1) not in ["移动到", "退课"]:
                        title = a_title.group(1).strip()
                    else:
                        title = f"课程_{cid_match.group(1)}"

                courses.append({
                    "course_id": cid_match.group(1),
                    "clazz_id": clazz_match.group(1),
                    "title": title
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
