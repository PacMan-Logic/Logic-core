import enum
from dataclasses import dataclass
from numpy import ndarray

# define constants
ROUND_BONUS_GAMMA = 1
EATEN_BY_GHOST = -20
EAT_PACMAN = 30
DESTORY_PACMAN_SHIELD = 5
EAT_ALL_BEANS = 30
PREVENT_PACMAN_EAT_ALL_BEANS = 20

MAX_ROUND = [0, 500, 400, 300]  # 每个棋盘最多轮数38*38 29*29 20*20
HUGE_BONUS_GAMMA = [0, 0.5, 0.7, 0.9]
OPERATION_NUM = 5  # 操作数（上下左右不动）
SPACE_CATEGORY = 8  # Note: 0:wall 1:empty 2:regular bean 3:bonus bean 4:speed bean 5:magnet bean 6:shield bean 7:*2 bean
SKILL_NUM = 4

MAX_LEVEL = 3  # 关卡数

# 交互相关数据
FIRST_MAX_AI_TIME = 10
MAX_AI_TIME = 2
MAX_PLAYER_TIME = 60
MAX_LENGTH = 1024


INITIAL_BOARD_SIZE = [0, 38, 29, 20]

DEFAULT_SKILL_TIME = [10, 10, 10]

PACMAN_HIT_OFFSET = -100
GHOST_HIT_OFFSET = -200


class Space(enum.Enum):
    WALL = 0
    EMPTY = 1
    REGULAR_BEAN = 2
    BONUS_BEAN = 3
    SPEED_BEAN = 4
    MAGNET_BEAN = 5
    SHIELD_BEAN = 6
    DOUBLE_BEAN = 7


class Skill(enum.Enum):
    DOUBLE_SCORE = 0
    SPEED_UP = 1
    MAGNET = 2
    SHIELD = 3


class Event(enum.Enum):
    # 0 and 1 should not occur simutaneously
    EATEN_BY_GHOST = 0  # when eaten by ghost, there are two events to be rendered. first, there should be a animation of pacman being caught by ghost. then, the game should be paused for a while, and display a respawning animaiton after receiving next coord infomation.
    SHEILD_DESTROYED = 1
    # 2 and 3 should not occur simutaneously
    FINISH_LEVEL = 2
    TIMEOUT = 3


class Move(enum.Enum):
    STAY = 0
    UP = 1
    LEFT = 2
    DOWN = 3
    RIGHT = 4


@dataclass
class GameState:
    level: int
    round: int
    board_size: int
    board: ndarray
    pacman_skill_status: list[int]
    pacman_pos: list[int]
    ghosts_pos: list[list[int]]
    pacman_score: int
    ghosts_score: int
