import platform
import uuid


def get_device_name():
    """
    获取设备名
    :return:
    """
    return platform.node() + "_" + str(uuid.getnode())
