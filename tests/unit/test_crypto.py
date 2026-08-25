"""AES 加解密单元测试：核心是「加密后能解密还原」的往返一致性。"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# 被测对象
from core.crypto import AESCipher


class TestAESCipher:
    # 往返测试：16 字节 key，加密 -> 解密，应还原原文（含中文）
    def test_roundtrip(self):
        cipher = AESCipher("0123456789abcdef")
        plaintext = "hello 接口自动化"
        encrypted = cipher.encrypt(plaintext)
        assert encrypted  # 密文非空
        assert cipher.decrypt(encrypted) == plaintext  # 解密能还原原文

    # 短 key 测试：5 字节 key 会自动补 \0 到 16 字节，仍能正常加解密
    def test_short_key_padded(self):
        cipher = AESCipher("short")
        assert cipher.decrypt(cipher.encrypt("x")) == "x"

    # 空值测试：空明文/空密文直接返回空串，不报错
    def test_empty(self):
        cipher = AESCipher("0123456789abcdef")
        assert cipher.encrypt("") == ""
        assert cipher.decrypt("") == ""
