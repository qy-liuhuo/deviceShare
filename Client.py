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
        self._broadcast_data = Message(MsgType.DEVICE_UP, (self._ip, self._port)).to_bytes()

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
                self._mouse.move(msg.data)
            elif msg.msg_type == MsgType.MOUSE_CLICK:
                self._mouse.click(msg.data[2], msg.data[3])
            elif msg.msg_type == MsgType.STOP_BROADCAST:
                print("stop broadcast")
                self.be_added = True

    def start_msg_listener(self):
        self.msg_listener = threading.Thread(target=self.msg_receiver)
        self.msg_listener.start()
        return self.msg_listener

    def start_broadcast(self):
        self._broadcast_thread = threading.Thread(target=self.broadcast_address)
        self._broadcast_thread.start()
        return self._broadcast_thread
