import socket


class UdpServer:
    def __init__(self, port=19999):
        self.__port = port
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__server.bind(("0.0.0.0", self.__port))

    def sendto(self, data: bytes, target: tuple):
        self.__server.sendto(data, target)

    def recv(self):
        return self.__server.recvfrom(1024)

    def close(self):
        self.__server.close()
