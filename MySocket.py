import queue
import socket
import threading

from MouseController import MouseController

UDP_PORT = 16666
TCP_PORT = 16667

class Udp:
    def __init__(self, port=16666):
        self.msg_listener = None
        self._udp_port = port
        self._udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp.bind(("0.0.0.0", self._udp_port))

    def allow_broadcast(self):
        self._udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def sendto(self, data: bytes, target: tuple):
        if target is None:
            return
        self._udp.sendto(data, target)

    def recv(self):
        return self._udp.recvfrom(1024)

    def close(self):
        self._udp.close()


class Tcp:
    def __init__(self, port=16667, listen_num=5, queue_size=5):
        self._tcp_port = port
        self._tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp.bind(("0.0.0.0", self._tcp_port))
        self._tcp.listen(listen_num)
        self._tcp_alive = True
        self.event_queue = queue.Queue(queue_size)
        threading.Thread(target=self.receive_loop).start()

    def receive_loop(self):
        while self._tcp_alive:
            conn, addr = self._tcp.accept()
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                self.event_queue.put((data, addr))
                conn.send(b'OK')
        self._tcp.close()

    def close(self):
        self._tcp.close()
        self._tcp_alive = False


class TcpClient:
    def __init__(self, target: tuple):
        self._tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp.connect(target)

    def send(self, data: bytes):
        self._tcp.send(data)

    def close(self):
        self._tcp.close()
