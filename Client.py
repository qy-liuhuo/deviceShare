import threading
import time

import pyperclip

from Message import Message, MsgType
from MouseController import MouseController
from MySocket import Udp, TcpClient, UDP_PORT, TCP_PORT
import pyautogui


class Client:

    def __init__(self):
        self.udp = Udp(UDP_PORT)
        self.udp.allow_broadcast()
        self.be_added = False
        self._mouse = MouseController()
        self._mouse.focus = False
        self.screen_size = pyautogui.size()
        self._broadcast_data = Message(MsgType.DEVICE_ONLINE,
                                       f'{self.screen_size.width}, {self.screen_size.height}').to_bytes()
        self.server_addr = None
        self.start_broadcast()
        self.start_msg_listener()
        self.last_clipboard_text = ''
        threading.Thread(target=self.clipboard_listener).start()

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

    def broadcast_address(self):
        while True:
            self.udp.sendto(self._broadcast_data, ('<broadcast>', UDP_PORT))  # 表示广播到16666端口
            time.sleep(2)

    def msg_receiver(self):
        while True:
            data, addr = self.udp.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.MOUSE_MOVE:
                position = self._mouse.move(msg.data[0], msg.data[1])
                if position[0] <= 1 and self.be_added and self.server_addr:
                    msg = Message(MsgType.MOUSE_BACK, f"{position[0]},{position[1]}")
                    tcp_client = TcpClient((self.server_addr[0], TCP_PORT))
                    tcp_client.send(msg.to_bytes())
                    tcp_client.close()
                    self._mouse.focus = False
            elif msg.msg_type == MsgType.MOUSE_MOVE_TO:  # 跨屏初始位置
                self._mouse.move_to(msg.data)
            elif msg.msg_type == MsgType.MOUSE_CLICK:
                self._mouse.click(msg.data[2], msg.data[3])
            elif msg.msg_type == MsgType.MOUSE_SCROLL:
                self._mouse.scroll(msg.data[0], msg.data[1])
            elif msg.msg_type == MsgType.SUCCESS_JOIN:
                self.server_addr = addr
                self.be_added = True
            elif msg.msg_type == MsgType.CLIPBOARD_UPDATE:
                self.last_clipboard_text = msg.data
                pyperclip.copy(msg.data)

    def start_msg_listener(self):
        msg_listener = threading.Thread(target=self.msg_receiver)
        msg_listener.start()
        return msg_listener

    def start_broadcast(self):
        broadcast_thread = threading.Thread(target=self.broadcast_address)
        broadcast_thread.start()
        return broadcast_thread
