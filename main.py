# main.py
"""
Usage:
  python main.py --width 20 --height 15 --seed 12345 --delay 0.01 --cell 24
"""
import sys
import argparse
import random
import pygame

from maze import N, S, E, W, generate_maze, draw_maze
from player import Player
from difficulty import select_difficulty

INFO_FONT_NAME = "malgungothic"
INFO_FONT_SIZE = 20

def parse_args(default_w, default_h, default_cell):
    p = argparse.ArgumentParser()
    p.add_argument('--width',  type=int, default=default_w)
    p.add_argument('--height', type=int)             # 기본: width와 동일
    p.add_argument('--seed',   type=int, default=None)
    p.add_argument('--delay',  type=float, default=0.0, help='벽 생성 사이 대기 시간(초)')
    p.add_argument('--cell',   type=int, default=default_cell, help='셀 픽셀 크기')
    return p.parse_args()

def main():
    # 난이도 선택 -> 기본값 세팅
    diff = select_difficulty()

    args   = parse_args(diff.width, diff.height, diff.cell)
    width  = args.width
    height = args.height if args.height is not None else width
    seed   = args.seed if args.seed is not None else random.randrange(0, 0xFFFF_FFFF)
    delay  = args.delay
    cell   = args.cell

    pygame.init()
    pygame.display.set_caption(f'Kruskal Maze ({width}x{height}) seed={seed}')
    screen_w, screen_h = width * cell, height * cell
    screen  = pygame.display.set_mode((screen_w, screen_h))
    surface = pygame.Surface((screen_w, screen_h))
    clock   = pygame.time.Clock()

    try:
        info_font = pygame.font.SysFont(INFO_FONT_NAME, INFO_FONT_SIZE)
    except:
        info_font = pygame.font.SysFont(None, INFO_FONT_SIZE)
    info_text = "(N: 미로 재생성, Q/ESC: 종료, 방향키: 이동)"

    # 생성 과정 시각화용 콜백
    def step_callback(grid, w, h):
        draw_maze(surface, grid, w, h, cell)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
        if delay > 0:
            pygame.time.delay(int(delay * 1000))
        screen.blit(surface, (0, 0))
        pygame.display.flip()

    # 최초 미로 생성
    grid = generate_maze(width, height, seed, step_callback=step_callback)
    player = Player(0, 0)

    # 메인 루프
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); return
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); return
                if ev.key == pygame.K_n:
                    seed = random.randrange(0, 0xFFFF_FFFF)
                    pygame.display.set_caption(f'Kruskal Maze ({width}x{height}) seed={seed}')
                    grid = generate_maze(width, height, seed, step_callback=step_callback)
                    player = Player(0, 0)
                elif ev.key == pygame.K_UP:    player.move(grid, N)
                elif ev.key == pygame.K_DOWN:  player.move(grid, S)
                elif ev.key == pygame.K_LEFT:  player.move(grid, W)
                elif ev.key == pygame.K_RIGHT: player.move(grid, E)

        draw_maze(surface, grid, width, height, cell)
        player.draw(surface, cell)

        info_surf = info_font.render(info_text, True, (0, 0, 0))
        surface.blit(info_surf, (10, 10))

        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
