"""HTTP 客户端统一封装：基于 requests.Session 的 base_url / 请求头 / 超时 / 日志。"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# 类型注解工具包
from typing import Any

# HTTP
import requests

# requests响应对象类型
from requests import Response

# 连接适配器 + 重试策略（网络抖动自动重试）
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 日志器
from core.logger import logger


class HttpClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: int = 30,
        headers: dict[str, str] | None = None,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")  # 去尾部斜杠
        self.timeout = timeout  # 统一超时
        self.session = requests.Session()  # Session复用连接 + cookie
        self.session.headers.update({"Content-Type": "application/json"})  # 默认请求头
        # 自动重试：连接失败/5xx 最多重试 max_retries 次，backoff 递增间隔
        retry = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504],  # 这些状态码也重试
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)  # 挂到 http/https 上
        self.session.mount("https://", adapter)
        if headers:
            self.session.headers.update(headers)

    # 绝对/相对路径统一管理
    def _build_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    # 处理请求
    def request(self, method: str, path: str, **kwargs: Any) -> Response:
        # 拼 URL
        url = self._build_url(path)
        # 超时兜底
        kwargs.setdefault("timeout", self.timeout)
        # 源头脱敏日志
        logger.info(f"{method.upper()} {url.split('?')[0]}")
        # 发请求+结果日志
        response = self.session.request(method, url, **kwargs)
        logger.info(f"<-{response.status_code}({response.elapsed.total_seconds():.2f}s)")
        return response

    # request包装，使调用方法是client.get(...)，而不是client.request("GET",...)
    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    # 登录后注入凭证 注入 Authorization 等请求头
    def set_header(self, key: str, value: str) -> None:
        self.session.headers.update({key: value})
