import re
import json
import time
import requests
from .session import XuexitongSession

class XuexitongSign:
    """
    学习通全类型签到逆向引擎
    覆盖常见签到类型：
    1. 普通签到 / 一键签到 (general)
    2. 手势签到 (gesture)
    3. 位置 / GPS 签到 (location)
    4. 签到码签到 (code)
    5. 二维码签到 (qrcode)
    6. 拍照签到 (photo)
    """
    def __init__(self, session_manager: XuexitongSession):
        self.sm = session_manager
        self.session = session_manager.session

    def get_active_signs(self, course_id: str, clazz_id: str):
        """
        获取当前班级正在进行中的未签到活动列表
        活动接口通常为：https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist
        """
        url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
        params = {
            "courseId": course_id,
            "classId": clazz_id,
            "uid": self.sm.session.cookies.get("UID", "")
        }
        resp = self.session.get(url, params=params, timeout=10)
        signs = []
        if not resp.ok:
            return signs

        try:
            data = resp.json()
            active_list = data.get("activeList", [])
            for item in active_list:
                # activeType == 2 代表签到活动, status == 1 代表进行中
                if item.get("activeType") == 2 and item.get("status") == 1:
                    signs.append({
                        "active_id": str(item.get("id")),
                        "name": item.get("nameOne", "签到活动"),
                        "other_id": str(item.get("otherId", "")), # 0普通/手势, 2二维码, 3位置, 4签到码
                        "start_time": item.get("createtime"),
                    })
        except Exception:
            pass
        return signs

    def sign_general(self, active_id: str):
        """
        1. 普通一键签到 / 手势签到
        """
        url = "https://mobilelearn.chaoxing.com/widget/sign/pcThirdSign"
        params = {"activeId": active_id}
        resp = self.session.get(url, params=params, timeout=10)
        return self._parse_sign_response(resp.text)

    def sign_location(self, active_id: str, address: str = "学校教学楼", lat: float = 34.757975, lng: float = 113.665412):
        """
        2. 位置 / GPS 签到 (可自定义经纬度坐标与地址名)
        """
        url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/receivedAttendanceSheet"
        params = {
            "activeId": active_id,
            "address": address,
            "latitude": lat,
            "longitude": lng,
            "fid": "0",
            "appType": "15"
        }
        resp = self.session.get(url, params=params, timeout=10)
        return self._parse_sign_response(resp.text)

    def sign_code(self, active_id: str, sign_code: str):
        """
        3. 签到码签到 (输入 4 位数字或特定手势轨迹)
        """
        url = "https://mobilelearn.chaoxing.com/widget/sign/pcThirdSign"
        params = {
            "activeId": active_id,
            "signCode": sign_code
        }
        resp = self.session.get(url, params=params, timeout=10)
        return self._parse_sign_response(resp.text)

    def sign_qrcode(self, active_id: str, enc: str = ""):
        """
        4. 二维码扫码签到 (逆向老师投屏上的 enc 动态盐)
        """
        url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/receivedAttendanceSheet"
        params = {
            "activeId": active_id,
            "enc": enc,
            "fid": "0",
            "appType": "15"
        }
        resp = self.session.get(url, params=params, timeout=10)
        return self._parse_sign_response(resp.text)

    def sign_photo(self, active_id: str, object_id: str = ""):
        """
        5. 拍照签到 (附带云盘图片 objectId)
        """
        url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/receivedAttendanceSheet"
        params = {
            "activeId": active_id,
            "objectId": object_id,
            "fid": "0",
            "appType": "15"
        }
        resp = self.session.get(url, params=params, timeout=10)
        return self._parse_sign_response(resp.text)

    def _parse_sign_response(self, text: str):
        if "您已签到过了" in text or "成功" in text or "success" in text.lower():
            return {"success": True, "message": "签到成功 / 已签到"}
        elif "不在签到范围内" in text:
            return {"success": False, "message": "位置超出签到范围"}
        elif "验证码错误" in text or "签到码错误" in text:
            return {"success": False, "message": "签到码或手势不匹配"}
        else:
            return {"success": False, "message": text[:80] if text else "未知响应"}
