import enum

import pynput


class MsgType(enum.IntEnum):
    DEVICE_ONLINE = enum.auto()
    SUCCESS_JOIN = enum.auto()
    MOUSE_BACK = enum.auto()
    MOUSE_MOVE = enum.auto()
    MOUSE_MOVE_TO = enum.auto()
    MOUSE_CLICK = enum.auto()
    MOUSE_SCROLL = enum.auto()
    KEYBOARD_CLICK = enum.auto()
    CLIPBOARD_UPDATE = enum.auto()


def get_click_button(btn: str):
    if btn == 'left':
        return pynput.mouse.Button.left
    elif btn == 'right':
        return pynput.mouse.Button.right
    elif btn == 'middle':
        return pynput.mouse.Button.middle
    return pynput.mouse.Button.unknown


class Message:
    SPLITTER = "@"

    def __init__(self, msg_type: MsgType, data):
        self.msg_type = msg_type
        self.data = data

    @staticmethod
    def from_bytes(byteData: bytes):
        msg_type, data = byteData.decode().split(Message.SPLITTER)
        if int(msg_type) == MsgType.MOUSE_MOVE:
            return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        elif int(msg_type) == MsgType.MOUSE_MOVE_TO:
            return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        elif int(msg_type) == MsgType.DEVICE_ONLINE:
            return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        elif int(msg_type) == MsgType.MOUSE_CLICK:
            data = data.split(',')
            data[2] = get_click_button(data[2].split('.')[1])
            data[3] = data[3] == 'True'
            return Message(MsgType(int(msg_type)), tuple(data))
        elif int(msg_type) == MsgType.KEYBOARD_CLICK:
            return Message(MsgType(int(msg_type)), tuple(data.split(',')))
        elif int(msg_type) == MsgType.MOUSE_SCROLL:
            return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        elif int(msg_type) == MsgType.SUCCESS_JOIN:
            data = tuple(data.split(','))
            return Message(MsgType(int(msg_type)), data)
        elif int(msg_type) == MsgType.MOUSE_BACK:
            return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        elif int(msg_type) == MsgType.CLIPBOARD_UPDATE:
            return Message(MsgType(int(msg_type)), data)
        return Message(MsgType(int(msg_type)), data)

    # def __init__(self,byteData:bytes):
    #     self.msg_type,self.data = byteData.split(self.SPLITTER)

    def to_bytes(self):
        return bytes(f"{int(self.msg_type)}{self.SPLITTER}{self.data}".encode())

    def __str__(self):
        return f"Message({self.msg_type},{self.data})"
