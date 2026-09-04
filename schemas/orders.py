"""订单响应模型。"""

from __future__ import annotations

from pydantic import BaseModel

from schemas.common import ApiResponse, PageData, PageResponse


class OrderItem(BaseModel):
    """订单商品明细。"""

    productId: int
    productName: str
    price: int | float
    quantity: int


class Order(BaseModel):
    """订单对象。"""

    id: int
    orderNo: str
    status: str
    totalAmount: int | float
    items: list[OrderItem]


class OrderListData(PageData[Order]):
    """订单列表分页数据。"""


class OrderListResponse(PageResponse[Order]):
    """订单列表响应。"""


class OrderResponse(ApiResponse):
    """单个订单响应。"""

    data: Order | None = None
