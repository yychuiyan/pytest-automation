"""操作日志接口契约用例。"""

from __future__ import annotations

import pytest

from apis.logs import LogApi
from schemas.logs import LogListResponse


@pytest.mark.regression
def test_logs_list_success(admin_client):
    """API-108：分页查询操作日志成功。"""
    api = LogApi(admin_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert "items" in resp.json()["data"]
    if resp.json()["data"]["items"]:
        item = resp.json()["data"]["items"][0]
        assert "action" in item
        assert "module" in item
    LogListResponse.model_validate(resp.json())


@pytest.mark.regression
def test_logs_list_without_login_unauthorized(anon_client):
    """API-109：未登录查询操作日志 → 401。"""
    api = LogApi(anon_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 401
    assert "未登录" in resp.json()["message"]


@pytest.mark.regression
def test_logs_list_as_user(user_client):
    """API-110：普通用户查询操作日志成功。"""
    api = LogApi(user_client)
    resp = api.list(page=1, pageSize=5)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
