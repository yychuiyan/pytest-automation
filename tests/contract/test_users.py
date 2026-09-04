"""用户管理接口契约用例：列表/详情/增删改/改角色。"""

from __future__ import annotations

import time

import pytest

from apis.users import UserApi
from core.config import config
from schemas.users import UserListResponse, UserResponse


def _stamp() -> str:
    return str(int(time.time() * 1000))


def _create_test_user(api: UserApi, prefix: str = "auto") -> int:
    """创建一个测试用户并返回 id；遇 429 限流则 skip 整个用例。"""
    stamp = _stamp()
    created = api.create(
        {
            "username": f"{prefix}_{stamp}",
            "password": "Test1234",
            "email": f"{prefix}_{stamp}@test.com",
            "role": "user",
        }
    )
    if created.status_code == 429:
        pytest.skip("线上写接口限流（429），稍后重跑")
    return created.json()["data"]["id"]


# ---- 列表（API-023~030）----


@pytest.mark.smoke
@pytest.mark.regression
def test_users_list_success(admin_client):
    """API-023：分页查询用户列表成功。"""
    api = UserApi(admin_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    data = resp.json()["data"]
    assert "items" in data
    assert data["page"] == 1
    assert data["pageSize"] == 5
    UserListResponse.model_validate(resp.json())


@pytest.mark.regression
def test_users_list_without_login_unauthorized(anon_client):
    """API-026：未登录查询用户列表 → 401。"""
    api = UserApi(anon_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_users_list_as_user(user_client):
    """API-027：普通用户查询用户列表成功（users.read）。"""
    api = UserApi(user_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.regression
def test_users_list_search_by_keyword(admin_client):
    """API-024：按关键词搜索用户。"""
    api = UserApi(admin_client)
    resp = api.list(page=1, pageSize=10, keyword="炊烟")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert "items" in resp.json()["data"]


@pytest.mark.regression
def test_users_list_filter_by_role(admin_client):
    """API-025：按角色筛选用户。"""
    api = UserApi(admin_client)
    resp = api.list(page=1, pageSize=10, role="admin")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    for item in resp.json()["data"]["items"]:
        assert item["role"] == "admin"


@pytest.mark.edge
def test_users_list_page_zero(admin_client):
    """API-028：page=0 返回空列表。"""
    api = UserApi(admin_client)
    resp = api.list(page=0, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["data"]["items"] == []


@pytest.mark.edge
def test_users_list_pagesize_zero(admin_client):
    """API-029：pageSize=0 返回空列表。"""
    api = UserApi(admin_client)
    resp = api.list(page=1, pageSize=0)
    assert resp.status_code == 200
    assert resp.json()["data"]["items"] == []


@pytest.mark.edge
def test_users_list_invalid_role(admin_client):
    """API-030：无效 role 返回空列表。"""
    api = UserApi(admin_client)
    resp = api.list(page=1, pageSize=5, role="nope")
    assert resp.status_code == 200
    assert resp.json()["data"]["items"] == []
    assert resp.json()["data"]["total"] == 0


# ---- 新增（API-031~035）----


@pytest.mark.regression
def test_create_user_success(admin_client):
    """API-031：管理员新增用户成功。"""
    stamp = _stamp()
    api = UserApi(admin_client)
    payload = {
        "username": f"auto_user_{stamp}",
        "password": "Test1234",
        "email": f"auto_user_{stamp}@test.com",
        "role": "user",
        "phone": "13900000000",
        "realName": "自动化用户",
    }
    resp = api.create(payload)
    # 线上写操作可能触发限流（429），属环境问题，跳过而非判失败
    if resp.status_code == 429:
        pytest.skip("线上写接口限流（429），稍后重跑")
    assert resp.status_code in (200, 201)
    assert resp.json()["success"] is True
    assert resp.json()["data"]["id"]
    # 后置清理
    api.remove(resp.json()["data"]["id"])


@pytest.mark.regression
def test_create_user_without_login_unauthorized(anon_client):
    """API-032：未登录新增用户 → 401。"""
    api = UserApi(anon_client)
    resp = api.create({"username": "auto_x", "password": "Test1234", "email": "x@test.com"})
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_create_user_as_user_forbidden(user_client):
    """API-033：普通用户新增用户 → 403。"""
    api = UserApi(user_client)
    resp = api.create({"username": "auto_x", "password": "Test1234", "email": "x@test.com"})
    assert resp.status_code == 403
    assert "无权限访问" in resp.json()["message"]


@pytest.mark.regression
def test_create_user_missing_required_fields(admin_client):
    """API-034：缺少必填字段 → 400。"""
    api = UserApi(admin_client)
    resp = api.create({"username": "auto_miss"})
    assert resp.status_code == 400
    assert "用户名、邮箱、密码为必填字段" in resp.json()["message"]


@pytest.mark.regression
def test_create_user_duplicate_username(admin_client):
    """API-035：用户名已存在 → 409。"""
    api = UserApi(admin_client)
    resp = api.create(
        {
            "username": config.unit.username,
            "password": "Test1234",
            "email": f"dup_{_stamp()}@test.com",
        }
    )
    assert resp.status_code == 409
    assert "用户名已存在" in resp.json()["message"]


# ---- 详情（API-036~040）----


@pytest.mark.regression
def test_get_user_success(admin_client):
    """API-036：获取用户详情成功。"""
    api = UserApi(admin_client)
    resp = api.get(1)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["data"]["id"] == 1
    UserResponse.model_validate(resp.json())


@pytest.mark.regression
def test_get_user_not_found(admin_client):
    """API-037：用户不存在 → 404。"""
    api = UserApi(admin_client)
    resp = api.get(999999)
    assert resp.status_code == 404
    assert "用户不存在" in resp.json()["message"]


@pytest.mark.regression
def test_get_user_without_login_unauthorized(anon_client):
    """API-038：未登录获取用户详情 → 401。"""
    api = UserApi(anon_client)
    resp = api.get(1)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_get_user_as_user(user_client):
    """API-039：普通用户获取用户详情成功。"""
    api = UserApi(user_client)
    resp = api.get(1)
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == 1


@pytest.mark.edge
def test_get_user_invalid_id(admin_client):
    """API-040：非法用户 id → 404。"""
    api = UserApi(admin_client)
    resp = api.get(999999)
    assert resp.status_code == 404


# ---- 编辑（API-041~044）----


@pytest.mark.regression
def test_update_user_success(admin_client):
    """API-041：管理员编辑测试用户成功。"""
    api = UserApi(admin_client)
    uid = _create_test_user(api, "auto_edit")
    try:
        resp = api.update(uid, {"realName": "自动化编辑", "phone": "13900000001"})
        assert resp.status_code == 200
        assert resp.json()["success"] is True
    finally:
        api.remove(uid)


@pytest.mark.regression
def test_update_user_without_login_unauthorized(anon_client):
    """API-042：未登录编辑用户 → 401。"""
    api = UserApi(anon_client)
    resp = api.update(1, {"realName": "x"})
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_update_user_as_user_forbidden(user_client):
    """API-043：普通用户编辑用户 → 403。"""
    api = UserApi(user_client)
    resp = api.update(3, {"realName": "x"})
    assert resp.status_code == 403
    assert "无权限访问" in resp.json()["message"]


@pytest.mark.regression
def test_update_user_not_found(admin_client):
    """API-044：编辑不存在用户 → 404。"""
    api = UserApi(admin_client)
    resp = api.update(999999, {"realName": "x"})
    assert resp.status_code == 404
    assert "用户不存在" in resp.json()["message"]


# ---- 删除（API-045~048）----


@pytest.mark.regression
def test_delete_user_success(admin_client):
    """API-045：管理员删除测试用户成功。"""
    api = UserApi(admin_client)
    uid = _create_test_user(api, "auto_del")
    resp = api.remove(uid)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.regression
def test_delete_user_without_login_unauthorized(anon_client):
    """API-046：未登录删除用户 → 401。"""
    api = UserApi(anon_client)
    resp = api.remove(12)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_delete_user_as_user_forbidden(user_client):
    """API-047：普通用户删除用户 → 403。"""
    api = UserApi(user_client)
    resp = api.remove(12)
    assert resp.status_code == 403
    assert "无权限访问" in resp.json()["message"]


@pytest.mark.regression
def test_delete_user_not_found(admin_client):
    """API-048：删除不存在用户 → 404。"""
    api = UserApi(admin_client)
    resp = api.remove(999999)
    assert resp.status_code == 404
    assert "用户不存在" in resp.json()["message"]


# ---- 改角色（API-049~054）----


@pytest.mark.regression
def test_change_role_success(admin_client):
    """API-049：管理员修改测试用户角色成功。"""
    api = UserApi(admin_client)
    uid = _create_test_user(api, "auto_role")
    try:
        resp = api.change_role(uid, "user")
        assert resp.status_code == 200
        assert resp.json()["success"] is True
    finally:
        api.remove(uid)


@pytest.mark.regression
def test_change_role_without_login_unauthorized(anon_client):
    """API-050：未登录改角色 → 401。"""
    api = UserApi(anon_client)
    resp = api.change_role(2, "user")
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_change_role_as_user_forbidden(user_client):
    """API-051：普通用户改角色 → 403。"""
    api = UserApi(user_client)
    resp = api.change_role(2, "admin")
    assert resp.status_code == 403
    assert "无权限访问" in resp.json()["message"]


@pytest.mark.regression
def test_change_role_invalid_role(admin_client):
    """API-052：无效角色 → 400。"""
    api = UserApi(admin_client)
    uid = _create_test_user(api, "auto_role2")
    try:
        resp = api.change_role(uid, "super")
        assert resp.status_code == 400
        assert "无效的角色" in resp.json()["message"]
    finally:
        api.remove(uid)


@pytest.mark.regression
def test_change_role_missing_role_field(admin_client):
    """API-053：缺少 role 字段 → 400。"""
    api = UserApi(admin_client)
    uid = _create_test_user(api, "auto_role3")
    try:
        resp = admin_client.put(f"/api/users/{uid}/role", json={})
        assert resp.status_code == 400
        assert "无效的角色" in resp.json()["message"]
    finally:
        api.remove(uid)


@pytest.mark.edge
def test_change_role_on_demo_account_forbidden(admin_client):
    """API-054：修改演示账号角色 → 403（演示账号保护）。"""
    api = UserApi(admin_client)
    resp = api.change_role(2, "admin")
    assert resp.status_code == 403
    assert "演示账号不可修改角色" in resp.json()["message"]
