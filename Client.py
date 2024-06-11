import threading
import time
from Message import Message, MsgType
from MouseController import MouseController
from Udp import Udp
import socket


class Client(Udp):
    def __init__(self, port=16667):
        super().__init__(port)
        self.be_added = False
        self._mouse = MouseController()
        self._broadcast_thread = None
        self._ip = socket.gethostbyname(socket.gethostname())
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._broadcast_data = Message(MsgType.DEVICE_JOIN, (self._ip, self._port)).to_bytes()
        self.server_addr = None

    def broadcast_address(self):
        while not self.be_added:
            print("broadcast")
            self._socket.sendto(self._broadcast_data, ('<broadcast>', 16666))  # 表示广播到16666端口
            time.sleep(2)

    def msg_receiver(self):
        while True:
            data, addr = self.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.MOUSE_MOVE:
                self._mouse.move(msg.data[0],msg.data[1])
            elif msg.msg_type == MsgType.MOUSE_MOVE_TO: # 跨屏初始位置
                self._mouse.move_to(msg.data)
                threading.Thread(target=self.mouse_listener).start()
            elif msg.msg_type == MsgType.MOUSE_CLICK:
                self._mouse.click(msg.data[2], msg.data[3])
            elif msg.msg_type == MsgType.MOUSE_SCROLL:
                self._mouse.scroll(msg.data[0], msg.data[1])
            elif msg.msg_type == MsgType.SUCCESS_JOIN:
                self.server_addr = addr
                self.be_added = True

    def mouse_listener(self):
        while True:
            data = self._mouse.get_position()
            if self.be_added and self.server_addr and data[0]<=1:
                msg = Message(MsgType.MOUSE_BACK, f"{data[0]},{data[1]}")
                self.sendto(msg.to_bytes(), self.server_addr)
                break
            time.sleep(0.1)


    def start_msg_listener(self):
        self.msg_listener = threading.Thread(target=self.msg_receiver)
        self.msg_listener.start()
        return self.msg_listener

    def start_broadcast(self):
        self._broadcast_thread = threading.Thread(target=self.broadcast_address)
        self._broadcast_thread.start()
        return self._broadcast_thread
