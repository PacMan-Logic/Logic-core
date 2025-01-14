from .gamedata import *
from .utils import *


class Pacman:
    def __init__(self):
        self._score = 0
        self._skill_status = [0, 0, 0, 0]
        self._coord = np.array([-1, -1])
        self._level = 1
        self._board_size = 20
        self._portal_coord = np.array([-1, -1])

    def update_score(self, points):
        reward = 2 * points if self._skill_status[Skill.DOUBLE_SCORE.value] > 0 else points
        self._score += reward
        return reward

    def just_eat(self, board, x, y):
        reward = 0
        if not in_movable_board([x, y], self._level):
            return 0

        if board[x][y] == Space.REGULAR_BEAN.value:
            board[x][y] = Space.EMPTY.value
            reward += self.update_score(1)

        elif board[x][y] == Space.BONUS_BEAN.value:
            board[x][y] = Space.EMPTY.value
            reward += self.update_score(2)

        elif board[x][y] == Space.SPEED_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.acquire_skill(Skill.SPEED_UP)

        elif board[x][y] == Space.MAGNET_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.acquire_skill(Skill.MAGNET)

        elif board[x][y] == Space.SHIELD_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.acquire_skill(Skill.SHIELD)

        elif board[x][y] == Space.DOUBLE_BEAN.value:
            board[x][y] = Space.EMPTY.value
            self.acquire_skill(Skill.DOUBLE_SCORE)

        return reward

    def eat_bean(self, board):
        reward = 0
        x, y = self._coord
        if self._skill_status[Skill.MAGNET.value] == 0:
            reward += self.just_eat(board, x, y)

        else:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    reward += self.just_eat(board, x + i, y + j)

        return reward

    def get_skills_status(self):
        return self._skill_status.copy()

    def acquire_skill(self, skill_index: Skill):
        if skill_index == Skill.SHIELD:
            self._skill_status[Skill.SHIELD.value] += 1
        else:
            self._skill_status[skill_index.value] = DEFAULT_SKILL_TIME[
                skill_index.value
            ]

    def set_level(self, level):
        self._level = level

    def set_size(self, size):
        self._board_size = size

    def get_coord(self):
        return self._coord.copy()

    def set_coord(self, coord):
        self._coord = coord

    def set_portal_coord(self, portal_coord):
        self._portal_coord = portal_coord

    def get_portal_coord(self):
        return self._portal_coord.copy()

    def diminish_skill_time(
        self,
    ):  # Note: reset the skill status when a new round starts
        if self._skill_status[Skill.DOUBLE_SCORE.value] > 0:
            self._skill_status[Skill.DOUBLE_SCORE.value] -= 1
        if self._skill_status[Skill.MAGNET.value] > 0:
            self._skill_status[Skill.MAGNET.value] -= 1
        if self._skill_status[Skill.SPEED_UP.value] > 0:
            self._skill_status[Skill.SPEED_UP.value] -= 1

    def get_score(self):
        return self._score

    def break_sheild(self):
        if self._skill_status[Skill.SHIELD.value] > 0:
            self._skill_status[Skill.SHIELD.value] -= 1
            return False
        else:
            return True

    def try_move(self, board, direction: Direction):
        offset = direction_to_offset(direction)
        new_coord = self._coord + offset
        if board[new_coord[0], new_coord[1]] == Space.WALL.value:
            return False
        self._coord = new_coord
        return True

    def clear_skills(self):
        self._skill_status = [0, 0, 0, 0]
