import os
import time
import json
import mimetypes
import requests
from .session import XuexitongSession

class XuexitongUploader:
    """
    学习通云盘与多媒体资源上传引擎
    用于上传作业附件（Word、PDF、图片）或拍照签到图片等合法资源
    """
    def __init__(self, session_manager: XuexitongSession):
        self.sm = session_manager
        self.session = session_manager.session

    def upload_pan_file(self, file_path: str):
        """
        上传文件至超星云盘，换取唯一 objectId 与下载链接
        接口：https://pan-yz.chaoxing.com/upload
        """
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        filename = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        upload_url = "https://pan-yz.chaoxing.com/upload"
        # 云盘上传需要携带 puid 与 _token 或凭据 Cookie
        puid = self.sm.session.cookies.get("UID", "")
        params = {
            "_token": "",
            "puid": puid
        }

        with open(file_path, "rb") as f:
            files = {
                "file": (filename, f, mime_type)
            }
            headers = {
                "Referer": "https://pan-yz.chaoxing.com/"
            }
            resp = self.session.post(upload_url, params=params, files=files, headers=headers, timeout=60)

        try:
            res_json = resp.json()
            # 云盘返回通常包含 objectId 或 crc、url
            return {
                "success": True,
                "filename": filename,
                "size": os.path.getsize(file_path),
                "object_id": res_json.get("objectId") or res_json.get("data", {}).get("objectId", ""),
                "raw_response": res_json
            }
        except Exception:
            return {
                "success": False,
                "message": resp.text[:120]
            }
