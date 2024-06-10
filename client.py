import time
import platform

import pynput

from Message import Message, MsgType
from MouseController import MouseController
from Udp import UdpServer

import socket



# 解决windows下缩放偏移问题
if platform.system().lower() == 'windows':
    import ctypes
    awareness = ctypes.c_int()
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

mouse = MouseController()
udp_service = UdpServer(16667)
while True:
    data,addr = udp_service.recv()
    msg = Message.from_bytes(data)
    if msg.msg_type == MsgType.MOUSE_MOVE:
        mouse.move_to(msg.data)
    elif msg.msg_type == MsgType.MOUSE_CLICK:
        mouse.click(msg.data[2],msg.data[3])