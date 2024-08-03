import socket
import sys
import threading
import time
import uuid
from queue import Queue

from screeninfo import get_monitors
import pynput
from zeroconf import ServiceInfo, Zeroconf
from src.controller.keyboard_controller import KeyboardController, KeyFactory
from src.device.device import Device
from src.screen_manager.gui import Gui, GuiMessage
from src.screen_manager.position import Position
from src.my_socket.message import Message, MsgType
from src.controller.mouse_controller import MouseController
from src.my_socket.my_socket import Udp, Tcp, UDP_PORT, TCP_PORT
import pyperclip

from src.screen_manager.screen import Screen
from src.sharer.client_state import ClientState
from src.utils.device_storage import DeviceStorage, create_table, delete_table
from src.utils.key_storage import KeyStorage
from src.utils.net import get_local_ip
from src.utils.rsautil import encrypt


class Server:
    def __init__(self):
        create_table()
        self.init_screen_info()
        self.server_queue = Queue()
        self.request_queue = Queue()
        self.response_queue = Queue()
        self.thread_list = []
        self.update_flag = threading.Event()
        self.manager_gui = Gui(update_flag = self.update_flag, request_queue=self.request_queue,
                               response_queue=self.response_queue)
        self.cur_device = None
        self._mouse = MouseController()
        self._keyboard = KeyboardController()
        self._keyboard_factory = KeyFactory()
        self.lock = threading.Lock()
        self.udp = Udp(UDP_PORT)
        self.udp.allow_broadcast()
        # self.tcp = Tcp(TCP_PORT)
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind(("0.0.0.0", TCP_PORT))
        self.tcp_server.listen(10)
        self.thread_list.append(threading.Thread(target=self.tcp_listener))
        self.thread_list.append(threading.Thread(target=self.msg_receiver))
        self.last_clipboard_text = ''
        self.service_register()
        self.thread_list.append(threading.Thread(target=self.clipboard_listener))
        self.thread_list.append(threading.Thread(target=self.valid_checker))
        self.thread_list.append(threading.Thread(target=self.main_loop))
        self.thread_list.append(threading.Thread(target=self.update_position))
        self.start_all_threads()
        self.manager_gui.run()
        delete_table()

    def valid_checker(self):
        device_storage = DeviceStorage()
        try:
            while True:
                devices = device_storage.get_all_devices()
                for device in devices:
                    if not device.check_valid():
                        device_storage.delete_device(device.device_id)
                        self.manager_gui.device_offline_notify(device.device_id)
                        if self.cur_device == device:
                            self.cur_device = None
                        self.manager_gui.update_devices()
                time.sleep(5)
        except InterruptedError:
            device_storage.close()

    def start_all_threads(self):
        for thread in self.thread_list:
            thread.setDaemon(True)
            thread.start()

    def init_screen_info(self):
        monitors = get_monitors()
        self.screen_size_width = monitors[0].width
        self.screen_size_height = monitors[0].height

    def service_register(self):
        info = ServiceInfo(type_="_deviceShare._tcp.local.", name="_deviceShare._tcp.local.",
                           addresses=[socket.inet_aton(get_local_ip())], port=UDP_PORT, weight=0, priority=0,
                           properties={"tcp_port": str(TCP_PORT), "udp_port": str(UDP_PORT)})
        self.zeroconf = Zeroconf()
        self.zeroconf.register_service(info)

    def msg_receiver(self):
        device_storage = DeviceStorage()
        try:
            while True:
                recv_data = self.udp.recv()
                if recv_data is None:
                    continue
                data, addr = recv_data
                msg = Message.from_bytes(data)
                if msg.msg_type == MsgType.CLIENT_HEARTBEAT:
                    device_storage.update_heartbeat(ip=addr[0])
                elif msg.msg_type == MsgType.CLIPBOARD_UPDATE:
                    self.last_clipboard_text = msg.data['text']
                    pyperclip.copy(msg.data['text'])
        except InterruptedError:
            device_storage.close()

    def tcp_listener(self):
        while True:
            client, addr = self.tcp_server.accept()
            print(f"Connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client, addr), daemon=True)
            client_handler.start()

    def handle_client(self, client_socket, addr):

        keys_manager = KeyStorage()
        state = ClientState.WAITING_FOR_KEY
        random_key = None
        new_device = Device(ip=addr[0], screen = None, position=Position.NONE)
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                msg = Message.from_bytes(data)
                if msg.msg_type == MsgType.MOUSE_BACK:
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
                    client_socket.send(Message(MsgType.TCP_ECHO).to_bytes())
                elif msg.msg_type == MsgType.SEND_PUBKEY and state == ClientState.WAITING_FOR_KEY:
                    client_id = msg.data['device_id']
                    public_key = msg.data['public_key']
                    new_device.pub_key = public_key
                    new_device.device_id = client_id
                    temp = keys_manager.get_key(client_id)
                    if temp is None or temp != public_key:
                        self.manager_gui.device_show_online_require(addr[0])
                        self.manager_gui.request_queue.put(
                            GuiMessage(GuiMessage.MessageType.ACCESS_REQUIRE, {"device_id": client_id}))
                        result = self.response_queue.get()
                        if result.data['result']:
                            keys_manager.set_key(client_id, public_key)
                            pass
                        else:
                            client_socket.send(Message(MsgType.ACCESS_DENY, {'result': 'access_deny'}).to_bytes())
                            continue
                    random_key = uuid.uuid1().bytes
                    client_socket.send(
                        Message(MsgType.KEY_CHECK, {'key': encrypt(public_key, random_key).hex()}).to_bytes())
                    state = ClientState.WAITING_FOR_CHECK
                elif msg.msg_type == MsgType.KEY_CHECK_RESPONSE and state == ClientState.WAITING_FOR_CHECK:
                    if msg.data['key'] == random_key.hex():
                        new_device.screen = Screen(screen_width=msg.data['screen_width'], screen_height=msg.data['screen_height'])
                        device_storage = DeviceStorage()
                        device_storage.add_device(new_device)  # 同时会更新device的position
                        device_storage.close()
                        client_socket.send(Message(MsgType.ACCESS_ALLOW, {'position': int(new_device.position)}).to_bytes())
                        self.manager_gui.device_online_notify(new_device.device_id)
                        self.manager_gui.update_devices()
                        state = ClientState.CONNECT
                    else:
                        client_socket.send(Message(MsgType.ACCESS_DENY, {'result': 'access_deny'}).to_bytes())
                        state = ClientState.WAITING_FOR_KEY
            except ConnectionResetError:
                print(f"Connection from {addr} closed")
                break
        client_socket.close()

    def clipboard_listener(self):
        while True:
            new_clip_text = pyperclip.paste()
            if new_clip_text != '' and new_clip_text != self.last_clipboard_text:
                self.last_clipboard_text = new_clip_text
                self.broadcast_clipboard(new_clip_text)
            time.sleep(1)

    def broadcast_clipboard(self, text):
        msg = Message(MsgType.CLIPBOARD_UPDATE, {'text': text})
        self.udp.sendto(msg.to_bytes(), ('<broadcast>', UDP_PORT))

    def add_mouse_listener(self):
        def on_click(x, y, button, pressed):
            msg = Message(MsgType.MOUSE_CLICK, {'x': x, 'y': y, 'button': str(button), 'pressed': pressed})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())

        def on_move(x, y):
            last_pos = self._mouse.get_last_position()
            msg = Message(MsgType.MOUSE_MOVE, {'x': x - last_pos[0], 'y': y - last_pos[1]})
            if self.cur_device is None:
                return False
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())
            # if self._mouse.get_position()[0] >= self.screen_size.width - 10: # 向右移出
            #     self.udp.sendto(msg.to_bytes(), self.device_manager.cur_device.get_udp_address())
            if not self._mouse.focus and self._mouse.get_position()[0] <= 200 or self._mouse.get_position()[1] <= 200 or \
                    self._mouse.get_position()[0] >= self.screen_size_width - 200 or self._mouse.get_position()[
                1] >= self.screen_size_height - 200:
                self._mouse.move_to((int(self.screen_size_width / 2), int(self.screen_size_height / 2)))
            self._mouse.update_last_position()

        def on_scroll(x, y, dx, dy):
            msg = Message(MsgType.MOUSE_SCROLL, {'dx': dx, 'dy': dy})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())

        mouse_listener = self._mouse.mouse_listener(on_click, on_move, on_scroll, suppress=True)
        mouse_listener.start()
        return mouse_listener

    def add_keyboard_listener(self):
        def on_press(key):
            data = self._keyboard_factory.input(key)
            msg = Message(MsgType.KEYBOARD_CLICK, {'type': "press", "keyData": (data[0], data[1])})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())

        def on_release(key):
            data = self._keyboard_factory.input(key)
            msg = Message(MsgType.KEYBOARD_CLICK, {'type': "release", "keyData": (data[0], data[1])})
            if self.cur_device:
                self.udp.sendto(msg.to_bytes(), self.cur_device.get_udp_address())

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

    # 待重写
    def update_position(self):
        while True:
            self.update_flag.wait()
            device_storage = DeviceStorage()
            devices = device_storage.get_all_devices()
            for device in devices:
                self.udp.sendto(Message(MsgType.POSITION_CHANGE, {'position': device.position}).to_bytes(),
                                device.get_udp_address())
            device_storage.close()
            self.update_flag.clear()
            time.sleep(1)

    def main_loop(self):
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
                mouse_listener = self.add_mouse_listener()
                keyboard_listener = self.add_keyboard_listener()
                mouse_listener.join()
                keyboard_listener.stop()  # 鼠标监听结束后关闭键盘监听
                self._mouse.focus = True

    def close(self):
        self.udp.close()
        # self.tcp.close()
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()
