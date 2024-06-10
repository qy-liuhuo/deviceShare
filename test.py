import time

from Udp import UdpClient

udp_client = UdpClient()

udp_client.start_broadcast()
udp_client.start_listener()