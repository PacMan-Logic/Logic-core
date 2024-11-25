import numpy as np
import random

# note: level1 9*20*20 level2 4*20*20 level3 1*20*20

def final_boardgenerator(actual_size):
    size = 20
    num_blocks = actual_size // size
    final_board = np.full((actual_size, actual_size), 2)
    
    for i in range(num_blocks):
        for j in range(num_blocks):
            block = boardgenerator(size, actual_size)
            final_board[i*size:(i+1)*size, j*size:(j+1)*size] = block
    
    if actual_size == 60:
        # 设置特定坐标的元素值为2(加通道)
        coordinates = [
            (9, 19), (9, 20),
            (10, 19), (10, 20),
            (29, 19), (29, 20),
            (30, 19), (30, 20), 
            (19, 9), (20, 9), 
            (19, 10), (20, 10), 
            (19, 29), (19, 30), 
            (20, 29), (20, 30),
            (9, 39), (9, 40),
            (10, 39), (10, 40),
            (19, 49), (19, 50), 
            (20, 49), (20, 50),
            (29, 39), (29, 40),
            (30, 39), (30, 40), 
            (49, 39), (49, 40),
            (50, 39), (50, 40), 
            (49, 19), (49, 20),
            (50, 19), (50, 20),
            (39, 9), (40, 9), 
            (39, 10), (40, 10), 
            (39, 29), (40, 29), 
            (39, 30), (40, 30), 
            (39, 49), (40, 49), 
            (39, 50), (40, 50)
        ]
        
        for coord in coordinates:
            final_board[coord] = 2

    elif actual_size == 40:
        coordinates = [
            (9, 19), (9, 20),
            (10, 19), (10, 20),
            (29, 19), (29, 20),
            (30, 19), (30, 20), 
            (19, 9), (20, 9), 
            (19, 10), (20, 10), 
            (19, 29), (19, 30), 
            (20, 29), (20, 30)
        ]
        for coord in coordinates:
            final_board[coord] = 2
    
    return final_board
    

def boardgenerator(size, actual_size):
    # 创建20x20的二维数组，所有元素初始化为2（普通豆子）
    board = np.full((size, size), 2)

    # 生成墙壁
    for i in range(2, size - 2, ((size - 4) // 2) + 1):
        for j in range(2, size - 2, ((size - 2) // 2) ):
            number = random.choice([1, 2, 3, 4, 5])
            if number == 1:
                board = l_wall_generator(board, ((size - 4) // 2), min(i + ((size - 4) // 2), size - 3) - 1 , j )
            elif number == 2:
                board = opposite_l_wall_generator(board, (size - 4) // 2, i, min(j + ((size - 4) // 2), size - 3) - 1)
            elif number == 3:
                board = cross_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            elif number == 4:
                board = c_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            elif number == 5:
                board = opposite_c_wall_generator(board, (size - 4) // 2, i + ((size - 4) // 4) - 1, j + ((size - 4) // 4) - 1)
            
	
	# 生成不同种类的豆子
    for i in range(1, size - 2):
        for j in range(1, size - 2):
            if board[i][j] == 2:
                number = random.randint(0, 100)
                if number < 5:
                    board[i][j] = 3
                elif number < 10:
                    board[i][j] = 4
                elif number < 15:
                    board[i][j] = 5
                elif number < 20:
                    board[i][j] = 6
                elif number < 25:
                    board[i][j] = 7
                elif (actual_size == 60 or actual_size == 40) and number > 75: # 空间太大，豆子太多，需要减少豆子数量
                    board[i][j] = 1
     
    # 在地图的边缘添加墙壁
    board[0, :] = board[-1, :] = board[:, 0] = board[:, -1] = 0
    
    return board

def l_wall_generator(board, size, x, y):
    # 生成L形墙
    board[x][y] = 0
    for i in range(1, size - 2):
        board[x - i][y] = 0
        board[x][y + i] = 0
    
    # 在组件区域内再生成随机的障碍物        
    if size == 8:
        cnt = 3    
    while cnt > 0:
        if size == 8: # 第三关地图20*20
            a = random.randint(x - size + 3,  x - 1)
            b = random.randint(y + 1,  y + size - 3)
            if board[a][b] == 2:
                board[a][b] = 0
                cnt -= 1
    return board

def opposite_l_wall_generator(board, size, x, y):
    # 生成反L形墙
    board[x][y] = 0
    for i in range(1, size - 2):
        board[x + i][y] = 0
        board[x][y - i] = 0
    
    # 在组件区域内再生成随机的障碍物        
    if size == 8:
        cnt = 3    
    while cnt > 0:
        if size == 8:
            a = random.randint(x + 1, x + size - 3)
            b = random.randint(y - size + 3,  y - 1)
            if board[a][b] == 2:
                board[a][b] = 0
                cnt -= 1
                
    return board
    
def cross_wall_generator(board, size, x, y):
    # 生成十字墙
    len = size // 2 
    if size == 8:
        board[x][y] = 0

    for i in range(1, len):
        if size == 8:
            board[x - i][y] = 0
            board[x + i][y] = 0
            board[x][y - i] = 0
            board[x][y + i] = 0
    return board

def c_wall_generator(board, size, x, y):
    len = (size // 2) - 1
    board[x][y] = 2
    for i in range(1, len + 1): # 组件内加障碍
        board[x - i][y + i] = 0
        board[x + i][y - i] = 0

    for i in range(0, len + 1):
        board[x - i][y + len] = 0
        board[x + i][y + len] = 0
        board[x - len][y + i] = 0
        board[x - len][y - i] = 0
        board[x + len][y + i] = 0
        board[x + len][y - i] = 0
        board[x - i][y - len] = 0
        board[x + i][y - len] = 0
        
    board[x][y + len] = 3
    board[x][y - len] = 3
   
    return board

def opposite_c_wall_generator(board, size, x, y):
    len = (size // 2) - 1
    board[x][y] = 2
    for i in range(1, len + 1): # 组件内加障碍
        board[x - i][y - i] = 0
        board[x + i][y + i] = 0
    
    for i in range(0, len + 1):
        board[x - i][y + len] = 0
        board[x + i][y + len] = 0
        board[x - len][y + i] = 0
        board[x - len][y - i] = 0
        board[x + len][y + i] = 0
        board[x + len][y - i] = 0
        board[x - i][y - len] = 0
        board[x + i][y - len] = 0
       
    board[x][y - len] = 3
    board[x - len][y] = 3
    
    return board