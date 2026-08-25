"""登录数据驱动用例：不同角色登录返回不同 role。"""

from __future__ import annotations

# pytest：用 @pytest.mark.parametrize 做参数化
import pytest

# yaml：读数据文件（只存角色场景，不存密码）
import yaml

# 接口封装：通过 AuthApi 调用
from apis.auth import AuthApi

# 配置中心：从 .env 读账号密码
from core.config import config

# 角色 → 账号密码 的映射：凭证从 config（.env）读，代码里无明文
ROLE_CREDENTIALS = {
    "admin": (config.admin.username, config.admin.password),
    "user": (config.unit.username, config.unit.password),
}


def load_login_cases():
    """从 data/login_cases.yaml 读角色场景（不含密码）。"""
    # 打开数据文件（encoding 指定 utf-8 处理中文）
    with open("data/login_cases.yaml", encoding="utf-8") as f:
        # safe_load：把 yaml 解析成 Python 列表（每个元素是一个 dict）
        return yaml.safe_load(f)


# smoke 标记 + 参数化：ids 用 case 字段给每个参数起名
@pytest.mark.smoke
@pytest.mark.parametrize("case", load_login_cases(), ids=lambda c: c["case"])
def test_login_role(case, http_client):
    """每种角色登录：返回 role 与场景一致。"""
    # 从场景取 role，再用 role 从 config 映射出账号密码
    username, password = ROLE_CREDENTIALS[case["role"]]
    api = AuthApi(http_client)
    resp = api.login(username, password)
    # 状态码 200
    assert resp.status_code == 200
    # 返回的 data.role 与场景里的 role 一致（admin vs user）
    assert resp.json()["data"]["role"] == case["role"]
