import socket
import threading
import time

from Message import MsgType, Message


class UdpServer:
    def __init__(self, port=16666):
        self.msg_listener = None
        self.__port = port
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__server.bind(("0.0.0.0", self.__port))
        self.client = []

    def sendto(self, data: bytes, target: tuple):
        self.__server.sendto(data, target)

    def recv(self):
        return self.__server.recvfrom(1024)

    def msg_receiver(self):
        while True:
            data, addr = self.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.DEVICE_UP and addr not in self.client:
                self.client.append(addr)
                self.sendto(Message(MsgType.STOP_BROADCAST, None).to_bytes(), addr)
                print(f"client {addr} connected")

    def start_listener(self):
        self.msg_listener = threading.Thread(target=self.msg_receiver)
        self.msg_listener.start()
        return self.msg_listener

    def close(self):
        self.__server.close()


class UdpClient:
    def __init__(self, port=16667):
        self.msg_listener = None
        self.be_added = False
        self.__broadcast_thread = None
        self.__ip = socket.gethostbyname(socket.gethostname())
        self.__port = port
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__client.bind(("0.0.0.0", self.__port))
        self.__client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.__broadcast_data = Message(MsgType.DEVICE_UP, (self.__ip, self.__port)).to_bytes()

    def sendto(self, data: bytes, target):
        self.__client.sendto(data, target)

    def broadcast_address(self):
        while not self.be_added:
            print("broadcast")
            self.__client.sendto(self.__broadcast_data, ('<broadcast>', 16666))  # 表示广播到16666端口
            time.sleep(2)

    def msg_receiver(self):
        while True:
            data, addr = self.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.STOP_BROADCAST:
                print("stop broadcast")
                self.be_added = True


    def start_listener(self):
        self.msg_listener = threading.Thread(target=self.msg_receiver)
        self.msg_listener.start()
        return self.msg_listener

    def start_broadcast(self):
        self.__broadcast_thread = threading.Thread(target=self.broadcast_address)
        self.__broadcast_thread.start()
        return self.__broadcast_thread

    def recv(self):
        return self.__client.recvfrom(1024)

    def close(self):
        self.__client.close()
