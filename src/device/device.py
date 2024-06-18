import time
from src.screen_manager.position import Position
from src.screen_manager.screen import Screen
from src.my_socket.my_socket import UDP_PORT


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
