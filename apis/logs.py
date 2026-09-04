"""操作日志接口封装。"""

from __future__ import annotations

from typing import Any

from requests import Response

from apis.base_api import BaseApi


class LogApi(BaseApi):
    """操作日志接口：分页查询。"""

    # 操作日志列表：GET /api/logs?page=&pageSize=
    def list(self, **query: Any) -> Response:
        return self.client.get("/api/logs", params=query)
