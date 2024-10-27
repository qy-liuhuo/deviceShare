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
import time
from src.gui.position import Position
from src.gui.screen import Screen
from src.communication.my_socket import UDP_PORT


class Device:
    """
    Device class to store device information
    """
    def __init__(self, ip: str, screen: Screen, position=Position.NONE, device_id=None, pub_key=None, expire_time=10):
        """
        初始化
        :param ip: ip
        :param screen: 屏幕信息
        :param position: 相对位置
        :param device_id: 设备id
        :param pub_key:  公钥
        :param expire_time: 过期时间
        """
        self.device_id = device_id
        self.ip = ip
        self.pub_key = pub_key
        self.screen = screen
        self.position = position
        self.focus = False
        self.last_Heartbeat = time.time()
        self.expire_time = expire_time

    def update_heartbeat(self):
        """
        更新心跳时间
        :return:
        """
        self.last_Heartbeat = time.time()

    def check_valid(self):
        """
        检查是否有效
        :return:
        """
        return time.time() - self.last_Heartbeat < self.expire_time

    def equals(self, device_id: str):
        """
        判断是否相等
        :param device_id: 设备id
        :return:
        """
        return self.device_id == device_id

    def get_udp_address(self):
        """
        获取udp地址
        :return:
        """
        return (self.ip, UDP_PORT)
