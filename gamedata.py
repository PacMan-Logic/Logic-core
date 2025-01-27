import enum
from dataclasses import dataclass
import numpy as np


class Type(enum.Enum):
    ABNORMAL = 0  # 未正常启动
    AI = 1  # ai
    PLAYER = 2  # 播放器


class Role(enum.Enum):
    PACMAN = 0
    GHOSTS = 1


# 与judger交互相关数据
FIRST_MAX_AI_TIME = 20
MAX_AI_TIME = 1
MAX_PLAYER_TIME = 60
MAX_LENGTH = 1024

# Pacman bonus
PACMAN_HUGE_BONUS_THRESHOLD = 100
PACMAN_HUGE_BONUS = 50
EATEN_BY_GHOST = -60
EAT_ALL_BEANS = 50

HUGE_BONUS_GAMMA = [0, 0.5, 0.7, 0.9]
ROUND_BONUS_GAMMA = 0.43

# Pacman skill
DEFAULT_SKILL_TIME = [10, 10, 10, 10, 10]


class Skill(enum.Enum):
    DOUBLE_SCORE = 0
    SPEED_UP = 1
    MAGNET = 2
    SHIELD = 3
    FROZEN = 4

SKILL_NUM = len(Skill)

# Ghost bonus
# NOTE: GHOST_HUGE_BONUS and PREVENT_PACMAN_EAT_ALL_BEANS will be added for all three ghosts!
GHOST_HUGE_BONUS_THRESHOLD = 5
GHOST_HUGE_BONUS = 20
PREVENT_PACMAN_EAT_ALL_BEANS = 25
EAT_PACMAN = 50
DESTORY_PACMAN_SHIELD = 10

# Portal
PORTAL_AVAILABLE = [0, 60, 50]

# Round & Level
MAX_ROUND = [0, 500, 400, 300]  # 每个棋盘最多轮数38*38 29*29 20*20
MAX_LEVEL = 3  # 关卡数


class Direction(enum.Enum):
    STAY = 0
    UP = 1
    LEFT = 2
    DOWN = 3
    RIGHT = 4

class Update(enum.Enum):
    STAY = (0, 0)
    UP = (1, 0)
    LEFT = (0, -1)
    DOWN = (-1, 0)
    RIGHT = (0, 1)
    
# Operation
OPERATION_NUM = len(Direction)  # 操作数（上下左右不动）

# Board
PASSAGE_WIDTH = 2
INITIAL_BOARD_SIZE = [0, 38 + 2*(PASSAGE_WIDTH - 1) + 1, 29 + 2*(PASSAGE_WIDTH - 1) + 1, 20 + 2*(PASSAGE_WIDTH - 1)]

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
    PORTAL = 8
    FROZEN_BEAN = 9

SPACE_CATEGORY = len(Space)  # Note: 0:wall 1:empty 2:regular bean 3:bonus bean 4:speed bean 5:magnet bean 6:shield bean 7:*2 bean 8:portal 9: frozen bean

BEANS_ITERATOR = [
    Space.REGULAR_BEAN.value,
    Space.BONUS_BEAN.value,
    Space.SPEED_BEAN.value,
    Space.MAGNET_BEAN.value,
    Space.SHIELD_BEAN.value,
    Space.DOUBLE_BEAN.value,
    Space.FROZEN_BEAN.value,
]
SPECIAL_BEANS_ITERATOR = [
    Space.SPEED_BEAN.value,
    Space.MAGNET_BEAN.value,
    Space.SHIELD_BEAN.value,
    Space.DOUBLE_BEAN.value,
    Space.BONUS_BEAN.value,
    Space.FROZEN_BEAN.value,
]
SKILL_BEANS_ITERATOR = [
    Space.SPEED_BEAN.value,
    Space.MAGNET_BEAN.value,
    Space.SHIELD_BEAN.value,
    Space.DOUBLE_BEAN.value,
    Space.FROZEN_BEAN.value,
]

# Event
class Event(enum.Enum):
    # 0 and 1 should not occur simutaneously
    EATEN_BY_GHOST = 0  # when eaten by ghost, there are two events to be rendered. first, there should be a animation of pacman being caught by ghost. then, the game should be paused for a while, and display a respawning animaiton after receiving next coord infomation.
    SHIELD_DESTROYED = 1
    # 2 and 3 should not occur simutaneously
    FINISH_LEVEL = 2
    TIMEOUT = 3


# 选手可获取的接口
@dataclass
class GameState:
    space_info: dict
    level: int
    round: int
    board_size: int
    board: np.ndarray
    pacman_skill_status: list[int]
    pacman_pos: np.ndarray
    ghosts_pos: list[np.ndarray]
    pacman_score: int
    ghosts_score: int
    beannumber: int
    portal_available: bool
    portal_coord: np.ndarray
    def gamestate_to_statedict(self):
        return {
            "level": self.level,
            "round": self.round,
            "board_size": self.board_size,
            "board": self.board,
            "pacman_skill_status": np.array(self.pacman_skill_status),
            "pacman_coord": self.pacman_pos,
            "ghosts_coord": self.ghosts_pos,
            "score": [self.pacman_score, self.ghosts_score],
            "beannumber": self.beannumber,
            "portal_available": self.portal_available,
            "portal_coord": self.portal_coord,
        }
