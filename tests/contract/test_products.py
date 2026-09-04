"""商品接口契约用例：列表/详情/增删改/分类。"""

from __future__ import annotations

import time

import pytest

from apis.products import ProductApi
from schemas.products import CategoryListResponse, ProductListResponse, ProductResponse


def _stamp() -> str:
    return str(int(time.time() * 1000))


def _create_test_product(api: ProductApi, prefix: str = "auto_p") -> int:
    """创建一个测试商品并返回 id；遇 429 限流则 skip 整个用例。"""
    created = api.create({"name": f"{prefix}_{_stamp()}", "price": 99, "originalPrice": 99, "status": "on"})
    if created.status_code == 429:
        pytest.skip("线上写接口限流（429），稍后重跑")
    return created.json()["data"]["id"]


# ---- 列表（API-055~057）----


@pytest.mark.smoke
@pytest.mark.regression
def test_products_list_success(admin_client):
    """API-055：分页查询商品列表成功。"""
    api = ProductApi(admin_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert "items" in resp.json()["data"]
    ProductListResponse.model_validate(resp.json())


@pytest.mark.regression
def test_products_list_without_login_unauthorized(anon_client):
    """API-056：未登录查询商品列表 → 401。"""
    api = ProductApi(anon_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_products_list_as_user(user_client):
    """API-057：普通用户查询商品列表成功。"""
    api = ProductApi(user_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ---- 新增（API-058~062）----


@pytest.mark.regression
def test_create_product_success(admin_client):
    """API-058：新增商品成功。"""
    api = ProductApi(admin_client)
    payload = {
        "name": f"自动化商品_{_stamp()}",
        "price": 99,
        "originalPrice": 129,
        "stock": 10,
        "category": "未分类",
        "status": "on",
        "description": "自动化创建",
    }
    resp = api.create(payload)
    if resp.status_code == 429:
        pytest.skip("线上写接口限流（429），稍后重跑")
    assert resp.status_code in (200, 201)
    assert resp.json()["success"] is True
    assert resp.json()["data"]["id"]
    api.remove(resp.json()["data"]["id"])


@pytest.mark.regression
def test_create_product_without_login_unauthorized(anon_client):
    """API-059：未登录新增商品 → 401。"""
    api = ProductApi(anon_client)
    resp = api.create({"name": "x", "price": 1})
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_create_product_as_user_forbidden(user_client):
    """API-060：普通用户新增商品 → 403。"""
    api = ProductApi(user_client)
    resp = api.create({"name": "x", "price": 1})
    assert resp.status_code == 403
    assert "无权限访问" in resp.json()["message"]


@pytest.mark.regression
def test_create_product_missing_name(admin_client):
    """API-061：缺少名称 → 400。"""
    api = ProductApi(admin_client)
    resp = api.create({"price": 1})
    assert resp.status_code == 400
    assert "商品名称和价格为必填项" in resp.json()["message"]


@pytest.mark.regression
def test_create_product_missing_price(admin_client):
    """API-062：缺少价格 → 400。"""
    api = ProductApi(admin_client)
    resp = api.create({"name": "onlyname"})
    assert resp.status_code == 400
    assert "商品名称和价格为必填项" in resp.json()["message"]


# ---- 详情（API-063~066）----


@pytest.mark.regression
def test_get_product_success(admin_client):
    """API-063：获取商品详情成功（取列表第一个真实 id）。"""
    api = ProductApi(admin_client)
    first = api.list(page=1, pageSize=1).json()["data"]["items"][0]
    resp = api.get(first["id"])
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == first["id"]
    ProductResponse.model_validate(resp.json())


@pytest.mark.regression
def test_get_product_not_found(admin_client):
    """API-064：商品不存在 → 404。"""
    api = ProductApi(admin_client)
    resp = api.get(999999)
    assert resp.status_code == 404
    assert "商品不存在" in resp.json()["message"]


@pytest.mark.regression
def test_get_product_without_login_unauthorized(anon_client):
    """API-065：未登录获取商品详情 → 401。"""
    api = ProductApi(anon_client)
    resp = api.get(17)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_get_product_as_user(user_client):
    """API-066：普通用户获取商品详情成功。"""
    api = ProductApi(user_client)
    first = api.list(page=1, pageSize=1).json()["data"]["items"][0]
    resp = api.get(first["id"])
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ---- 编辑（API-067~070）----


@pytest.mark.regression
def test_update_product_success(admin_client):
    """API-067：编辑商品成功。"""
    api = ProductApi(admin_client)
    pid = _create_test_product(api, "auto_p")
    try:
        resp = api.update(pid, {"name": "自动化商品_已编辑", "price": 88})
        assert resp.status_code == 200
        assert resp.json()["success"] is True
    finally:
        api.remove(pid)


@pytest.mark.regression
def test_update_product_without_login_unauthorized(anon_client):
    """API-068：未登录编辑商品 → 401。"""
    api = ProductApi(anon_client)
    resp = api.update(17, {"name": "x"})
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_update_product_as_user_forbidden(user_client):
    """API-069：普通用户编辑商品 → 403。"""
    api = ProductApi(user_client)
    resp = api.update(17, {"price": 1})
    assert resp.status_code == 403
    assert "无权限访问" in resp.json()["message"]


@pytest.mark.regression
def test_update_product_not_found(admin_client):
    """API-070：编辑不存在商品 → 404。"""
    api = ProductApi(admin_client)
    resp = api.update(999999, {"name": "x"})
    assert resp.status_code == 404
    assert "商品不存在" in resp.json()["message"]


# ---- 删除（API-071~074）----


@pytest.mark.regression
def test_delete_product_success(admin_client):
    """API-071：删除商品成功。"""
    api = ProductApi(admin_client)
    pid = _create_test_product(api, "auto_del_p")
    resp = api.remove(pid)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.regression
def test_delete_product_without_login_unauthorized(anon_client):
    """API-072：未登录删除商品 → 401。"""
    api = ProductApi(anon_client)
    resp = api.remove(17)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_delete_product_as_user_forbidden(user_client):
    """API-073：普通用户删除商品 → 403。"""
    api = ProductApi(user_client)
    resp = api.remove(17)
    assert resp.status_code == 403
    assert "无权限访问" in resp.json()["message"]


@pytest.mark.regression
def test_delete_product_not_found(admin_client):
    """API-074：删除不存在商品 → 404。"""
    api = ProductApi(admin_client)
    resp = api.remove(999999)
    assert resp.status_code == 404
    assert "商品不存在" in resp.json()["message"]


# ---- 分类（API-075~077）----


@pytest.mark.smoke
@pytest.mark.regression
def test_categories_success(admin_client):
    """API-075：获取商品分类列表成功。"""
    api = ProductApi(admin_client)
    resp = api.categories()
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert isinstance(resp.json()["data"], list)
    if resp.json()["data"]:
        assert "id" in resp.json()["data"][0]
        assert "name" in resp.json()["data"][0]
    CategoryListResponse.model_validate(resp.json())


@pytest.mark.regression
def test_categories_without_login_unauthorized(anon_client):
    """API-076：未登录获取分类 → 401。"""
    api = ProductApi(anon_client)
    resp = api.categories()
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_categories_as_user(user_client):
    """API-077：普通用户获取分类成功。"""
    api = ProductApi(user_client)
    resp = api.categories()
    assert resp.status_code == 200
    assert resp.json()["success"] is True
