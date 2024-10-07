"""
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: MobiNets
"""
import logging
import socket
import threading
import time
from zeroconf import Zeroconf, ServiceBrowser

from src.controller.clipboard_controller import get_clipboard_controller
from src.controller.file_controller import FileController_client
from src.controller.keyboard_controller import KeyboardController, get_keyboard_controller
from src.gui.client_gui import ClientGUI
from src.gui.position import Position
from src.communication.message import Message, MsgType
from src.controller.mouse_controller import MouseController, get_click_button
from src.communication.my_socket import Udp, TcpClient, UDP_PORT, TCP_PORT, read_data_from_tcp_socket
from screeninfo import get_monitors

from src.utils.device_name import get_device_name
from src.utils.rsautil import RsaUtil, decrypt
from src.utils.service_listener import ServiceListener


class Client:
    """
    被控机类
    """

    def __init__(self, app):

        self.logging = logging.getLogger("deviceShare.Client")  # 日志
        self.init_screen_info()  # 初始化屏幕信息
        self.clipboard_controller = get_clipboard_controller()  # 获取剪切板控制器
        self._keyboard = get_keyboard_controller()  # 键盘控制器
        self.file_controller = None
        self._mouse = MouseController()  # 鼠标控制器
        self._mouse.focus = False  # 鼠标焦点
        self.device_id = get_device_name()  # 获取设备名称
        self.position = None  # 位置
        self.udp = Udp(UDP_PORT)  # udp通信
        self.udp.allow_broadcast()  # 允许广播
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # tcp服务端
        self.tcp_server.bind(("0.0.0.0", TCP_PORT))  # 绑定端口
        self.tcp_server.listen(5)  # 监听
        self.be_added = False  # 是否被添加到服务
        self.rsa_util = RsaUtil()  # rsa加密工具
        self.server_ip = None  # 服务端ip
        self.zeroconf = Zeroconf()  # zeroconf服务
        self.gui = ClientGUI(app)  # 客户端gui

    def run(self):
        """
        启动被控机,并启动各种监听线程
        :param self:
        :return:
        """
        threading.Thread(target=self.wait_for_connect, daemon=True).start()
        try:
            self.gui.run()
        except Exception as e:
            self.logging.error(e)
        finally:
            self.close()

    def send_offline_msg(self):
        """
        发送离线消息
        :param self:
        :return:
        """
        if self.server_ip is not None:
            msg = Message(MsgType.CLIENT_OFFLINE, {'device_id': self.device_id})
            # 使用tcp发送离线消息
            tcp_client = TcpClient((self.server_ip, TCP_PORT))
            tcp_client.send(msg.to_bytes())
            tcp_client.close()

    def init_screen_info(self):
        """
        初始化屏幕信息
        :param self:
        :return:
        """
        monitors = get_monitors()
        self.screen_size_width = monitors[0].width
        self.screen_size_height = monitors[0].height

    def wait_for_connect(self):
        """
        服务发现，建立连接，启动各种监听线程
        :param self:
        :return:
        """
        ServiceBrowser(self.zeroconf, "_deviceShare._tcp.local.", ServiceListener(self))
        while self.server_ip is None:
            time.sleep(1)
        self.request_access()
        self.file_controller = FileController_client(self.server_ip)
        threading.Thread(target=self.heartbeat).start()  # 心跳机制
        threading.Thread(target=self.msg_receiver).start()  # 消息接收
        threading.Thread(target=self.clipboard_listener).start()  # 剪切板监听
        threading.Thread(target=self.tcp_listener).start()  # tcp监听
        threading.Thread(target=self.file_controller.file_listener).start()  # 文件监听

    def tcp_listener(self):
        """
        tcp监听服务
        :param self:
        :return:
        """
        while True:
            client, addr = self.tcp_server.accept()
            self.logging.info(f"Connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client, addr), daemon=True)  # 处理客户端请求线程
            client_handler.start()

    def handle_client(self, client_socket, addr):
        """
        处理客户端请求线程
        :param self:
        :param client_socket:
        :param addr:
        :return:
        """
        try:
            data = read_data_from_tcp_socket(client_socket)
            msg = Message.from_bytes(data)
            if msg.msg_type == MsgType.CLIPBOARD_UPDATE:
                new_text = self.rsa_util.decrypt(bytes.fromhex(msg.data['text'])).decode()
                self.clipboard_controller.copy(new_text)
            elif msg.msg_type == MsgType.FILE_MSG:
                self.file_controller.save_file(msg)
        except Exception as e:
            self.logging.error(e)
        finally:
            client_socket.close()

    def request_access(self):
        """
        请求建立连接
        :param self:
        :return:
        """
        while not self.be_added:
            tcp_client = TcpClient((self.server_ip, TCP_PORT))
            try:
                msg = Message(MsgType.SEND_PUBKEY,
                              {"device_id": self.device_id,
                               'public_key': self.rsa_util.public_key.save_pkcs1().decode()})
                tcp_client.send(msg.to_bytes())
                data = tcp_client.recv()
                if data is None:
                    tcp_client.close()
                    continue
                msg = Message.from_bytes(data)
                if msg.msg_type == MsgType.KEY_CHECK:  # 服务端返回公钥
                    decrypt_key = self.rsa_util.decrypt(bytes.fromhex(msg.data['key']))  # 解密服务端返回的key
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
                    if msg.msg_type == MsgType.ACCESS_ALLOW:  # 服务端允许连接
                        self.logging.info('Access allow')
                        self.be_added = True
                        self.position = Position(int(msg.data['position']))
                    elif msg.msg_type == MsgType.ACCESS_DENY:  # 服务端拒绝连接
                        self.logging.info('Access denied')
                        tcp_client.close()
                        break
                elif msg.msg_type == MsgType.ACCESS_DENY:
                    self.logging.info('Access denied')
                    tcp_client.close()
                    break
            except Exception as e:
                self.logging.error(e)
            finally:
                tcp_client.close()

    def clipboard_listener(self):
        """
        剪切板监听
        :param self:
        :return:
        """
        while True:
            new_clip_text = self.clipboard_controller.paste()  # 获取剪切板内容
            if new_clip_text != '' and new_clip_text != self.clipboard_controller.get_last_clipboard_text():  # 剪切板内容有变化
                self.clipboard_controller.update_last_clipboard_text(new_clip_text)
                # 发送剪切板内容给服务端
                tcp_client = TcpClient((self.server_ip, TCP_PORT))
                msg = Message(MsgType.CLIPBOARD_UPDATE, {'text': new_clip_text})
                tcp_client.send(msg.to_bytes())
                tcp_client.close()
            time.sleep(1)

    def heartbeat(self):
        """
        心跳机制,发送心跳包
        :param self:
        :return:
        """
        broadcast_data = Message(MsgType.CLIENT_HEARTBEAT, {}).to_bytes()
        while True:
            if self.server_ip:
                self.udp.sendto(broadcast_data, (self.server_ip, UDP_PORT))  # 发送心跳包
            time.sleep(2)

    def judge_move_out(self, x, y):
        """
        判断鼠标是否移出屏幕
        :param self:
        :param x:
        :param y:
        :return:
        """
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
        """
        消息接收
        :param self:
        :return:
        """
        try:
            while not self.udp.is_closed():
                data, addr = self.udp.recv()
                if data is None:
                    continue
                msg = Message.from_bytes(data)
                if msg.msg_type == MsgType.MOUSE_MOVE:  # 鼠标移动
                    position = self._mouse.move(msg.data['x'], msg.data['y'])
                    if self.judge_move_out(position[0],
                                           position[
                                               1]) and self.be_added and self.server_ip and self._mouse.focus:  # 鼠标移出屏幕
                        msg = Message(MsgType.MOUSE_BACK, {"x": position[0], "y": position[1]})
                        tcp_client = TcpClient((self.server_ip, TCP_PORT))
                        tcp_client.send(msg.to_bytes())
                        tcp_client.close()
                        self._mouse.focus = False
                elif msg.msg_type == MsgType.MOUSE_MOVE_TO:  # 跨屏初始位置
                    self.logging.info(f"Move to {msg.data['x']}, {msg.data['y']}")
                    self._mouse.focus = True
                    self._mouse.move_to((msg.data['x'], msg.data['y']))
                elif msg.msg_type == MsgType.MOUSE_CLICK:  # 鼠标点击
                    self._mouse.click(msg.data['button'], msg.data['pressed'])
                elif msg.msg_type == MsgType.KEYBOARD_CLICK:  # 键盘点击
                    self._keyboard.click(msg.data['type'], msg.data['keyData'])
                elif msg.msg_type == MsgType.MOUSE_SCROLL:  # 鼠标滚动
                    self._mouse.scroll(msg.data['dx'], msg.data['dy'])
                elif msg.msg_type == MsgType.POSITION_CHANGE:  # 屏幕位置改变
                    self.position = Position(int(msg.data['position']))
        except Exception as e:
            self.logging.error(e, stack_info=True)
            self.udp.close()

    def close(self):
        """
        关闭程序，释放资源
        :param self:
        :return:
        """
        self.send_offline_msg()
        self.gui.exit()
        self.udp.close()
        self.tcp_server.close()