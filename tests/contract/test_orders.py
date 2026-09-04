"""订单接口契约用例：列表/详情/改状态。"""

from __future__ import annotations

import pytest

from apis.orders import OrderApi
from schemas.orders import OrderListResponse, OrderResponse

# ---- 列表（API-078~080）----


@pytest.mark.smoke
@pytest.mark.regression
def test_orders_list_success(admin_client):
    """API-078：分页查询订单列表成功。"""
    api = OrderApi(admin_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert "items" in resp.json()["data"]
    OrderListResponse.model_validate(resp.json())


@pytest.mark.regression
def test_orders_list_without_login_unauthorized(anon_client):
    """API-079：未登录查询订单列表 → 401。"""
    api = OrderApi(anon_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_orders_list_as_user(user_client):
    """API-080：普通用户查询订单列表成功。"""
    api = OrderApi(user_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ---- 详情（API-081~084）----


@pytest.mark.regression
def test_get_order_success(admin_client):
    """API-081：获取订单详情成功。"""
    api = OrderApi(admin_client)
    first = api.list(page=1, pageSize=1).json()["data"]["items"][0]
    resp = api.get(first["id"])
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == first["id"]
    OrderResponse.model_validate(resp.json())


@pytest.mark.regression
def test_get_order_not_found(admin_client):
    """API-082：订单不存在 → 404。"""
    api = OrderApi(admin_client)
    resp = api.get(999999)
    assert resp.status_code == 404
    assert "订单不存在" in resp.json()["message"]


@pytest.mark.regression
def test_get_order_without_login_unauthorized(anon_client):
    """API-083：未登录获取订单详情 → 401。"""
    api = OrderApi(anon_client)
    resp = api.get(5)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_get_order_as_user(user_client):
    """API-084：普通用户获取订单详情成功。"""
    api = OrderApi(user_client)
    first = api.list(page=1, pageSize=1).json()["data"]["items"][0]
    resp = api.get(first["id"])
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ---- 改状态（API-085~090）----


@pytest.mark.regression
def test_update_order_status_success(admin_client):
    """API-085：修改订单状态成功。"""
    api = OrderApi(admin_client)
    first = api.list(page=1, pageSize=1).json()["data"]["items"][0]
    original_status = first["status"]
    try:
        resp = api.update_status(first["id"], "pending_payment")
        assert resp.status_code == 200
        assert resp.json()["success"] is True
    finally:
        # 还原原状态
        api.update_status(first["id"], original_status)


@pytest.mark.regression
def test_update_order_status_without_login_unauthorized(anon_client):
    """API-086：未登录改状态 → 401。"""
    api = OrderApi(anon_client)
    resp = api.update_status(5, "pending_payment")
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_update_order_status_as_user_forbidden(user_client):
    """API-087：普通用户改状态 → 403。"""
    api = OrderApi(user_client)
    resp = api.update_status(5, "pending_payment")
    assert resp.status_code == 403
    assert "无权限访问" in resp.json()["message"]


@pytest.mark.regression
def test_update_order_status_invalid(admin_client):
    """API-088：无效状态 → 400。"""
    api = OrderApi(admin_client)
    first = api.list(page=1, pageSize=1).json()["data"]["items"][0]
    resp = api.update_status(first["id"], "not_a_status")
    assert resp.status_code == 400
    assert "无效的状态" in resp.json()["message"]


@pytest.mark.regression
def test_update_order_status_missing_field(admin_client):
    """API-089：缺少 status 字段 → 400。"""
    api = OrderApi(admin_client)
    first = api.list(page=1, pageSize=1).json()["data"]["items"][0]
    resp = admin_client.put(f"/api/orders/{first['id']}/status", json={})
    assert resp.status_code == 400
    assert "无效的状态" in resp.json()["message"]


@pytest.mark.regression
def test_update_order_status_not_found(admin_client):
    """API-090：订单不存在改状态 → 404。"""
    api = OrderApi(admin_client)
    resp = api.update_status(999999, "pending_payment")
    assert resp.status_code == 404
    assert "订单不存在" in resp.json()["message"]
