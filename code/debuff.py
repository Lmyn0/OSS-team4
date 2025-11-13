import random
from enum import Enum
from collections import deque

N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {N: S, S: N, E: W, W: E}

class DebuffType(Enum):
    SLOW = "SLOW"           # 플레이어 속도 감소
    REVERSE = "REVERSE"     # 조작 반전
    TIME_LEFT = "TIME_LEFT" # 남은 게임 시간 차감

class DebuffItem:
    def __init__(self, gx, gy, dtype: DebuffType):
        self.gx = gx
        self.gy = gy
        self.dtype = dtype

class DebuffState:
    def __init__(self):
        self.slow_until_ms = 0
        self.reverse_until_ms = 0
        self.slow_multiplier = 0.5  # 기본 속도의 50%

    def is_slow(self, now_ms):
        return now_ms < self.slow_until_ms

    def is_reverse(self, now_ms):
        return now_ms < self.reverse_until_ms

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
    dtype = rng.choice([DebuffType.SLOW, DebuffType.TIME_LEFT, DebuffType.REVERSE])
    return DebuffItem(gx, gy, dtype)

# ===== 아이템 픽업 시 효과 적용 =====
def apply_debuff_on_pickup(now_ms, state: DebuffState, item: DebuffItem,
                           remaining_time_ms: int, penalty_ms: int = 5_000):
    """
    - SLOW/REVERSE: 남은 지속시간이 있으면 연장되도록 처리
    - TIME_PENALTY: 남은 전체 시간에서 penalty_ms 차감하여 반환
    반환값: 갱신된 remaining_time_ms
    """
    if item.dtype == DebuffType.SLOW:
        base = max(now_ms, state.slow_until_ms)
        state.slow_until_ms = base + state.slow_duration_ms
        return remaining_time_ms

    if item.dtype == DebuffType.REVERSE:
        base = max(now_ms, state.reverse_until_ms)
        state.reverse_until_ms = base + state.reverse_duration_ms
        return remaining_time_ms

    if item.dtype == DebuffType.TIME_LEFT:
        return max(0, remaining_time_ms - penalty_ms)

    return remaining_time_ms