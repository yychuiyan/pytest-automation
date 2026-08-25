"""统一断言器，封装常用接口断言"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# 类型注解工具，主要用于动态JSON数据用
from typing import Any

# requests响应对象类型
from requests import Response


class Assertor:
    """断言器：所有方法都是静态方法，不依赖实例状态：失败统一抛 AssertionError"""

    # 状态码断言：通过后返回 response 本身，支持链式调用（.status_code(resp).is_json(...)）
    @staticmethod
    def status_code(response: Response, expected: int = 200) -> Response:
        # 断言实际状态码 == 期望状态码；失败信息带上响应体片段（[:500] 截断防刷屏）便于排查
        assert response.status_code == expected, (
            f"状态码断言失败：期望 {expected}，实际 {response.status_code}，响应体：{response.text[:500]}"
        )
        # 通过则返回原 response，供下一步链式断言使用
        return response

    # JSON 解析断言：响应体必须是合法 JSON
    @staticmethod
    def is_json(response: Response) -> dict[str, Any] | list[Any]:
        # 尝试解析 JSON；响应体可能是对象也可能是数组，所以返回类型标注 dict | list
        try:
            return response.json()
        except ValueError as exc:
            # 解析失败：把原始响应体带进错误信息，并保留原始异常链（from exc）
            raise AssertionError(f"响应不是合法 JSON：{response.text[:500]}") from exc

    # 字段存在断言：字段必须在 data 里，通过后返回该字段的值
    @staticmethod
    def has_field(data: dict[str, Any], field: str) -> Any:
        # 断言 field 是 data 的键之一；失败时列出实际存在的字段方便排查
        assert field in data, f"字段缺失：{field}，实际字段：{list(data.keys())}"
        # 返回字段值（供 field_equal 等继续复用）
        return data[field]

    # 字段值断言：先确认字段存在，再断言值相等
    @staticmethod
    def field_equal(data: dict[str, Any], field: str, expected: Any) -> None:
        # 复用 has_field：字段不存在时由它抛错，避免这里拿到 None 产生误判
        actual = Assertor.has_field(data, field)
        # 断言实际值 == 期望值，失败信息带「期望 vs 实际」对比
        assert actual == expected, f"字段 {field} 断言失败：期望 {expected}，实际 {actual}"

    # 响应时间断言：接口性能门槛（如 < 0.5s）
    @staticmethod
    def elapsed_lt(response: Response, seconds: float) -> Response:
        # response.elapsed 是 requests 内置的耗时统计
        actual = response.elapsed.total_seconds()
        assert actual < seconds, f"响应时间断言失败：期望 < {seconds}s，实际 {actual:.2f}s"
        return response


# 模块级单例：全项目统一用 assertor 入口（与 config 单例同理）
assertor = Assertor()
