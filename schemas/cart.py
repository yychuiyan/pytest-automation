"""购物车响应模型。

注意：购物车列表 data 为数组（非分页），与其它列表接口不同。
"""

from __future__ import annotations

from pydantic import BaseModel

from schemas.common import ApiResponse


class CartItem(BaseModel):
    """购物车项。"""

    id: int
    productId: int
    quantity: int


class CartListResponse(ApiResponse):
    """购物车列表响应：data 为数组。"""

    data: list[CartItem] | None = None


class CartResponse(ApiResponse):
    """单个购物车项响应（添加/修改）。"""

    data: CartItem | None = None
