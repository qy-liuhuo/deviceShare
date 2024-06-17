import enum
import json
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

    def __init__(self, device_ip: str, screen: Screen, position=Position.NONE, expire_time=5):
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
        self.position_list = [None, None, None, None]
        self.cur_device = None
        threading.Thread(target=self.valid_checker).start()

    def refresh(self,ip,screen_width,screen_height,position=Position.NONE):
        for device in self.devices:
            if device.device_ip == ip:
                device.update_heartbeat()
                return device.position
        self.add_device(Device(ip, Screen(screen_width, screen_height), position))
        return self.get_device_by_ip(ip).position

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
        if device.position == Position.NONE:
            for p in range(4):
                if self.position_list[p] is None:
                    self.position_list[p] = device
                    device.position = Position(p+1)
                    break
        self.devices.append(device)
        self.write_file()
    def remove_device(self, device: Device):
        if self.cur_device == device:
            self.cur_device = None
        self.devices.remove(device)
        if device.position is not None:
            self.position_list[device.position.value-1] = None
        self.write_file()
    def write_file(self):
        device_info_dict = {}
        for device in self.devices:
            device_info_dict[device.device_ip] = (device.screen.screen_width, device.screen.screen_height, str(device.position))
        with open("devices.json", "w") as f:
            json.dump(device_info_dict, f)

    def get_device_by_ip(self, ip):
        for device in self.devices:
            if device.device_ip == ip:
                return device
        return None

    def get_device_by_position(self, position):
        # for device in self.devices:
        #     if device.position == position:
        #         return device
        # return None
        if self.position_list[position.value-1] is None:
            return None
        return self.position_list[position.value-1]


    def get_devices(self):
        return self.devices

