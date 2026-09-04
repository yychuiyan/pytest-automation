"""购物车接口契约用例：列表/添加/改数量/删除。"""

from __future__ import annotations

import pytest

from apis.cart import CartApi
from apis.products import ProductApi


def _existing_product_id(admin_client) -> int:
    """取一个真实存在的商品 id，供添加购物车用。"""
    api = ProductApi(admin_client)
    return api.list(page=1, pageSize=1).json()["data"]["items"][0]["id"]


# ---- 列表（API-091~093）----


@pytest.mark.smoke
@pytest.mark.regression
def test_cart_list_success(admin_client):
    """API-091：获取购物车列表成功。"""
    api = CartApi(admin_client)
    resp = api.list()
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert isinstance(resp.json()["data"], list)


@pytest.mark.regression
def test_cart_list_without_login_unauthorized(anon_client):
    """API-092：未登录获取购物车 → 401。"""
    api = CartApi(anon_client)
    resp = api.list()
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_cart_list_as_user(user_client):
    """API-093：普通用户获取自己的购物车成功。"""
    api = CartApi(user_client)
    resp = api.list()
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ---- 添加（API-094~099）----


@pytest.mark.regression
def test_cart_add_success(admin_client):
    """API-094：添加商品到购物车成功。"""
    api = CartApi(admin_client)
    pid = _existing_product_id(admin_client)
    resp = api.add(pid, 1)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["data"]["productId"] == pid
    # 后置清理：找到刚加入的项并删除
    items = api.list().json()["data"]
    for item in items:
        if item["productId"] == pid:
            api.remove(item["id"])
            break


@pytest.mark.regression
def test_cart_add_duplicate_updates_quantity(admin_client):
    """API-095：重复添加同一商品更新数量。"""
    api = CartApi(admin_client)
    pid = _existing_product_id(admin_client)
    api.add(pid, 1)
    try:
        resp = api.add(pid, 1)
        assert resp.status_code == 200
        assert "已更新数量" in resp.json()["message"]
    finally:
        items = api.list().json()["data"]
        for item in items:
            if item["productId"] == pid:
                api.remove(item["id"])
                break


@pytest.mark.regression
def test_cart_add_without_login_unauthorized(anon_client, admin_client):
    """API-096：未登录添加购物车 → 401。"""
    pid = _existing_product_id(admin_client)
    api = CartApi(anon_client)
    resp = api.add(pid, 1)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_cart_add_nonexistent_product(admin_client):
    """API-097：添加不存在商品 → 404。"""
    api = CartApi(admin_client)
    resp = api.add(999999, 1)
    assert resp.status_code == 404
    assert "商品不存在" in resp.json()["message"]


@pytest.mark.regression
def test_cart_add_missing_product_id(admin_client):
    """API-098：缺少 productId → 404。"""
    resp = admin_client.post("/api/cart", json={"quantity": 1})
    assert resp.status_code == 404
    assert "商品不存在" in resp.json()["message"]


@pytest.mark.edge
def test_cart_add_zero_quantity_still_ok(admin_client):
    """API-099：quantity=0 仍返回成功（线上已知差异，记为边界）。"""
    api = CartApi(admin_client)
    pid = _existing_product_id(admin_client)
    api.add(pid, 1)
    try:
        resp = api.add(pid, 0)
        assert resp.status_code == 200
        assert resp.json()["success"] is True
    finally:
        items = api.list().json()["data"]
        for item in items:
            if item["productId"] == pid:
                api.remove(item["id"])
                break


# ---- 改数量（API-100~103）----


@pytest.mark.regression
def test_cart_update_quantity_success(admin_client):
    """API-100：修改购物车商品数量成功。"""
    cart = CartApi(admin_client)
    pid = _existing_product_id(admin_client)
    cart.add(pid, 1)
    items = cart.list().json()["data"]
    item_id = next(i["id"] for i in items if i["productId"] == pid)
    try:
        resp = cart.update_quantity(item_id, 2)
        assert resp.status_code == 200
        assert resp.json()["success"] is True
    finally:
        cart.remove(item_id)


@pytest.mark.regression
def test_cart_update_without_login_unauthorized(anon_client):
    """API-101：未登录改购物车 → 401。"""
    api = CartApi(anon_client)
    resp = api.update_quantity(2, 1)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_cart_update_not_found(admin_client):
    """API-102：修改不存在购物车项 → 404。"""
    api = CartApi(admin_client)
    resp = api.update_quantity(999999, 1)
    assert resp.status_code == 404
    assert "购物车项不存在" in resp.json()["message"]


@pytest.mark.regression
def test_cart_update_other_user_item_not_found(user_client, admin_client):
    """API-103：普通用户改管理员购物车项 → 404（按用户隔离）。"""
    cart = CartApi(admin_client)
    pid = _existing_product_id(admin_client)
    cart.add(pid, 1)
    items = cart.list().json()["data"]
    admin_item_id = items[-1]["id"]
    try:
        user_cart = CartApi(user_client)
        resp = user_cart.update_quantity(admin_item_id, 1)
        assert resp.status_code == 404
        assert "购物车项不存在" in resp.json()["message"]
    finally:
        cart.remove(admin_item_id)


# ---- 删除（API-104~107）----


@pytest.mark.regression
def test_cart_remove_success(admin_client):
    """API-104：删除购物车商品成功。"""
    cart = CartApi(admin_client)
    pid = _existing_product_id(admin_client)
    cart.add(pid, 1)
    items = cart.list().json()["data"]
    item_id = next(i["id"] for i in items if i["productId"] == pid)
    resp = cart.remove(item_id)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.regression
def test_cart_remove_without_login_unauthorized(anon_client):
    """API-105：未登录删除购物车 → 401。"""
    api = CartApi(anon_client)
    resp = api.remove(2)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_cart_remove_not_found(admin_client):
    """API-106：删除不存在购物车项 → 404。"""
    api = CartApi(admin_client)
    resp = api.remove(999999)
    assert resp.status_code == 404
    assert "购物车项不存在" in resp.json()["message"]


@pytest.mark.regression
def test_cart_remove_other_user_item_not_found(user_client, admin_client):
    """API-107：普通用户删管理员购物车项 → 404（按用户隔离）。"""
    cart = CartApi(admin_client)
    pid = _existing_product_id(admin_client)
    cart.add(pid, 1)
    items = cart.list().json()["data"]
    admin_item_id = items[-1]["id"]
    try:
        user_cart = CartApi(user_client)
        resp = user_cart.remove(admin_item_id)
        assert resp.status_code == 404
        assert "购物车项不存在" in resp.json()["message"]
    finally:
        cart.remove(admin_item_id)
