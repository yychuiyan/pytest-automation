"""商品接口封装。"""

from __future__ import annotations

from typing import Any

from requests import Response

from apis.base_api import BaseApi


class ProductApi(BaseApi):
    """商品接口：列表/详情/增删改/分类。"""

    # 商品列表：GET /api/products?page=&pageSize=
    def list(self, **query: Any) -> Response:
        return self.client.get("/api/products", params=query)

    # 新增商品：POST /api/products
    def create(self, payload: dict[str, Any]) -> Response:
        return self.client.post("/api/products", json=payload)

    # 商品详情：GET /api/products/:id
    def get(self, product_id: int) -> Response:
        return self.client.get(f"/api/products/{product_id}")

    # 编辑商品：PUT /api/products/:id
    def update(self, product_id: int, payload: dict[str, Any]) -> Response:
        return self.client.put(f"/api/products/{product_id}", json=payload)

    # 删除商品：DELETE /api/products/:id
    def remove(self, product_id: int) -> Response:
        return self.client.delete(f"/api/products/{product_id}")

    # 商品分类：GET /api/products/categories
    def categories(self) -> Response:
        return self.client.get("/api/products/categories")
