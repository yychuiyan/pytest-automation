"""随机测试数据生成器。"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# random：生成测试数据用的随机数（注意：只能用于测试数据，不能用于密码学场景）
import random

# string：预置字符集（小写字母、数字、大小写字母等）
import string

# datetime：生成时间戳
from datetime import UTC, datetime


class DataGenerator:
    """随机数据生成器：核心思路 = 可读前缀 + 随机后缀，保证每次运行不重复。"""

    # 生成随机后缀：length 个小写字母+数字的随机组合（防重复的核心）
    @staticmethod
    def _suffix(length: int = 4) -> str:
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    # 用户名：测试人员_xxxx（前缀可读易区分，后缀防重复）
    @classmethod
    def username(cls) -> str:
        return f"测试人员_{cls._suffix()}"

    # 邮箱：test_xxxx@example.com（example.com 是保留域名，不会发到真实邮箱）
    @classmethod
    def email(cls) -> str:
        return f"test_{cls._suffix()}@example.com"

    # 手机号：1 + 1位 + 9位 = 11 位数字（测试数据，不要求真实号段）
    @classmethod
    def mobile(cls) -> str:
        return f"1{random.randint(0, 9)}{random.randint(100000000, 999999999)}"

    # 随机密码：默认 10 位，大小写字母+数字混合
    @classmethod
    def password(cls, length: int = 10) -> str:
        chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))

    # 时间戳：YYYYMMDDHHMMSS，14 位数字，可排序、可作唯一标识的一部分
    @staticmethod
    def timestamp() -> str:
        return datetime.now(UTC).strftime("%Y%m%d%H%M%S")
