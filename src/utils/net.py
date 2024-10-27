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
import netifaces

def get_local_ip():
    """
    获取本地ip
    :return: ip
    """
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for addr in addresses[netifaces.AF_INET]:
                ip = addr['addr']
                if ip != "127.0.0.1":
                    return ip
    return "127.0.0.1"
