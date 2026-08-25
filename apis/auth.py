"""认证接口封装"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# requests 响应对象类型
from requests import Response

# 接口基类
from apis.base_api import BaseApi


class AuthApi(BaseApi):
    """认证接口：登录后 Session 自动携带 cookie，后续请求自动带登录态"""

    # 登录：POST /api/auth/login
    def login(self, username: str, password: str) -> Response:
        return self.client.post("/api/auth/login", json={"username": username, "password": password})

    # 当前用户：GET /api/auth/me（需要登录态，Session 自动带cookie）
    def me(self) -> Response:
        return self.client.get("/api/auth/me")

    # 登出：POST /api/auth/logout
    def logout(self) -> Response:
        return self.client.post("/api/auth/logout")
