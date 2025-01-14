from .gamedata import *
from .utils import *


class Ghost:
    def __init__(self):
        self._score = 0
        self._coord = np.array([-1, -1])

    def get_coord(self):
        return self._coord.copy()

    def set_coord(self, coord):
        self._coord = coord

    def update_score(self, points):
        self._score += points
        return points

    def get_score(self):
        return self._score.copy()

    def try_move(self, board, direction):
        offset = direction_to_offset(direction)
        new_coord = self._coord + offset
        if board[new_coord[0], new_coord[1]] == Space.WALL.value:
            return False
        self._coord = new_coord
        return True
