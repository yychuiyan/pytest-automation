"""仪表盘接口封装。"""

from __future__ import annotations

from requests import Response

from apis.base_api import BaseApi


class DashboardApi(BaseApi):
    """仪表盘接口：统计卡片/趋势。"""

    # 统计卡片：GET /api/dashboard/stats
    def stats(self) -> Response:
        return self.client.get("/api/dashboard/stats")

    # 趋势数据：GET /api/dashboard/trends
    def trends(self) -> Response:
        return self.client.get("/api/dashboard/trends")
