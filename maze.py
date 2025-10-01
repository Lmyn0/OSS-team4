"""
Kruskal 알고리즘을 사용한 미로 생성

Usage:
    python maze_pygame.py --width 20 --height 15 --seed 12345 --delay 0.01 --cell 24
"""

import sys
import argparse
import random
import time
import pygame

def draw_button(screen, rect, text, font, color=(200,200,200), text_color=(0,0,0)):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0,0,0), rect, 2)  # 테두리
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def menu():
    pygame.init()
    screen = pygame.display.set_mode((600,400))
    pygame.display.set_caption("미로 게임 - 난이도 선택")

    font = pygame.font.SysFont("malgungothic", 25)

    button1 = pygame.Rect(200, 120, 200, 70)
    button2 = pygame.Rect(200, 220, 200, 70)

    while True:
        screen.fill((255, 255, 255))
        draw_button(screen, button1, "난이도 : 쉬움", font)
        draw_button(screen, button2, "난이도 : 어려움",font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button1.collidepoint(event.pos):
                    return 1
                elif button2.collidepoint(event.pos):
                    return 2
# 방향
N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {E: W, W: E, N: S, S: N}

# --- union-find 트리 ---
class Tree:
    def __init__(self):
        self.parent = None

    def root(self):
        return self.parent.root() if self.parent else self

    def connected(self, other):
        return self.root() is other.root()

    def connect(self, other):
        # 다른 트리의 루트를 자기 자신에 연결
        other.root().parent = self

# --- Kruscal 알고리즘을 통한 미로 생성 ---
def generate_maze(width, height, seed, step_callback=None):
    rand = random.Random(seed)
    grid = [[0 for _ in range(width)] for _ in range(height)]
    sets = [[Tree() for _ in range(width)] for _ in range(height)]

    edges = []
    for y in range(height):
        for x in range(width):
            if y > 0:
                edges.append((x, y, N))
            if x > 0:
                edges.append((x, y, W))

    rand.shuffle(edges)

    while edges:
        x, y, direction = edges.pop()
        nx, ny = x + DX[direction], y + DY[direction]
        set1, set2 = sets[y][x], sets[ny][nx]

        if not set1.connected(set2):
            if step_callback:
                step_callback(grid, width, height)

            set1.connect(set2)
            grid[y][x] |= direction
            grid[ny][nx] |= OPPOSITE[direction]
            
            if step_callback:
                step_callback(grid, width, height)

    # 최종 상태 콜백
    if step_callback:
        step_callback(grid, width, height)
    return grid

# --- Pygame을 통해 미로 그리기 ---
def draw_maze(surface, grid, width, height, cell, wall_thickness=2):
    surface.fill((255, 255, 255))  # 흰색
    # 외각 크기
    w_px = width * cell
    h_px = height * cell

    # 벽 : 검은색 선, 벽이 없는 부분 : 길
    for y in range(height):
        for x in range(width):
            cx = x * cell
            cy = y * cell
            cell_bits = grid[y][x]

            # 위쪽 벽
            if not (cell_bits & N):
                pygame.draw.line(surface, (0,0,0), (cx, cy), (cx + cell, cy), wall_thickness)
            # 왼쪽 벽
            if not (cell_bits & W):
                pygame.draw.line(surface, (0,0,0), (cx, cy), (cx, cy + cell), wall_thickness)
            # 아래쪽 벽
            if not (cell_bits & S):
                pygame.draw.line(surface, (0,0,0), (cx, cy + cell), (cx + cell, cy + cell), wall_thickness)
            # 오른쪽 벽
            if not (cell_bits & E):
                pygame.draw.line(surface, (0,0,0), (cx + cell, cy), (cx + cell, cy + cell), wall_thickness)


    pygame.display.get_surface().blit(surface, (0,0))
    pygame.display.flip()
# --- 메인 실행 ---
def main():
    mode = menu()

    if mode == 1:
        default_width = 15
        default_height = 15
        default_cell = 40
    elif mode == 2:
        default_width = 20
        default_height = 20
        default_cell = 30

    parser = argparse.ArgumentParser()
    parser.add_argument('--width', type=int, default=default_width)
    parser.add_argument('--height', type=int)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--delay', type=float, default=0,
                        help='벽 생성 사이 대기 시간(초)')
    parser.add_argument('--cell', type=int, default=default_cell, help='셀의 픽셀 크기')
    args = parser.parse_args()

    width = args.width
    height = args.height if args.height is not None else width
    seed = args.seed if args.seed is not None else random.randrange(0, 0xFFFF_FFFF)
    delay = args.delay
    cell = args.cell

    pygame.init()
    caption = f'Kruskal Maze ({width}x{height}) seed={seed}'
    pygame.display.set_caption(caption)

    screen_w = width * cell
    screen_h = height * cell
    screen = pygame.display.set_mode((screen_w, screen_h))
    surface = pygame.Surface((screen_w, screen_h))

    clock = pygame.time.Clock()

    
    def step_callback(grid, w, h):
        draw_maze(surface, grid, w, h, cell)
        # 그리기 + 창 응답성 유지
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        ms = int(delay * 1000)
        if ms > 0:
            pygame.time.delay(ms)

    # 최초 미로 생성 및 표시
    grid = generate_maze(width, height, seed, step_callback=step_callback)

    # 최종 미로 표시시
    draw_maze(surface, grid, width, height, cell)

    #N : 새로운 미로 생성 / Q,ESC : 종료
    info_font = pygame.font.SysFont("malgungothic", 20)
    info_text = f"(N: 미로 재생성, Q/ESC: 종료)"
    finished = True

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    return
                elif ev.key == pygame.K_n:
                    seed = random.randrange(0, 0xFFFF_FFFF)
                    pygame.display.set_caption(f'Kruskal Maze ({width}x{height}) seed={seed}')
                    grid = generate_maze(width, height, seed, step_callback=step_callback)
                    draw_maze(surface, grid, width, height, cell)

# --- 메인 실행 ---
        screen.blit(surface, (0,0))
        info_surf = info_font.render(info_text, True, (0,0,0))
        screen.blit(info_surf, (4, 4))
        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    main()