import enum
import time
import json
import pynput


class MsgType(enum.IntEnum):
    CLIENT_HEARTBEAT = enum.auto()
    MOUSE_BACK = enum.auto()
    MOUSE_MOVE = enum.auto()
    MOUSE_MOVE_TO = enum.auto()
    MOUSE_CLICK = enum.auto()
    MOUSE_SCROLL = enum.auto()
    KEYBOARD_CLICK = enum.auto()
    CLIPBOARD_UPDATE = enum.auto()
    POSITION_CHANGE = enum.auto()
    SEND_PUBKEY = enum.auto()
    TCP_ECHO = enum.auto()
    KEY_CHECK = enum.auto()
    KEY_CHECK_RESPONSE = enum.auto()
    ACCESS_DENY = enum.auto()
    ACCESS_ALLOW = enum.auto()
    CLIENT_OFFLINE = enum.auto()
    WRONG_MSG = enum.auto()



class Message:
    SPLITTER = "[@~|"
    def __init__(self, msg_type: MsgType, data=None):
        if data is None:
            data = {}
        self.msg_type = msg_type
        self.data = data

    @staticmethod
    def from_bytes(byteData: bytes):
        if isinstance(byteData, bytearray):
            byteData = bytes(byteData)
        msg_type, data = byteData.decode().split(Message.SPLITTER)
        return Message(MsgType(int(msg_type)), json.loads(data))
        #
        # if int(msg_type) == MsgType.MOUSE_MOVE:
        #     return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        # elif int(msg_type) == MsgType.MOUSE_MOVE_TO:
        #     return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        # elif int(msg_type) == MsgType.DEVICE_ONLINE:
        #     return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        # elif int(msg_type) == MsgType.MOUSE_CLICK:
        #     data = data.split(',')
        #     data[2] = get_click_button(data[2].split('.')[1])
        #     data[3] = data[3] == 'True'
        #     return Message(MsgType(int(msg_type)), tuple(data))
        # elif int(msg_type) == MsgType.KEYBOARD_CLICK:
        #     return Message(MsgType(int(msg_type)), tuple(data.split(',')))
        # elif int(msg_type) == MsgType.MOUSE_SCROLL:
        #     return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        # elif int(msg_type) == MsgType.SUCCESS_JOIN:
        #     data = tuple(data.split(','))
        #     return Message(MsgType(int(msg_type)), data)
        # elif int(msg_type) == MsgType.POSITION_CHANGE:
        #     data = tuple(data.split(','))
        #     return Message(MsgType(int(msg_type)), data)
        # elif int(msg_type) == MsgType.MOUSE_BACK:
        #     return Message(MsgType(int(msg_type)), tuple(map(int, data.split(','))))
        # elif int(msg_type) == MsgType.CLIPBOARD_UPDATE:
        #     return Message(MsgType(int(msg_type)), data)
        # elif int(msg_type) == MsgType.SEND_PUBKEY:
        #     data = tuple(data.split(','))
        #     return Message(MsgType(int(msg_type)), data)
        # return Message(MsgType(int(msg_type)), data)

    # def __init__(self,byteData:bytes):
    #     self.msg_type,self.data = byteData.split(self.SPLITTER)

    def to_bytes(self):
        return bytes(f"{int(self.msg_type)}{self.SPLITTER}{json.dumps(self.data)}".encode())

    def __str__(self):
        return f"Message({self.msg_type},{self.data})"


WRONG_MESSAGE = Message(MsgType.WRONG_MSG).to_bytes()