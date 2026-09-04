"""文件上传接口封装。

注意：上传使用 multipart/form-data，不能用默认的 application/json 请求头。
这里通过 files 参数让 requests 自动设置 Content-Type，并临时清除 session 的 json 头。
"""

from __future__ import annotations

from pathlib import Path

from requests import Response

from apis.base_api import BaseApi


class UploadApi(BaseApi):
    """文件上传接口：multipart/form-data。"""

    def upload(self, file_path: str, field_name: str = "file") -> Response:
        """上传文件。线上要求图片文件。

        Args:
            file_path: 本地文件路径。
            field_name: 表单字段名，默认 file。
        """
        path = Path(file_path)
        with path.open("rb") as f:
            files = {field_name: (path.name, f, "application/octet-stream")}
            # 上传时临时去掉默认的 application/json 头，让 requests 自动生成 multipart boundary
            saved = self.client.session.headers.get("Content-Type")
            if saved:
                self.client.session.headers.pop("Content-Type")
            try:
                resp = self.client.post("/api/upload", files=files)
            finally:
                if saved:
                    self.client.session.headers["Content-Type"] = saved
        return resp

    def upload_no_file(self) -> Response:
        """不携带 file 字段调用上传接口（用于测「请选择图片文件」）。"""
        saved = self.client.session.headers.get("Content-Type")
        if saved:
            self.client.session.headers.pop("Content-Type")
        try:
            resp = self.client.post("/api/upload")
        finally:
            if saved:
                self.client.session.headers["Content-Type"] = saved
        return resp
