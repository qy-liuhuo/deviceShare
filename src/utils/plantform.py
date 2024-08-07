import os


def is_wayland():
    return os.getenv('WAYLAND_DISPLAY') is not None