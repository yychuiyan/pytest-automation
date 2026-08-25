"""AES 加解密工具（AES-128-ECB + Pkcs7，Hex 密文）。"""

# 让类型注解变成字符串、延迟求值。防御性写法，避免注解里引用未定义类型时报错
from __future__ import annotations

# AES 加密算法实现（pycryptodome 包）
from Crypto.Cipher import AES

# Pkcs7 填充 / 去填充工具（把明文补成 16 字节整数倍）
from Crypto.Util.Padding import pad, unpad

# 密钥默认值从配置中心读取（.env 里的 AES_KEY）
from core.config import config


class AESCipher:
    """AES 加解密器：key 统一处理成 16 字节，encrypt/decrypt 成对使用。"""

    def __init__(self, key: str | None = None) -> None:
        # key 不传时从配置中心 config.aes_key 取（.env 里 AES_KEY 配置）
        raw = (key if key is not None else config.aes_key).encode("utf-8")
        # AES-128 需要 16 字节密钥：超长截断到 16，不足用 \0 补齐
        self.key = raw[:16].ljust(16, b"\0")

    def encrypt(self, plaintext: str) -> str:
        """明文 -> Hex 密文。空文本直接返回空串（避免无意义加密）。"""
        if not plaintext:
            return ""
        # ECB 模式不需要 IV（实现简单；代价是相同明文产生相同密文，测试场景可接受）
        cipher = AES.new(self.key, AES.MODE_ECB)
        # ① pad 做 Pkcs7 填充 ② 加密 ③ hex() 转十六进制字符串返回
        return cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size)).hex()

    def decrypt(self, hex_ciphertext: str) -> str:
        """Hex 密文 -> 明文。空密文直接返回空串。"""
        if not hex_ciphertext:
            return ""
        cipher = AES.new(self.key, AES.MODE_ECB)
        # ① bytes.fromhex 把十六进制还原成字节 ② 解密 ③ unpad 去掉 Pkcs7 填充 ④ UTF-8 解码
        return unpad(cipher.decrypt(bytes.fromhex(hex_ciphertext)), AES.block_size).decode("utf-8")
