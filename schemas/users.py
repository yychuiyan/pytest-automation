"""用户响应模型。"""

from __future__ import annotations

from pydantic import BaseModel

from schemas.common import ApiResponse, PageData, PageResponse


class User(BaseModel):
    """用户对象。"""

    id: int
    username: str
    email: str | None = None
    role: str
    status: str | None = None
    phone: str | None = None
    realName: str | None = None


class UserListData(PageData[User]):
    """用户列表分页数据。"""


class UserListResponse(PageResponse[User]):
    """用户列表响应。"""


class UserResponse(ApiResponse):
    """单个用户响应。"""

    data: User | None = None
