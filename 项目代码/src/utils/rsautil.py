# -*- coding:utf-8 -*-
import os
import rsa
from src.utils.device_name import get_device_name


def encrypt(public_key, data: bytes):
    """
    加密
    :param public_key: 公钥
    :param data: 待加密数据
    :return: 加密结果
    """
    public_key = rsa.PublicKey.load_pkcs1(public_key)
    result = []
    # 分块加密，每次加密245字节，处理超长剪切板
    for n in range(0, len(data), 245):
        part = data[n:n + 245]
        result.append(rsa.encrypt(part, public_key))
    return b''.join(result)


def decrypt(private_key, data: bytes):
    """
    解密
    :param private_key: 私钥
    :param data: 待解密数据
    :return: 解密结果
    """
    private_key = rsa.PrivateKey.load_pkcs1(private_key)
    result = bytearray()
    # 分块解密，每次解密256字节
    for n in range(0, len(data), 256):
        part = data[n:n + 256]
        result.extend(rsa.decrypt(part, private_key))
    return result.decode()


class RsaUtil:
    """
    RSA加密解密工具类
    """
    def __init__(self):
        """
        初始化
        """
        self.public_key = None
        self.private_key = None
        self.device_id = get_device_name()
        # 如果存在密钥则加载，否则生成密钥
        if self.exist_key():
            self.load_key()
        else:
            self.generate_key()
            self.save_key()

    def update_key(self):
        """
        更新密钥
        :return:
        """
        self.generate_key()
        self.save_key()

    def exist_key(self):
        """
        判断是否存在密钥
        :return:
        """
        return os.path.exists(self.device_id + "_public.key") and os.path.exists(self.device_id + "_private.key")

    def generate_key(self):
        """
        生成密钥
        :return:
        """
        self.public_key, self.private_key = rsa.newkeys(2048)
        return self.public_key, self.private_key

    def load_key(self):
        """
        加载密钥
        :return:
        """
        with open(self.device_id + "_public.key", "rb") as f:
            self.public_key = rsa.PublicKey.load_pkcs1(f.read())
        with open(self.device_id + "_private.key", "rb") as f:
            self.private_key = rsa.PrivateKey.load_pkcs1(f.read())

    def save_key(self):
        """
        保存密钥
        :return:
        """
        with open(self.device_id + "_public.key", "wb") as f:
            f.write(self.public_key.save_pkcs1())
        with open(self.device_id + "_private.key", "wb") as f:
            f.write(self.private_key.save_pkcs1())

    def encrypt(self, data: bytes):
        """
        加密
        :param data: 待加密数据
        :return: 加密结果
        """
        result = []
        for n in range(0, len(data), 245):
            part = data[n:n+245]
            result.append(rsa.encrypt(part, self.public_key))
        return b''.join(result)

    def decrypt(self, data: bytes):
        """
        解密
        :param data: 待解密数据
        :return: 解密结果
        """
        result = bytearray()
        for n in range(0, len(data), 256):
            part = data[n:n+256]
            result.extend(rsa.decrypt(part, self.private_key))
        return result

    def sign(self, data: bytes):
        """
        签名
        :param data: 待签名数据
        :return: 签名结果
        """
        return rsa.sign(data, self.private_key, 'SHA-1')

    def verify(self, data: bytes, signature: bytes):
        """
        验证签名
        :param data: 待验证数据
        :param signature: 签名
        :return:
        """
        return rsa.verify(data, signature, self.public_key)


if __name__ == '__main__':
    rsa_util = RsaUtil()
    e = rsa_util.encrypt(bytes(("""    def decrypt(self, data: bytes):
        result = bytearray()
        for n in range(0, len(data), 256):
            part = data[n:n+256]
            result.extend(rsa.decrypt(part, self.private_key))
        return result.decode()

    def sign(self, data: bytes):
        return rsa.sign(data, self.private_key, 'SHA-1')

    def verify(self, data: bytes, signature: bytes):
        return rsa.verify(data, signature, self.public_key)
    """).encode()))
    print(rsa_util.decrypt(e))
