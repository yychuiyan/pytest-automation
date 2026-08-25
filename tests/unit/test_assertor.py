"""断言器单元测试：验证四个断言方法各自的「通过 / 失败」两条路径。"""

from __future__ import annotations

# pytest：测试框架（pytest.raises 断言抛异常）
import pytest

# requests 的 Response 类型：用于构造假的响应对象
from requests import Response

# 被测对象
from core.assertor import Assertor


def _make_response(status_code: int, text: str = "") -> Response:
    """构造一个假的 Response：手动设置状态码和响应体（测试不用真发请求）。"""
    resp = Response()
    resp.status_code = status_code
    resp._content = text.encode("utf-8")  # _content 是响应体的字节存储，直接塞进去
    return resp


class TestAssertor:
    # 状态码断言：期望 200、实际 200 → 通过，且返回原 response（支持链式）
    def test_status_code_ok(self):
        resp = _make_response(200)
        assert Assertor.status_code(resp) is resp

    # 状态码断言：期望 200、实际 500 → 抛 AssertionError，信息含「状态码断言失败」
    def test_status_code_fail(self):
        with pytest.raises(AssertionError, match="状态码断言失败"):
            Assertor.status_code(_make_response(500), 200)

    # JSON 解析：合法 JSON 字符串 → 解析成 dict
    def test_is_json_ok(self):
        assert Assertor.is_json(_make_response(200, '{"a": 1}')) == {"a": 1}

    # JSON 解析：非法 JSON → 抛 AssertionError，信息含「不是合法 JSON」
    def test_is_json_fail(self):
        with pytest.raises(AssertionError, match="不是合法 JSON"):
            Assertor.is_json(_make_response(200, "not json"))

    # 字段存在：字段在 → 返回其值
    def test_has_field(self):
        assert Assertor.has_field({"a": 1}, "a") == 1

    # 字段存在：字段不在 → 抛 AssertionError，信息含「字段缺失」
    def test_has_field_missing(self):
        with pytest.raises(AssertionError, match="字段缺失"):
            Assertor.has_field({"a": 1}, "b")

    # 字段值相等：值一致 → 不抛异常（通过）
    def test_field_equal_ok(self):
        Assertor.field_equal({"a": 1}, "a", 1)

    # 字段值相等：值不一致 → 抛 AssertionError，信息含「字段 a 断言失败」
    def test_field_equal_fail(self):
        with pytest.raises(AssertionError, match="字段 a 断言失败"):
            Assertor.field_equal({"a": 1}, "a", 2)
