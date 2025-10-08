"""
Kruskal's Maze Generation with Pygame 🛠️

개발자: [OSS_TEAM4]
최종 업데이트: 2024년 10월 8일

이 코드는 Kruskal 알고리즘 (MST 최소 신장 트리)을 이용해 미로를 생성한다.
각 셀을 하나의 집합으로 보고, 벽을 무작위로 허물면서 두 집합이 연결되지 않았을 때만 합친다.

Usage:
    python maze_pygame.py --width 20 --height 15 --seed 12345 --delay 0.01 --cell 24
"""

import sys
import argparse
import random
import time
import pygame

# -----------------
# 🚀 기본 설정 상수
# -----------------
# 각 비트가 벽의 방향을 나타냄 (N/S/E/W)
N, S, E, W = 1, 2, 4, 8

# 방향별 좌표 변화량 (델타)
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}

# 반대 방향 맵. 벽을 허물 때 상대방 셀도 업데이트 해야 함.
OPPOSITE = {E: W, W: E, N: S, S: N}


# -----------------------------
# 🌳 Union-Find (Disjoint Set) 클래스
# -----------------------------
# Kruskal 알고리즘의 핵심. 두 셀이 이미 연결되었는지 확인하는 용도.
class DisjointSet:
    def __init__(self):
        # 처음에는 부모가 자기 자신 (자기 집합의 대표 원소)
        self.parent = self

    # 자기 집합의 루트(대표 원소)를 찾는다. (경로 압축 최적화 적용)
    def find_root(self):
        # 만약 부모가 자기 자신이 아니라면, 재귀적으로 루트를 찾는다.
        if self.parent != self:
            self.parent = self.parent.find_root() # 경로 압축!
        return self.parent

    # 두 셀이 같은 집합에 속하는지 확인
    def is_connected(self, other):
        return self.find_root() is other.find_root()

    # 두 집합을 연결한다 (Union)
    def union_sets(self, other):
        # 각 집합의 루트를 찾아서, 한 쪽 루트를 다른 쪽 루트의 자식으로 만든다.
        # (랭크나 크기 최적화는 생략하고 간단하게 구현)
        root1 = self.find_root()
        root2 = other.find_root()
        
        if root1 != root2:
            root2.parent = root1 # root1에 root2를 연결


