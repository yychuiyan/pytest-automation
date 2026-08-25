"""
环境配置：统一从 .env 读取配置，支持多环境切换
"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# 读取环境
import os

# 自动生成装饰器
from dataclasses import dataclass

# 路径
from pathlib import Path

# 读取.env文件
from dotenv import load_dotenv

# 项目根目录（core/ 的上一级），目的是不管在哪一级目录都能够准确找到项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent

APP_ENV = os.getenv("APP_ENV", "test")
# 从 shell/CI读取APP_ENV，加载环境
load_dotenv(ROOT_DIR / f".env.{APP_ENV}")
# 加载公共的.env，不覆盖已存在的变量
load_dotenv(ROOT_DIR / ".env", override=False)


# 封装os.getenv，目的是存在变量缺失时打日志，只需要改这个函数就可以
def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# 自动生成 __init__ 不用手动构造函数 frozen=True：创建后实例不可修改
@dataclass(frozen=True)
class AuthConfig:
    """登录验证相关配置"""

    login_api: str = _env("LOGIN_API_URL")
    token_field: str = _env("TOKEN_FIELD", "token")
    auth_header: str = _env("AUTH_HEADER", "Authorization")


@dataclass(frozen=True)
class UserConfig:
    """一个「账号角色」的用户名/密码 由Config负责传值，通用的角色容器"""

    username: str = ""
    password: str = ""


@dataclass(frozen=True)
class Config:
    # 全局配置单例
    env: str = _env("ENV", APP_ENV)
    base_url: str = _env("BASE_URL")
    aes_key: str = _env("AES_KEY")

    auth: AuthConfig = AuthConfig()
    # admin/unit 创建UserConfig时显示传入环境变量读取到的用户名密码
    admin: UserConfig = UserConfig(_env("ADMIN_USERNAME"), _env("ADMIN_PASSWORD"))
    unit: UserConfig = UserConfig(_env("UNIT_USERNAME"), _env("UNIT_PASSWORD"))


# 模块加载时创建一次，全项目任何地方拿到的都是同一个对象
config = Config()
