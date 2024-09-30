import json
import os.path
import threading
import time

from src.communication.message import Message, MsgType, File_Message
from src.communication.my_socket import TcpClient, TCP_PORT
from src.utils.device_storage import DeviceStorage
from src.utils.net import get_local_ip


class File:

    def __init__(self, name, size, host):
        self.name = name
        self.size = size
        self.host = host

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return File(data["name"], data["size"], data["host"])


def send_to_device(ip, msg):
    tcp_client = TcpClient((ip, TCP_PORT))
    tcp_client.send(msg)
    tcp_client.close()


class FileController:
    FILE_DIR = "shared_files"

    def __init__(self):
        if os.path.exists(self.FILE_DIR):
            os.remove(self.FILE_DIR)
        os.mkdir(self.FILE_DIR)
        self.file_list = []
        self.file_name_set = set()
        self.host = get_local_ip()
        self.lock = threading.Lock()

    def file_listener(self):
        pass

    def save_file_to_dir(self, file_name: str, file_data: bytes):
        with open(self.FILE_DIR + "/" + file_name, "wb") as f:
            f.write(file_data)


class FileController_server(FileController):
    def __init__(self):
        super().__init__()
        self.device_storage = DeviceStorage()

    def file_listener(self):
        while True:
            self.lock.acquire()  # 获取锁
            files = os.listdir(self.FILE_DIR)
            for file_name in files:
                if file_name not in self.file_name_set:
                    new_file = File(file_name, os.path.getsize(self.FILE_DIR + "/" + file_name), self.host)
                    self.send_to_all(new_file)
                    self.file_list.append(new_file)
                    self.file_name_set.add(file_name)
            time.sleep(2)
            self.lock.release()

    def save_file(self, file_msg: File_Message):
        self.lock.acquire()
        self.save_file_to_dir(file_msg.file.name, file_msg.data)
        self.file_list.append(file_msg.file)
        self.file_name_set.add(file_msg.file.name)
        self.send_to_all(file_msg)
        self.lock.release()

    def send_to_all(self, file_msg):
        for device in self.device_storage.get_all_devices():
            if device.ip != self.host:
                send_to_device(device.ip, file_msg)


class FileController_client(FileController):
    def __init__(self, master_ip):
        self.master_ip = master_ip
        super().__init__()

    def file_listener(self):
        while True:
            self.lock.acquire()  # 获取锁
            files = os.listdir("shared_files")
            for file_name in files:
                if file_name not in self.file_name_set:
                    new_file = File(file_name, os.path.getsize("shared_files/" + file_name), self.host)
                    new_file_data = open("shared_files/" + file_name, "rb").read()
                    self.send_to_master(File_Message(new_file, new_file_data))
                    self.file_list.append(new_file)
                    self.file_name_set.add(file_name)
            time.sleep(2)
            self.lock.release()

    def send_to_master(self, file_msg):
        tcp_client = TcpClient((self.master_ip, TCP_PORT))
        tcp_client.send(file_msg)
        tcp_client.close()

    def save_file(self, file_msg: File_Message):
        self.lock.acquire()
        if file_msg.file.name not in self.file_name_set:
            self.save_file_to_dir(file_msg.file.name, file_msg.file_data)
            self.file_list.append(file_msg.file)
            self.file_name_set.add(file_msg.file.name)
        self.lock.release()
