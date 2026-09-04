"""仪表盘接口契约用例：stats / trends。"""

from __future__ import annotations

import pytest

from apis.dashboard import DashboardApi
from schemas.dashboard import DashboardStatsResponse, DashboardTrendsResponse


@pytest.mark.smoke
@pytest.mark.regression
def test_dashboard_stats_success(admin_client):
    """API-018：管理员获取统计卡片成功。"""
    api = DashboardApi(admin_client)
    resp = api.stats()
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    data = resp.json()["data"]
    for key in (
        "totalUsers",
        "totalProducts",
        "totalOrders",
        "cartCount",
        "revenueToday",
        "revenueMonth",
    ):
        assert key in data
    DashboardStatsResponse.model_validate(resp.json())


@pytest.mark.regression
def test_dashboard_stats_without_login_unauthorized(anon_client):
    """API-019：未登录获取统计 → 401。"""
    api = DashboardApi(anon_client)
    resp = api.stats()
    assert resp.status_code == 401
    assert resp.json()["success"] is False
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_dashboard_stats_as_user(user_client):
    """API-020：普通用户获取统计成功。"""
    api = DashboardApi(user_client)
    resp = api.stats()
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.regression
def test_dashboard_trends_success(admin_client):
    """API-021：获取趋势数据成功。"""
    api = DashboardApi(admin_client)
    resp = api.trends()
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    data = resp.json()["data"]
    assert isinstance(data, list)
    if data:
        assert "date" in data[0]
        assert "value" in data[0]
    DashboardTrendsResponse.model_validate(resp.json())


@pytest.mark.regression
def test_dashboard_trends_without_login_unauthorized(anon_client):
    """API-022：未登录获取趋势 → 401。"""
    api = DashboardApi(anon_client)
    resp = api.trends()
    assert resp.status_code == 401
    assert resp.json()["success"] is False
    assert "未登录" in resp.json()["message"]
