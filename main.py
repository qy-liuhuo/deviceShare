import time

import pynput

from Message import Message, MsgType
from MouseController import MouseController
from Server import UdpServer

mouse = MouseController()
udp_service = UdpServer(16666)

target = ('192.168.3.109',16667)


def on_click(x, y, button, pressed):
    msg = Message(MsgType.MOUSE_CLICK, f"{x},{y},{button},{pressed}")
    udp_service.sendto(msg.to_bytes(), target)

mouse_listener = mouse.mouse_listener(on_click)
mouse_listener.start()

while True:
    time.sleep(0.02)
    msg = Message(MsgType.MOUSE_MOVE, mouse.get_position())
    udp_service.sendto(msg.to_bytes(), target)