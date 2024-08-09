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