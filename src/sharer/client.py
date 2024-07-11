import socket
import threading
import time
import pyperclip
import rsa
from zeroconf import Zeroconf, ServiceBrowser
from src.controller.keyboard_controller import KeyboardController
from src.screen_manager.position import Position
from src.my_socket.message import Message, MsgType
from src.controller.mouse_controller import MouseController
from src.my_socket.my_socket import Udp, TcpClient, UDP_PORT, TCP_PORT
from screeninfo import get_monitors

from src.utils.device_name import get_device_name
from src.utils.rsautil import RsaUtil, decrypt
from src.utils.service_listener import ServiceListener
class Client:

    def __init__(self):
        self.device_id = get_device_name()
        self.position = None
        self.udp = Udp(UDP_PORT)
        self.udp.allow_broadcast()
        self.be_added = False
        self._mouse = MouseController()
        self._mouse.focus = False
        self._keyboard = KeyboardController()
        monitors = get_monitors()
        self.screen_size_width = monitors[0].width
        self.screen_size_height = monitors[0].height
        self._broadcast_data = Message(MsgType.DEVICE_ONLINE,
                                       f'{self.screen_size_width}, {self.screen_size_height}').to_bytes()
        self.rsa_util = RsaUtil()
        self.server_addr = None
        self.zeroconf = Zeroconf()
        ServiceBrowser(self.zeroconf, "_deviceShare._tcp.local.", ServiceListener(self))
        while self.server_addr is None:
            time.sleep(1)
        self.start_broadcast()
        self.start_msg_listener()
        self.last_clipboard_text = ''
        threading.Thread(target=self.clipboard_listener).start()

    def request_access(self):
        tcp_client = TcpClient((self.server_addr[0], TCP_PORT))
        msg = Message(MsgType.SEND_PUBKEY, f'{self.device_id}, {self.rsa_util.public_key.save_pkcs1().decode()}')
        tcp_client.send(msg.to_bytes())
        data = tcp_client.recv()
        msg = Message.from_bytes(data)
        if msg.msg_type == MsgType.KEY_CHECK:
            decrypt_key = decrypt(self.rsa_util.private_key, msg.data[0].encode())
            msg = Message(MsgType.KEY_CHECK_RESPONSE, f'{decrypt_key.decode()}')
            tcp_client.send(msg.to_bytes())
            data = tcp_client.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.ACCESS_ALLOW:
                self.be_added = True
                self.position = Position(int(msg.data[0]))
            elif msg.msg_type == MsgType.ACCESS_DENY:
                print('Access denied')
        tcp_client.close()

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

    def judge_move_out(self, x,y):
        if x <= 5 and self.position == Position.RIGHT:
            return True
        elif x >= self.screen_size_width - 5 and self.position == Position.LEFT:
            return True
        elif y <= 5 and self.position == Position.BOTTOM:
            return True
        elif y >= self.screen_size_height - 5 and self.position == Position.TOP:
            return True
        return False

    def msg_receiver(self):
        while True:
            data, addr = self.udp.recv()
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.MOUSE_MOVE:
                position = self._mouse.move(msg.data[0], msg.data[1])
                if self.judge_move_out(position[0],position[1]) and self.be_added and self.server_addr and self._mouse.focus:
                    msg = Message(MsgType.MOUSE_BACK, f"{int(position[0])},{int(position[1])}")
                    tcp_client = TcpClient((self.server_addr[0], TCP_PORT))
                    tcp_client.send(msg.to_bytes())
                    tcp_client.close()
                    self._mouse.focus = False
            elif msg.msg_type == MsgType.MOUSE_MOVE_TO:  # 跨屏初始位置
                self._mouse.focus = True
                self._mouse.move_to(msg.data)
            elif msg.msg_type == MsgType.MOUSE_CLICK:
                self._mouse.click(msg.data[2], msg.data[3])
            elif msg.msg_type == MsgType.KEYBOARD_CLICK:
                self._keyboard.click(msg.data[0],(msg.data[1],msg.data[2]))
            elif msg.msg_type == MsgType.MOUSE_SCROLL:
                self._mouse.scroll(msg.data[0], msg.data[1])
            # elif msg.msg_type == MsgType.SUCCESS_JOIN:
            #     self.server_addr = addr
            #     self.be_added = True
            #     self.position = Position(int(msg.data[2]))
            elif msg.msg_type == MsgType.CLIPBOARD_UPDATE:
                self.last_clipboard_text = msg.data
                pyperclip.copy(msg.data)
            elif msg.msg_type == MsgType.POSITION_CHANGE:
                self.position = Position(int(msg.data[0]))

    def start_msg_listener(self):
        msg_listener = threading.Thread(target=self.msg_receiver)
        msg_listener.start()
        return msg_listener

    def start_broadcast(self):
        broadcast_thread = threading.Thread(target=self.broadcast_address)
        broadcast_thread.start()
        return broadcast_thread
