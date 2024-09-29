"""
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: MobiNets
"""
import enum
import json


class MsgType(enum.IntEnum):
    """
    MsgType enum
    """
    CLIENT_HEARTBEAT = enum.auto() # 客户端心跳
    MOUSE_BACK = enum.auto() # 鼠标返回
    MOUSE_MOVE = enum.auto() # 鼠标移动
    MOUSE_MOVE_TO = enum.auto() # 鼠标移动到
    MOUSE_CLICK = enum.auto() # 鼠标点击
    MOUSE_SCROLL = enum.auto() # 鼠标滚动
    KEYBOARD_CLICK = enum.auto() # 键盘点击
    CLIPBOARD_UPDATE = enum.auto() # 剪贴板更新
    POSITION_CHANGE = enum.auto() # 位置改变
    SEND_PUBKEY = enum.auto() # 发送公钥
    TCP_ECHO = enum.auto() # TCP回声
    KEY_CHECK = enum.auto() # 键盘检查
    KEY_CHECK_RESPONSE = enum.auto() # 键盘检查响应
    ACCESS_DENY = enum.auto() # 拒绝访问
    ACCESS_ALLOW = enum.auto() # 允许访问
    CLIENT_OFFLINE = enum.auto() # 客户端离线
    WRONG_MSG = enum.auto() # 错误消息



class Message:
    """
    Message
    """
    SPLITTER = "[@~|"
    def __init__(self, msg_type: MsgType, data=None):
        if data is None:
            data = {}
        self.msg_type = msg_type
        self.data = data

    @staticmethod
    def from_bytes(byteData: bytes):
        """
        从字节数据中解析消息
        :param byteData: 字节数据
        :return: 消息
        """
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
        """
        转换为字节数据
        :return:
        """
        return bytes(f"{int(self.msg_type)}{self.SPLITTER}{json.dumps(self.data)}".encode())

    def __str__(self):
        return f"Message({self.msg_type},{self.data})"

# 错误消息标志
WRONG_MESSAGE = Message(MsgType.WRONG_MSG).to_bytes()