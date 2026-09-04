"""购物车接口封装。"""

from __future__ import annotations

from requests import Response

from apis.base_api import BaseApi


class CartApi(BaseApi):
    """购物车接口：列表/添加/改数量/删除。"""

    # 购物车列表：GET /api/cart（data 为数组，非分页）
    def list(self) -> Response:
        return self.client.get("/api/cart")

    # 添加商品到购物车：POST /api/cart
    def add(self, product_id: int, quantity: int = 1) -> Response:
        return self.client.post("/api/cart", json={"productId": product_id, "quantity": quantity})

    # 修改购物车项数量：PUT /api/cart/:id
    def update_quantity(self, cart_item_id: int, quantity: int) -> Response:
        return self.client.put(f"/api/cart/{cart_item_id}", json={"quantity": quantity})

    # 删除购物车项：DELETE /api/cart/:id
    def remove(self, cart_item_id: int) -> Response:
        return self.client.delete(f"/api/cart/{cart_item_id}")
