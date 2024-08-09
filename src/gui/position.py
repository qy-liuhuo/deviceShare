import enum


class Position(enum.IntEnum):
    """
    Position enum
    """
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()
    NONE = enum.auto()