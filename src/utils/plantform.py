import os


def is_wayland():
    """
    Check if the current display server is Wayland
    :return:
    """
    return os.getenv('WAYLAND_DISPLAY') is not None
