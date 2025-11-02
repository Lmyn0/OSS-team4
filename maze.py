# maze.py
import random
import pygame

# 방향 상수 및 보조 테이블
N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {E: W, W: E, N: S, S: N}

WINDOW_BG = (255, 255, 255)
WALL_COLOR = (0, 0, 0)

# --- union-find 트리 ---
class _Tree:
    def __init__(self):
        self.parent = None
    def root(self):
        return self.parent.root() if self.parent else self
    def connected(self, other):
        return self.root() is other.root()
    def connect(self, other):
        other.root().parent = self

def generate_maze(width, height, seed=None, step_callback=None):
    """Kruskal 알고리즘으로 미로 생성. 셀 비트에 열린 방향을 기록."""
    rand = random.Random(seed)
    grid = [[0 for _ in range(width)] for _ in range(height)]
    sets = [[_Tree() for _ in range(width)] for _ in range(height)]

    edges = []
    for y in range(height):
        for x in range(width):
            if y > 0: edges.append((x, y, N))
            if x > 0: edges.append((x, y, W))
    rand.shuffle(edges)

    while edges:
        x, y, d = edges.pop()
        nx, ny = x + DX[d], y + DY[d]
        a, b = sets[y][x], sets[ny][nx]
        if not a.connected(b):
            if step_callback: step_callback(grid, width, height)
            a.connect(b)
            grid[y][x]     |= d
            grid[ny][nx]   |= OPPOSITE[d]
            if step_callback: step_callback(grid, width, height)

    if step_callback: step_callback(grid, width, height)
    return grid

def draw_maze(surface, grid, width, height, cell, wall_thickness=2):
    """셀 비트(N,S,E,W) 기준으로 벽/길 그리기"""
    surface.fill(WINDOW_BG)
    for y in range(height):
        for x in range(width):
            cx, cy = x * cell, y * cell
            bits = grid[y][x]
            if not (bits & N):
                pygame.draw.line(surface, WALL_COLOR, (cx, cy), (cx + cell, cy), wall_thickness)
            if not (bits & W):
                pygame.draw.line(surface, WALL_COLOR, (cx, cy), (cx, cy + cell), wall_thickness)
            if not (bits & S):
                pygame.draw.line(surface, WALL_COLOR, (cx, cy + cell), (cx + cell, cy + cell), wall_thickness)
            if not (bits & E):
                pygame.draw.line(surface, WALL_COLOR, (cx + cell, cy), (cx + cell, cy + cell), wall_thickness)
