import time

import pynput

from Message import Message, MsgType
from MouseController import MouseController
from Server import UdpServer

mouse = MouseController()
udp_service = UdpServer(16667)
while True:
    data,addr = udp_service.recv()
    msg = Message.from_bytes(data)
    if msg.msg_type == MsgType.MOUSE_MOVE:
        mouse.move(msg.data)
    elif msg.msg_type == MsgType.MOUSE_CLICK:
        print(msg.data[2],msg.data[3])
        mouse.click(msg.data[2],msg.data[3])