import json
import threading
import time

from src.device.device import Device
from src.screen_manager.position import Position
from src.screen_manager.screen import Screen


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
