import enum


class Position(enum.IntEnum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()
    NONE = enum.auto()