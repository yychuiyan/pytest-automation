"""登录接口契约用例：单接口维度。"""

from __future__ import annotations

# pytest：用 @pytest.mark 打标记
import pytest

# 接口封装：通过 AuthApi 调用（不是裸 http_client），这样封装层才被覆盖
from apis.auth import AuthApi

# 配置中心：从 .env 读凭证，不硬编码明文
from core.config import config

# 第六步的 pydantic 模型：校验登录响应结构
from schemas.auth import LoginResponse


# 冒烟 + 回归双标记：make smoke 和 make regression 都会跑它
@pytest.mark.smoke
@pytest.mark.regression
def test_login_success(http_client):
    """成功路径：正确账号密码 → 200 + success=True + 响应结构符合模型。"""
    # 通过 AuthApi 调用登录（正确凭证从 .env 读）
    api = AuthApi(http_client)
    resp = api.login(config.admin.username, config.admin.password)
    # ① 状态码契约：期望 200
    assert resp.status_code == 200
    # ② 业务码契约：响应里的 success 字段必须为 True
    assert resp.json()["success"] is True
    # ③ schema 校验：响应字段符合 LoginResponse 模型
    LoginResponse.model_validate(resp.json())


# 只贴 regression：回归跑，冒烟不跑
@pytest.mark.regression
def test_login_wrong_password(http_client):
    """异常路径：错误密码 → 401 + success=False。"""
    # 用户名从 config 读，密码是"错误的测试值"（非敏感，可硬编码）
    api = AuthApi(http_client)
    resp = api.login(config.admin.username, "wrong-password")
    # ① 状态码契约：未授权 401
    assert resp.status_code == 401
    # ② 业务码契约：success 为 False
    assert resp.json()["success"] is False
