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
import platform
import socket
import threading
import time
import uuid
from queue import Queue

from screeninfo import get_monitors
from zeroconf import ServiceInfo, Zeroconf

from src.controller.clipboard_controller import get_clipboard_controller
from src.controller.file_controller import FileController_server
from src.controller.keyboard_controller import KeyFactory, get_keyboard_controller
from src.utils.device import Device
from src.gui.server_gui import ServerGUI, GuiMessage
from src.gui.position import Position
from src.communication.message import Message, MsgType
from src.controller.mouse_controller import MouseController
from src.communication.my_socket import Udp, UDP_PORT, TCP_PORT, read_data_from_tcp_socket, send_data_to_tcp_socket, \
    TcpClient

from src.gui.screen import Screen
from src.communication.client_state import ClientState
from src.utils.device_storage import DeviceStorage, create_table, delete_table
from src.utils.key_storage import KeyStorage
from src.utils.net import get_local_ip
from src.utils.plantform import is_wayland
from src.utils.rsautil import encrypt


class Server:
    """
    服务端类
    """
    def __init__(self,app):
        self.logging = logging.getLogger("deviceShare.Server") # 日志
        create_table() # 创建数据库表
        self.init_screen_info() # 初始化屏幕信息
        self.clipboard_controller = get_clipboard_controller() # 获取剪贴板控制器
        self.server_queue = Queue() # 服务端队列
        self.request_queue = Queue() # 请求队列
        self.response_queue = Queue() # 响应队列
        self.thread_list = [] # 线程列表
        self.update_flag = threading.Event() # 更新标志
        self.manager_gui = ServerGUI(app, update_flag=self.update_flag, request_queue=self.request_queue,
                                     response_queue=self.response_queue) # 服务端GUI
        self.cur_device = None # 当前设备
        self._mouse = MouseController() # 鼠标控制器
        self.file_controller = FileController_server() # 文件控制器
        self._keyboard = get_keyboard_controller() # 键盘控制器
        self._keyboard_factory = KeyFactory() # 键码转换器
        self.lock = threading.Lock() # 锁
        self.udp = Udp(UDP_PORT) # UDP
        self.udp.allow_broadcast() # 允许广播
        # self.tcp = Tcp(TCP_PORT)
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP服务器
        self.tcp_server.bind(("0.0.0.0", TCP_PORT)) # 绑定
        self.tcp_server.listen(10) # 监听
        self.thread_list.append(threading.Thread(target=self.tcp_listener)) # TCP监听线程
        self.thread_list.append(threading.Thread(target=self.msg_receiver)) # 消息接收线程
        self.thread_list.append(threading.Thread(target=self.clipboard_listener)) # 剪贴板监听线程
        self.thread_list.append(threading.Thread(target=self.valid_checker)) # 客户端在线检查线程
        self.thread_list.append(threading.Thread(target=self.main_loop)) # 主循环线程
        self.thread_list.append(threading.Thread(target=self.update_position)) # 更新位置线程
        self.thread_list.append(threading.Thread(target=self.file_controller.file_listener)) # 文件监听线程

    def run(self):
        """
        运行
        :return:
        """
        try:
            self.service_register() # 服务注册
            self.start_all_threads() # 启动所有线程
            self.manager_gui.run() # 运行GUI
        except Exception as e:
            self.logging.error(e)
        finally:
            self.close() # 关闭


    def valid_checker(self):
        """
        客户端在线检查
        :return:
        """
        device_storage = DeviceStorage() # 设备存储
        try:
            while True:
                devices = device_storage.get_all_devices()
                for device in devices:
                    if not device.check_valid():
                        device_storage.delete_device(device.device_id) # 删除设备
                        self.manager_gui.device_offline_notify(device.device_id) # 设备下线通知
                        if self.cur_device == device:
                            self.cur_device = None # 当前设备置空
                        self.manager_gui.update_devices() # 更新设备
                time.sleep(5)
        except InterruptedError:
            device_storage.close()

    def start_all_threads(self):
        """
        启动所有线程
        :return:
        """
        for thread in self.thread_list:
            thread.setDaemon(True)
            thread.start()

    def init_screen_info(self):
        """
        初始化屏幕信息
        :return:
        """
        monitors = get_monitors()
        self.screen_size_width = monitors[0].width
        self.screen_size_height = monitors[0].height

    def service_register(self):
        """
        服务注册
        :return:
        """
        info = ServiceInfo(type_="_deviceShare._tcp.local.", name="_deviceShare._tcp.local.",
                           addresses=[socket.inet_aton(get_local_ip())], port=UDP_PORT, weight=0, priority=0,
                           properties={"tcp_port": str(TCP_PORT), "udp_port": str(UDP_PORT)})
        self.zeroconf = Zeroconf()
        self.zeroconf.register_service(info)

    def msg_receiver(self):
        """
        UDP息接收
        :return:
        """
        device_storage = DeviceStorage()
        try:
            while True:
                data, addr = self.udp.recv() # 接收数据
                if data is None:
                    continue
                msg = Message.from_bytes(data)
                if msg.msg_type == MsgType.CLIENT_HEARTBEAT: # 客户端心跳
                    device_storage.update_heartbeat(ip=addr[0])
                elif msg.msg_type == MsgType.CLIPBOARD_UPDATE: # 剪贴板更新
                    self.clipboard_controller.copy(msg.data['text']) # 复制
                    self.clipboard_controller.update_last_clipboard_text(msg.data['text']) # 更新剪贴板文本
        except InterruptedError:
            device_storage.close()
        finally:
            self.udp.close()

    def tcp_listener(self):
        """
        TCP监听
        :return:
        """
        while True:
            client, addr = self.tcp_server.accept()
            self.logging.info(f"Connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client, addr), daemon=True)
            client_handler.start()

    def handle_access(self, access_client_socket, msg, addr):
        """
        处理客户端请求
        :param access_client_socket: 访问客户端套接字
        :param msg: 消息
        :param addr: 地址
        :return:
        """
        keys_manager = KeyStorage()
        state = ClientState.WAITING_FOR_KEY # 等待密钥
        random_key = None # 随机密钥
        new_device = Device(ip=addr[0], screen=None, position=Position.NONE) # 新设备
        if msg.msg_type == MsgType.SEND_PUBKEY and state == ClientState.WAITING_FOR_KEY: # 发送公钥
            client_id = msg.data['device_id']
            public_key = msg.data['public_key']
            new_device.pub_key = public_key
            new_device.device_id = client_id
            temp = keys_manager.get_key(client_id)
            if temp is None or temp != public_key: # 无密钥或密钥不匹配
                self.manager_gui.device_show_online_require(addr[0]) # 上线请求
                self.manager_gui.request_queue.put(
                    GuiMessage(GuiMessage.MessageType.ACCESS_REQUIRE, {"device_id": client_id})) # 请求队列
                result = self.response_queue.get() # 响应队列
                if result.data['result']: # 结果
                    keys_manager.set_key(client_id, public_key) # 设置密钥

                else:
                    send_data_to_tcp_socket(access_client_socket,
                                            Message(MsgType.ACCESS_DENY, {'result': 'access_deny'}).to_bytes()) # 拒绝
                    return
            random_key = uuid.uuid1().bytes # 随机密钥
            send_data_to_tcp_socket(access_client_socket, Message(MsgType.KEY_CHECK,
                                                                  {'key': encrypt(public_key,
                                                                                  random_key).hex()}).to_bytes()) # 发送密钥检查
            state = ClientState.WAITING_FOR_CHECK # 更新状态
            data = read_data_from_tcp_socket(access_client_socket) # 读取数据
            msg = Message.from_bytes(data) # 消息
            if msg.msg_type == MsgType.KEY_CHECK_RESPONSE and state == ClientState.WAITING_FOR_CHECK: # 密钥检查响应
                if msg.data['key'] == random_key.hex(): # 密钥匹配
                    new_device.screen = Screen(screen_width=msg.data['screen_width'],
                                               screen_height=msg.data['screen_height'])
                    device_storage = DeviceStorage()
                    device_storage.add_device(new_device)  # 同时会更新device的position
                    device_storage.close()
                    send_data_to_tcp_socket(access_client_socket, Message(MsgType.ACCESS_ALLOW,
                                                                          {'position': int(
                                                                              new_device.position)}).to_bytes())
                    self.manager_gui.device_online_notify(new_device.device_id)
                    self.manager_gui.update_devices()
                    state = ClientState.CONNECT # 更新状态
                else: # 密钥不匹配
                    send_data_to_tcp_socket(access_client_socket,
                                            Message(MsgType.ACCESS_DENY, {'result': 'access_deny'}).to_bytes())
                    state = ClientState.WAITING_FOR_KEY
            else:
                send_data_to_tcp_socket(access_client_socket,
                                        Message(MsgType.ACCESS_DENY, {'result': 'access_deny'}).to_bytes())
        else:
            send_data_to_tcp_socket(access_client_socket,
                                    Message(MsgType.ACCESS_DENY, {'result': 'access_deny'}).to_bytes())

    def handle_client(self, client_socket, addr):
        """
        处理客户端
        :param client_socket:  客户端套接字
        :param addr:  地址
        :return:
        """
        data = read_data_from_tcp_socket(client_socket) # 读取数据
        msg = Message.from_bytes(data) # 消息
        self.logging.info(f"Message from {addr}: {msg}")
        try:
            if msg.msg_type == MsgType.SEND_PUBKEY: # 发送公钥
                self.handle_access(client_socket, msg, addr)
            elif msg.msg_type == MsgType.CLIENT_OFFLINE: # 客户端下线
                device_storage = DeviceStorage()
                device_storage.delete_device(msg.data['device_id'])
                device_storage.close()
                self.manager_gui.device_offline_notify(msg.data['device_id'])
                if self.cur_device and self.cur_device.device_id == msg.data['device_id']:
                    self.cur_device = None
                self.manager_gui.update_devices()
            elif msg.msg_type == MsgType.MOUSE_BACK: # 鼠标返回
                self.lock.acquire()
                if self.cur_device is not None:
                    device_position = self.cur_device.position
                    self.cur_device = None
                    self._mouse.focus = True
                    if device_position == Position.RIGHT:
                        self._mouse.move_to((self.screen_size_width - 30, msg.data['y']))
                    elif device_position == Position.LEFT:
                        self._mouse.move_to((30, msg.data['y']))
                    elif device_position == Position.TOP:
                        self._mouse.move_to((msg.data['x'], 30))
                    elif device_position == Position.BOTTOM:
                        self._mouse.move_to((msg.data['x'], self.screen_size_height - 30))
                self.lock.release()
                send_data_to_tcp_socket(client_socket, Message(MsgType.TCP_ECHO).to_bytes())
            elif msg.msg_type == MsgType.CLIPBOARD_UPDATE: # 剪贴板更新
                self.clipboard_controller.copy(msg.data['text'])
                self.clipboard_controller.update_last_clipboard_text(msg.data['text'])
                self.broadcast_clipboard(msg.data['text'])
            elif msg.msg_type == MsgType.FILE_MSG:
                self.file_controller.save_file(msg)
        except ConnectionResetError:
            self.logging.warning(f"Connection from {addr} closed")
        finally:
            client_socket.close()

    def clipboard_listener(self):
        """
        剪贴板监听
        :return:
        """
        while True:
            new_clip_text = self.clipboard_controller.paste()
            if new_clip_text != '' and new_clip_text != self.clipboard_controller.get_last_clipboard_text():
                self.clipboard_controller.update_last_clipboard_text(new_clip_text)
                self.broadcast_clipboard(new_clip_text)
            time.sleep(1)

    def broadcast_clipboard(self, text):
        """
        广播剪贴板
        :param text: 文本
        :return:
        """
        device_storage = DeviceStorage()
        for device in device_storage.get_all_devices():
            text_encrypted = encrypt(device.pub_key, text.encode()).hex() # 加密
            msg = Message(MsgType.CLIPBOARD_UPDATE, {'text': text_encrypted}) # 剪贴板更新
            tcp_client = TcpClient((device.ip, TCP_PORT))
            tcp_client.send(msg.to_bytes())
            tcp_client.close()

    def add_mouse_listener(self):
        """
        添加鼠标监听
        :return:
        """
        def on_click(x, y, button, pressed):
            """
            鼠标点击
            :param x: 点击x坐标
            :param y: 点击y坐标
            :param button: 按钮
            :param pressed: press or release
            :return:
            """
            msg = Message(MsgType.MOUSE_CLICK, {'x': x, 'y': y, 'button': str(button), 'pressed': pressed})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())

        def on_move(x, y):
            """
            鼠标移动
            :param x: x坐标
            :param y: y坐标
            :return:
            """
            last_pos = self._mouse.get_last_position()
            msg = Message(MsgType.MOUSE_MOVE, {'x': x - last_pos[0], 'y': y - last_pos[1]}) # 鼠标移动
            if self.cur_device is None:
                return False
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())
            # if self._mouse.get_position()[0] >= self.screen_size.width - 10: # 向右移出
            #     self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())
            if not self._mouse.focus and self._mouse.get_position()[0] <= 200 or self._mouse.get_position()[1] <= 200 or \
                    self._mouse.get_position()[0] >= self.screen_size_width - 200 or self._mouse.get_position()[1] >= self.screen_size_height - 200:
                self._mouse.move_to((int(self.screen_size_width / 2), int(self.screen_size_height / 2)))
            self._mouse.update_last_position()


        def on_scroll(x, y, dx, dy):
            """
            鼠标滚动
            :param x: x坐标
            :param y: y坐标
            :param dx: x位移
            :param dy: y位移
            :return:
            """
            msg = Message(MsgType.MOUSE_SCROLL, {'dx': dx, 'dy': dy})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())

        mouse_listener = self._mouse.mouse_listener(on_click, on_move, on_scroll, suppress=True) # 鼠标监听
        mouse_listener.start() # 启动
        return mouse_listener

    def add_mouse_listener_linux(self):
        """
        添加Linux鼠标监听
        :return:
        """
        def on_click(x, y, button, pressed):
            """
            Linux 鼠标点击
            :param x:
            :param y:
            :param button:
            :param pressed:
            :return:
            """
            msg = Message(MsgType.MOUSE_CLICK, {'x': x, 'y': y, 'button': str(button), 'pressed': pressed})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())
        def on_move_linux(dx, dy):
            """
            Linux 鼠标移动
            :param dx: 相对x位移
            :param dy: 相对y位移
            :return:
            """
            if self.cur_device:
                msg = Message(MsgType.MOUSE_MOVE, {'x': dx, 'y': dy})
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())
                return True
            else:
                return False
        def on_scroll(x, y, dx, dy):
            """
            Linux 鼠标滚动
            :param x:
            :param y:
            :param dx:
            :param dy:
            :return:
            """
            msg = Message(MsgType.MOUSE_SCROLL, {'dx': dx, 'dy': dy})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())

        self._mouse.mouse_listener_linux(on_click, on_move_linux, on_scroll, suppress=True)


    def add_keyboard_listener(self):
        """
        添加键盘监听
        :return:
        """
        def on_press(key):
            """
            按下
            :param key:
            :return:
            """
            data = self._keyboard_factory.input(key)
            msg = Message(MsgType.KEYBOARD_CLICK, {'type': "press", "keyData": (data[0], data[1])})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())

        def on_release(key):
            """
            释放
            :param key:
            :return:
            """
            data = self._keyboard_factory.input(key)
            msg = Message(MsgType.KEYBOARD_CLICK, {'type': "release", "keyData": (data[0], data[1])})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())
        if is_wayland():
            # wayland下需要特殊处理
            self._keyboard.keyboard_listener(on_press, on_release,True)
            return None
        else:
            # x11下
            keyboard_listener = self._keyboard.keyboard_listener(on_press, on_release)
            keyboard_listener.start()
            return keyboard_listener

    def judge_move_out(self, x, y):
        """
        判断是否移出
        :param x: x坐标
        :param y: y坐标
        :return:
        """
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
        """
        更新位置
        :return:
        """
        while True:
            self.update_flag.wait() # 等待更新
            device_storage = DeviceStorage()
            devices = device_storage.get_all_devices()
            for device in devices:
                self.udp.sendto(Message(MsgType.POSITION_CHANGE, {'position': device.position}).to_bytes(),
                                device.get_udp_address()) # 发送更新消息
            device_storage.close() # 关闭
            self.update_flag.clear() # 清除
            time.sleep(1)

    def main_loop(self):
        """
        主循环
        :return:
        """
        if platform.system().lower() == "linux" and is_wayland(): # wayland下
            while True:
                self._mouse.update_position_by_listeners() # 更新位置
                try:
                    while True:
                        if self._mouse.position is None:
                            continue
                        x,y = self._mouse.position
                        move_out = self.judge_move_out(x, y)
                        if move_out and self.cur_device is None: # 移出且当前设备为空
                            self._mouse.focus = False
                            self.lock.acquire()
                            device_storage_connect = DeviceStorage()
                            self.cur_device = device_storage_connect.get_device_by_position(move_out)
                            if self.cur_device is None:
                                self.lock.release()
                                continue
                            device_storage_connect.close()
                            time.sleep(0.01)
                            if self.cur_device is not None: # 当前设备不为空
                                # 发送鼠标移动消息
                                if move_out == Position.LEFT:
                                    self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, {
                                        'x': self.cur_device.screen.screen_width - 30,
                                        'y': y}).to_bytes(),
                                                    self.cur_device.get_udp_address())
                                elif move_out == Position.RIGHT:
                                    self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, {'x': 30, 'y': y}).to_bytes(),
                                                    self.cur_device.get_udp_address())
                                elif move_out == Position.TOP:
                                    self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO,
                                                            {'x': x,
                                                            'y': self.cur_device.screen.screen_height - 30}).to_bytes(),
                                                    self.cur_device.get_udp_address())
                                elif move_out == Position.BOTTOM:
                                    self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO,
                                                            {'x': x, 'y': 30}).to_bytes(),
                                                    self.cur_device.get_udp_address())
                                self._mouse.wait_for_event_puter_stop()
                                self._mouse.move_to((int(self.screen_size_width / 2), int(self.screen_size_height / 2)))
                                self.lock.release()
                                break
                        time.sleep(0.1)
                finally:
                    self._mouse.wait_for_event_puter_stop() # 停止监听

                if not self._mouse.focus:
                    self.add_keyboard_listener() # 添加键盘监听
                    self.add_mouse_listener_linux() # 添加鼠标监听
                    self._keyboard.stop_listener() # 停止键盘监听
                    self._mouse.focus = True # 重新聚焦
        else:
            import pynput
            while True:
                with pynput.mouse.Events() as events:
                    for event in events:
                        if isinstance(event, pynput.mouse.Events.Move):
                            x, y = event.x, event.y
                            move_out = self.judge_move_out(x, y)
                            if move_out and self.cur_device is None:
                                self._mouse.focus = False
                                self.lock.acquire()
                                device_storage_connect = DeviceStorage()
                                self.cur_device = device_storage_connect.get_device_by_position(move_out)
                                if self.cur_device is None:
                                    self.lock.release()
                                    continue
                                device_storage_connect.close()
                                time.sleep(0.01)  # 不加识别不到？
                                if self.cur_device is not None:
                                    if move_out == Position.LEFT:
                                        self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, {
                                            'x': self.cur_device.screen.screen_width - 30,
                                            'y': y}).to_bytes(),
                                                        self.cur_device.get_udp_address())
                                    elif move_out == Position.RIGHT:
                                        self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO, {'x': 30, 'y': y}).to_bytes(),
                                                        self.cur_device.get_udp_address())
                                    elif move_out == Position.TOP:
                                        self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO,
                                                                {'x': x,
                                                                 'y': self.cur_device.screen.screen_height - 30}).to_bytes(),
                                                        self.cur_device.get_udp_address())
                                    elif move_out == Position.BOTTOM:
                                        self.udp.sendto(Message(MsgType.MOUSE_MOVE_TO,
                                                                {'x': x, 'y': 30}).to_bytes(),
                                                        self.cur_device.get_udp_address())
                                    self._mouse.move_to((int(self.screen_size_width / 2), int(self.screen_size_height / 2)))
                                    self.lock.release()
                                    break

                if not self._mouse.focus:
                    if platform.system().lower() == "linux":
                        keyboard_listener = self.add_keyboard_listener()
                        self.add_mouse_listener_linux()
                        keyboard_listener.stop()
                        self._mouse.focus = True
                    else:
                        mouse_listener = self.add_mouse_listener()
                        keyboard_listener = self.add_keyboard_listener()
                        mouse_listener.join()
                        keyboard_listener.stop()  # 鼠标监听结束后关闭键盘监听
                        self._mouse.focus = True

    def close(self):
        """
        关闭,释放资源
        :return:
        """
        self.manager_gui.exit()
        delete_table()
        self.udp.close()
        self.tcp_server.close()
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()
