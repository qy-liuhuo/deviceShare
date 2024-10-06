"""
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: MobiNets
"""
import os.path
import threading
import time

from src.communication.message import File_Message
from src.communication.my_socket import TcpClient, TCP_PORT
from src.utils.device_storage import DeviceStorage
from src.utils.file import File
from src.utils.net import get_local_ip


def remove_all_files(dir_path):
    for root, dirs, files in os.walk(dir_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def send_to_device(ip, msg):
    tcp_client = TcpClient((ip, TCP_PORT))
    tcp_client.send(msg.to_bytes())
    tcp_client.close()


def save_file_to_dir(file_path: str, file_data: bytes):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, "wb") as f:
        f.write(file_data)


class FileController:
    FILE_DIR = "shared_files"

    def __init__(self):
        if not os.path.exists(self.FILE_DIR):
            os.mkdir(self.FILE_DIR)
        else:
            remove_all_files(self.FILE_DIR)
        self.file_list = []
        self.file_set = set()
        self.host = get_local_ip()
        self.lock = threading.Lock()

    def file_listener(self):
        pass


class FileController_server(FileController):
    def __init__(self):
        super().__init__()

    def file_listener(self):
        while True:
            self.lock.acquire()  # 获取锁
            for root, dirs, files in os.walk(self.FILE_DIR, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    new_file = File(name, path, os.path.getsize(path), self.host)
                    new_file_data = open(path, "rb").read()
                    self.send_to_all(File_Message(new_file, new_file_data))
                    self.file_list.append(new_file)
                    self.file_set.add(path)
            time.sleep(2)
            self.lock.release()

    def save_file(self, file_msg: File_Message):
        self.lock.acquire()
        save_file_to_dir(file_msg.file.path, file_msg.data)
        self.file_list.append(file_msg.file)
        self.file_set.add(file_msg.file.path)
        self.send_to_all(file_msg)
        self.lock.release()

    def send_to_all(self, file_msg):
        device_storage = DeviceStorage()
        for device in device_storage.get_all_devices():
            if device.ip != self.host:
                send_to_device(device.ip, file_msg)


class FileController_client(FileController):
    def __init__(self, master_ip):
        self.master_ip = master_ip
        super().__init__()

    def file_listener(self):
        while True:
            self.lock.acquire()  # 获取锁
            for root, dirs, files in os.walk(self.FILE_DIR, topdown=False):
                for name in files:
                    path = os.path.join(root, name)
                    new_file = File(name, path, os.path.getsize(path), self.host)
                    new_file_data = open(path, "rb").read()
                    self.send_to_master(File_Message(new_file, new_file_data))
                    self.file_list.append(new_file)
                    self.file_set.add(path)
            time.sleep(2)
            self.lock.release()

    def send_to_master(self, file_msg):
        tcp_client = TcpClient((self.master_ip, TCP_PORT))
        tcp_client.send(file_msg.to_bytes())
        tcp_client.close()

    def save_file(self, file_msg: File_Message):
        self.lock.acquire()
        if file_msg.file.path not in self.file_set:
            save_file_to_dir(file_msg.file.path, file_msg.file_data)
            self.file_list.append(file_msg.file)
            self.file_set.add(file_msg.file.path)
        self.lock.release()

