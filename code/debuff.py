# debuff.py
import random
from enum import Enum
from collections import deque

# 방향 비트
N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {N: S, S: N, E: W, W: E}

class DebuffType(Enum):
    SLOW = "SLOW"             # 속도 감소
    WALL_SHIFT = "WALL_SHIFT" # 맵 구조 주기적 변경
    REVERSE = "REVERSE"       # 조작 반전
    TIME_LEFT = "TIME_LEFT"   # 남은 시간 차감(선택적)

class DebuffItem:
    def __init__(self, gx, gy, dtype: DebuffType):
        self.gx = gx
        self.gy = gy
        self.dtype = dtype

class DebuffState:
    def __init__(self):
        self.slow_until_ms = 0
        self.reverse_until_ms = 0
        self.wallshift_until_ms = 0
        self.wallshift_interval_ms = 1200
        self._last_shift_ms = 0
        self.slow_multiplier = 0.5  # 기본 속도의 50%
        self.wallshift_permanent = False  # ★ 게임 끝까지 지속

    def is_slow(self, now_ms):        return now_ms < self.slow_until_ms
    def is_reverse(self, now_ms):     return now_ms < self.reverse_until_ms
    def is_wallshift(self, now_ms):   return self.wallshift_permanent or (now_ms < self.wallshift_until_ms)

    def time_left(self, now_ms, until_ms):
        return max(0, int((until_ms - now_ms)/1000))

# ===== 경로 유지 확인용 BFS =====
def has_path(grid, w, h, sx, sy, gx, gy):
    q = deque([(sx, sy)])
    seen = [[False]*w for _ in range(h)]
    seen[sy][sx] = True
    while q:
        x, y = q.popleft()
        if (x, y) == (gx, gy):
            return True
        cell = grid[y][x]
        for d in (N, S, E, W):
            if cell & d:
                nx, ny = x + DX[d], y + DY[d]
                if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                    seen[ny][nx] = True
                    q.append((nx, ny))
    return False

# ===== 벽 토글(양방향 동기화) =====
def _toggle_passage(grid, x, y, d):
    w, h = len(grid[0]), len(grid)
    nx, ny = x + DX[d], y + DY[d]
    if not (0 <= nx < w and 0 <= ny < h): return False
    if (grid[y][x] & d) and (grid[ny][nx] & OPPOSITE[d]):
        grid[y][x] &= ~d
        grid[ny][nx] &= ~OPPOSITE[d]
    else:
        grid[y][x] |= d
        grid[ny][nx] |= OPPOSITE[d]
    return True

# ===== 맵 변형(경로 보장) =====
def mutate_maze_preserving_path(grid, w, h, start, goal, rng):
    sx, sy = start
    gx, gy = goal

    # 1) 열린 통로 하나 닫아보기(경로 유지되면 확정)
    candidates_open = []
    for y in range(h):
        for x in range(w):
            cell = grid[y][x]
            for d in (N, S, E, W):
                nx, ny = x + DX[d], y + DY[d]
                if 0 <= nx < w and 0 <= ny < h:
                    if (cell & d) and (grid[ny][nx] & OPPOSITE[d]) and d in (E, S):
                        candidates_open.append((x, y, d))
    rng.shuffle(candidates_open)
    snapshot = [row[:] for row in grid]
    for (x, y, d) in candidates_open:
        _toggle_passage(grid, x, y, d)  # 닫기
        if has_path(grid, w, h, sx, sy, gx, gy):
            break
        # 경로 깨졌으면 롤백하고 다른 후보 시도
        for j in range(h):
            grid[j] = snapshot[j][:]

    # 2) 벽 하나 열기
    candidates_wall = []
    for y in range(h):
        for x in range(w):
            cell = grid[y][x]
            for d in (N, S, E, W):
                nx, ny = x + DX[d], y + DY[d]
                if 0 <= nx < w and 0 <= ny < h:
                    if not (cell & d) and not (grid[ny][nx] & OPPOSITE[d]) and d in (E, S):
                        candidates_wall.append((x, y, d))
    if candidates_wall:
        x, y, d = rng.choice(candidates_wall)
        _toggle_passage(grid, x, y, d)

# ===== 출발지점 인접 랜덤 스폰 =====
def spawn_debuff_near_start(grid, w, h, rng, start=(0,0)):
    sx, sy = start
    neighbors = []
    cell = grid[sy][sx]
    for d in (N, S, E, W):
        nx, ny = sx + DX[d], sy + DY[d]
        if 0 <= nx < w and 0 <= ny < h and (cell & d):
            neighbors.append((nx, ny))
    if not neighbors:
        neighbors = [(0, 1)] if h > 1 else ([(1, 0)] if w > 1 else [(0, 0)])
    gx, gy = rng.choice(neighbors)

    # 세 가지 중 하나 랜덤
    dtype = rng.choice([DebuffType.SLOW, DebuffType.WALL_SHIFT, DebuffType.REVERSE])
    return DebuffItem(gx, gy, dtype)

# ===== 매 프레임 갱신 =====
def update_debuffs(now_ms, state: DebuffState, grid, w, h, start, goal, rng):
    if state.is_wallshift(now_ms):
        if now_ms - state._last_shift_ms >= state.wallshift_interval_ms:
            mutate_maze_preserving_path(grid, w, h, start, goal, rng)
            state._last_shift_ms = now_ms

# ===== 남은 시간 차감 헬퍼(선택) =====
def apply_debuff_on_pickup(now_ms, state: DebuffState, item: DebuffItem,
                           remaining_time_ms: int, penalty_ms: int) -> int:
    """TIME_LEFT 아이템을 밟았을 때 남은 시간(ms)을 차감하고 결과를 반환"""
    if item.dtype is DebuffType.TIME_LEFT:
        remaining_time_ms = max(0, remaining_time_ms - penalty_ms)
    return remaining_time_ms
