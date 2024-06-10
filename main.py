import platform
import time

import pynput

from Message import Message, MsgType
from MouseController import MouseController
from Udp import UdpServer

# 解决windows下缩放偏移问题
if platform.system().lower() == 'windows':
    import ctypes

    awareness = ctypes.c_int()
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

mouse = MouseController()
udp_service = UdpServer(16666)

target = ('192.168.3.88', 16667)


def on_click(x, y, button, pressed):
    msg = Message(MsgType.MOUSE_CLICK, f"{x},{y},{button},{pressed}")
    udp_service.sendto(msg.to_bytes(), target)


def on_move(x, y):
    msg = Message(MsgType.MOUSE_MOVE, f"{x},{y}")
    udp_service.sendto(msg.to_bytes(), target)


mouse_listener = mouse.mouse_listener(on_click)
mouse_listener.start()
