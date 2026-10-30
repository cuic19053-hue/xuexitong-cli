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
        lis = re.findall(r'<li[^>]*?class="[^"]*?courseItem[^"]*?".*?</li>', html, re.S)
        for li in lis:
            cid_match = re.search(r'name="courseId"\s+value="(\d+)"', li)
            clazz_match = re.search(r'name="classId"\s+value="(\d+)"', li)
            
            name_match = (
                re.search(r'class="courseName"[^>]*?title="([^"]+)"', li) or
                re.search(r'class="courseName"[^>]*?>([^<]+)<', li) or
                re.search(r'<h3[^>]*?title="([^"]+)"', li) or
                re.search(r'title="([^"]+)"', li)
            )

            if cid_match and clazz_match:
                title = name_match.group(1).strip() if name_match else f"课程_{cid_match.group(1)}"
                if title in ["移动到", "退课"]:
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
        全量解析课程章节目录树：
        适配超星最新 mooc-ans 架构与传统 studentstudyAjax 架构
        """
        chapters = []

        # 方式 1：通过 stucoursemiddle 获取学生端真实课程门户并提取小节（新版超星主干架构）
        middle_url = f"https://mooc1-2.chaoxing.com/visit/stucoursemiddle?courseid={course_id}&clazzid={clazz_id}&vc=1"
        try:
            resp_mid = self.session.get(middle_url, timeout=12)
            if resp_mid.ok:
                html = resp_mid.text
                # 匹配章节小节节点：href="/mooc-ans/mycourse/studentstudy?chapterId=...&courseId=..."
                pattern = re.compile(
                    r'href=[\'"]([^\'"]*?chapterId=(\d+)[^\'"]*?)[\'"].*?'
                    r'<span class="chapterNumber">([^<]*)</span>.*?'
                    r'<span class="articlename"[^>]*?title="([^"]+)"',
                    re.S
                )
                matches = pattern.findall(html)
                for study_url, chapter_id, num, name in matches:
                    title_full = f"{num.strip()} {name.strip()}".strip()
                    chapters.append({
                        "chapter_id": chapter_id,
                        "title": title_full,
                        "study_url": study_url
                    })
        except Exception:
            pass

        # 方式 2：如果方式 1 为空，尝试旧版 studentstudyAjax 解析
        if not chapters:
            ajax_url = f"https://mooc1-1.chaoxing.com/mycourse/studentstudyAjax?courseId={course_id}&clazzid={clazz_id}&cpi={cpi}"
            try:
                resp_ajax = self.session.get(ajax_url, timeout=10)
                if resp_ajax.ok and len(resp_ajax.text) > 20:
                    html_ajax = resp_ajax.text
                    node_pattern = re.compile(r'href="javascript:void\(0\);"[^>]*?onclick="[^"]*?getTeacherAjax\(\'(\d+)\'[^"]*?\)"[^>]*?title="([^"]+)"', re.S)
                    matches_ajax = node_pattern.findall(html_ajax)
                    for chapter_id, title in matches_ajax:
                        chapters.append({
                            "chapter_id": chapter_id,
                            "title": title.strip(),
                            "study_url": ""
                        })
            except Exception:
                pass

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