# --------------------------
# 🎨 Pygame UI/드로잉 함수
# --------------------------
def draw_button(screen, rect, text, font, color=(200,200,200), text_color=(0,0,0)):
    # 버튼 배경과 테두리를 그린다
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0,0,0), rect, 2)
    
    # 텍스트를 렌더링하고 버튼 중앙에 배치한다
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def menu():
    # 메뉴도 독립적인 창이므로 여기서 간단히 처리
    pygame.init()
    screen = pygame.display.set_mode((600,400))
    pygame.display.set_caption("미로 생성기 - 난이도 선택")

    font = pygame.font.SysFont("malgungothic", 25)

    # 버튼 좌표 설정
    button_easy = pygame.Rect(200, 120, 200, 70)
    button_hard = pygame.Rect(200, 220, 200, 70)

    while True:
        screen.fill((255, 255, 255))
        draw_button(screen, button_easy, "쉬움 (15x15)", font)
        draw_button(screen, button_hard, "어려움 (20x20)", font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_easy.collidepoint(event.pos):
                    return 1 # 쉬움 선택
                elif button_hard.collidepoint(event.pos):
                    return 2 # 어려움 선택


def draw_maze(surface, grid, width, height, cell_size, wall_thickness=2):
    """
    미로의 현재 상태를 Pygame surface에 그린다.
    grid 배열의 비트 정보를 읽어서 벽을 그릴지 말지 결정한다.
    """
    surface.fill((255, 255, 255))  # 바탕은 흰색

    # 벽을 그린다 (미로의 외곽선 포함)
    for y in range(height):
        for x in range(width):
            cx = x * cell_size
            cy = y * cell_size
            cell_bits = grid[y][x]

            # 상, 좌, 하, 우 순서로 벽을 검사하며 그린다.
            # 중요한 점: Kruskal 미로는 '길'이 없다는 의미로 벽을 그리는 방식!

            # 1. 위쪽 벽 (N): N 방향 길이 없다면 벽을 그린다. (y=0 행은 무조건 그려짐)
            if not (cell_bits & N):
                pygame.draw.line(surface, (0,0,0), (cx, cy), (cx + cell_size, cy), wall_thickness)
            
            # 2. 왼쪽 벽 (W): W 방향 길이 없다면 벽을 그린다. (x=0 열은 무조건 그려짐)
            if not (cell_bits & W):
                pygame.draw.line(surface, (0,0,0), (cx, cy), (cx, cy + cell_size), wall_thickness)
            
            # 3. 아래쪽 벽 (S): y=height-1 행에 도달하면 무조건 벽을 그린다.
            #    미로 생성 과정에서 S 비트가 켜지지 않은 경우에도 벽을 그린다.
            if y == height - 1 or not (cell_bits & S):
                pygame.draw.line(surface, (0,0,0), (cx, cy + cell_size), (cx + cell_size, cy + cell_size), wall_thickness)
            
            # 4. 오른쪽 벽 (E): x=width-1 열에 도달하면 무조건 벽을 그린다.
            #    미로 생성 과정에서 E 비트가 켜지지 않은 경우에도 벽을 그린다.
            if x == width - 1 or not (cell_bits & E):
                pygame.draw.line(surface, (0,0,0), (cx + cell_size, cy), (cx + cell_size, cy + cell_size), wall_thickness)


    pygame.display.get_surface().blit(surface, (0,0))
    pygame.display.flip()


# --------------------------
# 🏗️ Kruskal 알고리즘 구현
# --------------------------
def generate_maze(width, height, seed, step_callback=None):
    """
    Kruskal 알고리즘을 사용해 미로 그리드 데이터를 생성한다.
    """
    # 시드 고정. 랜덤성은 이 객체에 의존한다.
    prng = random.Random(seed)
    
    # 0으로 초기화된 미로 격자. 각 셀은 연결된 벽의 방향 비트 정보를 가짐.
    grid = [[0 for _ in range(width)] for _ in range(height)]
    
    # 모든 셀에 대해 DisjointSet 객체를 할당. 처음엔 모든 셀이 독립적인 집합.
    sets = [[DisjointSet() for _ in range(width)] for _ in range(height)]

    # 모든 가능한 벽(간선) 리스트를 만든다. (오른쪽 및 아래쪽 벽만 고려)
    edges = []
    for y in range(height):
        for x in range(width):
            # 위쪽 벽 (N) -> y > 0인 경우만 해당
            if y > 0:
                edges.append((x, y, N))
            # 왼쪽 벽 (W) -> x > 0인 경우만 해당
            if x > 0:
                edges.append((x, y, W))

    # 벽을 무작위 순서로 처리하기 위해 셔플
    prng.shuffle(edges)

    # ------------------
    # 🌟 메인 루프: 벽 허물기
    # ------------------
    while edges:
        x, y, direction = edges.pop() # 무작위 벽을 하나 꺼낸다.
        
        # 벽 건너편 셀의 좌표 계산
        nx, ny = x + DX[direction], y + DY[direction]
        
        # 현재 셀과 이웃 셀의 DisjointSet 객체
        set1, set2 = sets[y][x], sets[ny][nx]

        # 1. 두 셀이 이미 연결되어 있는지 확인 (루트가 같은지)
        if not set1.is_connected(set2):
            
            # 연결되어 있지 않다면, 벽을 허물고 두 집합을 연결한다.
            set1.union_sets(set2)
            
            # 현재 셀에 길 방향 비트를 추가
            grid[y][x] |= direction
            
            # 이웃 셀에도 반대 방향의 길 비트를 추가
            grid[ny][nx] |= OPPOSITE[direction]
            
            # 시각화 콜백이 있다면 미로 상태를 그린다.
            if step_callback:
                # 여기서 한 번만 호출해서 처리하는게 더 일반적일 수 있음.
                step_callback(grid, width, height) 

    # 최종 미로 그리드 데이터 반환
    return grid

# --------------------------
# 🏃‍♂️ 메인 실행 로직
# --------------------------
def main():
    # 1. 난이도 메뉴 표시
    mode = menu()

    if mode == 1: # 쉬움
        default_width = 15
        default_height = 15
        default_cell = 40
    else: # 어려움 (mode == 2)
        default_width = 20
        default_height = 20
        default_cell = 30

    # 2. 인자 파싱 (메뉴에서 설정된 값 기본값으로 사용)
    parser = argparse.ArgumentParser(description='Kruskal 알고리즘 미로 생성기')
    parser.add_argument('--width', type=int, default=default_width, help='미로의 가로 셀 개수')
    parser.add_argument('--height', type=int, default=default_height, help='미로의 세로 셀 개수')
    parser.add_argument('--seed', type=int, default=None, help='미로 생성을 위한 시드 값')
    parser.add_argument('--delay', type=float, default=0.0,
                        help='벽 생성 단계 사이의 대기 시간 (초). 0이면 즉시 완료.')
    parser.add_argument('--cell', type=int, default=default_cell, help='각 셀의 픽셀 크기')
    args = parser.parse_args()

    # 인자 정리
    width = args.width
    height = args.height
    seed = args.seed if args.seed is not None else random.randrange(0, 0xFFFF_FFFF)
    delay = args.delay
    cell = args.cell

    # 3. Pygame 초기화 및 화면 설정
    pygame.init()
    caption = f'Kruskal Maze ({width}x{height}) seed={seed}'
    pygame.display.set_caption(caption)

    screen_w = width * cell
    screen_h = height * cell
    screen = pygame.display.set_mode((screen_w, screen_h))
    surface = pygame.Surface((screen_w, screen_h)) # 미로를 그릴 주 서피스

    # 4. 단계별 시각화를 위한 콜백 함수 정의
    def visual_callback(grid, w, h):
        draw_maze(surface, grid, w, h, cell)
        
        # 창 응답성 유지를 위해 이벤트 처리 (이게 중요!)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
                
        # 딜레이 설정 (단계별 생성 속도 조절)
        ms = int(delay * 1000)
        if ms > 0:
            pygame.time.delay(ms)

    # 5. 미로 생성 시작!
    print(f"미로 생성 시작: {width}x{height}, Seed: {seed}")
    grid = generate_maze(width, height, seed, step_callback=visual_callback)

    # 6. 최종 미로를 다시 한 번 깨끗하게 그린다.
    draw_maze(surface, grid, width, height, cell)

    # 7. 메인 루프 (새 미로 생성/종료 대기)
    info_font = pygame.font.SysFont("malgungothic", 20)
    info_text = f"(N: 새로운 미로, Q/ESC: 종료)"
    
    # 무한 루프
    while True:
        # 이벤트 처리
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                return
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    return
                elif ev.key == pygame.K_n:
                    # 'N' 키를 누르면 새 시드로 미로 재생성
                    seed = random.randrange(0, 0xFFFF_FFFF)
                    pygame.display.set_caption(f'Kruskal Maze ({width}x{height}) seed={seed}')
                    print(f"새 미로 생성 시작: {width}x{height}, Seed: {seed}")
                    grid = generate_maze(width, height, seed, step_callback=visual_callback)
                    draw_maze(surface, grid, width, height, cell) # 최종 그림

        # 화면 업데이트
        screen.blit(surface, (0,0))
        # 하단 또는 상단에 정보 텍스트 표시
        info_surf = info_font.render(info_text, True, (0,0,0))
        screen.blit(info_surf, (4, screen_h - 24)) # 화면 하단에 배치
        pygame.display.flip()
        
        # CPU 점유율을 너무 높이지 않도록 30 FPS 제한
        pygame.time.Clock().tick(30)

if __name__ == '__main__':
    main()
