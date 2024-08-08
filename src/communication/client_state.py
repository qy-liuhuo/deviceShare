import enum


class ClientState(enum.IntEnum):
    WAITING_FOR_KEY = enum.auto()
    WAITING_FOR_CHECK = enum.auto()
    CONNECT = enum.auto()