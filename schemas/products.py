"""商品响应模型。"""

from __future__ import annotations

from pydantic import BaseModel

from schemas.common import ApiResponse, PageData, PageResponse


class Product(BaseModel):
    """商品对象。"""

    id: int
    name: str
    price: int | float
    originalPrice: int | float | None = None
    category: str | None = None
    categoryId: int | None = None
    stock: int | None = None
    status: str | None = None


class Category(BaseModel):
    """商品分类。"""

    id: int
    name: str
    icon: str | None = None


class ProductListData(PageData[Product]):
    """商品列表分页数据。"""


class ProductListResponse(PageResponse[Product]):
    """商品列表响应。"""


class ProductResponse(ApiResponse):
    """单个商品响应。"""

    data: Product | None = None


class CategoryListResponse(ApiResponse):
    """商品分类列表响应：data 为数组。"""

    data: list[Category] | None = None
