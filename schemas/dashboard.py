"""仪表盘响应模型。"""

from __future__ import annotations

from pydantic import BaseModel

from schemas.common import ApiResponse


class DashboardStats(BaseModel):
    """统计卡片数据。"""

    totalUsers: int
    totalProducts: int
    totalOrders: int
    cartCount: int
    revenueToday: int | float
    revenueMonth: int | float


class TrendPoint(BaseModel):
    """趋势数据点。"""

    date: str
    value: int | float


class DashboardStatsResponse(ApiResponse):
    """统计卡片响应。"""

    data: DashboardStats | None = None


class DashboardTrendsResponse(ApiResponse):
    """趋势数据响应：data 为数组。"""

    data: list[TrendPoint] | None = None
