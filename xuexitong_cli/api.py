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
        """获取当前用户加入的所有课程"""
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
        """全量解析课程章节目录树"""
        chapters = []
        middle_url = f"https://mooc1-2.chaoxing.com/visit/stucoursemiddle?courseid={course_id}&clazzid={clazz_id}&vc=1"
        try:
            resp_mid = self.session.get(middle_url, timeout=12)
            if resp_mid.ok:
                html = resp_mid.text
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
        return chapters

    def get_chapter_card_attachments(self, course_id: str, clazz_id: str, chapter_id: str):
        """
        深度穿透小节的多个标签页 (num=0, 1, 2...)，拉取该小节名下所有真实的挂载任务（视频、随堂测验等）
        """
        attachments = []
        cpi = self.sm.session.cookies.get("cpi", "485218371")
        for num in range(5):
            url = f"https://mooc1-2.chaoxing.com/mooc-ans/knowledge/cards?clazzid={clazz_id}&courseid={course_id}&knowledgeid={chapter_id}&num={num}&ut=s&cpi={cpi}"
            try:
                resp = self.session.get(url, timeout=8)
                if not resp.ok or len(resp.text) < 100:
                    break
                m = re.search(r'mArg\s*=\s*(\{.*?\});', resp.text, re.S) or re.search(r'\$mArg\s*=\s*(\{.*?\});', resp.text, re.S)
                if m:
                    data = json.loads(m.group(1))
                    card_atts = data.get("attachments", [])
                    if not card_atts:
                        break
                    for item in card_atts:
                        item["_card_num"] = num
                        attachments.append(item)
                else:
                    break
            except Exception:
                break
        return attachments

    def get_video_metadata(self, object_id: str):
        """获取视频对象的真实物理时长与信息"""
        url = f"https://mooc1-1.chaoxing.com/ananas/status/{object_id}?k=2237&_flag=1"
        headers = {"Referer": "https://mooc1-1.chaoxing.com/ananas/modules/video/index.html"}
        try:
            resp = self.session.get(url, headers=headers, timeout=8)
            if resp.ok:
                data = resp.json()
                return {
                    "duration": float(data.get("duration", 0)),
                    "filename": data.get("filename", ""),
                    "dtoken": data.get("dtoken", "")
                }
        except Exception:
            pass
        return {"duration": 300.0, "filename": "", "dtoken": ""}

    def report_video_progress(self, clazz_id: str, jobid: str, object_id: str, duration: float, playing_time: float, clip_time: str = "0", is_drag: int = 0):
        """上报视频播放进度（核心心跳发包）"""
        enc = calculate_enc(clazz_id, jobid, object_id, playing_time, duration, clip_time)
        clip_str = f"0_{int(duration)}" if clip_time == "0" else str(clip_time)
        
        cpi = self.sm.session.cookies.get("cpi", "485218371")
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
