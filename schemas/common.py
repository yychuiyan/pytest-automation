"""通用响应模型：统一外层 + 分页结构。

testing-online 统一响应格式：{success: bool, message: str, data: ...}
分页格式：data = {items, total, page, pageSize, totalPages}
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel):
    """通用响应外层。"""

    success: bool
    message: str


class PageData(BaseModel, Generic[T]):
    """分页数据体：列表接口的 data 统一长这样。"""

    items: list[T]
    total: int
    page: int
    pageSize: int
    totalPages: int | None = None  # pageSize=0 时可能为 null


class PageResponse(ApiResponse, Generic[T]):
    """分页响应：data 为 PageData。"""

    data: PageData[T] | None = None
