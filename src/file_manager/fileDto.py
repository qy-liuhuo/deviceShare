
import socket
from datetime import datetime


def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


class fileDto:
    def __init__(self, file_path):
        self.file_path = file_path
        self.ip_addr = get_host_ip()
        self.update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')