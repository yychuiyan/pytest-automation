"""全局 pytest fixtures：HTTP 客户端与会话级登录。"""

# 让类型注解变成字符串、延迟求值（防御性写法）
from __future__ import annotations

# Generator：类型注解用（yield 的函数返回生成器类型）
from collections.abc import Generator

# pytest：拿 @pytest.fixture 装饰器
import pytest

# 配置中心：读 BASE_URL、账号密码
from core.config import config

# HTTP 客户端封装（第四步）
from core.http_client import HttpClient


# session 级 fixture：整个测试会话只创建一次，所有用例共享一个连接池
@pytest.fixture(scope="session")
def http_client() -> Generator[HttpClient, None, None]:
    # 前置（setup）：从配置中心读 base_url 创建客户端
    client = HttpClient(config.base_url)
    # 交付：把 client 交给测试用例用（测试函数参数写 http_client 就能拿到）
    yield client
    # 后置（teardown）：整个会话结束后关闭连接
    client.session.close()


# 登录 fixture：依赖 http_client（pytest 自动先创建 http_client 再登录）
@pytest.fixture(scope="session")
def logged_in(http_client: HttpClient) -> bool:
    """登录一次建立 cookie 会话（testing-online 是 cookie 认证，Session 自动保存）。"""
    # 没配登录接口时直接返回 False（跳过登录）
    if not config.auth.login_api:
        return False
    # 账号密码从配置中心取（.env.test 里的 ADMIN_USERNAME/ADMIN_PASSWORD）
    payload = {"username": config.admin.username, "password": config.admin.password}
    # POST 登录，成功后 Session 自动保存 auth_token cookie，后续请求自动带登录态
    resp = http_client.post(config.auth.login_api, json=payload)
    return resp.status_code == 200


# ---- 以下为新增 fixture：为不同登录态提供独立 HttpClient，避免 session 互相污染 ----


def _login(client: HttpClient, username: str, password: str) -> None:
    """用指定账号登录到给定 client，建立该 client 自己的 cookie 会话。"""
    client.post("/api/auth/login", json={"username": username, "password": password})


@pytest.fixture(scope="session")
def admin_client() -> Generator[HttpClient, None, None]:
    """管理员登录态客户端：独立 Session，预登录 admin，供需要 admin 权限的用例使用。"""
    client = HttpClient(config.base_url)
    _login(client, config.admin.username, config.admin.password)
    yield client
    client.session.close()


@pytest.fixture(scope="session")
def user_client() -> Generator[HttpClient, None, None]:
    """普通用户登录态客户端：独立 Session，预登录普通用户，供测 403/读权限用例使用。"""
    client = HttpClient(config.base_url)
    _login(client, config.unit.username, config.unit.password)
    yield client
    client.session.close()


@pytest.fixture(scope="session")
def anon_client() -> Generator[HttpClient, None, None]:
    """未登录客户端：独立 Session，不带任何登录态，供测 401 用例使用。"""
    client = HttpClient(config.base_url)
    yield client
    client.session.close()
