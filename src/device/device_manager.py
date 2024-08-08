import json
import threading
import time

from src.device.device import Device
from src.gui.position import Position
from src.gui.screen import Screen


class DeviceManager:
    def __init__(self,devices, device_offline_callback=None):
        self.devices = []
        self.position_list = [None, None, None, None]
        self.cur_device = None
        self.device_offline_callback = device_offline_callback
        threading.Thread(target=self.valid_checker, daemon=True).start()


    def add_or_update(self, ip, screen_width, screen_height, position=Position.NONE):
        for device in self.devices:
            if device.ip == ip:
                device.update_heartbeat()
                return device.position
        self.add_device(Device(ip, Screen(screen_width, screen_height), position))
        return self.get_device_by_ip(ip).position

    def update_heartbeat(self, ip):
        for device in self.devices:
            if device.ip == ip:
                device.update_heartbeat()
                break

    def valid_checker(self):
        while True:
            for device in self.devices:
                if not device.check_valid():
                    self.remove_device(device)
            time.sleep(5)

    def change_position(self, device_id, position):
        for device in self.devices:
            if device.device_id == device_id:
                device.position = position

    def add_device(self, device: Device):
        if device.position == Position.NONE:
            for p in range(4):
                if self.position_list[p] is None:
                    self.position_list[p] = device
                    device.position = Position(p + 1)
                    break
        self.devices.append(device)
        self.position_list[device.position.value - 1] = device

    def remove_device(self, device: Device):
        if self.cur_device == device:
            self.cur_device = None
        self.devices.remove(device)
        self.device_offline_callback(device.ip)
        if device.position is not None:
            self.position_list[device.position.value - 1] = None
        #self.write_file()

    def write_file(self):
        device_info_dict = {}
        for device in self.devices:
            device_info_dict[device.ip] = (
            device.screen.screen_width, device.screen.screen_height, int(device.position))
        with open("devices.json", "w") as f:
            json.dump(device_info_dict, f)

    def get_device_by_ip(self, ip):
        for device in self.devices:
            if device.ip == ip:
                return device
        return None

    def get_device_by_position(self, position):
        # for device in self.devices:
        #     if device.position == position:
        #         return device
        # return None
        if self.position_list[position.value - 1] is None:
            return None
        return self.position_list[position.value - 1]

    def update_device_by_file(self):
        self.devices = []
        self.cur_device = None
        with open("devices.json", "r") as f:
            device_info_dict = json.load(f)
        for ip, info in device_info_dict.items():
            if self.get_device_by_ip(ip) is None:
                self.add_device(Device(ip, Screen(info[0], info[1]), Position(info[2])))

    def get_devices(self):
        return self.devices
