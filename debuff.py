# debuff.py
import random
from enum import Enum
from collections import deque

# maze.py에서 쓰는 방향 비트 재사용을 위해 import 없이 상수만 복사해도 됨
N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {N: S, S: N, E: W, W: E}

class DebuffType(Enum):
    SLOW = "SLOW"           # 플레이어 속도 감소
    WALL_SHIFT = "WALL_SHIFT"  # 맵 구조 주기적 변경

class DebuffItem:
    def __init__(self, gx, gy, dtype: DebuffType):
        self.gx = gx
        self.gy = gy
        self.dtype = dtype

class DebuffState:
    def __init__(self):
        self.slow_until_ms = 0
        self.wallshift_until_ms = 0
        self.wallshift_interval_ms = 1200
        self._last_shift_ms = 0
        self.slow_multiplier = 0.5  # 기본 속도의 50%

    def is_slow(self, now_ms):
        return now_ms < self.slow_until_ms

    def is_wallshift(self, now_ms):
        return now_ms < self.wallshift_until_ms

    def time_left(self, now_ms, until_ms):
        return max(0, int((until_ms - now_ms)/1000))

# ===== 경로 유지 확인용 BFS =====
def has_path(grid, w, h, sx, sy, gx, gy):
    q = deque()
    q.append((sx, sy))
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
                    q.append((nx, ny))
                    seen[ny][nx] = True
    return False

# ===== 벽 토글(양방향 동기화) =====
def _toggle_passage(grid, x, y, d):
    """벽이 있으면 열고, 통로면 닫음. 반대쪽 셀도 동기화."""
    w, h = len(grid[0]), len(grid)
    nx, ny = x + DX[d], y + DY[d]
    if not (0 <= nx < w and 0 <= ny < h):
        return False
    # 통로면 닫기, 벽이면 열기
    if (grid[y][x] & d) and (grid[ny][nx] & OPPOSITE[d]):
        grid[y][x] &= ~d
        grid[ny][nx] &= ~OPPOSITE[d]
    else:
        grid[y][x] |= d
        grid[ny][nx] |= OPPOSITE[d]
    return True

# ===== 맵 변형: 한 곳은 닫고(가능하면), 다른 곳은 열어서 난이도 유지 =====
def mutate_maze_preserving_path(grid, w, h, start, goal, rng):
    sx, sy = start
    gx, gy = goal

    # 1) 이미 열린 통로를 하나 골라 닫아보기 (경로 유지되면 확정)
    candidates_open = []
    for y in range(h):
        for x in range(w):
            cell = grid[y][x]
            for d in (N, S, E, W):
                nx, ny = x + DX[d], y + DY[d]
                if 0 <= nx < w and 0 <= ny < h:
                    if (cell & d) and (grid[ny][nx] & OPPOSITE[d]):
                        # 통로
                        # 양쪽 중복 방지: 오른쪽/아래쪽만 대표로 처리
                        if d in (E, S):
                            candidates_open.append((x, y, d))
    rng.shuffle(candidates_open)

    closed_one = False
    snapshot = [row[:] for row in grid]  # 실패 시 롤백용

    for (x, y, d) in candidates_open:
        # 닫아보고
        _toggle_passage(grid, x, y, d)
        if has_path(grid, w, h, sx, sy, gx, gy):
            closed_one = True
            break
        else:
            # 경로 깨짐 → 롤백
            for j in range(h):
                grid[j] = snapshot[j][:]
    # 2) 벽을 하나 열기 (언제나 가능)
    candidates_wall = []
    for y in range(h):
        for x in range(w):
            cell = grid[y][x]
            for d in (N, S, E, W):
                nx, ny = x + DX[d], y + DY[d]
                if 0 <= nx < w and 0 <= ny < h:
                    # 벽(양쪽 다 막힘)만 후보
                    if not (cell & d) and not (grid[ny][nx] & OPPOSITE[d]):
                        if d in (E, S):
                            candidates_wall.append((x, y, d))
    if candidates_wall:
        x, y, d = rng.choice(candidates_wall)
        _toggle_passage(grid, x, y, d)

    return closed_one  # 정보용 반환

# ===== 출발지점 인접 랜덤 스폰 =====
def spawn_debuff_near_start(grid, w, h, rng, start=(0,0)):
    sx, sy = start
    neighbors = []
    cell = grid[sy][sx]
    for d in (N, S, E, W):
        nx, ny = sx + DX[d], sy + DY[d]
        if 0 <= nx < w and 0 <= ny < h:
            # 출발지점에서 실제로 이동 가능한 방향만 후보
            if cell & d:
                neighbors.append((nx, ny))
    if not neighbors:
        # 혹시 출발이 사방막힘이면 임의로 (0,1) 같은 유효칸 배치
        if h > 1:
            neighbors = [(0, 1)]
        elif w > 1:
            neighbors = [(1, 0)]
        else:
            neighbors = [(0, 0)]
    gx, gy = rng.choice(neighbors)
    dtype = rng.choice([DebuffType.SLOW, DebuffType.WALL_SHIFT])
    return DebuffItem(gx, gy, dtype)

# ===== 매 프레임 갱신 =====
def update_debuffs(now_ms, state: DebuffState, grid, w, h, start, goal, rng):
    # WALL_SHIFT가 켜져 있으면 일정 간격으로 맵 변형
    if state.is_wallshift(now_ms):
        if now_ms - state._last_shift_ms >= state.wallshift_interval_ms:
            mutate_maze_preserving_path(grid, w, h, start, goal, rng)
            state._last_shift_ms = now_ms
