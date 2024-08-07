import socket
import threading
import time
from zeroconf import Zeroconf, ServiceBrowser

from src.controller.clipboard_controller import get_clipboard_controller
from src.controller.keyboard_controller import KeyboardController
from src.screen_manager.client_gui import ClientGUI
from src.screen_manager.position import Position
from src.my_socket.message import Message, MsgType
from src.controller.mouse_controller import MouseController, get_click_button
from src.my_socket.my_socket import Udp, TcpClient, UDP_PORT, TCP_PORT, read_data_from_tcp_socket
from screeninfo import get_monitors

from src.utils.device_name import get_device_name
from src.utils.rsautil import RsaUtil, decrypt
from src.utils.service_listener import ServiceListener


class Client:

    def __init__(self,app):
        self.init_screen_info()
        self.clipboard_controller = get_clipboard_controller()
        self.device_id = get_device_name()
        self.position = None
        self.udp = Udp(UDP_PORT)
        self.udp.allow_broadcast()
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind(("0.0.0.0", TCP_PORT))
        self.tcp_server.listen(5)
        self.be_added = False
        self._mouse = MouseController()
        self._mouse.focus = False
        self._keyboard = KeyboardController()
        self.rsa_util = RsaUtil()
        self.server_ip = None
        self.zeroconf = Zeroconf()
        threading.Thread(target=self.wait_for_connect, daemon=True).start()
        self.gui = ClientGUI(app)
        self.gui.run()
        self.send_offline_msg()

    def send_offline_msg(self):
        msg = Message(MsgType.CLIENT_OFFLINE, {'device_id': self.device_id})
        # 使用tcp发送离线消息
        tcp_client = TcpClient((self.server_ip, TCP_PORT))
        tcp_client.send(msg.to_bytes())

    def init_screen_info(self):
        monitors = get_monitors()
        self.screen_size_width = monitors[0].width
        self.screen_size_height = monitors[0].height

    def wait_for_connect(self):
        ServiceBrowser(self.zeroconf, "_deviceShare._tcp.local.", ServiceListener(self))
        while self.server_ip is None:
            time.sleep(1)
        self.request_access()
        threading.Thread(target=self.heartbeat).start()  # 心跳机制
        threading.Thread(target=self.msg_receiver).start()  # 消息接收
        threading.Thread(target=self.clipboard_listener).start()  # 剪切板监听
        threading.Thread(target=self.tcp_listener).start()  # tcp监听

    def tcp_listener(self):
        while True:
            client, addr = self.tcp_server.accept()
            print(f"Connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client, addr), daemon=True)
            client_handler.start()

    def handle_client(self, client_socket, addr):
        try:
            data = read_data_from_tcp_socket(client_socket)
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.CLIPBOARD_UPDATE:
                new_text = self.rsa_util.decrypt(bytes.fromhex(msg.data['text'])).decode()
                self.clipboard_controller.copy(new_text)
        except Exception as e:
            print(e)
        finally:
            client_socket.close()

    def request_access(self):
        while not self.be_added:
            tcp_client = TcpClient((self.server_ip, TCP_PORT))
            msg = Message(MsgType.SEND_PUBKEY,
                          {"device_id": self.device_id, 'public_key': self.rsa_util.public_key.save_pkcs1().decode()})
            tcp_client.send(msg.to_bytes())
            data = tcp_client.recv()
            if data is None:
                tcp_client.close()
                continue
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.KEY_CHECK:
                decrypt_key = self.rsa_util.decrypt(bytes.fromhex(msg.data['key']))
                msg = Message(MsgType.KEY_CHECK_RESPONSE,
                              {'key': decrypt_key.hex(), 'device_id': self.device_id,
                               'screen_width': self.screen_size_width,
                               'screen_height': self.screen_size_height})
                tcp_client.send(msg.to_bytes())
                data = tcp_client.recv()
                if data is None:
                    tcp_client.close()
                    continue
                msg = Message.from_bytes(data)
                if msg.msg_type == MsgType.ACCESS_ALLOW:
                    print('Access allow')
                    self.be_added = True
                    self.position = Position(int(msg.data['position']))
                elif msg.msg_type == MsgType.ACCESS_DENY:
                    print('Access denied')
                    tcp_client.close()
                    break
            elif msg.msg_type == MsgType.ACCESS_DENY:
                print('Access denied')
                tcp_client.close()
                break
            tcp_client.close()

    def clipboard_listener(self):
        while True:
            new_clip_text = self.clipboard_controller.paste()
            if new_clip_text != '' and new_clip_text != self.clipboard_controller.get_last_clipboard_text():
                self.clipboard_controller.update_last_clipboard_text(new_clip_text)
                tcp_client = TcpClient((self.server_ip, TCP_PORT))
                msg = Message(MsgType.CLIPBOARD_UPDATE, {'text': new_clip_text})
                tcp_client.send(msg.to_bytes())
            time.sleep(1)

    def heartbeat(self):
        broadcast_data = Message(MsgType.CLIENT_HEARTBEAT, {}).to_bytes()
        while True:
            if self.server_ip:
                self.udp.sendto(broadcast_data, (self.server_ip, UDP_PORT))
            time.sleep(2)

    def judge_move_out(self, x, y):
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
            if data is None:
                continue
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.MOUSE_MOVE:
                position = self._mouse.move(msg.data['x'], msg.data['y'])
                if self.judge_move_out(position[0],
                                       position[1]) and self.be_added and self.server_ip and self._mouse.focus:
                    msg = Message(MsgType.MOUSE_BACK, {"x": position[0], "y": position[1]})
                    tcp_client = TcpClient((self.server_ip, TCP_PORT))
                    tcp_client.send(msg.to_bytes())
                    tcp_client.close()
                    self._mouse.focus = False
            elif msg.msg_type == MsgType.MOUSE_MOVE_TO:  # 跨屏初始位置
                print("moved into")
                self._mouse.focus = True
                self._mouse.move_to((msg.data['x'], msg.data['y']))
            elif msg.msg_type == MsgType.MOUSE_CLICK:
                self._mouse.click(get_click_button(msg.data['button']), msg.data['pressed'])
            elif msg.msg_type == MsgType.KEYBOARD_CLICK:
                self._keyboard.click(msg.data['type'], msg.data['keyData'])
            elif msg.msg_type == MsgType.MOUSE_SCROLL:
                self._mouse.scroll(msg.data['dx'], msg.data['dy'])
            elif msg.msg_type == MsgType.POSITION_CHANGE:
                self.position = Position(int(msg.data['position']))
