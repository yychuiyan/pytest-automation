"""接口基类：所有业务接口对象继承此基类，持有共享的 HttpClient"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# HTTP客户端
from core.http_client import HttpClient


class BaseApi:
    """接口基类：只做「持有client」这一件事情"""

    def __init__(self, client: HttpClient) -> None:
        # 一个业务一个API实例 = 一个 HttpClient（共享连接/请求头/超时）
        self.client = client
