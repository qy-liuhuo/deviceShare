import socket
import struct

from src.communication.message import WRONG_MESSAGE

UDP_PORT = 16666
TCP_PORT = 16667


class Udp:
    """
    UDP通信
    """
    packet_size = 1024 # 包大小

    def __init__(self, port=16666):
        """
        初始化
        :param port: 端口
        """
        self.msg_listener = None
        self._udp_port = port
        self._udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp.bind(("0.0.0.0", self._udp_port))

    def allow_broadcast(self):
        """
        允许广播
        :return:
        """
        self._udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def sendto(self, data: bytes, target: tuple):
        """
        发送数据
        :param data: 数据
        :param target: 目标
        :return:
        """
        try:
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
        except Exception as e:
            print(e)
            self.close()

    def recv(self):
        """
        接收数据
        :return:
        """
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
                if expected_packets is None:
                    expected_packets = total_packets
                if len(fragments) > packet_id and fragments[packet_id] is not None:
                    data = WRONG_MESSAGE
                fragments[packet_id] = chunk
                if len(fragments) == expected_packets:
                    data = b''.join(fragments[i] for i in range(expected_packets))
                    break
        except Exception as e:
            print(e)
            self.close()
        finally:
            return data, addr

    def close(self):
        """
        关闭连接
        :return:
        """
        self._udp.close()




class TcpClient:
    """
    TCP客户端
    """
    def __init__(self, target: tuple):
        """
        初始化
        :param target: 目标服务地址
        """
        self._tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp.connect(target)

    def send(self, data: bytes):
        """
        发送数据
        :param data: 数据
        :return:
        """
        try:
            # 先发送数据长度
            data_len = struct.pack('!I', len(data))
            self._tcp.sendall(data_len)
            # 再发送实际数据
            self._tcp.sendall(data)
        except Exception as e:
            print(e)
            self.close()


    def close(self):
        """
        关闭连接
        :return:
        """
        self._tcp.close()

    def recv(self):
        """
        接收数据
        :return:
        """
        try:
            # 先接收数据长度
            raw_data_len = self._tcp.recv(4)
            if not raw_data_len:
                return WRONG_MESSAGE
            data_len = struct.unpack('!I', raw_data_len)[0]
            # 接收实际数据
            received_data = bytearray()
            while len(received_data) < data_len:
                packet = self._tcp.recv(data_len - len(received_data))
                if not packet:
                    break
                received_data.extend(packet)
            return received_data
        except Exception as e:
            print(e)
            self.close()




def read_data_from_tcp_socket(client_socket):
    """
    从TCP套接字中读取数据
    :param client_socket: 客户端套接字
    :return:
    """
    try:
        # 先接收数据长度
        raw_data_len = client_socket.recv(4)
        if not raw_data_len:
            return WRONG_MESSAGE
        data_len = struct.unpack('!I', raw_data_len)[0]
        # 接收实际数据
        received_data = bytearray()
        while len(received_data) < data_len:
            packet = client_socket.recv(data_len - len(received_data))
            if not packet:
                break
            received_data.extend(packet)
        return received_data
    except Exception as e:
        print(e)
        return WRONG_MESSAGE

def send_data_to_tcp_socket(client_socket, data: bytes):
    """
    发送数据到TCP套接字
    :param client_socket: 客户端socket
    :param data: 数据
    :return:
    """
    try:
        # 先发送数据长度
        data_len = struct.pack('!I', len(data))
        client_socket.sendall(data_len)
        # 再发送实际数据
        client_socket.sendall(data)
    except Exception as e:
        print(e)
        client_socket.close()