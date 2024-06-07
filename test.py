import pynput

from Server import UdpServer

mouse = pynput.mouse.Controller()
udp_service = UdpServer(16667)

while True:
    data = udp_service.recv()
    print(data)