import enum
import threading
import time

from MySocket import UDP_PORT


class Screen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height


class Position(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()
    NONE = enum.auto()


class Device:

    def __init__(self, device_ip: str, screen: Screen, position: Position, expire_time=5):
        self.device_ip = device_ip
        self.screen = screen
        self.position = position
        self.focus = False
        self.last_Heartbeat = time.time()
        self.expire_time = expire_time


    def update_heartbeat(self):
        self.last_Heartbeat = time.time()

    def check_valid(self):
        return time.time() - self.last_Heartbeat < self.expire_time

    def equals(self, ip: str):
        return self.device_ip == ip

    def get_udp_address(self):
        return (self.device_ip, UDP_PORT)


class DeviceManager:
    def __init__(self):
        self.devices = []
        self.cur_device = None
        threading.Thread(target=self.valid_checker).start()

    def refresh(self,ip,screen_width,screen_height,position=Position.NONE):
        for device in self.devices:
            if device.device_ip == ip:
                device.update_heartbeat()
                return
        self.add_device(Device(ip, Screen(screen_width, screen_height), position))
        print(f"client {ip} connected")

    def valid_checker(self):
        while True:
            for device in self.devices:
                if not device.check_valid():
                    self.remove_device(device)
            time.sleep(5)

    def change_position(self, ip, position):
        for device in self.devices:
            if device.device_ip == ip:
                device.position = position

    def add_device(self, device: Device):
        self.devices.append(device)

    def remove_device(self, device: Device):
        if self.cur_device == device:
            self.cur_device = None
        self.devices.remove(device)

    def get_device_by_ip(self, ip):
        for device in self.devices:
            if device.device_ip == ip:
                return device
        return None

    def get_device_by_position(self, position):
        for device in self.devices:
            if device.position == position:
                return device
        return None

    def get_devices(self):
        return self.devices
