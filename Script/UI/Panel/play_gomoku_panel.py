import random
import numpy as np
from collections import deque, defaultdict
import re

from Script.UI.Moudle import draw
from Script.Core import cache_control, game_type, get_text, flow_handle, constant, py_cmd
from types import FunctionType
from Script.Config import normal_config, game_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
line_feed = draw.NormalDraw()
""" 换行绘制对象 """
line_feed.text = "\n"
line_feed.width = 1
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """

COLUMN = 15
ROW = 15
FIVE = 10000000
BLOCK_FIVE = FIVE
FOUR = 100000
FOUR_FOUR = FOUR  # 双冲四
FOUR_THREE = FOUR  # 冲四活三
THREE_THREE = FOUR / 2  # 双三
BLOCK_FOUR = 1500
THREE = 1000
BLOCK_THREE = 150
TWO_TWO = 200  # 双活二
TWO = 100
BLOCK_TWO = 15
ONE = 10
BLOCK_ONE = 1
MAX = 1000000000

config = {
    'enable_cache': True,  # 是否开启缓存
    'points_limit': 20,  # 每一层最多搜索节点数
    'only_in_line': False,  # 是否只搜索一条线上的点位，一种优化方式。
    'inline_count': 4,  # 最近多少个点位能算作
    'in_line_distance': 5,  # 判断点位是否在一条线上的最大距离
}

ALL_DIRECTIONS = [
    (0, 1),  # Horizontal
    (1, 0),  # Vertical
    (1, 1),  # Diagonal \
    (1, -1)  # Diagonal /
]

PERFORMANCE = {
    'updateTime': 0,
    'getPointsTime': 0,
}

# 缓存内容：depth, value, move
CACHE_HITS = {
    'search': 0,
    'total': 0,
    'hit': 0
}

PATTERNS = {
    'five': re.compile('11111'),
    'blockfive': re.compile('211111|111112'),
    'four': re.compile('011110'),
    'blockFour': re.compile('10111|11011|11101|211110|211101|211011|210111|011112|101112|110112|111012'),
    'three': re.compile('011100|011010|010110|001110'),
    'blockThree': re.compile('211100|211010|210110|001112|010112|011012'),
    'two': re.compile('001100|011000|000110|010100|001010'),
}

SHAPES = {
    'FIVE': 5,
    'BLOCK_FIVE': 50,
    'FOUR': 4,
    'FOUR_FOUR': 44,  # 双冲四
    'FOUR_THREE': 43,  # 冲四活三
    'THREE_THREE': 33,  # 双三
    'BLOCK_FOUR': 40,
    'THREE': 3,
    'BLOCK_THREE': 30,
    'TWO_TWO': 22,  # 双活二
    'TWO': 2,
    'NONE': 0,
}

PERFORMANCE_SHAPE = {
    'five': 0,
    'blockFive': 0,
    'four': 0,
    'blockFour': 0,
    'three': 0,
    'blockThree': 0,
    'two': 0,
    'none': 0,
    'total': 0,
}

only_three_threshold = 6


class Gomoku_Cache:
    def __init__(self, capacity=1000000):
        self.capacity = capacity
        self.gomoku_cache = deque()
        self.map = {}

    # 获取一个键的值
    def get(self, key):
        if not config['enable_cache']:
            return False
        return self.map.get(key, None)

    # 设置或插入一个值
    def put(self, key, value):
        if not config['enable_cache']:
            return False
        if len(self.gomoku_cache) >= self.capacity:
            oldest_key = self.gomoku_cache.popleft()  # 移除最老的键
            del self.map[oldest_key]  # 从map中也删除它

        if key not in self.map:
            self.gomoku_cache.append(key)  # 将新键添加到cache数组
        self.map[key] = value  # 更新或设置键值

    # 检查缓存中是否存在某个键
    def has(self, key):
        if not config['enable_cache']:
            return False
        return key in self.map

class Gomoku_Board:
    def __init__(self, size=15, first_role=1):
        self.size = size
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.first_role = first_role  # 1 for black, -1 for white
        self.role = first_role  # 1 for black, -1 for white
        self.history = []
        self.zobrist = ZobristCache(self.size)
        self.winner_cache = Gomoku_Cache()
        self.gameover_cache = Gomoku_Cache()
        self.evaluate_cache = Gomoku_Cache()
        self.valuable_moves_cache = Gomoku_Cache()
        self.evaluate_time = 0
        self.evaluator = Evaluate(self.size)

    def is_game_over(self):
        hash_value = self.hash()
        if self.gameover_cache.get(hash_value):
            return self.gameover_cache.get(hash_value)
        if self.get_winner() != 0:
            self.gameover_cache.put(hash_value, True)
            return True  # Someone has won
        # Game is over when there is no empty space on the board or someone has won
        if np.any(self.board == 0):
            self.gameover_cache.put(hash_value, False)
            return False
        self.gameover_cache.put(hash_value, True)
        return True

    def get_winner(self):
        hash_value = self.hash()
        if self.winner_cache.get(hash_value):
            return self.winner_cache.get(hash_value)
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Horizontal, Vertical, Diagonal
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i, j] == 0:
                    continue
                for direction in directions:
                    count = 0
                    while (0 <= i + direction[0] * count < self.size and
                           0 <= j + direction[1] * count < self.size and
                           self.board[i + direction[0] * count, j + direction[1] * count] == self.board[i, j]):
                        count += 1
                    if count >= 5:
                        self.winner_cache.put(hash_value, self.board[i, j])
                        return self.board[i, j]
        self.winner_cache.put(hash_value, 0)
        return 0

    def get_valid_moves(self):
        print("get_valid_moves is deprecated. Use get_valuable_moves instead.")
        return list(zip(*np.where(self.board == 0)))

    def put(self, i, j, role=None):
        if role is None:
            role = self.role
        if not (0 <= i < self.size and 0 <= j < self.size):
            print("Invalid move Not Number!", i, j)
            return False
        if self.board[i, j] != 0:
            print("Invalid move!", i, j)
            return False
        self.board[i, j] = role
        self.history.append((i, j, role))
        self.zobrist.toggle_piece(i, j, role)
        self.evaluator.move(i, j, role)
        self.role *= -1  # Switch role
        return True

    def undo(self):
        if not self.history:
            print("No moves to undo!")
            return False
        last_move = self.history.pop()
        self.board[last_move[0], last_move[1]] = 0  # Remove the piece from the board
        self.role = last_move[2]  # Switch back to the previous player
        self.zobrist.toggle_piece(last_move[0], last_move[1], last_move[2])
        self.evaluator.undo(last_move[0], last_move[1])
        return True

    def position2coordinate(self, position):
        row = position // self.size
        col = position % self.size
        return row, col

    def coordinate2position(self, coordinate):
        return coordinate[0] * self.size + coordinate[1]

    def get_valuable_moves(self, role, depth=0, only_three=False, only_four=False):
        hash_value = self.hash()
        prev = self.valuable_moves_cache.get(hash_value)
        if prev and prev['role'] == role and prev['depth'] == depth and prev['only_three'] == only_three and prev['only_four'] == only_four:
            return prev['moves']
        moves = self.evaluator.get_moves(role, depth, only_three, only_four)
        # Handle a special case where the center point is not occupied, add the center point by default
        if not only_three and not only_four:
            center = self.size // 2
            if self.board[center, center] == 0:
                moves.append((center, center))
        self.valuable_moves_cache.put(hash_value, {
            'role': role,
            'moves': moves,
            'depth': depth,
            'only_three': only_three,
            'only_four': only_four
        })
        return moves

    def display(self, extra_points=[]):
        extra_positions = [self.coordinate2position(point) for point in extra_points]
        result = '  ' + ' '.join(f'{i:2}' for i in range(self.size)) + '\n'  # 顶部列标注
        for i in range(self.size):
            result += f'{i:2} '  # 左侧行标注
            for j in range(self.size):
                position = self.coordinate2position((i, j))
                if position in extra_positions:
                    result += ' ? '
                    continue
                if self.board[i, j] == 1:
                    result += ' O '
                elif self.board[i, j] == -1:
                    result += ' X '
                else:
                    result += ' - '
            result += f' {i:2}\n'  # 右侧行标注
        result += '  ' + ' '.join(f'{i:2}' for i in range(self.size)) + '\n'  # 底部列标注
        return result

    def hash(self):
        return self.zobrist.get_hash()

    def evaluate(self, role):
        hash_value = self.hash()
        prev = self.evaluate_cache.get(hash_value)
        if prev and prev['role'] == role:
            return prev['score']
        winner = self.get_winner()
        if winner != 0:
            score = FIVE * winner * role
        else:
            score = self.evaluator.evaluate(role)
        self.evaluate_cache.put(hash_value, {'role': role, 'score': score})
        return score

    def reverse(self):
        new_board = Gomoku_Board(self.size, -self.first_role)
        for move in self.history:
            new_board.put(move[0], move[1], -move[2])
        return new_board

    def __str__(self):
        return '\n'.join(''.join(str(cell) for cell in row) for row in self.board)

    # def play_game(self, ai_difficulty=4):
    #     player_role = 1  # 玩家执黑棋
    #     ai_role = -1  # AI执白棋
    #     while not self.is_game_over():
    #         print(self.display())
    #         if self.role == player_role:
    #             move = self.get_player_move()
    #         else:
    #             _, move, _ = minmax(self, ai_role, depth=ai_difficulty)
    #             print(f"AI move: {move}")
    #         if not self.put(*move):
    #             print("Invalid move. Try again.")
    #             continue
    #         if self.is_game_over():
    #             print(self.display())
    #             winner = self.get_winner()
    #             if winner == 1:
    #                 print("Black wins!")
    #             elif winner == -1:
    #                 print("White wins!")
    #             else:
    #                 print("It's a draw!")
    #             break

    def get_player_move(self):
        while True:
            try:
                move = input(f"Player {self.role} move (row,col): ")
                i, j = map(int, move.split(','))
                return i, j
            except ValueError:
                print("Invalid input. Please enter row and column separated by a comma.")


class ZobristCache:
    def __init__(self, size):
        self.size = size
        self.zobrist_table = self.initialize_zobrist_table(size)
        self.hash = 0

    def initialize_zobrist_table(self, size):
        table = []
        for i in range(size):
            row = []
            for j in range(size):
                row.append({
                    1: self.random_bit_string(64),  # black
                    -1: self.random_bit_string(64)  # white
                })
            table.append(row)
        return table

    def random_bit_string(self, length):
        return int(''.join(str(random.randint(0, 1)) for _ in range(length)), 2)

    def toggle_piece(self, x, y, role):
        self.hash ^= self.zobrist_table[x][y][role]

    def get_hash(self):
        return self.hash


class Evaluate:
    def __init__(self, size=15):
        self.size = size
        self.board = np.zeros((self.size + 2, self.size + 2), dtype=int)
        self.board[0, :] = self.board[:, 0] = self.board[-1, :] = self.board[:, -1] = 2
        self.black_scores = np.zeros((self.size, self.size), dtype=int)
        self.white_scores = np.zeros((self.size, self.size), dtype=int)
        self.init_points()
        self.history = []  # 记录历史 [position, role]

    def move(self, x, y, role):
        # 清空记录
        for d in range(4):
            self.shape_cache[role][d][x][y] = 0
            self.shape_cache[-role][d][x][y] = 0
        self.black_scores[x][y] = 0
        self.white_scores[x][y] = 0

        # 更新分数
        self.board[x + 1, y + 1] = role  # Adjust for the added wall
        self.update_point(x, y)
        self.history.append((coordinate2position(x, y, self.size), role))

    def undo(self, x, y):
        self.board[x + 1, y + 1] = 0  # Adjust for the added wall
        self.update_point(x, y)
        self.history.pop()

    def init_points(self):
        # 缓存每个点位的分数，避免重复计算
        # 结构： [role][direction][x][y] = shape
        self.shape_cache = defaultdict(lambda: defaultdict(lambda: np.full((self.size, self.size), SHAPES['NONE'], dtype=int)))
        # 缓存每个形状对应的点位
        # 结构： points_cache[role][shape] = Set(direction1, direction2);
        self.points_cache = defaultdict(lambda: defaultdict(set))

    def get_points_in_line(self, role):
        points_in_line = defaultdict(set)  # 在一条线上的点位
        has_points_in_line = False
        last2_points = [position for position, _ in self.history[-config['inline_count']:]]
        processed = {}  # 已经处理过的点位
        for r in [role, -role]:
            for point in last2_points:
                x, y = position2coordinate(point, self.size)
                for ox, oy in ALL_DIRECTIONS:
                    for sign in [1, -1]:  # -1 for negative direction, 1 for positive direction
                        for step in range(1, config['in_line_distance'] + 1):
                            nx, ny = x + sign * step * ox, y + sign * step * oy
                            position = coordinate2position(nx, ny, self.size)
                            if nx < 0 or nx >= self.size or ny < 0 or ny >= self.size:
                                break
                            if self.board[nx + 1, ny + 1] != 0:
                                continue
                            if processed.get(position) == r:
                                continue
                            processed[position] = r
                            for direction in range(4):
                                shape = self.shape_cache[r][direction][nx][ny]
                                if shape:
                                    points_in_line[shape].add(coordinate2position(nx, ny, self.size))
                                    has_points_in_line = True
        if has_points_in_line:
            return points_in_line
        return False

    def get_points(self, role, depth, vct, vcf):
        first = role if depth % 2 == 0 else -role  # 先手
        start = PERFORMANCE['getPointsTime']
        if config['only_in_line'] and len(self.history) >= config['inline_count']:
            points_in_line = self.get_points_in_line(role)
            if points_in_line:
                PERFORMANCE['getPointsTime'] += PERFORMANCE['getPointsTime'] - start
                return points_in_line

        points = defaultdict(set)  # 全部点位
        last_points = [position for position, _ in self.history[-4:]]

        for r in [role, -role]:
            for i in range(self.size):
                for j in range(self.size):
                    four_count = block_four_count = three_count = 0
                    for direction in range(4):
                        if self.board[i + 1, j + 1] != 0:
                            continue
                        shape = self.shape_cache[r][direction][i][j]
                        if not shape:
                            continue
                        point = i * self.size + j
                        if vct:
                            if depth % 2 == 0:
                                if depth == 0 and r != first:
                                    continue
                                if shape != SHAPES['THREE'] and not is_four(shape) and not is_five(shape):
                                    continue
                                if shape == SHAPES['THREE'] and r != first:
                                    continue
                                if depth == 0 and r != first:
                                    continue
                                if depth > 0:
                                    if shape == SHAPES['THREE'] and len(get_all_shapes_of_point(self.shape_cache, i, j, r)) == 1:
                                        continue
                                    if shape == SHAPES['BLOCK_FOUR'] and len(get_all_shapes_of_point(self.shape_cache, i, j, r)) == 1:
                                        continue
                            else:
                                if shape != SHAPES['THREE'] and not is_four(shape) and not is_five(shape):
                                    continue
                                if shape == SHAPES['THREE'] and r == -first:
                                    continue
                                if depth > 1:
                                    if shape == SHAPES['BLOCK_FOUR'] and len(get_all_shapes_of_point(self.shape_cache, i, j, r)) == 1:
                                        continue
                                    if shape == SHAPES['BLOCK_FOUR'] and not has_in_line(point, last_points, self.size):
                                        continue
                        if vcf:
                            if not is_four(shape) and not is_five(shape):
                                continue
                        if depth > 2 and (shape == SHAPES['TWO'] or shape == SHAPES['TWO_TWO'] or shape == SHAPES['BLOCK_THREE']) and not has_in_line(point, last_points, self.size):
                            continue
                        points[shape].add(point)
                        if shape == SHAPES['FOUR']:
                            four_count += 1
                        elif shape == SHAPES['BLOCK_FOUR']:
                            block_four_count += 1
                        elif shape == SHAPES['THREE']:
                            three_count += 1
                        union_shape = None
                        if four_count >= 2:
                            union_shape = SHAPES['FOUR_FOUR']
                        elif block_four_count and three_count:
                            union_shape = SHAPES['FOUR_THREE']
                        elif three_count >= 2:
                            union_shape = SHAPES['THREE_THREE']
                        if union_shape:
                            points[union_shape].add(point)

        PERFORMANCE['getPointsTime'] += PERFORMANCE['getPointsTime'] - start
        return points

    def update_point(self, x, y):
        start = PERFORMANCE['updateTime']
        self.update_single_point(x, y, 1)
        self.update_single_point(x, y, -1)

        for ox, oy in ALL_DIRECTIONS:
            for sign in [1, -1]:  # -1 for negative direction, 1 for positive direction
                for step in range(1, 6):
                    reach_edge = False
                    for role in [1, -1]:
                        nx, ny = x + sign * step * ox + 1, y + sign * step * oy + 1
                        if self.board[nx, ny] == 2:
                            reach_edge = True
                            break
                        elif self.board[nx, ny] == -role:
                            continue
                        elif self.board[nx, ny] == 0:
                            self.update_single_point(nx - 1, ny - 1, role, (sign * ox, sign * oy))
                    if reach_edge:
                        break
        PERFORMANCE['updateTime'] += PERFORMANCE['updateTime'] - start

    def update_single_point(self, x, y, role, direction=None):
        if self.board[x + 1, y + 1] != 0:
            return

        self.board[x + 1, y + 1] = role

        directions = [direction] if direction else ALL_DIRECTIONS
        shape_cache = self.shape_cache[role]

        for ox, oy in directions:
            shape_cache[direction2index(ox, oy)][x][y] = SHAPES['NONE']

        score = 0
        block_four_count = three_count = two_count = 0
        for int_direction in range(4):
            shape = shape_cache[int_direction][x][y]
            if shape > SHAPES['NONE']:
                score += get_real_shape_score(shape)
                if shape == SHAPES['BLOCK_FOUR']:
                    block_four_count += 1
                if shape == SHAPES['THREE']:
                    three_count += 1
                if shape == SHAPES['TWO']:
                    two_count += 1

        for ox, oy in directions:
            int_direction = direction2index(ox, oy)
            shape, self_count = get_shape_fast(self.board, x, y, ox, oy, role)
            if not shape:
                continue
            shape_cache[int_direction][x][y] = shape
            if shape == SHAPES['BLOCK_FOUR']:
                block_four_count += 1
            if shape == SHAPES['THREE']:
                three_count += 1
            if shape == SHAPES['TWO']:
                two_count += 1
            if block_four_count >= 2:
                shape = SHAPES['FOUR_FOUR']
            elif block_four_count and three_count:
                shape = SHAPES['FOUR_THREE']
            elif three_count >= 2:
                shape = SHAPES['THREE_THREE']
            elif two_count >= 2:
                shape = SHAPES['TWO_TWO']
            score += get_real_shape_score(shape)

        self.board[x + 1, y + 1] = 0

        if role == 1:
            self.black_scores[x][y] = score
        else:
            self.white_scores[x][y] = score

        return score

    def evaluate(self, role):
        black_score = np.sum(self.black_scores)
        white_score = np.sum(self.white_scores)
        score = black_score - white_score if role == 1 else white_score - black_score
        return score

    def get_moves(self, role, depth, only_three=False, only_four=False):
        moves = [(move // self.size, move % self.size) for move in self._get_moves(role, depth, only_three, only_four)]
        return moves

    def _get_moves(self, role, depth, only_three=False, only_four=False):
        points = self.get_points(role, depth, only_three, only_four)
        fives = points[SHAPES['FIVE']]
        block_fives = points[SHAPES['BLOCK_FIVE']]
        if fives or block_fives:
            return set(fives | block_fives)
        fours = points[SHAPES['FOUR']]
        block_fours = points[SHAPES['BLOCK_FOUR']]
        if only_four or fours:
            return set(fours | block_fours)
        four_fours = points[SHAPES['FOUR_FOUR']]
        if four_fours:
            return set(four_fours | block_fours)
        threes = points[SHAPES['THREE']]
        four_threes = points[SHAPES['FOUR_THREE']]
        if four_threes:
            return set(four_threes | block_fours | threes)
        three_threes = points[SHAPES['THREE_THREE']]
        if three_threes:
            return set(three_threes | block_fours | threes)
        if only_three:
            return set(block_fours | threes)
        block_threes = points[SHAPES['BLOCK_THREE']]
        two_twos = points[SHAPES['TWO_TWO']]
        twos = points[SHAPES['TWO']]
        res = set(list(block_fours | threes | block_threes | two_twos | twos)[:config['points_limit']])
        return res

    def display(self):
        result = ''
        for i in range(1, self.size + 1):
            for j in range(1, self.size + 1):
                if self.board[i, j] == 1:
                    result += 'O '
                elif self.board[i, j] == -1:
                    result += 'X '
                else:
                    result += '- '
            result += '\n'
        print(result)

def check_winner(list, COLUMN, ROW):
    # 检查是否有五子连珠
    for m in range(COLUMN):
        for n in range(ROW):
            if n < ROW - 4 and (m, n) in list and (m, n + 1) in list and (m, n + 2) in list and (m, n + 3) in list and (m, n + 4) in list:
                return True
            elif m < ROW - 4 and (m, n) in list and (m + 1, n) in list and (m + 2, n) in list and (m + 3, n) in list and (m + 4, n) in list:
                return True
            elif m < ROW - 4 and n < ROW - 4 and (m, n) in list and (m + 1, n + 1) in list and (m + 2, n + 2) in list and (m + 3, n + 3) in list and (m + 4, n + 4) in list:
                return True
            elif m < ROW - 4 and n > 3 and (m, n) in list and (m + 1, n - 1) in list and (m + 2, n - 2) in list and (m + 3, n - 3) in list and (m + 4, n - 4) in list:
                return True
    return False

# 形状转换分数，注意这里的分数是当前位置还没有落子的分数
def get_real_shape_score(shape):
    if shape == SHAPES['FIVE']:
        return FOUR
    elif shape == SHAPES['BLOCK_FIVE']:
        return BLOCK_FOUR
    elif shape == SHAPES['FOUR']:
        return THREE
    elif shape == SHAPES['FOUR_FOUR']:
        return THREE
    elif shape == SHAPES['FOUR_THREE']:
        return THREE
    elif shape == SHAPES['BLOCK_FOUR']:
        return BLOCK_THREE
    elif shape == SHAPES['THREE']:
        return TWO
    elif shape == SHAPES['THREE_THREE']:
        return THREE_THREE / 10
    elif shape == SHAPES['BLOCK_THREE']:
        return BLOCK_TWO
    elif shape == SHAPES['TWO']:
        return ONE
    elif shape == SHAPES['TWO_TWO']:
        return TWO_TWO / 10
    else:
        return 0

def direction2index(ox, oy):
    if ox == 0:
        return 0  # |
    if oy == 0:
        return 1  # -
    if ox == oy:
        return 2  # \
    if ox != oy:
        return 3  # /

# 坐标转换函数
def position2coordinate(position, size):
    return [position // size, position % size]

def coordinate2position(x, y, size):
    return x * size + y

# a和b是否在一条直线上，且距离小于maxDistance
def is_line(a, b, size):
    max_distance = config['in_line_distance']
    x1, y1 = position2coordinate(a, size)
    x2, y2 = position2coordinate(b, size)
    return (
        (x1 == x2 and abs(y1 - y2) < max_distance) or
        (y1 == y2 and abs(x1 - x2) < max_distance) or
        (abs(x1 - x2) == abs(y1 - y2) and abs(x1 - x2) < max_distance)
    )

def is_all_in_line(p, arr, size):
    for i in range(len(arr)):
        if not is_line(p, arr[i], size):
            return False
    return True

def has_in_line(p, arr, size):
    for i in range(len(arr)):
        if is_line(p, arr[i], size):
            return True
    return False

# 使用字符串匹配的方式实现的形状检测，速度较慢，但逻辑比较容易理解
def get_shape(board, x, y, offsetX, offsetY, role):
    opponent = -role
    empty_count = 0
    self_count = 1
    opponent_count = 0
    shape = SHAPES['NONE']

    # 跳过为空的节点
    if (board[x + offsetX + 1][y + offsetY + 1] == 0 and
        board[x - offsetX + 1][y - offsetY + 1] == 0 and
        board[x + 2 * offsetX + 1][y + 2 * offsetY + 1] == 0 and
        board[x - 2 * offsetX + 1][y - 2 * offsetY + 1] == 0):
        return [SHAPES['NONE'], self_count, opponent_count, empty_count]

    # two 类型占比超过一半，做一下优化
    # 活二是不需要判断特别严谨的
    for i in range(-3, 4):
        if i == 0:
            continue
        nx, ny = x + i * offsetX + 1, y + i * offsetY + 1
        if nx < 0 or ny < 0 or nx >= len(board) or ny >= len(board[0]):
            continue
        current_role = board[nx][ny]
        if current_role == 2:
            opponent_count += 1
        elif current_role == role:
            self_count += 1
        elif current_role == 0:
            empty_count += 1
    if self_count == 2:
        if not opponent_count:
            return [SHAPES['TWO'], self_count, opponent_count, empty_count]
        else:
            return [SHAPES['NONE'], self_count, opponent_count, empty_count]
    # two 类型优化结束，不需要的话可以在直接删除这一段代码不影响功能

    # three类型大约占比有20%，也优化一下

    empty_count = 0
    self_count = 1
    opponent_count = 0
    result_string = '1'

    for i in range(1, 6):
        nx, ny = x + i * offsetX + 1, y + i * offsetY + 1
        current_role = board[nx][ny]
        if current_role == 2:
            result_string += '2'
        elif current_role == 0:
            result_string += '0'
        else:
            result_string += '1' if current_role == role else '2'
        if current_role == 2 or current_role == opponent:
            opponent_count += 1
            break
        if current_role == 0:
            empty_count += 1
        if current_role == role:
            self_count += 1
    for i in range(1, 6):
        nx, ny = x - i * offsetX + 1, y - i * offsetY + 1
        current_role = board[nx][ny]
        if current_role == 2:
            result_string = '2' + result_string
        elif current_role == 0:
            result_string = '0' + result_string
        else:
            result_string = ('1' if current_role == role else '2') + result_string
        if current_role == 2 or current_role == opponent:
            opponent_count += 1
            break
        if current_role == 0:
            empty_count += 1
        if current_role == role:
            self_count += 1
    if PATTERNS['five'].search(result_string):
        shape = SHAPES['FIVE']
        PERFORMANCE_SHAPE['five'] += 1
        PERFORMANCE_SHAPE['total'] += 1
    elif PATTERNS['four'].search(result_string):
        shape = SHAPES['FOUR']
        PERFORMANCE_SHAPE['four'] += 1
        PERFORMANCE_SHAPE['total'] += 1
    elif PATTERNS['blockFour'].search(result_string):
        shape = SHAPES['BLOCK_FOUR']
        PERFORMANCE_SHAPE['blockFour'] += 1
        PERFORMANCE_SHAPE['total'] += 1
    elif PATTERNS['three'].search(result_string):
        shape = SHAPES['THREE']
        PERFORMANCE_SHAPE['three'] += 1
        PERFORMANCE_SHAPE['total'] += 1
    elif PATTERNS['blockThree'].search(result_string):
        shape = SHAPES['BLOCK_THREE']
        PERFORMANCE_SHAPE['blockThree'] += 1
        PERFORMANCE_SHAPE['total'] += 1
    elif PATTERNS['two'].search(result_string):
        shape = SHAPES['TWO']
        PERFORMANCE_SHAPE['two'] += 1
        PERFORMANCE_SHAPE['total'] += 1
    # 尽量减少多余字符串生成
    if self_count <= 1 or len(result_string) < 5:
        return [shape, self_count, opponent_count, empty_count]

    return [shape, self_count, opponent_count, empty_count]

def count_shape(board, x, y, offsetX, offsetY, role):
    opponent = -role

    inner_empty_count = 0  # 棋子中间的内部空位
    temp_empty_count = 0
    self_count = 0
    total_length = 0

    side_empty_count = 0  # 边上的空位
    no_empty_self_count = 0
    one_empty_self_count = 0

    # right
    for i in range(1, 6):
        nx, ny = x + i * offsetX + 1, y + i * offsetY + 1
        current_role = board[nx][ny]
        if current_role == 2 or current_role == opponent:
            break
        if current_role == role:
            self_count += 1
            side_empty_count = 0
            if temp_empty_count:
                inner_empty_count += temp_empty_count
                temp_empty_count = 0
            if inner_empty_count == 0:
                no_empty_self_count += 1
                one_empty_self_count += 1
            elif inner_empty_count == 1:
                one_empty_self_count += 1
        total_length += 1
        if current_role == 0:
            temp_empty_count += 1
            side_empty_count += 1
        if side_empty_count >= 2:
            break
    if not inner_empty_count:
        one_empty_self_count = 0
    return {
        'self_count': self_count,
        'total_length': total_length,
        'no_empty_self_count': no_empty_self_count,
        'one_empty_self_count': one_empty_self_count,
        'inner_empty_count': inner_empty_count,
        'side_empty_count': side_empty_count
    }

# 使用遍历位置的方式实现的形状检测，速度较快，大约是字符串速度的2倍 但理解起来会稍微复杂一些
def get_shape_fast(board, x, y, offsetX, offsetY, role):
    # 有一点点优化效果：跳过为空的节点
    if (board[x + offsetX + 1][y + offsetY + 1] == 0 and
        board[x - offsetX + 1][y - offsetY + 1] == 0 and
        board[x + 2 * offsetX + 1][y + 2 * offsetY + 1] == 0 and
        board[x - 2 * offsetX + 1][y - 2 * offsetY + 1] == 0):
        return [SHAPES['NONE'], 1]

    self_count = 1
    total_length = 1
    shape = SHAPES['NONE']

    left_empty = 0
    right_empty = 0  # 左右边上的空位
    no_empty_self_count = 1
    one_empty_self_count = 1

    left = count_shape(board, x, y, -offsetX, -offsetY, role)
    right = count_shape(board, x, y, offsetX, offsetY, role)

    self_count = left['self_count'] + right['self_count'] + 1
    total_length = left['total_length'] + right['total_length'] + 1
    no_empty_self_count = left['no_empty_self_count'] + right['no_empty_self_count'] + 1
    one_empty_self_count = max(left['one_empty_self_count'] + right['no_empty_self_count'], left['no_empty_self_count'] + right['one_empty_self_count']) + 1
    right_empty = right['side_empty_count']
    left_empty = left['side_empty_count']

    if total_length < 5:
        return [shape, self_count]
    # five 
    if no_empty_self_count >= 5:
        if right_empty > 0 and left_empty > 0:
            return [SHAPES['FIVE'], self_count]
        else:
            return [SHAPES['BLOCK_FIVE'], self_count]
    if no_empty_self_count == 4:
        # 注意这里的空位判断条件， 右边有有两种，分别是 XX空 和 XX空X,第二种情况下，虽然 right_empty 可能不是true，也是符合的，通过 one_empty_self_count > no_empty_self_count 来判断
        if ((right_empty >= 1 or right['one_empty_self_count'] > right['no_empty_self_count']) and
            (left_empty >= 1 or left['one_empty_self_count'] > left['no_empty_self_count'])):  # four
            return [SHAPES['FOUR'], self_count]
        elif not (right_empty == 0 and left_empty == 0):  # block four
            return [SHAPES['BLOCK_FOUR'], self_count]
    if one_empty_self_count == 4:
        return [SHAPES['BLOCK_FOUR'], self_count]
    # three
    if no_empty_self_count == 3:
        if (right_empty >= 2 and left_empty >= 1) or (right_empty >= 1 and left_empty >= 2):
            return [SHAPES['THREE'], self_count]
        else:
            return [SHAPES['BLOCK_THREE'], self_count]
    if one_empty_self_count == 3:
        if right_empty >= 1 and left_empty >= 1:
            return [SHAPES['THREE'], self_count]
        else:
            return [SHAPES['BLOCK_THREE'], self_count]
    if (no_empty_self_count == 2 or one_empty_self_count == 2) and total_length > 5:  # two
        shape = SHAPES['TWO']

    return [shape, self_count]

def is_five(shape):
    return shape == SHAPES['FIVE'] or shape == SHAPES['BLOCK_FIVE']

def is_four(shape):
    return shape == SHAPES['FOUR'] or shape == SHAPES['BLOCK_FOUR']

def get_all_shapes_of_point(shape_cache, x, y, role):
    roles = [role] if role else [1, -1]
    result = []
    for r in roles:
        for d in range(4):
            shape = shape_cache[r][d][x][y]
            if shape > 0:
                result.append(shape)
    return result


class GomokuPanel:
    """
    五子棋面板对象
    Keyword arguments:
    width -- 绘制宽度
    """

    def __init__(self, width: int):
        """初始化绘制对象"""
        self.width: int = width
        """ 绘制的最大宽度 """
        self.board_draw = [['┼' for _ in range(15)] for _ in range(15)]
        """ 棋盘绘制 """
        self.selected_row = -1
        """ 选中的行 """
        self.selected_col = -1
        """ 选中的列 """
        self.current_player = 'O'
        """ 当前玩家 """
        self.game_over = False
        """ 游戏是否结束 """
        # 初始化AI相关变量
        self.list1 = []  # AI的棋子位置
        self.list2 = []  # 人类玩家的棋子位置
        self.list3 = []  # 所有棋子的位置
        self.next_point = [0, 0]  # AI下一步最应该下的位置
        self.ratio = 1  # 进攻的系数
        self.DEPTH = 2  # 搜索深度
        self.last_player_move = None  # 记录玩家的上一步棋
        self.last_ai_move = None  # 记录AI的上一步棋

        # 玩家与NPC的角色数据
        self.pl_character_data = cache.character_data[0]
        self.target_character_data = cache.character_data[self.pl_character_data.target_character_id]

        # 选择AI难度
        self.choose_ai_difficulty()

        # 初始化AI
        self._minmax = self.factory() # ai判断
        self.vct = self.factory(True) # 三连判断
        self.vcf = self.factory(False, True) # 四连判断
        self.gomoku_cache = Gomoku_Cache()  # 放在这里，则minmax, vct和vcf会共用同一个缓存
        self.board_class = Gomoku_Board() # 棋盘类

    def choose_ai_difficulty(self):
        """选择AI难度"""
        line_draw = draw.LineDraw("-", self.width)
        line_draw.draw()
        line_feed.draw()
        target_ability_lv = self.target_character_data.ability[45]

        while 1:
            return_list = []
            low_button = draw.CenterButton(_("[低难度，计算速度快]"), _("低难度"), self.width / 3, cmd_func=self.set_ai_difficulty, args=(2,))
            low_button.draw()
            return_list.append(low_button.return_text)

            if target_ability_lv >= 4 or cache.debug_mode:
                medium_button = draw.CenterButton(_("[中难度，计算速度中等]"), _("中难度"), self.width / 3, cmd_func=self.set_ai_difficulty, args=(4,))
                medium_button.draw()
                return_list.append(medium_button.return_text)
            else:
                info_draw = draw.CenterDraw()
                info_draw.text = _("[中难度 - 需要{0}的{1}达到4级]".format(self.target_character_data.name, game_config.config_ability[45].name))
                info_draw.width = self.width / 3
                info_draw.draw()

            if target_ability_lv >= 6 or cache.debug_mode:
                high_button = draw.CenterButton(_("[高难度，计算速度慢]"), _("高难度"), self.width / 3, cmd_func=self.set_ai_difficulty, args=(6,))
                high_button.draw()
                return_list.append(high_button.return_text)
            else:
                info_draw = draw.CenterDraw()
                info_draw.text = _("[高难度 - 需要{0}的{1}达到6级]".format(self.target_character_data.name, game_config.config_ability[45].name))
                info_draw.width = self.width / 3
                info_draw.draw()

            line_feed.draw()

            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def set_ai_difficulty(self, depth: int):
        """设置AI难度"""
        self.DEPTH = depth

    def draw(self):
        """绘制对象"""
        title_draw = draw.TitleLineDraw(_("五子棋"), self.width)
        title_draw.draw()
        py_cmd.clr_cmd()

        self.choose_first_player()

        while 1:
            return_list = []
            line_draw = draw.LineDraw("-", self.width)
            line_draw.draw()

            # 绘制列按钮
            empty_col = "    "
            empty_draw = draw.NormalDraw()
            empty_draw.text = empty_col
            empty_draw.width = 4
            empty_draw.draw()
            for col in range(15):
                col_button = draw.CenterButton(f"[{col:2}]", f"col_{col}", 4, cmd_func=self.select_col, args=(col,))
                # 选中列高亮
                if self.selected_col == col:
                    col_button = draw.CenterButton(f"[{col:2}]", f"col_{col}", 4, cmd_func=self.select_col, args=(col), normal_style='gold_enrod')
                col_button.draw()
                return_list.append(col_button.return_text)
            line_feed.draw()

            # 绘制棋盘
            for row in range(15):
                # 绘制行按钮
                row_button = draw.LeftButton(f"[{row:2}]", f"row_{row}", 4, cmd_func=self.select_row, args=(row,))
                # 选中行高亮
                if self.selected_row == row:
                    row_button = draw.LeftButton(f"[{row:2}]", f"row_{row}", 4, cmd_func=self.select_row, args=(row), normal_style='gold_enrod')
                row_button.draw()
                return_list.append(row_button.return_text)

                # 绘制棋盘行
                row_cells = ''

                row_draw = draw.NormalDraw()
                for col in range(15):
                    cell = self.board_draw[row][col]
                    # 选中单元格高亮
                    if self.selected_col == col and self.selected_row == row:
                        row_cells += f"-[O]"
                    # 标识上一步棋
                    elif self.last_player_move == (row, col) or self.last_ai_move == (row, col):
                        row_cells += f"-'{cell}-"
                    else:
                        row_cells += f"--{cell}-"
                row_draw.text = row_cells
                row_draw.width = self.width - 4
                row_draw.draw()
                line_feed.draw()

            # 绘制确定按钮
            line_feed.draw()
            if not self.game_over and self.selected_row != -1 and self.selected_col != -1:
                confirm_button = draw.CenterButton(_("[确定]"), _("确定"), self.width / 2, cmd_func=self.place_piece)
                confirm_button.draw()
                return_list.append(confirm_button.return_text)

            if self.game_over:
                line_feed.draw()
                line_feed.draw()
                if self.current_player == 'O':
                    winner_name = self.pl_character_data.name
                    self.end_settle(0)
                else:
                    winner_name = self.target_character_data.name
                    self.end_settle(1)
                win_draw = draw.NormalDraw()
                win_draw.text = _("{0} 获胜!\n\n\n").format(winner_name)
                win_draw.width = self.width
                win_draw.draw()
                restart_button = draw.CenterButton(_("[再来一局]"), _("再来一局"), self.width / 2, cmd_func=self.reset_board)
                restart_button.draw()
                return_list.append(restart_button.return_text)

            back_draw = draw.CenterButton(_("[结束游戏]"), _("结束游戏"), self.width / 2)
            back_draw.draw()
            return_list.append(back_draw.return_text)
            yrn = flow_handle.askfor_all(return_list)
            if yrn == back_draw.return_text:
                cache.now_panel_id = constant.Panel.IN_SCENE
                break

    def end_settle(self, winner: int):
        """游戏结束结算"""

        from Script.Design import handle_instruct

        # 写入游戏类型与难度
        hard_level = self.DEPTH // 2
        self.pl_character_data.behavior.board_game_type = 1
        self.pl_character_data.behavior.board_game_ai_difficulty = hard_level

        # 结算状态
        if winner == 0:
            handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_PL_WIN_IN_BOARD_GAME, force_taget_wait = True)
        else:
            handle_instruct.chara_handle_instruct_common_settle(constant.CharacterStatus.STATUS_PL_LOSE_IN_BOARD_GAME, force_taget_wait = True)

    def choose_first_player(self):
        """选择先后手"""
        line_feed.draw()
        while 1:
            return_list = []
            first_button = draw.CenterButton(_("[玩家先手]"), _("玩家先手"), self.width / 2, cmd_func=self.set_first_player, args=('player',))
            first_button.draw()
            return_list.append(first_button.return_text)

            second_button = draw.CenterButton(_("[AI先手]"), _("AI先手"), self.width / 2, cmd_func=self.set_first_player, args=('ai',))
            second_button.draw()
            return_list.append(second_button.return_text)

            yrn = flow_handle.askfor_all(return_list)
            if yrn in return_list:
                break

    def set_first_player(self, first_player: str):
        """设置先后手"""
        if first_player == 'player':
            self.current_player = 'O'
        else:
            self.current_player = 'X'
            # AI先手，第一步下在(7, 7)
            self.board_draw[7][7] = self.current_player
            self.list1.append((7, 7))
            self.list3.append((7, 7))
            self.last_ai_move = (7, 7)
            self.current_player = 'O'

    def select_row(self, row: int):
        """选择行"""
        # 如果已经选中该行了，再次点击取消选中
        if self.selected_row == row:
            self.selected_row = -1
        else:
            self.selected_row = row

    def select_col(self, col: int):
        """选择列"""
        # 如果已经选中该列了，再次点击取消选中
        if self.selected_col == col:
            self.selected_col = -1
        else:
            self.selected_col = col

    def place_piece(self):
        """放置棋子"""
        if self.board_draw[self.selected_row][self.selected_col] == '┼':
            piece_type = 1 if self.current_player == 'O' else -1  # 假设'O'为玩家，类型为0；'X'为AI，类型为1
            self.board_draw[self.selected_row][self.selected_col] = self.current_player
            self.list2.append((self.selected_row, self.selected_col))
            self.list3.append((self.selected_row, self.selected_col))
            self.last_player_move = (self.selected_row, self.selected_col)
            self.board_class.put(self.selected_row, self.selected_col, piece_type)
            if self.check_winner(self.list2):
                self.game_over = True
            else:
                self.current_player = 'X'
                self.selected_row = -1
                self.selected_col = -1
                # 绘制等待信息
                info_draw = draw.NormalDraw()
                info_draw.text = _("\n{0}思考中...\n".format(self.target_character_data.name))
                info_draw.width = self.width
                info_draw.draw()
                self.ai_move()

    def factory(self, only_three=False, only_four=False):
        # depth 表示总深度，cDepth表示当前搜索深度
        def helper(board, role, depth, c_depth=0, path=None, alpha=-MAX, beta=MAX):
            board = self.board_class
            # print('depth:', depth, 'c_depth:', c_depth)
            if path is None:
                path = []
            CACHE_HITS['search'] += 1
            if c_depth >= depth or board.is_game_over():
                return [board.evaluate(role), None, path[:]]
            hash_value = board.hash()
            prev = self.gomoku_cache.get(hash_value)
            if prev and prev['role'] == role:
                if (abs(prev['value']) >= FIVE or prev['depth'] >= depth - c_depth) and prev['only_three'] == only_three and prev['only_four'] == only_four:
                    CACHE_HITS['hit'] += 1
                    return [prev['value'], prev['move'], path + prev['path']]
            value = -MAX
            move = None
            best_path = path[:]  # Copy the current path
            best_depth = 0
            points = board.get_valuable_moves(role, c_depth, only_three or c_depth > only_three_threshold, only_four)
            # if c_depth == 0:
            #     print('points:', points)
            # board.display(points)
            if not points:
                # points = board.get_valid_moves(role)
                return [board.evaluate(role), None, path[:]]
            for d in range(c_depth + 1, depth + 1):
                # 迭代加深过程中只找己方能赢的解，因此只搜索偶数层即可
                if d % 2 != 0:
                    continue
                break_all = False
                for point in points:
                    board.put(point[0], point[1], role)
                    new_path = path + [point]  # Add current move to path
                    current_value, current_move, current_path = helper(board, -role, d, c_depth + 1, new_path, -beta, -alpha)
                    current_value = -current_value
                    board.undo()
                    # 迭代加深的过程中，除了能赢的棋，其他都不要
                    # 原因是：除了必胜的，其他评估不准。比如必输的棋，由于走的步数偏少，也会变成没有输，比如 5步之后输了，但是1步肯定不会输，这时候1步的分数是不准确的，显然不能选择。
                    if current_value >= FIVE or d == depth:
                        # 必输的棋，也要挣扎一下，选择最长的路径
                        if (current_value > value) or (current_value <= -FIVE and value <= -FIVE and len(current_path) > best_depth):
                            value = current_value
                            move = point
                            best_path = current_path
                            best_depth = len(current_path)
                    alpha = max(alpha, value)
                    if alpha >= FIVE:  # 自己赢了也结束，但是对方赢了还是要继续搜索的
                        break_all = True
                        break
                    if alpha >= beta:
                        break
                if break_all:
                    break
            # 缓存
            if (c_depth < only_three_threshold or only_three or only_four) and (not prev or prev['depth'] < depth - c_depth):
                CACHE_HITS['total'] += 1
                self.gomoku_cache.put(hash_value, {
                    'depth': depth - c_depth,  # 剩余搜索深度
                    'value': value,
                    'move': move,
                    'role': role,
                    'path': best_path[c_depth:],  # 剩余搜索路径
                    'only_three': only_three,
                    'only_four': only_four,
                })
            return [value, move, best_path]
        return helper

    def minmax(self, board, role, depth=4, enable_vct=True):
        board = self.board_class
        if enable_vct:
            vct_depth = depth + 4
            # 先看自己有没有杀棋
            value, move, best_path = self.vct(board, role, vct_depth)
            if value >= FIVE:
                return [value, move, best_path]
            value, move, best_path = self._minmax(board, role, depth)
            # 假设对方有杀棋，先按自己的思路走，走完之后看对方是不是还有杀棋
            # 如果对方没有了，那么就说明走的是对的
            # 如果对方还是有，那么要对比对方的杀棋路径和自己没有走棋时的长短
            # 如果走了棋之后路径变长了，说明走的是对的
            # 如果走了棋之后，对方杀棋路径长度没变，甚至更短，说明走错了，此时就优先封堵对方
            if move is not None:
                board.put(move[0], move[1], role)
                value2, move2, best_path2 = self.vct(board.reverse(), role, vct_depth)
                board.undo()
                if value < FIVE and value2 == FIVE and len(best_path2) > len(best_path):
                    value3, move3, best_path3 = self.vct(board.reverse(), role, vct_depth)
                    if len(best_path2) <= len(best_path3):
                        return [value, move2, best_path2]  # value2 是被挡住的，所以这里还是用value
            # print('value:', value, 'move:', move, 'best_path:', best_path)
            if move is None:
                valid_moves = board.get_valid_moves()
                if valid_moves:
                    move = valid_moves[0]
            return [value, move, best_path]
        else:
            value, move, best_path = self._minmax(board, role, depth)
            if move is None:
                # 如果没有找到合适的移动，返回一个默认的有效移动
                print("因为没有找到合适的移动，返回一个默认的有效移动")
                valid_moves = board.get_valid_moves()
                if valid_moves:
                    move = valid_moves[0]
            return [value, move, best_path]


    def ai_move(self):
        """AI 使用算法选择棋子位置"""
        x, y = self.ai()
        self.board_draw[x][y] = self.current_player
        self.list1.append((x, y))
        self.list3.append((x, y))
        self.last_ai_move = (x, y)
        piece_type = 1 if self.current_player == 'O' else -1  # 假设'O'为玩家，类型为1；'X'为AI，类型为-1
        self.board_class.put(x, y, piece_type)

        if self.check_winner(self.list1):
            self.game_over = True
        else:
            self.current_player = 'O'

    def check_winner(self, lst) -> bool:
        """检查是否有玩家获胜"""
        return check_winner(lst, COLUMN, ROW)

    def reset_board(self):
        """重置棋盘"""
        self.board_draw = [['┼' for _ in range(15)] for _ in range(15)]
        self.current_player = 'O'
        self.selected_row = -1
        self.selected_col = -1
        self.last_ai_move = None
        self.last_player_move = None
        self.game_over = False
        self.list1.clear()
        self.list2.clear()
        self.list3.clear()
        self.board_class = Gomoku_Board()
        self.choose_ai_difficulty()
        self.choose_first_player()

    def ai(self):
        """AI决策，返回下一步位置"""
        ai_role = 1 if self.current_player == 'O' else -1  # 假设'O'为玩家，类型为0；'X'为AI，类型为1
        _, move, _ = self.minmax(self, ai_role, depth=self.DEPTH)
        # print('move:', move)
        self.next_point[0], self.next_point[1] = move

        return self.next_point[0], self.next_point[1]
