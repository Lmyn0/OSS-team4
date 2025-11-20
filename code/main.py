import sys
import pygame
import random
from difficulty import select_difficulty
from maze import generate_maze, N, S, E, W
from player import Player
from renderer import draw_maze, draw_debuff_items, draw_debuff_hud
from debuff import (
    DebuffType, DebuffState,DebuffItem, spawn_debuff_near_start,
    apply_debuff_on_pickup
)

SLOW_DURATION_MS = 30_000       # 느려짐 30초
REVERSE_DURATION_MS = 15_000    # 역방향 15초
TIME_LEFT_MS = 30_000           # 제한 시간 30초 감소

MAX_DEBUFF_ITEMS = 25

def main():
    difficulty = select_difficulty()
    width, height, cell_size = difficulty.width, difficulty.height, difficulty.cell
    TIME_LIMIT_SECONDS = difficulty.time_limit

    seed = random.randint(0, 999999)
    rng = random.Random(seed)
    grid = generate_maze(width, height, seed)

    pygame.init()

    font = pygame.font.Font(None, 24)
    timer_font = pygame.font.SysFont(None, 40)
    clock = pygame.time.Clock()

    # 1. 고정된 게임 표면 크기 계산
    game_width = width * cell_size
    game_height = height * cell_size

    # 2. 실제 창(Window)을 RESIZABLE 플래그와 함께 생성
    window_surface = pygame.display.set_mode((game_width, game_height), pygame.RESIZABLE)
    pygame.display.set_caption(f"Kruskal Maze with Player (seed={seed})")

    # 3. 게임 로직이 그려질 내부 표면(Surface) 생성
    game_surface = pygame.Surface((game_width, game_height))

    base_speed = max(1, cell_size // 8)
    player = Player(0, 0, speed=cell_size // 8)
    player.pixel_x = player.grid_x * cell_size
    player.pixel_y = player.grid_y * cell_size
    player.target_pixel_x = player.pixel_x
    player.target_pixel_y = player.pixel_y

    goal_x, goal_y = width - 1, height - 1

    debuff_state = DebuffState()
    debuff_items = []
    #    초반 긴장감을 위해 하나는 시작점 근처에 둠
    start_item = spawn_debuff_near_start(grid, width, height, rng, start=(0, 0))
    debuff_items.append(start_item)

    # 2) 이미 사용된 위치 기록
    occupied_positions = set()
    occupied_positions.add((0, 0))                           # 시작점
    occupied_positions.add((goal_x, goal_y))                 # 도착점
    occupied_positions.add((start_item.gx, start_item.gy))   # 첫 번째 아이템 위치

    # 3) 추가로 배치할 수 있는 최대 개수 계산
    remaining_slots = MAX_DEBUFF_ITEMS - len(debuff_items)
    if remaining_slots < 0:
        remaining_slots = 0

    # 4) 맵 크기 기반으로 후보 개수 계산 (그래도 너무 많지 않게 min 처리)
    total_cells = width * height
    percent_based = int(total_cells * 0.05)      # 원래 쓰던 5% 기준
    target_item_count = min(remaining_slots, percent_based)

    current_added = 0
    while current_added < target_item_count:
        rx = rng.randint(0, width - 1)
        ry = rng.randint(0, height - 1)

        if (rx, ry) not in occupied_positions:
            dtype = rng.choice([DebuffType.SLOW, DebuffType.TIME_LEFT, DebuffType.REVERSE])
            new_item = DebuffItem(rx, ry, dtype)
            debuff_items.append(new_item)

            occupied_positions.add((rx, ry))
            current_added += 1

    print(f"디버프 아이템 총 {len(debuff_items)}개 배치됨.")

    # 시간 관련 기준점: 게임 시작 시각(ms)
    start_time_ms = pygame.time.get_ticks()

    game_over_message = ""
    running = True

    while running:
        # ───────── 시간 계산 ─────────
        dt = clock.tick(60)                             # 프레임 간격(ms)
        now_ms = pygame.time.get_ticks()                # 현재 시각(ms)

        elapsed_ms = now_ms - start_time_ms
        total_limit_ms = TIME_LIMIT_SECONDS * 1000
        remaining_time_ms = max(0, total_limit_ms - elapsed_ms)
        remaining_time = remaining_time_ms / 1000.0     # 초 단위

        # 시간 초과 체크
        if remaining_time_ms <= 0:
            game_over_message = "시간 초과!"
            break

        # ───────── 이벤트 처리 ─────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                window_surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if debuff_state.is_reverse(now_ms):
                    if event.key == pygame.K_UP:
                        player.start_move(grid, S, cell_size)
                    elif event.key == pygame.K_DOWN:
                        player.start_move(grid, N, cell_size)
                    elif event.key == pygame.K_LEFT:
                        player.start_move(grid, E, cell_size)
                    elif event.key == pygame.K_RIGHT:
                        player.start_move(grid, W, cell_size)
                else:
                    if event.key == pygame.K_UP:
                        player.start_move(grid, N, cell_size)
                    elif event.key == pygame.K_DOWN:
                        player.start_move(grid, S, cell_size)
                    elif event.key == pygame.K_LEFT:
                        player.start_move(grid, W, cell_size)
                    elif event.key == pygame.K_RIGHT:
                        player.start_move(grid, E, cell_size)

        # ───────── 디버프 아이템 처리 ─────────
        if debuff_items:
            next_items = []
            for it in debuff_items:
                picked = (player.grid_x, player.grid_y) == (it.gx, it.gy)

                if not picked:
                    next_items.append(it)
                    continue

                # 아이템을 밟았을 때만 발동 (한 번만!)
                if it.dtype == DebuffType.SLOW:
                    debuff_state.slow_until_ms = max(now_ms, debuff_state.slow_until_ms) + SLOW_DURATION_MS

                elif it.dtype == DebuffType.REVERSE:
                    debuff_state.reverse_until_ms = max(now_ms, debuff_state.reverse_until_ms) + REVERSE_DURATION_MS

                elif it.dtype == DebuffType.TIME_LEFT:
                    # 현재 남은 시간(ms)에서 30초 차감
                    new_remaining_ms = max(0, remaining_time_ms - TIME_LEFT_MS)

                    # 남은 시간을 강제로 줄였으니, start_time_ms를 그에 맞게 앞으로 당겨줌
                    # total_limit_ms - new_remaining_ms = 경과한 시간(ms)
                    elapsed_ms_after = total_limit_ms - new_remaining_ms
                    start_time_ms = now_ms - elapsed_ms_after

            debuff_items = next_items

        # ───────── 디버프 효과 반영 (속도) ─────────
        if debuff_state.is_slow(now_ms):
            player.speed = max(1, int(base_speed * debuff_state.slow_multiplier))
        else:
            player.speed = base_speed

        # ───────── 플레이어 상태 업데이트 ─────────
        player.update()

        # 승리 조건 확인
        if player.grid_x == goal_x and player.grid_y == goal_y:
            running = False
            game_over_message = "GAME OVER!"

        # ───────── 그리기 ─────────
        game_surface.fill((255, 255, 255))

        draw_maze(game_surface, grid, cell_size, goal_x, goal_y)
        draw_debuff_items(game_surface, debuff_items, cell_size)
        player.draw(game_surface, cell_size)

        # 상태창 (오른쪽 상단 HUD) – 항상 최신 now_ms / remaining_time_ms 사용
        draw_debuff_hud(game_surface, debuff_state, now_ms, remaining_time_ms, font)

        # 스케일링 후 화면에 표시
        scaled_surface = pygame.transform.scale(game_surface, window_surface.get_size())
        window_surface.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    # ───────── 게임 오버 화면 ─────────
    if game_over_message:
        msg_surf = timer_font.render(game_over_message, True, (0, 0, 0))
        msg_rect = msg_surf.get_rect(center=game_surface.get_rect().center)

        game_surface.fill((220, 220, 220))
        game_surface.blit(msg_surf, msg_rect)

        scaled_surface = pygame.transform.scale(game_surface, window_surface.get_size())
        window_surface.blit(scaled_surface, (0, 0))
        pygame.display.flip()

        pygame.time.wait(3000)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
