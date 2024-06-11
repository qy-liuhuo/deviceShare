import socket
from MouseController import MouseController


class Udp:
    def __init__(self, port=16666):
        self.msg_listener = None
        self._mouse = MouseController()
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(("0.0.0.0", self._port))

    def sendto(self, data: bytes, target: tuple):
        self._socket.sendto(data, target)

    def recv(self):
        return self._socket.recvfrom(1024)

    def close(self):
        self._socket.close()


