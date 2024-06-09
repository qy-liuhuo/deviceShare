import time

import pynput

from Message import Message, MsgType
from MouseController import MouseController
from Server import UdpServer

mouse = MouseController()
udp_service = UdpServer(16666)

target = ('127.0.0.1',16667)


def on_click(x, y, button, pressed):
    msg = Message(MsgType.MOUSE_CLICK, f"{x},{y},{button},{pressed}")
    udp_service.sendto(msg.to_bytes(), target)


mouse_listener = mouse.mouse_listener(on_click)
mouse_listener.start()

while True:
    msg = Message(MsgType.MOUSE_MOVE, mouse.get_position())
    udp_service.sendto(msg.to_bytes(), target)