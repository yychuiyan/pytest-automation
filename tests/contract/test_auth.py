"""认证接口契约用例：logout / me / register，以及 login 的剩余负向场景。

login 的成功/错误密码/角色参数化已由 test_login.py / test_login_param.py 覆盖，
本文件补全 logout、me、register 及 login 的缺参/空字段场景。
"""

from __future__ import annotations

import pytest

from apis.auth import AuthApi
from core.config import config
from schemas.auth import LoginResponse

# ---- login 剩余负向（API-005~009）----


@pytest.mark.regression
def test_login_empty_password(http_client):
    """API-005：空密码登录失败 → 401。"""
    api = AuthApi(http_client)
    resp = api.login(config.admin.username, "")
    assert resp.status_code == 401
    assert resp.json()["success"] is False


@pytest.mark.regression
def test_login_empty_username(http_client):
    """API-006：空用户名登录失败 → 401。"""
    api = AuthApi(http_client)
    resp = api.login("", config.admin.password)
    assert resp.status_code == 401
    assert resp.json()["success"] is False


@pytest.mark.regression
def test_login_missing_username(http_client):
    """API-007：缺少 username 字段 → 401。"""
    resp = http_client.post("/api/auth/login", json={"password": config.admin.password})
    assert resp.status_code == 401
    assert resp.json()["success"] is False


@pytest.mark.regression
def test_login_missing_password(http_client):
    """API-008：缺少 password 字段 → 401。"""
    resp = http_client.post("/api/auth/login", json={"username": config.admin.username})
    assert resp.status_code == 401
    assert resp.json()["success"] is False


@pytest.mark.regression
def test_login_empty_body(http_client):
    """API-009：空请求体 → 401。"""
    resp = http_client.post("/api/auth/login", json={})
    assert resp.status_code == 401
    assert resp.json()["success"] is False


# ---- logout（API-010~011）----


@pytest.mark.regression
def test_logout_then_me_unauthorized(http_client):
    """API-010：登录→登出→再访问 me 应 401。"""
    api = AuthApi(http_client)
    resp = api.login(config.admin.username, config.admin.password)
    assert resp.status_code == 200

    logout = api.logout()
    assert logout.status_code == 200
    assert logout.json()["success"] is True

    me = api.me()
    assert me.status_code == 401
    assert me.json()["success"] is False


@pytest.mark.edge
def test_logout_without_login_still_ok(anon_client):
    """API-011：未登录直接 logout 仍 200（线上幂等）。"""
    api = AuthApi(anon_client)
    resp = api.logout()
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ---- me（API-012~013）----


@pytest.mark.smoke
@pytest.mark.regression
def test_me_success(admin_client):
    """API-012：已登录获取当前用户信息成功。"""
    api = AuthApi(admin_client)
    resp = api.me()
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["data"]["username"] == config.admin.username
    assert resp.json()["data"]["role"] == "admin"
    LoginResponse.model_validate(resp.json())


@pytest.mark.regression
def test_me_without_login_unauthorized(anon_client):
    """API-013：未登录访问 me → 401。"""
    api = AuthApi(anon_client)
    resp = api.me()
    assert resp.status_code == 401
    assert resp.json()["success"] is False
    assert "未登录" in resp.json()["message"]


# ---- register（API-014~017）----


@pytest.mark.regression
def test_register_success(http_client):
    """API-014：公开注册新用户成功。"""
    import time

    stamp = int(time.time() * 1000)
    username = f"auto_reg_{stamp}"
    email = f"auto_{stamp}@test.com"
    api = AuthApi(http_client)
    resp = api.register(username, "Test1234", email)
    if resp.status_code == 429:
        pytest.skip("线上注册接口限流（429），稍后重跑")
    assert resp.status_code in (200, 201)
    assert resp.json()["success"] is True


@pytest.mark.regression
def test_register_duplicate_username(http_client):
    """API-015：重复用户名注册 → 409。"""
    import time

    stamp = int(time.time() * 1000)
    api = AuthApi(http_client)
    resp = api.register(config.admin.username, "Test1234", f"dup_{stamp}@test.com")
    assert resp.status_code == 409
    assert resp.json()["success"] is False
    assert "用户名已被注册" in resp.json()["message"]


@pytest.mark.regression
def test_register_username_too_short(http_client):
    """API-016：用户名少于 3 个字符 → 400。"""
    api = AuthApi(http_client)
    resp = api.register("ab", "Test1234", "ab@test.com")
    assert resp.status_code == 400
    assert resp.json()["success"] is False
    assert "用户名至少 3 个字符" in resp.json()["message"]


@pytest.mark.regression
def test_register_invalid_email(http_client):
    """API-017：缺少有效邮箱 → 400。"""
    api = AuthApi(http_client)
    resp = api.register("auto_reg_noemail", "Test1234", "")
    assert resp.status_code == 400
    assert resp.json()["success"] is False
    assert "请输入有效的邮箱地址" in resp.json()["message"]
