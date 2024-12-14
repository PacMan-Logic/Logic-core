from .gamedata import *
from numpy import array

def direction_to_offset(direction: Direction):
    """将运动方向转换为棋盘上的偏移"""
    if direction == Direction.UP:
        return array(Update.UP.value)
    elif direction == Direction.DOWN:
        return array(Update.DOWN.value)
    elif direction == Direction.LEFT:
        return array(Update.LEFT.value)
    elif direction == Direction.RIGHT:
        return array(Update.RIGHT.value)
    else:
        return array(Update.STAY.value)


def in_movable_board(coord, level):
    """在棋盘内部"""
    return (
        0 < coord[0] < INITIAL_BOARD_SIZE[level] - 1
        and 0 < coord[1] < INITIAL_BOARD_SIZE[level] - 1
    )


def manhattan_distance(a, b):
    """曼哈顿距离"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
