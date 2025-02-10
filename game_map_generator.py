# import random

# def generate_level(L, H, N_traps, N_drops, N_coins):
#     # 创建空白关卡
#     level = [[" " for _ in range(L)] for _ in range(H)]

#     # 生成地面（最底部的某一行）
#     ground_y = H - 2  # 地面在倒数第二行
#     for x in range(L):
#         if random.random() > 0.1:  # 10% 概率留空形成跳跃挑战
#             level[ground_y][x] = "x"

#     # 生成陷阱（!），放在地面上
#     for _ in range(N_traps):
#         while True:
#             x = random.randint(1, L - 2)
#             if level[ground_y][x] == "x":  # 只在地面上放陷阱
#                 level[ground_y][x] = "!"
#                 break

#     # 生成掉落机关（v），随机浮空放置
#     for _ in range(N_drops):
#         while True:
#             x = random.randint(1, L - 2)
#             y = random.randint(1, ground_y - 3)  # 不要太低
#             if level[y][x] == " ":  # 确保是空位
#                 level[y][x] = "v"
#                 break

#     # 生成金币（o），放在略高的空中平台
#     for _ in range(N_coins):
#         while True:
#             x = random.randint(1, L - 2)
#             y = random.randint(2, ground_y - 1)
#             if level[y][x] == " " and level[y + 1][x] in ["x", "v"]:  # 确保在地面或机关上方
#                 level[y][x] = "o"
#                 break

#     # 生成玩家出生点（@）
#     level[ground_y - 1][1] = "@"  # 左侧出生点

#     # 生成出口（终点）
#     level[ground_y - 1][L - 2] = "E"  # 右侧终点

#     return ["".join(row) for row in level]

# # 生成第 6 关的难度水平
# L, H = 50, 15  # 关卡大小
# N_traps = 10   # 陷阱数量
# N_drops = 5    # 掉落机关
# N_coins = 8    # 金币数量

# level_data = generate_level(L, H, N_traps, N_drops, N_coins)

# # 打印关卡
# for row in level_data:
#     print(f'"{row}",')

# levels = []
# for difficulty in range(1, 21):  # 生成 20 关
#     L, H = 100, 30
#     N_traps = difficulty * 4  # 陷阱数量递增
#     N_drops = max(1, difficulty * 2)  # 掉落机关
#     N_coins = 10 - difficulty // 2  # 金币随难度减少
#     level = generate_level(L, H, N_traps, N_drops, N_coins)
#     levels.append(level)

# # 打印所有关卡
# for i, level in enumerate(levels):
#     print(f"#### Level {i+1} ####")
#     for row in level:
#         print(f'"{row}",')
#     print("\n")


import random
import copy
from collections import deque

import random
import numpy as np
from collections import deque

# ===========================
# 1️⃣ 评估地图难度
# ===========================

def calculate_difficulty(level):
    """
    计算地图的难度评分，结合地图尺寸、障碍物数量、跳跃复杂度等。
    """
    L = len(level[0])  # 地图宽度
    H = len(level)  # 地图高度

    N_traps = sum(row.count("!") for row in level)  # 普通陷阱
    N_moving_traps = sum(row.count("v") + row.count("|") + row.count("=") for row in level)  # 移动陷阱
    N_coins = sum(row.count("o") for row in level)  # 金币数

    # 估算跳跃复杂度（计算 `x` 之间的间隔）
    platform_positions = [i for i, row in enumerate(level) for ch in row if ch == "x"]
    if len(platform_positions) > 1:
        jump_complexity = sum(abs(platform_positions[i] - platform_positions[i - 1]) for i in range(1, len(platform_positions))) // 10
    else:
        jump_complexity = 0

    # **优化权重**
    difficulty = (
        0.1 * L +          # 地图长度（小幅度影响）
        0.1 * H +          # 地图高度
        10 * N_traps +     # 普通陷阱
        15 * N_moving_traps +  # 移动陷阱（更难，所以权重大）
        5 * jump_complexity +  # 跳跃复杂度
         2 * N_coins      # 金币减少难度（反向影响）
    )

    return round(difficulty, 2)


