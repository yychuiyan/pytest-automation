"""随机数据生成器单元测试：验证「格式合法 + 不重复」两个核心承诺。"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# 被测对象
from core.data_generator import DataGenerator


class TestDataGenerator:
    # 用户名格式：必须带「测试人员_」前缀
    def test_username_format(self):
        u = DataGenerator.username()
        assert u.startswith("测试人员_")

    # 邮箱格式：test_ 开头、@example.com 结尾
    def test_email_format(self):
        e = DataGenerator.email()
        assert e.endswith("@example.com") and e.startswith("test_")

    # 手机号格式：1 开头、总共 11 位、全数字
    def test_mobile_format(self):
        m = DataGenerator.mobile()
        assert m.startswith("1") and len(m) == 11 and m.isdigit()

    # 密码长度：默认 10 位；显式传 length 也生效
    def test_password_length(self):
        assert len(DataGenerator.password()) == 10
        assert len(DataGenerator.password(16)) == 16

    # 时间戳格式：14 位纯数字（YYYYMMDDHHMMSS）
    def test_timestamp(self):
        ts = DataGenerator.timestamp()
        assert len(ts) == 14 and ts.isdigit()

    # 不重复性：生成 50 个用户名，去重后仍是 50 个（随机后缀生效）
    def test_no_duplicate_username(self):
        assert len({DataGenerator.username() for _ in range(50)}) == 50
