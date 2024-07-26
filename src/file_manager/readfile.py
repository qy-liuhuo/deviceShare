import base64
import json
import os

from src.file_manager.fileDto import get_host_ip


# 拖出文件时，将文件内容发送给其他用户
def send_file(ip_addr, file_path):
    ip = get_host_ip()
    if get_host_ip() != ip_addr:
        return
    with open(file_path, 'rb') as file:
        binary_data = file.read()

    # encode data
    base64_data = base64.b64encode(binary_data).decode('utf-8')

    # 创建JSON对象
    json_data = {
        'file_name': file_path,
        'file_data': base64_data
    }
    # test
    # json_file_path = 'output.json'
    # with open(json_file_path, 'w') as json_file:
    #     json.dump(json_data, json_file, indent=4)
    return json_data


def receive_file(json_data):
    file_name = json_data['file_name']
    base64_data = json_data['file_data']
    binary_data = base64.b64decode(base64_data)
    with open('output.txt', 'wb') as file:
        file.write(binary_data)
    return file_name


if __name__ == '__main__':
    json = send_file("192.168.1.100", '/Users/kicheng/kicheng_docs/test.txt')
    receive_file(json)
