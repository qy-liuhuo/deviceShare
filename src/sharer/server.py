import socket
import threading
import time

from screeninfo import get_monitors
import pynput


from src.controller.keyboard_controller import KeyboardController, KeyFactory
from src.device.device_manager import DeviceManager
from src.screen_manager.position import Position
from src.my_socket.message import Message, MsgType
from src.controller.mouse_controller import MouseController
from src.my_socket.my_socket import Udp, Tcp, UDP_PORT, TCP_PORT
import pyperclip


class Server:
    def __init__(self):
        self.udp = Udp(UDP_PORT)
        self.udp.allow_broadcast()
        self.tcp = Tcp(TCP_PORT)
        self.device_manager = DeviceManager()
        self._mouse = MouseController()
        self._keyboard = KeyboardController()
        self._keyboard_factory = KeyFactory()
        self.lock = threading.Lock()
        self.start_event_processor()
        self.start_msg_listener()
        monitors = get_monitors()
        self.screen_size_width = monitors[0].width
        self.screen_size_height = monitors[0].height
        self.last_clipboard_text = ''
        threading.Thread(target=self.clipboard_listener).start()
        threading.Thread(target=self.main_loop).start()



    def msg_receiver(self):
        while True:
            data, addr = self.udp.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.DEVICE_ONLINE:  # 客户端上线及心跳
                position = self.device_manager.refresh(ip=addr[0], screen_width=msg.data[0], screen_height=msg.data[1])  # 临时测试
                # self.cur_client = addr  # 临时测试
                self.udp.sendto(Message(MsgType.SUCCESS_JOIN,
                                        f'{socket.gethostbyname(socket.gethostname())},{UDP_PORT},{int(position)}').to_bytes(), addr)

            elif msg.msg_type == MsgType.CLIPBOARD_UPDATE:
                self.last_clipboard_text = msg.data
                pyperclip.copy(msg.data)

    def event_processor(self):
        while True:
            data, addr = self.tcp.event_queue.get()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.MOUSE_BACK:
                self.lock.acquire()
                if self.device_manager.cur_device is not None:
                    device_position = self.device_manager.cur_device.position
                    self.device_manager.cur_device = None
                    self._mouse.focus = True
                    if device_position == Position.RIGHT:
                        self._mouse.move_to((self.screen_size_width - 30, msg.data[1]))
                    elif device_position == Position.LEFT:
                        self._mouse.move_to((30, msg.data[1]))
                    elif device_position == Position.TOP:
                        self._mouse.move_to((msg.data[0], 30))
                    elif device_position == Position.BOTTOM:
                        self._mouse.move_to((msg.data[0], self.screen_size_height - 30))
                self.lock.release()

    def start_msg_listener(self):
        msg_listener = threading.Thread(target=self.msg_receiver)
        msg_listener.start()
        return msg_listener

    def start_event_processor(self):
        event_processor = threading.Thread(target=self.event_processor)
        event_processor.start()
        return event_processor

    def clipboard_listener(self):
        while True:
            new_clip_text = pyperclip.paste()
            if new_clip_text != '' and new_clip_text != self.last_clipboard_text:
                self.last_clipboard_text = new_clip_text
                self.broadcast_clipboard(new_clip_text)
            time.sleep(1)

    def broadcast_clipboard(self, text):
        msg = Message(MsgType.CLIPBOARD_UPDATE, text)
        self.udp.sendto(msg.to_bytes(), ('<broadcast>', UDP_PORT))

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
            if not self._mouse.focus and self._mouse.get_position()[0] <= 200 or self._mouse.get_position()[1] <= 200 or \
                    self._mouse.get_position()[0] >= self.screen_size_width - 200 or self._mouse.get_position()[
                1] >= self.screen_size_height - 200:
                self._mouse.move_to((int(self.screen_size_width / 2), int(self.screen_size_height / 2)))
            self._mouse.update_last_position()

        def on_scroll(x, y, dx, dy):
            msg = Message(MsgType.MOUSE_SCROLL, f"{dx},{dy}")
            if self.device_manager.cur_device:
                self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())

        mouse_listener = self._mouse.mouse_listener(on_click, on_move, on_scroll, suppress=True)
        mouse_listener.start()
        return mouse_listener

    def add_keyboard_listener(self):
        def on_press(key):
            data = self._keyboard_factory.input(key)
            msg = Message(MsgType.KEYBOARD_CLICK, f"press,{data[0]},{data[1]}")
            if self.device_manager.cur_device:
                self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())

        def on_release(key):
            data = self._keyboard_factory.input(key)
            msg = Message(MsgType.KEYBOARD_CLICK, f"release,{data[0]},{data[1]}")
            if self.device_manager.cur_device:
                self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())

        keyboard_listener = self._keyboard.keyboard_listener(on_press, on_release)
        keyboard_listener.start()
        return keyboard_listener

    def judge_move_out(self, x, y):
        if x <= 5:
            return Position.LEFT
        if y <= 5:
            return Position.TOP
        if x >= self.screen_size_width - 5:
            return Position.RIGHT
        if y >= self.screen_size_height - 5:
            return Position.BOTTOM
        return False

    def update_position(self):
        self.device_manager.update_device_by_file()
        for device in self.device_manager.devices:
            self.udp.sendto(Message(MsgType.POSITION_CHANGE, f'{int(device.position)}').to_bytes(),
                            device.get_udp_address())

    def main_loop(self):
        while True:
            with pynput.mouse.Events() as events:
                for event in events:
                    if isinstance(event, pynput.mouse.Events.Move):
                        x, y = event.x, event.y
                        move_out = self.judge_move_out(x, y)
                        if move_out and self.device_manager.cur_device is None:
                            self._mouse.focus = False
                            self.lock.acquire()
                            self.device_manager.cur_device = self.device_manager.get_device_by_position(move_out)
                            time.sleep(0.01)  # 不加识别不到？
                            if self.device_manager.cur_device is not None:
                                if move_out == Position.LEFT:
                                    self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, f'{self.device_manager.cur_device.screen.screen_width-30},{y}').to_bytes(),
                                                    self.device_manager.cur_device.get_udp_address())
                                elif move_out == Position.RIGHT:
                                    self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, f'{30},{y}').to_bytes(),
                                                    self.device_manager.cur_device.get_udp_address())
                                elif move_out == Position.TOP:
                                    self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, f'{x},{self.device_manager.cur_device.screen.screen_height-30}').to_bytes(),
                                                    self.device_manager.cur_device.get_udp_address())
                                elif move_out == Position.BOTTOM:
                                    self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, f'{x},{30}').to_bytes(),
                                                    self.device_manager.cur_device.get_udp_address())
                                self._mouse.move_to((int(self.screen_size_width / 2), int(self.screen_size_height / 2)))
                                self.lock.release()
                                break

            if not self._mouse.focus:
                mouse_listener = self.add_mouse_listener()
                keyboard_listener = self.add_keyboard_listener()
                mouse_listener.join()
                keyboard_listener.stop()  # 鼠标监听结束后关闭键盘监听
                self._mouse.focus = True
