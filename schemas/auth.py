"""认证响应模型"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# pydantic 基类：自动校验字段类型/必填
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """通用响应外层"""

    success: bool  # 是否成功
    message: str  # 提示信息


class LoginData(BaseModel):
    """登录成功返回的数据体"""

    username: str
    token: str
    role: str
    permissions: list[str]


class LoginResponse(ApiResponse):
    """登录响应：继承外层，data字段类型化"""

    data: LoginData | None = None  # 失败时data可能为空
