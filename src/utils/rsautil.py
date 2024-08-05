# -*- coding:utf-8 -*-
import os
import rsa
from src.utils.device_name import get_device_name


def encrypt(public_key, data: bytes):
    public_key = rsa.PublicKey.load_pkcs1(public_key)
    result = []
    for n in range(0, len(data), 245 * 8):
        part = data[n:n + 245 * 8]
        result.append(rsa.encrypt(part, public_key))
    return b''.join(result)


def decrypt(private_key, data: bytes):
    private_key = rsa.PrivateKey.load_pkcs1(private_key)
    result = bytearray()
    for n in range(0, len(data), 256):
        part = data[n:n + 256]
        result.extend(rsa.decrypt(part, private_key))
    return result.decode()


class RsaUtil:
    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.device_id = get_device_name()
        if self.exist_key():
            self.load_key()
        else:
            self.generate_key()
            self.save_key()

    def update_key(self):
        self.generate_key()
        self.save_key()

    def exist_key(self):
        return os.path.exists(self.device_id + "_public.key") and os.path.exists(self.device_id + "_private.key")

    def generate_key(self):
        self.public_key, self.private_key = rsa.newkeys(2048)
        return self.public_key, self.private_key

    def load_key(self):
        with open(self.device_id + "_public.key", "rb") as f:
            self.public_key = rsa.PublicKey.load_pkcs1(f.read())
        with open(self.device_id + "_private.key", "rb") as f:
            self.private_key = rsa.PrivateKey.load_pkcs1(f.read())

    def save_key(self):
        with open(self.device_id + "_public.key", "wb") as f:
            f.write(self.public_key.save_pkcs1())
        with open(self.device_id + "_private.key", "wb") as f:
            f.write(self.private_key.save_pkcs1())

    def encrypt(self, data: bytes):
        result = []
        for n in range(0, len(data), 245*8):
            part = data[n:n+245*8]
            result.append(rsa.encrypt(part, self.public_key))
        return b''.join(result)

    def decrypt(self, data: bytes):
        result = bytearray()
        for n in range(0, len(data), 256):
            part = data[n:n+256]
            result.extend(rsa.decrypt(part, self.private_key))
        return result.decode()

    def sign(self, data: bytes):
        return rsa.sign(data, self.private_key, 'SHA-1')

    def verify(self, data: bytes, signature: bytes):
        return rsa.verify(data, signature, self.public_key)


if __name__ == '__main__':
    rsa_util = RsaUtil()
