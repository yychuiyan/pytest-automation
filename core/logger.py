"""日志工具，基于loguru，带敏感信息脱敏"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# 正则
import re

# 标准错误输出流 sys.stderr
import sys
from typing import Any

# loguru日志对象
from loguru import logger

# 敏感信息脱敏规则：（正则，替换文本），顺序：身份证在手机号之前
_SENSITIVE_PATTERNS: list[tuple[str, str]] = [
    (
        r'(?i)(password|passwd|pwd|token|secret|aes_key|authorization)(\s*[:=]\s*["\']?)[^\s"\',}]+',
        r"\1\2***",
    ),
    (r"\b\d{17}[\dXx]\b", "******************"),
    (r"\b1[3-9]\d{9}\b", "1**********"),
]


# loguru filter 回调：每条日志输出前改 message 做脱敏，返回 True 放行
def _redact(record: dict[str, Any]) -> bool:
    """对每条日志消息做敏感信息脱敏"""
    for pattern, repl in _SENSITIVE_PATTERNS:
        record["message"] = re.sub(pattern, repl, record["message"])
    return True


"""
logger.remove()：loguru 默认自带一个 handler（输出到 stderr）。先清掉它，否则同样的日志会打两遍（默认的 + 我们自定义的）
logger.add(sys.stderr, ...)：注册唯一的自定义 handler
add() 各参数：

参数	含义
sys.stderr	输出到标准错误流（终端就能看到，CI 也能捕获）
level="DEBUG"	DEBUG 及以上级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）都记录
filter=_redact	每条日志进输出前先过脱敏（第 3 段）
format=...	输出模板
"""
logger.remove()
logger.add(
    sys.stderr,
    level="DEBUG",
    filter=_redact,  # type: ignore[arg-type]  # loguru 运行时传入普通 dict
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <6}</level> | <level>{message}</level>",
)

# 文件落盘：INFO 及以上写文件，按 10MB 滚动，保留 5 个（loguru 自动创建 logs/ 目录）
logger.add(
    "logs/app.log",
    level="INFO",
    filter=_redact,  # type: ignore[arg-type]
    rotation="10 MB",
    retention=5,
    encoding="utf-8",
)

"""
声明「from core.logger import * 时只导出 logger」——内部实现不对外暴露，公共 API 只有 logger。
"""
__all__ = ["logger"]
