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
import socket


class ServiceListener:
    """
    服务监听类
    """
    def __init__(self, client):
        self.client = client

    def add_service(self, zeroconf, service_type, name):
        """
        服务注册
        :param zeroconf: zeroconf对象
        :param service_type: 服务类型
        :param name: 服务名
        :return:
        """
        info = zeroconf.get_service_info(service_type, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            port = info.port
            properties = info.properties
            print(f"Service {name} added, address: {address}:{port}, properties: {properties}")
            self.client.server_ip = address

    def update_service(self, zeroconf, service_type, name):
        """
        服务更新
        :param zeroconf:
        :param service_type:
        :param name:
        :return:
        """
        print(f"Service {name} updated")
        info = zeroconf.get_service_info(service_type, name)
        return

    def remove_service(self, zeroconf, service_type, name):
        """'
        服务移除事件
        """
        print(f"Service {name} removed")