# -*- coding:utf-8 -*-
import rsa
import base64


# 生成RSA公钥和私钥
(pubkey, privkey) = rsa.newkeys(2048)

# 生成公钥
pub_key = pubkey.save_pkcs1()
pub_file = open('api_public_key.key', 'wb')
pub_file.write(pub_key)
pub_file.close()
print(pub_key)

# 生成私钥
private_key = privkey.save_pkcs1()
pri_file = open('api_private_key.key', 'wb')
pri_file.write(private_key)
pri_file.close()

print(private_key)