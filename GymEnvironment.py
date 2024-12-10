import json
import time
from typing import List
import random
import gym
import numpy as np
from gym import spaces
from .board import *
from .pacman import Pacman
from .ghost import Ghost
from .gamedata import *


import os


class PacmanEnv(gym.Env):
    metadata = {"render_modes": ["local", "logic", "ai"]}

    def __init__(
        self,
        render_mode=None,
        size=INITIAL_BOARD_SIZE[1],
    ):
        assert size >= 3
        self._size = size
        self._player = 0

        # Note: use round instead of time to terminate the game
        self._round = 0
        self._pacman = Pacman()
        self._ghosts = [Ghost(), Ghost(), Ghost()]
        self._event_list = []
        self._last_skill_status = [0] * SKILL_NUM
        self._level = 0  # Note: this will plus 1 in the reset function every time
        self._pacman_continuous_alive = 0
        self._eaten_time = 0

        self._beannumber = 0
        # store runtime details for rendering
        self._last_operation = []
        self._pacman_step_block = []
        self._ghosts_step_block = [[], [], []]
        self._pacman_score = 0
        self._ghosts_score = 0

        self._observation_space = spaces.MultiDiscrete(
            np.ones((size, size)) * SPACE_CATEGORY
        )  # 这段代码定义了环境的观察空间。在强化学习中，观察空间代表了智能体可以观察到的环境状态的所有可能值

        self._pacman_action_space = spaces.Discrete(OPERATION_NUM)
        self._ghost_action_space = spaces.MultiDiscrete(np.ones(3) * OPERATION_NUM)
        # 这段代码定义了环境的动作空间。在训练过程中，吃豆人和幽灵应该索取不同的动作空间

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    # return the current state of the game
    def render(self, mode="logic"):
        if mode == "local":
            # os.system("clear")
            for i in range(self._size - 1, -1, -1):  # 翻转y轴
                for j in range(self._size):
                    if self._pacman.get_coord() == [i, j]:
                        print("\033[1;40m  \033[0m", end="")
                        continue
                    if [i, j] in [ghost.get_coord() for ghost in self._ghosts]:
                        print("\033[1;40m  \033[0m", end="")
                        continue
                    if self._board[i][j] == 0:
                        print("\033[1;41m  \033[0m", end="")  # 墙：红
                    elif self._board[i][j] == 1:
                        print("\033[1;43m  \033[0m", end="")  # 空地：黄
                    elif self._board[i][j] == 2:
                        print("\033[1;44m  \033[0m", end="")  # 普通豆子：蓝
                    elif self._board[i][j] == 3:
                        print("\033[1;42m  \033[0m", end="")  # 奖励豆子：绿
                    elif self._board[i][j] == 4:
                        print("\033[1;47m  \033[0m", end="")  # 速度豆子：白
                    elif self._board[i][j] == 5:
                        print("\033[1;45m  \033[0m", end="")  # 磁铁豆子：紫
                    elif self._board[i][j] == 6:
                        print("\033[1;46m  \033[0m", end="")  # 护盾豆子：青
                    elif self._board[i][j] == 7:
                        print("\033[1;48;5;208m  \033[0m", end="")  # *2豆子：橘
                    elif self._board[i][j] == 8:
                        print("\033[1;48;5;0m  \033[0m", end="") # 传送门：黑
                print()

        elif mode == "logic":  # 返回一个字典
            return_dict = {
                "round": self._round,
                "level": self._level,
                # "board": self._board.tolist(),
                "pacman_step_block": self._pacman_step_block,
                "pacman_coord": self._pacman.get_coord(),
                "pacman_skills": self._last_skill_status,
                "ghosts_step_block": self._ghosts_step_block,
                "ghosts_coord": [
                    self._ghosts[0].get_coord(),
                    self._ghosts[1].get_coord(),
                    self._ghosts[2].get_coord(),
                ],
                "score": [self._pacman_score, self._ghosts_score],
                "events": [i.value for i in self._event_list],
                "StopReason": None,
            }
            return return_dict

    def reset(self):
        self._level += 1  # 0 1 2 3
        self._size = INITIAL_BOARD_SIZE[self._level]

        # regenerate at the corner
        coords = [
            [1, 1],
            [1, self._size - 2],
            [self._size - 2, 1],
            [self._size - 2, self._size - 2],
        ]

        # shuffle the coords
        random.shuffle(coords)

        # distribute the coords
        self._pacman.set_coord(coords[0])
        self._pacman.set_level(self._level)
        self._pacman.set_size(self._size)
        self._ghosts[0].set_coord(coords[1])
        self._ghosts[1].set_coord(coords[2])
        self._ghosts[2].set_coord(coords[3])

        self._board, self._beannumber = final_boardgenerator(self._size, self._level)

        self._round = 0

        return_board = self._board.tolist()

        beannum = self._beannumber

        return_dict = {
            "ghosts_coord": [
                self._ghosts[0].get_coord(),
                self._ghosts[1].get_coord(),
                self._ghosts[2].get_coord(),
            ],
            "pacman_coord": self._pacman.get_coord(),
            "score": [self._pacman_score, self._ghosts_score],
            "level": self._level,
            "board": return_board,
            "events": [],
            "beannumber": beannum,
        }
        return return_dict

    def ai_reset(self, dict):  # Note: this function is used for AI to reset the game
        self._level = dict["level"]

        self._size = INITIAL_BOARD_SIZE[self._level]

        self._ghosts[0].set_coord(dict["ghosts_coord"][0])
        self._ghosts[1].set_coord(dict["ghosts_coord"][1])
        self._ghosts[2].set_coord(dict["ghosts_coord"][2])
        self._pacman.set_coord(dict["pacman_coord"])

        self._ghosts_score = dict["score"][1]
        self._pacman_score = dict["score"][0]

        self._round = 0
        self._board = np.array(dict["board"])
        self._beannumber = dict["beannumber"]

        return

    def update_all_score(self):
        self._pacman_score = self.get_pacman_score()
        self._ghosts_score = self.get_ghosts_score()

    # Note: 如果pacman撞墙(x,y), step(x-100, y-100); 如果ghost撞墙(x,y), step(x-200, y-200)
    def step(self, pacmanAction: int, ghostAction: List[int]):

        self._round += 1
        # 重置事件列表（本轮）
        self._event_list = []

        self._last_operation = []
        self._ghosts_step_block = [[], [], []]
        self._pacman_step_block = []

        self._last_skill_status = self._pacman.get_skills_status()
        self._last_operation = [pacmanAction, ghostAction]

        pacman_coord = self._pacman.get_coord()
        ghost_coords = [ghost.get_coord() for ghost in self._ghosts]

        # pacman move
        # Note: double_score: 0, speed_up: 1, magnet: 2, shield: 3
        self._pacman_step_block.append(pacman_coord)
        for i in range(3):
            self._ghosts_step_block[i].append(ghost_coords[i])

        self._pacman.eat_bean(self._board)  # 吃掉此处的豆子
        pacman_skills = self._pacman.get_skills_status()  # 更新状态
        # Note: 向下和向上的位置对调
        if pacman_skills[Skill.SPEED_UP.value] > 0:
            if pacmanAction == 0:
                self._pacman_step_block.append(self._pacman.get_coord())
                self._pacman_step_block.append(self._pacman.get_coord())
            elif pacmanAction == 3:  # 向下移动
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.up(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET - 1,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET,
                    ]
                )
                self._pacman.eat_bean(self._board)
                pacman_skills = self._pacman.get_skills_status()  # 更新状态
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.up(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET - 1,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET,
                    ]
                )
            elif pacmanAction == 2:  # 向左移动
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.left(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET - 1,
                    ]
                )
                self._pacman.eat_bean(self._board)
                pacman_skills = self._pacman.get_skills_status()  # 更新状态
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.left(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET - 1,
                    ]
                )
            elif pacmanAction == 1:  # 向上移动
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.down(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET + 1,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET,
                    ]
                )
                self._pacman.eat_bean(self._board)
                pacman_skills = self._pacman.get_skills_status()  # 更新状态
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.down(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET + 1,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET,
                    ]
                )
            elif pacmanAction == 4:  # 向右移动
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.right(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET + 1,
                    ]
                )
                self._pacman.eat_bean(self._board)
                pacman_skills = self._pacman.get_skills_status()  # 更新状态
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.right(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET + 1,
                    ]
                )
            else:  # 退出程序
                raise ValueError("Invalid action number of speedy pacman")
        else:
            if pacmanAction == 0:
                self._pacman_step_block.append(self._pacman.get_coord())
            elif pacmanAction == 3:
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.up(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET - 1,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET,
                    ]
                )
            elif pacmanAction == 2:
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.left(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET - 1,
                    ]
                )
            elif pacmanAction == 1:
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.down(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET + 1,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET,
                    ]
                )
            elif pacmanAction == 4:
                self._pacman_step_block.append(
                    self._pacman.get_coord()
                    if self._pacman.right(self._board)
                    else [
                        self._pacman.get_coord()[0] + PACMAN_HIT_OFFSET,
                        self._pacman.get_coord()[1] + PACMAN_HIT_OFFSET + 1,
                    ]
                )
            else:
                raise ValueError("Invalid action number of normal pacman")
        self.update_all_score()
        # ghost move
        for i in range(3):
            if ghostAction[i] == 0:
                self._ghosts_step_block[i].append(self._ghosts[i].get_coord())
                pass
            elif ghostAction[i] == 3:
                self._ghosts_step_block[i].append(
                    self._ghosts[i].get_coord()
                    if self._ghosts[i].up(self._board)
                    else [
                        self._ghosts[i].get_coord()[0] + GHOST_HIT_OFFSET - 1,
                        self._ghosts[i].get_coord()[1] + GHOST_HIT_OFFSET,
                    ]
                )
            elif ghostAction[i] == 2:
                self._ghosts_step_block[i].append(
                    self._ghosts[i].get_coord()
                    if self._ghosts[i].left(self._board)
                    else [
                        self._ghosts[i].get_coord()[0] + GHOST_HIT_OFFSET,
                        self._ghosts[i].get_coord()[1] + GHOST_HIT_OFFSET - 1,
                    ]
                )
            elif ghostAction[i] == 1:
                self._ghosts_step_block[i].append(
                    self._ghosts[i].get_coord()
                    if self._ghosts[i].down(self._board)
                    else [
                        self._ghosts[i].get_coord()[0] + GHOST_HIT_OFFSET + 1,
                        self._ghosts[i].get_coord()[1] + GHOST_HIT_OFFSET,
                    ]
                )
            elif ghostAction[i] == 4:
                self._ghosts_step_block[i].append(
                    self._ghosts[i].get_coord()
                    if self._ghosts[i].right(self._board)
                    else [
                        self._ghosts[i].get_coord()[0] + GHOST_HIT_OFFSET,
                        self._ghosts[i].get_coord()[1] + GHOST_HIT_OFFSET + 1,
                    ]
                )
            else:
                raise ValueError("Invalid action of ghost")
        self.update_all_score()

        # check if ghosts caught pacman
        flag = False
        parsed_pacman_step_block = []
        for i in range(len(self._pacman_step_block)):
            if self._pacman_step_block[i][0] < 0:
                if self._pacman_step_block[i - 1][0] < 0:
                    parsed_pacman_step_block.append(self._pacman_step_block[i - 2])
                else:
                    parsed_pacman_step_block.append(self._pacman_step_block[i - 1])
            else:
                parsed_pacman_step_block.append(self._pacman_step_block[i])

        parsed_ghosts_step_block = []
        for i in range(3):
            parsed_ghost_step_block = []
            for j in range(len(self._ghosts_step_block[i])):
                if self._ghosts_step_block[i][j][0] < 0:
                    if self._ghosts_step_block[i][j - 1][0] < 0:
                        parsed_ghost_step_block.append(
                            self._ghosts_step_block[i][j - 2]
                        )
                    else:
                        parsed_ghost_step_block.append(
                            self._ghosts_step_block[i][j - 1]
                        )
                else:
                    parsed_ghost_step_block.append(self._ghosts_step_block[i][j])
            parsed_ghosts_step_block.append(parsed_ghost_step_block)

        # parse into same stamps
        if len(parsed_pacman_step_block) == 2:
            parsed_pacman_step_block = [
                parsed_pacman_step_block[0],
                [
                    (parsed_pacman_step_block[0][0] + parsed_pacman_step_block[1][0])
                    / 2,
                    (parsed_pacman_step_block[0][1] + parsed_pacman_step_block[1][1])
                    / 2,
                ],
                parsed_pacman_step_block[1],
            ]

        for i in range(3):
            parsed_ghosts_step_block[i] = [
                parsed_ghosts_step_block[i][0],
                [
                    (
                        parsed_ghosts_step_block[i][0][0]
                        + parsed_ghosts_step_block[i][1][0]
                    )
                    / 2,
                    (
                        parsed_ghosts_step_block[i][0][1]
                        + parsed_ghosts_step_block[i][1][1]
                    )
                    / 2,
                ],
                parsed_ghosts_step_block[i][1],
            ]

        def distance(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # FIXED issue 2: not counting the first step
        for i in range(1, len(parsed_pacman_step_block)):
            for j in range(3):
                if (
                    distance(
                        parsed_pacman_step_block[i], parsed_ghosts_step_block[j][i]
                    )
                    <= 0.5
                ):
                    flag = True
                    break

        if flag:
            if not self._pacman.encounter_ghost():
                self._ghosts[i].update_score(DESTORY_PACMAN_SHIELD)
                self.update_all_score()
                self._pacman_continuous_alive = 0
                self._event_list.append(Event.SHEILD_DESTROYED)
            else:
                self._pacman.update_score(EATEN_BY_GHOST)
                self._ghosts[i].update_score(EAT_PACMAN)
                self.update_all_score()
                self._eaten_time += 1
                self._pacman_continuous_alive = 0
                self._pacman.clear_skills()
                self._last_skill_status = self._pacman.get_skills_status()
                self._pacman.set_coord(self.find_distant_emptyspace())
                # FIXED issue 3: respawn coord can be fetched in pacman_coord, and len(pacman_step_block) == speed + 1
                self._event_list.append(Event.EATEN_BY_GHOST)

        # diminish the skill time
        self._pacman.new_round()
        # 避免出现最后一轮明明达到了最后一个豆子，但是还是会被判定为超时的问题
        try:
            self._pacman.eat_bean(self._board)
        except:
            print("Pacman eat bean error")
            exit(1)

        # FIXED issue 1: HUGE BONUS
        if not flag:
            self._pacman_continuous_alive += 1
            if self._pacman_continuous_alive >= PACMAN_HUGE_BONUS_THRESHOLD:
                self._pacman.update_score(PACMAN_HUGE_BONUS)
                self.update_all_score()
                self._pacman_continuous_alive = 0

        if flag and self._eaten_time >= GHOST_HUGE_BONUS_THRESHOLD:
            for ghost in self._ghosts:
                ghost.update_score(GHOST_HUGE_BONUS)
            self.update_all_score()
            self._eaten_time = 0

        # 通关
        count_remain_beans = 0
        for i in range(self._size):
            for j in range(self._size):
                if (self._board[i][j] == Space.REGULAR_BEAN.value) or (self._board[i][j] == Space.BONUS_BEAN.value):
                    count_remain_beans += 1

        if count_remain_beans == 0:
            self._pacman.update_score(
                EAT_ALL_BEANS
                + (MAX_ROUND[self._level] - self._round) * ROUND_BONUS_GAMMA
            )
            self.update_all_score()
            self._pacman.reset()
            self._event_list.append(Event.FINISH_LEVEL)
            self._pacman_continuous_alive = 0
            self._eaten_time = 0
            # return true means game over
            return (self._board, [self._pacman_score, self._ghosts_score], True)

        # 超时
        if self._round >= MAX_ROUND[self._level]:
            for i in self._ghosts:
                i.update_score(PREVENT_PACMAN_EAT_ALL_BEANS)
            self.update_all_score()
            self._pacman.reset()
            self._event_list.append(Event.TIMEOUT)
            self._pacman_continuous_alive = 0
            self._eaten_time = 0
            return (self._board, [self._pacman_score, self._ghosts_score], True)

        # 正常
        return self._board, [self._pacman_score, self._ghosts_score], False

    def get_pacman_score(self):
        return self._pacman.get_score()

    def get_ghosts_score(self):
        ghost_scores = [ghost.get_score() for ghost in self._ghosts]
        return sum(ghost_scores)

    # in case of respawn just beside the ghosts, find a distant empty space
    def find_distant_emptyspace(self):
        coord = []
        max = 0
        for i in range(self._size):
            for j in range(self._size):
                if self._board[i][j] == Space.EMPTY.value:
                    sum = 0
                    for k in self._ghosts:
                        sum += abs(k.get_coord()[0] - i) + abs(k.get_coord()[1] - j)
                    if sum > max:
                        max = sum
                        coord = [i, j]
        if coord == []:
            raise ValueError("No empty space found")
        return coord

    def get_level(self):
        return self._level

    # utils functions for user ai
    def observation_space(self):
        return self._observation_space

    def pacman_action_space(self):
        return self._pacman_action_space

    def ghost_action_space(self):
        return self._ghost_action_space

    def events(self):
        return self._event_list

    def game_state(self):
        return GameState(
            level=self._level,
            round=self._round,
            board_size=self._size,
            board=self._board,
            pacman_skill_status=self._pacman.get_skills_status(),
            pacman_pos=self._pacman.get_coord(),
            ghosts_pos=[ghost.get_coord() for ghost in self._ghosts],
            pacman_score=self._pacman_score,
            ghosts_score=self._ghosts_score,
        )
