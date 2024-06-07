import enum


class MsgType(enum.IntEnum):
    MOUSE_MOVE = 1
    MOUSE_CLICK = 2
    MOUSE_SCROLL = 3


class Message:

    SPLITTER = "sPlItTeR"

    def __init__(self, msg_type:MsgType, data):
        self.msg_type = msg_type
        self.data = data

    @staticmethod
    def from_bytes(byteData:bytes):
        msg_type,data = byteData.decode().split(Message.SPLITTER)
        if int(msg_type) == MsgType.MOUSE_MOVE:
            return Message(MsgType(int(msg_type)),tuple(map(int,data.split(','))))
        return Message(MsgType(int(msg_type)),data)

    # def __init__(self,byteData:bytes):
    #     self.msg_type,self.data = byteData.split(self.SPLITTER)

    def to_bytes(self):
        return bytes(f"{int(self.msg_type)}{self.SPLITTER}{self.data}".encode())
    def __str__(self):
        return f"Message({self.msg_type},{self.data})"