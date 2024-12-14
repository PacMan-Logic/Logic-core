import numpy as np
import random
from .gamedata import *

# note: level1 38*38 level2 29*29 level3 20*20

def final_boardgenerator(actual_size, level):
    size = 20
    if actual_size == 20:
        num_blocks = 1
    else:
        num_blocks = 2
    
    original_board = np.full((20 * num_blocks, 20 * num_blocks), Space.REGULAR_BEAN.value)
    
    if num_blocks == 1:
        original_board = boardgenerator(actual_size)
    
    else:
        original_board[0:20, 0:20] = boardgenerator(actual_size)
        original_board[0:20, (size - 2):(size + 18)] = boardgenerator(actual_size)
        original_board[(size - 2):(size + 18), 0:20] = boardgenerator(actual_size)
        original_board[(size - 2): (size + 18), (size - 2): (size + 18)] = boardgenerator(actual_size)
    
    final_board = original_board[0:actual_size, 0:actual_size]
    
    # fix：在最中间的3*3的可走区域，加一个传送门
    flag = False
    middle = actual_size // 2 # fix:integer here
    if level == 3:
        flag = True # fix:level3 不设置传送门
    
    a = -1
    b = -1
    while not flag:
        a = random.randint(middle - 1, middle + 1)
        b = random.randint(middle - 1, middle + 1)
        if final_board[a][b] != Space.WALL.value:
            final_board[a][b] = Space.PORTAL.value # 传送门
            flag = True
        
    # 护盾每关3个
    iter = 0
    while iter < 3:
        x = random.randint(1, size - 2)
        y = random.randint(1, size - 2)
        if final_board[x][y] == Space.EMPTY.value or final_board[x][y] == Space.REGULAR_BEAN.value:
            final_board[x][y] = Space.SHIELD_BEAN.value
            iter += 1
    
    # 在地图的边缘添加墙壁
    final_board[0, :] = final_board[-1, :] = final_board[:, 0] = final_board[:, -1] = 0
    
    t = 0
    for i in range(actual_size):
        for j in range(actual_size):
            if final_board[i][j] == Space.REGULAR_BEAN.value or final_board[i][j] == Space.BONUS_BEAN.value or final_board[i][j] == Space.SPEED_BEAN.value or final_board[i][j] == Space.MAGNET_BEAN.value or final_board[i][j] == Space.SHIELD_BEAN.value or final_board[i][j] == Space.DOUBLE_BEAN.value:
                t += 1
                

    return final_board, t, np.array([a, b])
    

def boardgenerator(actual_size):
    # 创建20x20的二维数组，所有元素初始化为2（普通豆子）
    size = 20
    board = np.full((size, size), 2)

	# 生成墙壁
    for i in range(2, size - 2, ((size - 4) // 2) + 1):
        for j in range(2, size - 2, ((size - 2) // 2) ):
            number = random.choice([1, 2, 3, 4, 5])
            if number == 1:
                board = l_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1 )
            elif number == 2:
                board = opposite_l_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            elif number == 3:
                board = cross_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            elif number == 4:
                board = c_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            elif number == 5:
                board = opposite_c_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
	
            
	# 生成不同种类的豆子fix:降低护盾数，每一关3个
    for i in range(1, size - 2):
        for j in range(1, size - 2):
            if board[i][j] == Space.REGULAR_BEAN.value:
                number = random.randint(0, 100)
                if number < 5:
                    board[i][j] = Space.BONUS_BEAN.value
                elif number < 15:# fix: 加速豆比例上升
                    board[i][j] = Space.SPEED_BEAN.value
                elif number < 25:# fix：磁铁比例上升
                    board[i][j] = Space.MAGNET_BEAN.value
                elif number < 30:
                    board[i][j] = Space.DOUBLE_BEAN.value
                elif number > 75: # fix：不能豆子全铺满
                    board[i][j] = Space.EMPTY.value
        
    
    return board

def l_wall_generator(board, size, a, b):
    # 生成L形墙
    x = a + 3
    y = b - 3
    board[x][y] = Space.WALL.value
    for i in range(1, size - 2):
        board[x - i][y] = Space.WALL.value
        board[x][y + i] = Space.WALL.value
    
    # 在组件区域内再生成随机的障碍物        
    if size == 8:
        cnt = 3    
    while cnt > 0:
        if size == 8: # 第三关地图20*20
            a = random.randint(x - size + 3,  x - 1)
            b = random.randint(y + 1,  y + size - 3)
            if board[a][b] == Space.REGULAR_BEAN.value:
                board[a][b] = Space.WALL.value
                cnt -= 1
    return board

def opposite_l_wall_generator(board, size, a, b):
    # 生成反L形墙
    x = a - 3
    y = b + 3
    board[x][y] = Space.WALL.value
    for i in range(1, size - 2):
        board[x + i][y] = Space.WALL.value
        board[x][y - i] = Space.WALL.value
    
    # 在组件区域内再生成随机的障碍物        
    if size == 8:
        cnt = 3    
    while cnt > 0:
        if size == 8:
            a = random.randint(x + 1, x + size - 3)
            b = random.randint(y - size + 3,  y - 1)
            if board[a][b] == Space.REGULAR_BEAN.value:
                board[a][b] = Space.WALL.value
                cnt -= 1
                
    return board
    
def cross_wall_generator(board, size, x, y):
    # 生成十字墙
    len = size // 2 
    if size == 8:
        board[x][y] = Space.WALL.value

    for i in range(1, len):
        if size == 8:
            board[x - i][y] = Space.WALL.value
            board[x + i][y] = Space.WALL.value
            board[x][y - i] = Space.WALL.value
            board[x][y + i] = Space.WALL.value
    return board

def c_wall_generator(board, size, x, y):
    len = (size // 2) - 1
    board[x][y] = Space.REGULAR_BEAN.value
    for i in range(1, len + 1): # 组件内加障碍
        board[x - i][y + i] = Space.WALL.value
        board[x + i][y - i] = Space.WALL.value

    for i in range(0, len + 1):
        board[x - i][y + len] = Space.WALL.value
        board[x + i][y + len] = Space.WALL.value
        board[x - len][y + i] = Space.WALL.value
        board[x - len][y - i] = Space.WALL.value
        board[x + len][y + i] = Space.WALL.value
        board[x + len][y - i] = Space.WALL.value
        board[x - i][y - len] = Space.WALL.value
        board[x + i][y - len] = Space.WALL.value
        
    board[x][y + len] = Space.BONUS_BEAN.value
    board[x][y - len] = Space.BONUS_BEAN.value
   
    return board

def opposite_c_wall_generator(board, size, x, y):
    len = (size // 2) - 1
    board[x][y] = Space.REGULAR_BEAN.value
    for i in range(1, len + 1): # 组件内加障碍
        board[x - i][y - i] = Space.WALL.value
        board[x + i][y + i] = Space.WALL.value
    
    for i in range(0, len + 1):
        board[x - i][y + len] = Space.WALL.value
        board[x + i][y + len] = Space.WALL.value
        board[x - len][y + i] = Space.WALL.value
        board[x - len][y - i] = Space.WALL.value
        board[x + len][y + i] = Space.WALL.value
        board[x + len][y - i] = Space.WALL.value
        board[x - i][y - len] = Space.WALL.value
        board[x + i][y - len] = Space.WALL.value
       
    board[x][y - len] = Space.BONUS_BEAN.value
    board[x - len][y] = Space.BONUS_BEAN.value
    
    return board