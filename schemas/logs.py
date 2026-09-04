"""操作日志响应模型。"""

from __future__ import annotations

from pydantic import BaseModel

from schemas.common import PageData, PageResponse


class LogEntry(BaseModel):
    """日志条目。"""

    id: int
    action: str
    module: str
    username: str | None = None


class LogListData(PageData[LogEntry]):
    """日志列表分页数据。"""


class LogListResponse(PageResponse[LogEntry]):
    """日志列表响应。"""