# ===========================
# 2️⃣ 生成过渡地图
# ===========================
def generate_transition_map(L, H, N_traps, N_moving_traps, N_coins, prev_map, next_map):
    """
    生成一张过渡地图，结合 prev_map 和 next_map，平滑调整难度
    """
    # 确保 prev_map 和 next_map 大小与 L, H 一致
    def resize_map(map_data, L, H):
        resized_map = []
        for y in range(H):
            if y < len(map_data):
                row = map_data[y]
                if len(row) < L:
                    row += " " * (L - len(row))  # 右侧填充空格
                resized_map.append(row[:L])  # 截取保证不会越界
            else:
                resized_map.append(" " * L)  # 额外行填充空格
        return resized_map

    prev_map = resize_map(prev_map, L, H)
    next_map = resize_map(next_map, L, H)

    # 初始化新关卡
    level = [[" " for _ in range(L)] for _ in range(H)]
    
    # 复制 prev_map 和 next_map 作为参考，避免索引越界
    for y in range(H):
        for x in range(L):
            if prev_map[y][x] in ["x", "!", "v", "o"] and random.random() > 0.5:  
                level[y][x] = prev_map[y][x]
            elif next_map[y][x] in ["x", "!", "v", "o"] and random.random() > 0.3:  
                level[y][x] = next_map[y][x]

    # 生成地面
    for x in range(L):
        if random.random() > 0.1:
            level[H-2][x] = "x"

    # 生成陷阱，减少陷阱密度
    for _ in range(N_traps):
        for _ in range(5):  # 只尝试 5 次，避免死循环
            x = random.randint(3, L - 3)  # 避免最左和最右
            y = random.randint(H // 2, H - 3)  # 陷阱靠近底部
            if level[y][x] == " " and level[y + 1][x] == "x":
                level[y][x] = "!"
                break

    # 生成移动陷阱，减少出现概率
    for _ in range(N_moving_traps):
        for _ in range(3):
            x = random.randint(3, L - 3)
            y = random.randint(3, H - 5)
            if level[y][x] == " ":
                level[y][x] = "v"
                break

    # 生成金币，增加 50% 的金币奖励
    for _ in range(N_coins + int(N_coins * 0.5)):  
        for _ in range(3):
            x = random.randint(3, L - 3)
            y = random.randint(3, H - 3)
            if level[y][x] == " " and level[y + 1][x] in ["x", "v"]:
                level[y][x] = "o"
                break

    # 生成玩家和终点
    level[H-3][1] = "@"  # 左侧出生点
    # level[H-3][L-2] = "E"  # 右侧终点

    return ["".join(row) for row in level]


# ===========================
# 3️⃣ 确保可解性
# ===========================
def is_solvable(level):
    """
    检测关卡是否可解
    """
    H = len(level)
    L = len(level[0])
    
    # 找到玩家位置 @ 和终点 E
    start = None
    end = None
    for y in range(H):
        for x in range(L):
            if level[y][x] == "@":
                start = (x, y)
            if level[y][x] == "E":
                end = (x, y)
    
    if not start or not end:
        return False  # 没有起点或终点
    
    # BFS 搜索路径
    queue = deque([start])
    visited = set([start])
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 上下左右移动

    while queue:
        cx, cy = queue.popleft()
        
        if (cx, cy) == end:
            return True  # 可解
        
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < L and 0 <= ny < H and (nx, ny) not in visited:
                if level[ny][nx] not in ("x", "!", "v"):  # 不能走墙壁和陷阱
                    queue.append((nx, ny))
                    visited.add((nx, ny))
    
    return False  # 找不到路径


# ===========================
# 4️⃣ 生成 `[x, x+n]` 难度的过渡地图
# ===========================
def generate_levels(start_difficulty, end_difficulty, prev_level, next_level, x):
    levels = []
    total_difficulty = end_difficulty - start_difficulty

    prev_L = len(prev_level[0])
    prev_H = len(prev_level)
    prev_traps = sum(row.count("!") for row in prev_level)
    prev_moving_traps = sum(row.count("v") + row.count("|") + row.count("=") for row in prev_level)
    prev_coins = sum(row.count("o") for row in prev_level)

    next_L = len(next_level[0])
    next_H = len(next_level)
    next_traps = sum(row.count("!") for row in next_level)
    next_moving_traps = sum(row.count("v") + row.count("|") + row.count("=") for row in next_level)
    next_coins = sum(row.count("o") for row in next_level)

    for difficulty in np.linspace(start_difficulty, end_difficulty, num=x):
        progress = (difficulty - start_difficulty) / total_difficulty

        L = int(prev_L + progress * (next_L - prev_L))
        H = int(prev_H + progress * (next_H - prev_H))
        N_traps = int(prev_traps + progress * (next_traps - prev_traps))
        N_moving_traps = int(prev_moving_traps + progress * (next_moving_traps - prev_moving_traps))
        N_coins = max(2, int(prev_coins + progress * (next_coins - prev_coins)))

        # 预生成 5 张候选地图
        candidate_maps = [generate_transition_map(L, H, N_traps, N_moving_traps, N_coins, prev_level, next_level) for _ in range(10000)]
        
        # 选择第一个可解的地图
        level = next((m for m in candidate_maps if is_solvable(m)), None)

        if level is None:
            print(f"⚠️ 无法找到可解地图，增加尝试次数！")
            while not level:
                level = generate_transition_map(L, H, N_traps, N_moving_traps, N_coins, prev_level, next_level)
                if is_solvable(level):
                    break

        levels.append(level)

    return levels


level_x_n1 = [
   "                                                                                                              ",
					"                                                                                                              ",
					"                                                                                                              ",
					"                                                                                                              ",
					"                                                                                                              ",
					"                                        o                                                                     ",
					"                                                                                                              ",
					"                                        x                                                                     ",
					"                                        x                                                                     ",
					"                                        x                                                                     ",
					"                                        x                                                                     ",
					"                                       xxx                                                                    ",
					"                                       x x                 !!!        !!!  xxx                                ",
					"                                       x x                 !x!        !x!                                     ",
					"                                     xxx xxx                x          x                                      ",
					"                                      x   x                 x   oooo   x       xxx                            ",
					"                                      x   x                 x          x      x!!!x                           ",
					"                                      x   x                 xxxxxxxxxxxx       xxx                            ",
					"                                     xx   xx      x   x      x                                                ",
					"                                      x   xxxxxxxxx   xxxxxxxx              x x                               ",
					"                                      x   x           x                    x!!!x                              ",
					"                                      x   x           x                     xxx                               ",
					"                                     xx   xx          x                                                       ",
					"                                      x   x= = = =    x            xxx                                        ",
					"                                      x   x           x           x!!!x                                       ",
					"                                      x   x    = = = =x     o      xxx       xxx                              ",
					"                                     xx   xx          x                     x!!!x                             ",
					"                              o   o   x   x           x     x                xxv        xxx                   ",
					"                                      x   x           x              x                 x!!!x                  ",
					"                             xxx xxx xxx xxx     o o  x!!!!!!!!!!!!!!x                   vx                   ",
					"                             x xxx x x xxx x          x!!!!!!!!!!!!!!x                                        ",
					"                             x             x   xxxxxxxxxxxxxxxxxxxxxxx                                        ",
					"                             xx           xx                                         xxx                      ",
					"  xxx                         x     x     x                                         x!!!x                xxx  ",
					"  x x                         x    xxx    x                                          xxx                 x x  ",
					"  x                           x    xxx    xxxxxxx                        xxxxx                             x  ",
					"  x                           x           x                              x   x                             x  ",
					"  x                           xx          x                              x x x                             x  ",
					"  x                                       x       |xxxx|    |xxxx|     xxx xxx                             x  ",
					"  x                xxx             o o    x                              x         xxx                     x  ",
					"  x               xxxxx       xx          x                             xxx       x!!!x          x         x  ",
					"  x               oxxxo       x    xxx    x                             x x        xxx          xxx        x  ",
					"  x                xxx        xxxxxxxxxxxxx  x oo x    x oo x    x oo  xx xx                    xxx        x  ",
					"  x      @          x         x           x!!x    x!!!!x    x!!!!x    xx   xx                    x         x  ",
					"  xxxxxxxxxxxxxxxxxxxxxxxxxxxxx           xxxxxxxxxxxxxxxxxxxxxxxxxxxxx     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  ",
					"                                                                                                              ",
				]
level_x_1 = [
    "                                      x!!x                        xxxxxxx                                    x!x  ",
					"                                      x!!x                     xxxx     xxxx                                 x!x  ",
					"                                      x!!xxxxxxxxxx           xx           xx                                x!x  ",
					"                                      xx!!!!!!!!!!xx         xx             xx                               x!x  ",
					"                                       xxxxxxxxxx!!x         x                                    o   o   o  x!x  ",
					"                                                xx!x         x     o   o                                    xx!x  ",
					"                                                 x!x         x                                xxxxxxxxxxxxxxx!!x  ",
					"                                                 xvx         x     x   x                        !!!!!!!!!!!!!!xx  ",
					"                                                             xx  |   |   |  xx            xxxxxxxxxxxxxxxxxxxxx   ",
					"                                                              xx!!!!!!!!!!!xx            v                        ",
					"                                                               xxxx!!!!!xxxx                                      ",
					"                  xvx                          x     x            xxxxxvx        xxx         xxx                  ",
					"                                               x     x                           x x         x x                  ",
					"                                               x     x                             x         x                    ",
					"                                               x     x                             xx        x                    ",
					"                                               xx    x                             x         x                    ",
					"                                               x     x      o  o     x   x         x         x                    ",
					"               xxxxxxx        xxx   xxx        x     x               x   x         x         x                    ",
					"              xx     xx         x   x          x     x     xxxxxx    x   x   xxxxxxxxx       x                    ",
					"             xx       xx        x o x          x    xx               x   x   x               x                    ",
					"     @       x         x        x   x          x     x               x   x   x               x                    ",
					"    xxx      x         x        x   x          x     x               x   xxxxx   xxxxxx      x                    ",
					"    x x      x         x       xx o xx         x     x               x     o     x x         x                    ",
					"!!!!x x!!!!!!x         x!!!!!!xx     xx!!!!!!!!xx    x!!!!!!!!!!     x     =     x x         x                    ",
					"!!!!x x!!!!!!x         x!!!!!xx       xxxxxxxxxx     x!!!!!!!xx!     xxxxxxxxxxxxx xx  o o  xx                    ",
					"!!!!x x!!!!!!x         x!!!!!x    o                 xx!!!!!!xx !                    xx     xx                     ",
					"!!!!x x!!!!!!x         x!!!!!x                     xx!!!!!!xx  !                     xxxxxxx                      ",
					"!!!!x x!!!!!!x         x!!!!!xx       xxxxxxxxxxxxxx!!!!!!xx   !                                                  ",
					"!!!!x x!!!!!!x         x!!!!!!xxxxxxxxx!!!!!!!!!!!!!!!!!!xx    !                                                  ",
					"!!!!x x!!!!!!x         x!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!xx     !                                                  "
]

x_n_diff = int(calculate_difficulty(level_x_1))
x_n1_diff = int(calculate_difficulty(level_x_n1))
print("Diff(x_n):", x_n_diff)
print("Diff(x_n1):", x_n1_diff)

generated_levels = generate_levels(x_n_diff, x_n1_diff, prev_level=level_x_1, next_level=level_x_n1, x=4)

# 输出生成的关卡
for i, level in enumerate(generated_levels):
    print(f"#### Level {i+1} ####")
   
    print('\n'.join(f'"{"".join(row)}",' for row in level))
       
    print("\n")
