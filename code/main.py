import sys
import pygame
import random
from difficulty import select_difficulty
from maze import generate_maze, N, S, E, W
from player import Player
from renderer import draw_maze, draw_debuff_items, draw_debuff_hud
from debuff import (
    DebuffType, DebuffState, DebuffItem, spawn_debuff_near_start,
    apply_debuff_on_pickup
)
from boss import Boss

SLOW_DURATION_MS = 30_000       
REVERSE_DURATION_MS = 15_000    
TIME_LEFT_MS = 30_000           

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

    game_width = width * cell_size
    game_height = height * cell_size

    window_surface = pygame.display.set_mode((game_width, game_height), pygame.RESIZABLE)
    pygame.display.set_caption(f"Kruskal Maze (seed={seed})")

    game_surface = pygame.Surface((game_width, game_height))

    base_speed = max(1, cell_size // 8)
    player = Player(0, 0, speed=cell_size // 8)
    player.pixel_x = player.grid_x * cell_size
    player.pixel_y = player.grid_y * cell_size
    player.target_pixel_x = player.pixel_x
    player.target_pixel_y = player.pixel_y

    goal_x, goal_y = width - 1, height - 1

    # ───────── 보스 생성 (Hard 모드 + 속성 적용) ─────────
    boss = None 
    # 난이도 체크 (difficulty.name이 'Hard' 또는 '어려움'일 때)
    if getattr(difficulty, 'name', '') in ["Hard", "어려움"]:
        while True:
            bx = rng.randint(0, width - 1)
            by = rng.randint(0, height - 1)
            if (bx, by) != (0, 0) and (bx, by) != (goal_x, goal_y):
                # max_hp=5 설정
                boss = Boss(bx, by, cell_size, max_hp=5)
                print(f"[시스템] 보스 등장! (HP: {boss.hp}) 위치: ({bx}, {by})")
                break
    # ────────────────────────────────────────────────

    debuff_state = DebuffState()
    debuff_items = []
    
    start_item = spawn_debuff_near_start(grid, width, height, rng, start=(0, 0))
    debuff_items.append(start_item)

    occupied_positions = set()
    occupied_positions.add((0, 0))
    occupied_positions.add((goal_x, goal_y))
    occupied_positions.add((start_item.gx, start_item.gy))
    
    # 보스가 있고 '살아있으면' 아이템 생성 위치에서 제외
    if boss and boss.is_alive:
        occupied_positions.add((boss.x, boss.y))

    remaining_slots = MAX_DEBUFF_ITEMS - len(debuff_items)
    if remaining_slots < 0: remaining_slots = 0
    total_cells = width * height
    percent_based = int(total_cells * 0.05)
    target_item_count = min(remaining_slots, percent_based)

    current_added = 0
    while current_added < target_item_count:
        rx = rng.randint(0, width - 1)
        ry = rng.randint(0, height - 1)
        if (rx, ry) not in occupied_positions:
            dtype = rng.choice([DebuffType.SLOW, DebuffType.TIME_LEFT, DebuffType.REVERSE])
            debuff_items.append(DebuffItem(rx, ry, dtype))
            occupied_positions.add((rx, ry))
            current_added += 1

    start_time_ms = pygame.time.get_ticks()
    game_over_message = ""
    running = True

    while running:
        dt = clock.tick(60)
        now_ms = pygame.time.get_ticks()

        elapsed_ms = now_ms - start_time_ms
        total_limit_ms = TIME_LIMIT_SECONDS * 1000
        remaining_time_ms = max(0, total_limit_ms - elapsed_ms)
        
        if remaining_time_ms <= 0:
            game_over_message = "시간 초과!"
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                # 플레이어 이동 입력
                if debuff_state.is_reverse(now_ms):
                    if event.key == pygame.K_UP: player.start_move(grid, S, cell_size)
                    elif event.key == pygame.K_DOWN: player.start_move(grid, N, cell_size)
                    elif event.key == pygame.K_LEFT: player.start_move(grid, E, cell_size)
                    elif event.key == pygame.K_RIGHT: player.start_move(grid, W, cell_size)
                else:
                    if event.key == pygame.K_UP: player.start_move(grid, N, cell_size)
                    elif event.key == pygame.K_DOWN: player.start_move(grid, S, cell_size)
                    elif event.key == pygame.K_LEFT: player.start_move(grid, W, cell_size)
                    elif event.key == pygame.K_RIGHT: player.start_move(grid, E, cell_size)
                
                # (테스트용) 스페이스바를 누르면 보스에게 데미지 1
                if event.key == pygame.K_SPACE:
                    if boss and boss.is_alive:
                        # 거리 제한 없이 테스트로 감소
                        boss.take_damage(1)
                        print(f"보스 타격! 남은 HP: {boss.hp}")

        # ───────── 보스 업데이트 (살아있을 때만) ─────────
        if boss and boss.is_alive:
            boss.update()
            
            # 충돌 체크: 보스가 살아있을 때만 충돌하면 게임 오버
            dist_x = abs(player.pixel_x - boss.pixel_x)
            dist_y = abs(player.pixel_y - boss.pixel_y)
            
            if dist_x < cell_size / 2 and dist_y < cell_size / 2:
                game_over_message = "보스와 충돌했습니다!"
                running = False
        # ──────────────────────────────────────────────

        if debuff_items:
            next_items = []
            for it in debuff_items:
                picked = (player.grid_x, player.grid_y) == (it.gx, it.gy)
                if not picked:
                    next_items.append(it)
                    continue

                if it.dtype == DebuffType.SLOW:
                    debuff_state.slow_until_ms = max(now_ms, debuff_state.slow_until_ms) + SLOW_DURATION_MS
                elif it.dtype == DebuffType.REVERSE:
                    debuff_state.reverse_until_ms = max(now_ms, debuff_state.reverse_until_ms) + REVERSE_DURATION_MS
                elif it.dtype == DebuffType.TIME_LEFT:
                    new_remaining_ms = max(0, remaining_time_ms - TIME_LEFT_MS)
                    elapsed_ms_after = total_limit_ms - new_remaining_ms
                    start_time_ms = now_ms - elapsed_ms_after
            debuff_items = next_items

        if debuff_state.is_slow(now_ms):
            player.speed = max(1, int(base_speed * debuff_state.slow_multiplier))
        else:
            player.speed = base_speed

        player.update()

        if player.grid_x == goal_x and player.grid_y == goal_y:
            running = False
            game_over_message = "탈출 성공! (WIN)"

        game_surface.fill((255, 255, 255))
        draw_maze(game_surface, grid, cell_size, goal_x, goal_y)
        draw_debuff_items(game_surface, debuff_items, cell_size)
        
        # 보스가 있고 살아있으면 그리기 (HP바 포함)
        if boss and boss.is_alive:
            boss.draw(game_surface)
        
        player.draw(game_surface, cell_size)
        draw_debuff_hud(game_surface, debuff_state, now_ms, remaining_time_ms, font)

        scaled_surface = pygame.transform.scale(game_surface, window_surface.get_size())
        window_surface.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    if game_over_message:
        text_color = (0, 180, 0) if "성공" in game_over_message else (255, 0, 0)
        msg_surf = timer_font.render(game_over_message, True, text_color)
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