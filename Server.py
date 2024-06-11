import socket
import threading

import pynput

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
            if msg.msg_type == MsgType.DEVICE_JOIN and addr not in self.clients:
                self.clients.append(addr)
                self.cur_client = addr  # 临时测试
                self.sendto(Message(MsgType.SUCCESS_JOIN,
                                    f'{socket.gethostbyname(socket.gethostname())},{self._port}').to_bytes(), addr)
                print(f"client {addr} connected")
            elif msg.msg_type == MsgType.MOUSE_BACK:
                self._mouse.move_to((3840, msg.data[1]))

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
            msg = Message(MsgType.MOUSE_MOVE, f"{x - last_pos[0]},{y - last_pos[1]}")
            if self.cur_client:
                self.sendto(msg.to_bytes(), self.cur_client)
            if self._mouse.get_position()[0] <= 20 or self._mouse.get_position()[1] <= 20 or self._mouse.get_position()[0] >= 3838 or self._mouse.get_position()[1] >= 2158:
                self._mouse.move_to((500, 500))
            self._mouse.update_last_position()
            if self._mouse.get_position() == (0, 0):
                return False

        def on_scroll(x, y, dx, dy):
            msg = Message(MsgType.MOUSE_SCROLL, f"{dx},{dy}")
            if self.cur_client:
                self.sendto(msg.to_bytes(), self.cur_client)

        mouse_listener = self._mouse.mouse_listener(on_click, on_move, on_scroll, suppress=True)
        mouse_listener.start()
        return mouse_listener

    def main_loop(self):
        while True:
            with pynput.mouse.Events() as events:
                for event in events:
                    if isinstance(event, pynput.mouse.Events.Move):
                        x, y = event.x, event.y
                        if x > 3838:
                            self._mouse.focus = False
                            self.cur_client = self.clients[0]
                            self.sendto(Message(MsgType.MOUSE_MOVE_TO, f'{x - 3838},{y}').to_bytes(), self.cur_client)
                            self._mouse.move_to((500, 500))
                            break
            if not self._mouse.focus:
                mouse_listener = self.add_mouse_listener()
                mouse_listener.join()
