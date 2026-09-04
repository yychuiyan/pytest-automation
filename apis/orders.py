"""订单接口封装。"""

from __future__ import annotations

from typing import Any

from requests import Response

from apis.base_api import BaseApi


class OrderApi(BaseApi):
    """订单接口：列表/详情/改状态。"""

    # 订单列表：GET /api/orders?page=&pageSize=
    def list(self, **query: Any) -> Response:
        return self.client.get("/api/orders", params=query)

    # 订单详情：GET /api/orders/:id
    def get(self, order_id: int) -> Response:
        return self.client.get(f"/api/orders/{order_id}")

    # 修改订单状态：PUT /api/orders/:id/status
    def update_status(self, order_id: int, status: str) -> Response:
        return self.client.put(f"/api/orders/{order_id}/status", json={"status": status})
