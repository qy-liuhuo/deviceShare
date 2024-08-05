import queue
import socket
import struct
import threading

UDP_PORT = 16666
TCP_PORT = 16667


class Udp:
    packet_size = 1024

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
        total_packets = (len(data) + Udp.packet_size - 1) // Udp.packet_size
        packet_id = 0
        while data:
            chunk = data[:Udp.packet_size]
            data = data[Udp.packet_size:]
            header = struct.pack('!IHH', packet_id, total_packets, len(chunk))
            packet = header + chunk
            self._udp.sendto(packet, target)
            packet_id += 1

    def recv(self):
        fragments = {}
        expected_packets = None
        data = None
        addr = None
        try:
            while True:
                packet, addr = self._udp.recvfrom(Udp.packet_size + 8)  # 8 bytes for header
                header = packet[:8]
                packet_id, total_packets, chunk_size = struct.unpack('!IHH', header)
                chunk = packet[8:8 + chunk_size]
                fragments[packet_id] = chunk
                if expected_packets is None:
                    expected_packets = total_packets
                if len(fragments) == expected_packets:
                    data = b''.join(fragments[i] for i in range(expected_packets))
                    break
        except Exception as e:
            print(e)
        finally:
            return data,addr
    def close(self):
        self._udp.close()


class Tcp:
    def __init__(self, port=16667, listen_num=5, queue_size=5):
        self._tcp_port = port
        self._tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
        self._tcp.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 60 * 1000, 30 * 1000))
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

    def recv(self):
        try:
            return self._tcp.recv(1024)
        except Exception as e:
            return None
