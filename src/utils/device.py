import time
from src.gui.position import Position
from src.gui.screen import Screen
from src.communication.my_socket import UDP_PORT


class Device:

    def __init__(self, ip: str, screen: Screen, position=Position.NONE, device_id=None, pub_key=None, expire_time=10):
        self.device_id = device_id
        self.ip = ip
        self.pub_key = pub_key
        self.screen = screen
        self.position = position
        self.focus = False
        self.last_Heartbeat = time.time()
        self.expire_time = expire_time

    def update_heartbeat(self):
        self.last_Heartbeat = time.time()

    def check_valid(self):
        return time.time() - self.last_Heartbeat < self.expire_time

    def equals(self, device_id: str):
        return self.device_id == device_id

    def get_udp_address(self):
        return (self.ip, UDP_PORT)
