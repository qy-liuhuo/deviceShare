import threading
from Message import Message, MsgType
from MouseController import MouseController
from Udp import Udp


class Server(Udp):
    def __init__(self, port=16666):
        super().__init__(port)
        self.clients = []
        self.cur_client = None
        self._mouse = MouseController()

    def msg_receiver(self):
        while True:
            data, addr = self.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.DEVICE_UP and addr not in self.clients:
                self.clients.append(addr)
                self.cur_client = addr  # 临时测试
                self.sendto(Message(MsgType.STOP_BROADCAST, None).to_bytes(), addr)
                print(f"client {addr} connected")

    def start_msg_listener(self):
        self.msg_listener = threading.Thread(target=self.msg_receiver)
        self.msg_listener.start()
        return self.msg_listener

    def add_mouse_listener(self):
        def on_click(x, y, button, pressed):
            msg = Message(MsgType.MOUSE_CLICK, f"{x},{y},{button},{pressed}")
            if self.cur_client:
                self.sendto(msg.to_bytes(), self.cur_client)

        def on_move(x, y):
            last_pos = self._mouse.get_last_position()
            msg = Message(MsgType.MOUSE_MOVE, f"{x-last_pos[0]},{y-last_pos[1]}")
            if self.cur_client:
                self.sendto(msg.to_bytes(), self.cur_client)
            self._mouse.update_last_position()

        mouse_listener = self._mouse.mouse_listener(on_click, on_move)
        mouse_listener.start()
        return mouse_listener
