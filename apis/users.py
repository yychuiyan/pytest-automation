"""用户管理接口封装。"""

from __future__ import annotations

from typing import Any

from requests import Response

from apis.base_api import BaseApi


class UserApi(BaseApi):
    """用户管理接口：列表支持分页+搜索+角色筛选。"""

    # 用户列表：GET /api/users?page=&pageSize=&keyword=&role=，query 透传为 params
    def list(self, **query: Any) -> Response:
        return self.client.get("/api/users", params=query)

    # 新增用户：POST /api/users，body 为用户字段（username/email/password/role...）
    def create(self, payload: dict[str, Any]) -> Response:
        return self.client.post("/api/users", json=payload)

    # 用户详情：GET /api/users/:id
    def get(self, user_id: int) -> Response:
        return self.client.get(f"/api/users/{user_id}")

    # 编辑用户：PUT /api/users/:id
    def update(self, user_id: int, payload: dict[str, Any]) -> Response:
        return self.client.put(f"/api/users/{user_id}", json=payload)

    # 删除用户：DELETE /api/users/:id（需 admin 角色）
    def remove(self, user_id: int) -> Response:
        return self.client.delete(f"/api/users/{user_id}")

    # 修改角色：PUT /api/users/:id/role（需 admin 角色）
    def change_role(self, user_id: int, role: str) -> Response:
        return self.client.put(f"/api/users/{user_id}/role", json={"role": role})
