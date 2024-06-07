import pynput

from Message import Message, MsgType
from MouseController import MouseController
from Server import UdpServer

mouse = MouseController()
udp_service = UdpServer(16666)

while True:
    msg = Message(MsgType.MOUSE_MOVE, mouse.get_position())
    udp_service.sendto(msg.to_bytes(), ('127.0.0.1',16667))