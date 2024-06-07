import pynput

from Server import UdpServer

mouse = pynput.mouse.Controller()
udp_service = UdpServer(16666)

while True:
    udp_service.sendto(str(mouse.position).encode(), ('127.0.0.1',16667))