"""跨接口流程：登录 → me → 用户列表。"""

from __future__ import annotations

import pytest

# 配置中心：从 .env 读凭证，不硬编码明文
from core.config import config

# 接口封装：通过 AuthApi 调用（跨接口流程用封装层串联）
from apis.auth import AuthApi


@pytest.mark.regression
def test_login_then_me(http_client):
    """流程：登录后带 cookie 访问 me，应返回当前用户。"""
    # ① 通过 AuthApi 登录（Session 自动保存 auth_token cookie）
    api = AuthApi(http_client)
    resp = api.login(config.admin.username, config.admin.password)
    assert resp.status_code == 200
    # ② 通过 AuthApi 访问 me（cookie 自动带上，无需手动传 token）
    me = api.me()
    assert me.status_code == 200
    # ③ me 返回的用户名应该是刚才登录的账号
    assert me.json()["data"]["username"] == config.admin.username


@pytest.mark.regression
def test_login_then_list_users(http_client):
    """流程：登录后带 cookie 访问用户列表，应返回分页结构。"""
    # ① 每个集成用例自己登录（不依赖 session 共享态，避免 cookie 被别的用例覆盖）
    api = AuthApi(http_client)
    resp = api.login(config.admin.username, config.admin.password)
    assert resp.status_code == 200
    # ② 访问用户列表：params 透传为 query 参数（page=1&pageSize=5）
    users = http_client.get("/api/users", params={"page": 1, "pageSize": 5})
    assert users.status_code == 200
    # ③ 响应 data 里应有 items（分页数据的关键字段）
    assert "items" in users.json()["data"]
