from typing import List
import random
import gym
import numpy as np
from gym import spaces
from .board import *
from .pacman import Pacman
from .ghost import Ghost
from .gamedata import *
from .utils import *


class PacmanEnv(gym.Env):
    """吃豆人游戏的抽象类，管理游戏状态、玩家操作、游戏逻辑等"""

    metadata = {"render_modes": ["local", "logic", "ai"]}

    def __init__(
        self,
        render_mode=None,
        size=INITIAL_BOARD_SIZE[1],
    ):
        self._size = size
        self._player = 0

        self._round = 0
        self._pacman = Pacman()
        self._ghosts = [Ghost() for _ in range(3)]
        self._event_list = []
        self._last_skill_status = [0] * SKILL_NUM
        self._level = 0
        self._pacman_continuous_alive = 0
        self._eaten_time = 0
        self._portal_available = False
        self._beannumber = 0
        self._ghosts_step_block = [np.empty((0, 2), dtype=int) for _ in range(3)]
        self._pacman_step_block = np.empty((0, 2), dtype=int)
        self._pacman_score = 0
        self._ghosts_score = 0
        self._portal_coord = np.array([-1, -1])

        self._observation_space = spaces.MultiDiscrete(
            np.ones((size, size)) * SPACE_CATEGORY
        )
        self._pacman_action_space = spaces.Discrete(OPERATION_NUM)
        self._ghost_action_space = spaces.MultiDiscrete(np.ones(3) * OPERATION_NUM)
        self.render_mode = render_mode

    def render(self, mode="logic"):
        """渲染&输出游戏状态"""
        if mode == "local":  # 本地模式
            for i in range(self._size - 1, -1, -1):  # 翻转y轴
                for j in range(self._size):
                    if self._pacman.get_coord().tolist() == [i, j]:
                        print("\033[1;48;5;226m  \033[0m", end="")  # Pacman：亮黄色
                        continue
                    if [i, j] in [ghost.get_coord().tolist() for ghost in self._ghosts]:
                        print("\033[1;48;5;199m  \033[0m", end="")  # 幽灵：粉红色
                        continue
                    if self._board[i][j] == Space.WALL.value:
                        print("\033[1;48;5;160m  \033[0m", end="")  # 墙：深红色
                    elif self._board[i][j] == Space.EMPTY.value:
                        print("\033[1;48;5;244m  \033[0m", end="")  # 空地：灰色
                    elif self._board[i][j] == Space.REGULAR_BEAN.value:
                        print("\033[1;48;5;39m  \033[0m", end="")  # 普通豆子：天蓝色
                    elif self._board[i][j] == Space.BONUS_BEAN.value:
                        print("\033[1;48;5;82m  \033[0m", end="")  # 奖励豆子：浅绿色
                    elif self._board[i][j] == Space.SPEED_BEAN.value:
                        print("\033[1;48;5;214m  \033[0m", end="")  # 速度豆子：橙色
                    elif self._board[i][j] == Space.MAGNET_BEAN.value:
                        print("\033[1;48;5;165m  \033[0m", end="")  # 磁铁豆子：紫色
                    elif self._board[i][j] == Space.SHIELD_BEAN.value:
                        print("\033[1;48;5;51m  \033[0m", end="")  # 护盾豆子：青色
                    elif self._board[i][j] == Space.DOUBLE_BEAN.value:
                        print("\033[1;48;5;208m  \033[0m", end="")  # *2豆子：深橙色
                    elif self._board[i][j] == Space.PORTAL.value:
                        print("\033[1;48;5;93m  \033[0m", end="")  # 传送门：深紫色
                    elif self._board[i][j] == Space.FROZE_BEAN.value:
                        print("\033[1;48;5;118m  \033[0m", end="")  # 冻结豆子：亮绿色
                print()
        elif mode == "logic":  # 通信模式
            return_dict = {
                "round": self._round,
                "level": self._level,
                "pacman_step_block": self._pacman_step_block.tolist(),
                "pacman_coord": self._pacman.get_coord().tolist(),
                "pacman_skills": self._last_skill_status,
                "ghosts_step_block": [ghost_step_block.tolist() for ghost_step_block in self._ghosts_step_block],
                "ghosts_coord": [ghost.get_coord().tolist() for ghost in self._ghosts],
                "score": [self._pacman_score, self._ghosts_score],
                "events": [i.value for i in self._event_list],
                "portal_available": self._portal_available,
                "StopReason": None,
            }
            return return_dict

    def get_return_dict(self):
        return_dict = {
            "level": self._level,
            "round": self._round,
            "board_size": self._size,
            "board": self._board,
            "pacman_skill_status": np.array(self._pacman.get_skills_status()),
            "pacman_coord": self._pacman.get_coord(),
            "ghosts_coord": [ghost.get_coord() for ghost in self._ghosts],
            "score": [self._pacman_score, self._ghosts_score],
            "beannumber": self._beannumber,
            "portal_available": self._portal_available,
            "portal_coord": self._portal_coord,
        }
        return return_dict

    def reset(self, mode="logic"):
        """初始化游戏状态"""
        if mode == "local" and self.get_level() == 3:
            self._level = 1
        else:
            self._level += 1  # 0 1 2 3
        self._round = 0
        self._size = INITIAL_BOARD_SIZE[self._level]
        self._observation_space = spaces.MultiDiscrete(
            np.ones((self._size, self._size)) * SPACE_CATEGORY
        )
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
        self._pacman.set_coord(np.array(coords[0]))
        self._pacman.set_level(self._level)
        self._pacman.set_size(self._size)
        self._pacman.clear_skills() 
        for i in range(3):
            self._ghosts[i].set_coord(np.array(coords[i + 1]))

        self._board, self._beannumber, self._portal_coord = final_boardgenerator(
            self._size, self._level
        )
        self._pacman.set_portal_coord(self._portal_coord)
        self._portal_available = False

        return_dict = self.get_return_dict()
        return return_dict

    def ai_reset(self, reset_dict):
        """初始化(重置)AI游戏状态"""
        self._level = reset_dict["level"]
        self._round = 0
        self._size = INITIAL_BOARD_SIZE[self._level]
        self._observation_space = spaces.MultiDiscrete(
            np.ones((self._size, self._size)) * SPACE_CATEGORY
        )
        for i in range(3):
            self._ghosts[i].set_coord(np.array(reset_dict["ghosts_coord"][i]))
        self._pacman.set_coord(np.array(reset_dict["pacman_coord"]))
        self._pacman.clear_skills()
        self._ghosts_score = reset_dict["score"][1]
        self._pacman_score = reset_dict["score"][0]
        self._board = np.array(reset_dict["board"])
        self._beannumber = reset_dict["beannumber"]
        self._portal_coord = np.array(reset_dict["portal_coord"])
        self._portal_available = False
        return

    def update_all_score(self):
        self._pacman_score = self.get_pacman_score()
        self._ghosts_score = self.get_ghosts_score()

    def step(self, pacmanAction: int, ghostAction: List[int]) :
        """主逻辑：根据玩家的操作，更新游戏状态，返回(局面信息,吃豆人reward,幽灵reward,当前关卡是否结束,是否吃完所有的豆子)"""
        self._round += 1
        self._event_list = []
        pacman_action = Direction(pacmanAction)
        ghost_actions = [Direction(action) for action in ghostAction]
        self._ghosts_step_block = [np.empty((0, 2), dtype=int) for _ in range(3)]
        self._pacman_step_block = np.empty((0, 2), dtype=int)
        self._last_skill_status = self._pacman.get_skills_status()
        pacman_reward = 0
        ghosts_reward = [0,0,0]

        # 技能时间更新
        self._pacman.decrease_skill_time()
        
        # 若冰冻技能存在，将幽灵操作冻结
        if self._last_skill_status[Skill.FROZE.value] > 0:
            ghost_actions = [Direction.STAY] * 3
            self._pacman.decrease_skill_time([Skill.FROZE])

        self._pacman_step_block = np.vstack((self._pacman_step_block, np.array(self._pacman.get_coord())))

        for i in range(3):
            self._ghosts_step_block[i] = np.vstack((self._ghosts_step_block[i], np.array(self._ghosts[i].get_coord())))

        # 吃豆人移动
        for _ in range(1 if self._last_skill_status[Skill.SPEED_UP.value] == 0 else 2):
            pacman_reward += self._pacman.eat_bean(self._board)
            appendix = self._pacman.get_coord() + direction_to_offset(pacman_action)
            success = self._pacman.try_move(self._board, pacman_action)
            if not success:
                appendix += PACMAN_HIT_OFFSET
            self._pacman_step_block = np.vstack((self._pacman_step_block, appendix))
        self.update_all_score()
        # 幽灵移动
        for i in range(len(self._ghosts)):
            appendix = self._ghosts[i].get_coord() + direction_to_offset(
                ghost_actions[i]
            )
            success = self._ghosts[i].try_move(self._board, ghost_actions[i])
            if not success:
                appendix += GHOST_HIT_OFFSET
            self._ghosts_step_block[i] = np.vstack((self._ghosts_step_block[i], appendix))
        self.update_all_score()

        # 预处理吃豆人和幽灵经过的路径，便于后续判断
        # 将“撞墙”坐标转换回原坐标
        caught = False

        def find_last_positive_coord(arr, idx):
            """找到数组 arr 中从 idx 往前的最后一个正坐标"""
            arr_slice = arr[:idx+1]
            mask = arr_slice[:, 0] > 0
            if np.any(mask):  
                return arr_slice[mask][-1]
            raise ValueError("No positive item found")

        parsed_pacman_step_block = np.array([
            find_last_positive_coord(self._pacman_step_block, i)
            for i in range(len(self._pacman_step_block))
        ])

        parsed_ghosts_step_block = [
            np.array([
                find_last_positive_coord(self._ghosts_step_block[j], i)
                for i in range(len(self._ghosts_step_block[j]))
            ])
            for j in range(3)
        ]

        # 统一长度
        def from2to3(start, end):
            """将长度为 2 的路径取中点转换为长度为 3"""
            return np.array([
                start,
                (start + end) / 2,
                end
            ])

        if len(parsed_pacman_step_block) == 2:
            parsed_pacman_step_block = from2to3(
                parsed_pacman_step_block[0], parsed_pacman_step_block[1]
            )

        for i in range(3):
            if len(parsed_ghosts_step_block[i]) == 2:
                parsed_ghosts_step_block[i] = from2to3(
                    parsed_ghosts_step_block[i][0], parsed_ghosts_step_block[i][1]
                )
        
        pacman_reward += self._pacman.eat_bean(self._board)
        self.update_all_score()

        count_remain_beans = 0
        for i in range(self._size):
            for j in range(self._size):
                if (self._board[i][j] == Space.REGULAR_BEAN.value) or (
                    self._board[i][j] == Space.BONUS_BEAN.value
                ):
                    count_remain_beans += 1

        ghost_num = 0
        for i in range(1, len(parsed_pacman_step_block)):
            for j in range(3):
                if (
                    manhattan_distance(
                        parsed_pacman_step_block[i], parsed_ghosts_step_block[j][i]
                    )
                    <= 0.5
                ):
                    caught = True
                    ghost_num = j
                    break
        respwan = False
        if caught:
            if not self._pacman.try_break_shield():  # 有护盾保护
                ghosts_reward[ghost_num] += self._ghosts[ghost_num].update_score(DESTORY_PACMAN_SHIELD)
                self.update_all_score()
                self._pacman_continuous_alive = 0
                self._event_list.append(Event.SHIELD_DESTROYED)
            else:  # 没有护盾保护
                respwan = True
                pacman_reward += self._pacman.update_bonus(EATEN_BY_GHOST)
                ghosts_reward[ghost_num] += self._ghosts[ghost_num].update_score(EAT_PACMAN)
                self.update_all_score()
                self._eaten_time += 1
                self._pacman_continuous_alive = 0
                self._pacman.clear_skills()
                self._last_skill_status = self._pacman.get_skills_status()
                self._pacman.set_coord(np.array(self.find_distant_emptyspace()))
                self._event_list.append(Event.EATEN_BY_GHOST)

            if (
                self._eaten_time >= GHOST_HUGE_BONUS_THRESHOLD
            ):  # 被吃掉次数达到阈值，幽灵获得额外加分
                for i in range(3):
                    ghosts_reward[i] += self._ghosts[i].update_score(GHOST_HUGE_BONUS)
                self.update_all_score()
                self._eaten_time = 0
        else:
            self._pacman_continuous_alive += 1
            if (
                self._pacman_continuous_alive >= PACMAN_HUGE_BONUS_THRESHOLD
            ):  # 连续存活次数达到阈值，吃豆人获得额外加分
                pacman_reward += self._pacman.update_bonus(PACMAN_HUGE_BONUS)
                self.update_all_score()
                self._pacman_continuous_alive = 0

        self._pacman.update_current_skill()
        
        if self._portal_available and not respwan:  # 传送门开启且吃豆人未被吃掉
            if self._portal_coord.tolist() in self._pacman_step_block:
                eaten_all_beans = False
                if count_remain_beans == 0:
                    eaten_all_beans = True
                    pacman_reward += self._pacman.update_bonus(EAT_ALL_BEANS)
                    self.update_all_score()
                pacman_reward += self._pacman.update_bonus(
                    (int)((MAX_ROUND[self._level] - self._round) * ROUND_BONUS_GAMMA)
                )
                self.update_all_score()
                self._pacman.clear_skills()
                self._event_list.append(Event.FINISH_LEVEL)
                self._pacman_continuous_alive = 0
                self._eaten_time = 0
                return (self.get_return_dict(), pacman_reward, ghosts_reward, True, eaten_all_beans)

        if (
            self._level != MAX_LEVEL and self._round >= PORTAL_AVAILABLE[self._level]
        ):  # 传送门开启
            self._portal_available = True

        if count_remain_beans == 0:  # 吃豆人吃掉所有豆子
            pacman_reward += self._pacman.update_bonus(EAT_ALL_BEANS)
            self.update_all_score()
            pacman_reward += self._pacman.update_bonus(
                (int)((MAX_ROUND[self._level] - self._round) * ROUND_BONUS_GAMMA)
            )
            self.update_all_score()
            self._pacman.clear_skills()
            self._event_list.append(Event.FINISH_LEVEL)
            self._pacman_continuous_alive = 0
            self._eaten_time = 0
            return (self.get_return_dict(), pacman_reward, ghosts_reward, True, True)

        # 超时
        if self._round >= MAX_ROUND[self._level]:
            for i in range(3):
                ghosts_reward[i] += self._ghosts[i].update_score(PREVENT_PACMAN_EAT_ALL_BEANS)
            self.update_all_score()
            self._pacman.clear_skills()
            self._event_list.append(Event.TIMEOUT)
            self._pacman_continuous_alive = 0
            self._eaten_time = 0
            return (self.get_return_dict(), pacman_reward, ghosts_reward, True, False)

        # 仍在关卡中
        return (self.get_return_dict(), pacman_reward, ghosts_reward, False, False)

    def get_pacman_score(self):
        """功能函数：获取吃豆人的分数"""
        return self._pacman.get_score()

    def get_ghosts_score(self):
        """功能函数：获取幽灵的分数"""
        ghost_scores = [ghost.get_score() for ghost in self._ghosts]
        return sum(ghost_scores)

    def get_level(self):
        """功能函数：获取关卡序号"""
        return self._level

    def find_distant_emptyspace(self):
        """功能函数：找到远离最近幽灵的空地坐标，避免重生在幽灵附近"""
        best_coord = []
        max_distance = 0

        for i in range(self._size):
            for j in range(self._size):
                if self._board[i][j] == Space.EMPTY.value:
                    min_distance = float("inf") 
                    for ghost in self._ghosts: 
                        ghost_x, ghost_y = ghost.get_coord()
                        dist = abs(ghost_x - i) + abs(ghost_y - j)
                        min_distance = min(min_distance, dist)

                    if min_distance > max_distance:
                        max_distance = min_distance
                        best_coord = [i, j]

        if not best_coord:
            raise ValueError("没有找到可用的空地")

        return best_coord

    def observation_space(self):
        """AI接口：获取观察空间"""
        return self._observation_space

    def pacman_action_space(self):
        """AI接口：获取吃豆人的操作空间"""
        return self._pacman_action_space

    def ghost_action_space(self):
        """AI接口：获取幽灵的操作空间"""
        return self._ghost_action_space

    def game_state(self):
        """AI接口：获取游戏状态"""
        return GameState(
            space_info={
                "observation_space": self._observation_space,
                "pacman_action_space": self._pacman_action_space,
                "ghost_action_space": self._ghost_action_space,
            },
            level=self._level,
            round=self._round,
            board_size=self._size,
            board=self._board,
            pacman_skill_status=self._pacman.get_skills_status(),
            pacman_pos=self._pacman.get_coord(),
            ghosts_pos=[ghost.get_coord() for ghost in self._ghosts],
            pacman_score=self._pacman_score,
            ghosts_score=self._ghosts_score,
            beannumber=self._beannumber,
            portal_available=self._portal_available,
            portal_coord=self._portal_coord,
        )
