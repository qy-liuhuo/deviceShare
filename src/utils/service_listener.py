import socket


class ServiceListener:
    def __init__(self, client):
        self.client = client

    def add_service(self, zeroconf, service_type, name):
        info = zeroconf.get_service_info(service_type, name)
        if info:
            address = socket.inet_ntoa(info.addresses[0])
            port = info.port
            properties = info.properties
            print(f"Service {name} added, address: {address}:{port}, properties: {properties}")
            self.client.server_addr = (address, port)

    def update_service(self, zeroconf, service_type, name):
        print(f"Service {name} updated")
        info = zeroconf.get_service_info(service_type, name)
        return

    def remove_service(self, zeroconf, service_type, name):
        print(f"Service {name} removed")