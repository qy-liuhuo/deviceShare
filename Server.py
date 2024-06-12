import queue
import socket
import threading

import pyautogui
import pynput

from Device import DeviceManager, Position
from Message import Message, MsgType
from MouseController import MouseController
from MySocket import Udp, Tcp, UDP_PORT,TCP_PORT




class Server:
    def __init__(self):
        self.udp = Udp(UDP_PORT)
        self.tcp = Tcp(TCP_PORT)
        self.device_manager = DeviceManager()
        self._mouse = MouseController()
        self.lock = threading.Lock()
        self.start_event_processor()
        self.start_msg_listener()
        self.screen_size = pyautogui.size()

    def msg_receiver(self):
        while True:
            data, addr = self.udp.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.DEVICE_ONLINE: # 客户端上线及心跳
                self.device_manager.refresh(ip=addr[0], screen_width=msg.data[0], screen_height=msg.data[1] ,position=Position.RIGHT) # 临时测试
                # self.cur_client = addr  # 临时测试
                self.udp.sendto(Message(MsgType.SUCCESS_JOIN,
                                        f'{socket.gethostbyname(socket.gethostname())},{UDP_PORT}').to_bytes(), addr)
                print(f"client {addr} connected")

    def event_processor(self):
        while True:
            data, addr = self.tcp.event_queue.get()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.MOUSE_BACK:
                self.lock.acquire()
                self.device_manager.cur_device = None
                self._mouse.move_to((self.screen_size.width, msg.data[1]))
                self.lock.release()

    def start_msg_listener(self):
        msg_listener = threading.Thread(target=self.msg_receiver)
        msg_listener.start()
        return msg_listener

    def start_event_processor(self):
        event_processor = threading.Thread(target=self.event_processor)
        event_processor.start()
        return event_processor

    def add_mouse_listener(self):
        def on_click(x, y, button, pressed):
            msg = Message(MsgType.MOUSE_CLICK, f"{x},{y},{button},{pressed}")
            if self.device_manager.cur_device:
                self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())

        def on_move(x, y):
            last_pos = self._mouse.get_last_position()
            msg = Message(MsgType.MOUSE_MOVE, f"{x - last_pos[0]},{y - last_pos[1]}")
            if self.device_manager.cur_device is None:
                return False
            if self.device_manager.cur_device:
                self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())
            # if self._mouse.get_position()[0] >= self.screen_size.width - 10: # 向右移出
            #     self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())
            if self._mouse.get_position()[0] <= 100 or self._mouse.get_position()[1] <= 100 or \
                    self._mouse.get_position()[0] >= self.screen_size.width-100 or self._mouse.get_position()[1] >= self.screen_size.height-100:
                self._mouse.move_to((int(self.screen_size.width/2), int(self.screen_size.height/2)))
            self._mouse.update_last_position()

        def on_scroll(x, y, dx, dy):
            msg = Message(MsgType.MOUSE_SCROLL, f"{dx},{dy}")
            if self.device_manager.cur_device:
                self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())

        mouse_listener = self._mouse.mouse_listener(on_click, on_move, on_scroll, suppress=True)
        mouse_listener.start()
        return mouse_listener

    def main_loop(self):
        while True:
            with pynput.mouse.Events() as events:
                for event in events:
                    if isinstance(event, pynput.mouse.Events.Move):
                        x, y = event.x, event.y
                        if x > self.screen_size.width-10 and self.device_manager.cur_device is None:
                            self._mouse.focus = False
                            self.lock.acquire()
                            self.device_manager.cur_device = self.device_manager.get_device_by_position(Position.RIGHT)
                            self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, f'{0},{y}').to_bytes(),
                                            self.device_manager.cur_device.get_udp_address())
                            self._mouse.move_to((int(self.screen_size.width/2), int(self.screen_size.height/2)))
                            self.lock.release()
                            break

            if not self._mouse.focus:
                mouse_listener = self.add_mouse_listener()
                mouse_listener.join()
                self._mouse.focus = True
