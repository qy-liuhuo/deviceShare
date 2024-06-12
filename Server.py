import queue
import socket
import threading

import pynput

from Message import Message, MsgType
from MouseController import MouseController
from MySocket import Udp, Tcp, UDP_PORT,TCP_PORT


class Server:
    def __init__(self):
        self.udp = Udp(UDP_PORT)
        self.tcp = Tcp(TCP_PORT)
        self.clients = []
        self.cur_client = None
        self._mouse = MouseController()
        self.lock = threading.Lock()
        self.start_event_processor()
        self.start_msg_listener()

    def msg_receiver(self):
        while True:
            print("msg_receiver")
            data, addr = self.udp.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.DEVICE_JOIN and addr not in self.clients:
                self.clients.append(addr)
                # self.cur_client = addr  # 临时测试
                self.udp.sendto(Message(MsgType.SUCCESS_JOIN,
                                        f'{socket.gethostbyname(socket.gethostname())},{UDP_PORT}').to_bytes(), addr)
                print(f"client {addr} connected")

    def event_processor(self):
        while True:
            print("event_processor")
            data, addr = self.tcp.event_queue.get()
            print(data)
            msg = Message.from_bytes(data)
            print(msg)
            if msg.msg_type == MsgType.MOUSE_BACK:
                self.lock.acquire()
                self.cur_client = None
                self._mouse.move_to((3840, msg.data[1]))
                self.lock.release()

    def start_msg_listener(self):
        self.msg_listener = threading.Thread(target=self.msg_receiver)
        self.msg_listener.start()
        return self.msg_listener

    def start_event_processor(self):
        self.event_processor = threading.Thread(target=self.event_processor)
        self.event_processor.start()
        return self.event_processor

    def add_mouse_listener(self):
        def on_click(x, y, button, pressed):
            msg = Message(MsgType.MOUSE_CLICK, f"{x},{y},{button},{pressed}")
            if self.cur_client:
                self.udp.sendto(msg.to_bytes(), self.cur_client)

        def on_move(x, y):
            last_pos = self._mouse.get_last_position()
            msg = Message(MsgType.MOUSE_MOVE, f"{x - last_pos[0]},{y - last_pos[1]}")
            if self.cur_client is None:
                return False
            if self.cur_client:
                self.udp.sendto(msg.to_bytes(), self.cur_client)
            if self._mouse.get_position()[0] <= 20 or self._mouse.get_position()[1] <= 20 or self._mouse.get_position()[
                0] >= 3838 or self._mouse.get_position()[1] >= 2158:
                self.udp.sendto(msg.to_bytes(), self.cur_client)
            if self._mouse.get_position()[0] <= 100 or self._mouse.get_position()[1] <= 100 or \
                    self._mouse.get_position()[0] >= 3740 or self._mouse.get_position()[1] >= 2060:
                self._mouse.move_to((500, 500))
            self._mouse.update_last_position()

        def on_scroll(x, y, dx, dy):
            msg = Message(MsgType.MOUSE_SCROLL, f"{dx},{dy}")
            if self.cur_client:
                self.udp.sendto(msg.to_bytes(), self.cur_client)

        mouse_listener = self._mouse.mouse_listener(on_click, on_move, on_scroll, suppress=True)
        mouse_listener.start()
        return mouse_listener

    def main_loop(self):
        while True:
            with pynput.mouse.Events() as events:
                for event in events:
                    if isinstance(event, pynput.mouse.Events.Move):
                        x, y = event.x, event.y
                        if x > 3838 and self.cur_client is None:
                            self._mouse.focus = False
                            self.lock.acquire()
                            self.cur_client = self.clients[0]
                            self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, f'{x - 3838},{y}').to_bytes(),
                                            self.cur_client)
                            self._mouse.move_to((500, 500))
                            self.lock.release()
                            break

            if not self._mouse.focus:
                mouse_listener = self.add_mouse_listener()
                mouse_listener.join()
                self._mouse.focus = True
