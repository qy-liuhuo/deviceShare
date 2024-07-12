import platform
import uuid


def get_device_name():
    return platform.node() + "_" + str(uuid.getnode())
