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
    # 1. 난이도 선택
    difficulty = select_difficulty()
    width, height, cell_size = difficulty.width, difficulty.height, difficulty.cell
    TIME_LIMIT_SECONDS = difficulty.time_limit

    # 2. Pygame 초기화
    pygame.init()
    font = pygame.font.Font(None, 24)
    timer_font = pygame.font.SysFont(None, 40)
    pause_font = pygame.font.SysFont(None, 60)
    
    # 버튼용 폰트
    button_font = pygame.font.SysFont(None, 30)

    clock = pygame.time.Clock()

    game_width = width * cell_size
    game_height = height * cell_size

    window_surface = pygame.display.set_mode((game_width, game_height), pygame.RESIZABLE)
    pygame.display.set_caption("Maze Game") 

    game_surface = pygame.Surface((game_width, game_height))

    # 일시정지 버튼 영역 (우상단)
    pause_btn_rect = pygame.Rect(game_width - 80, 10, 70, 30)

    while True:
        # --- 초기화 ---
        seed = random.randint(0, 999999)
        rng = random.Random(seed)
        pygame.display.set_caption(f"Maze Game (seed={seed})") 

        grid = generate_maze(width, height, seed)

        base_speed = max(1, cell_size // 8)
        player = Player(0, 0, speed=cell_size // 8)
        player.pixel_x = player.grid_x * cell_size
        player.pixel_y = player.grid_y * cell_size
        player.target_pixel_x = player.pixel_x
        player.target_pixel_y = player.pixel_y

        goal_x, goal_y = width - 1, height - 1

        # 보스 생성
        boss = None 
        if getattr(difficulty, 'name', '') in ["Hard", "어려움"]:
            while True:
                bx = rng.randint(0, width - 1)
                by = rng.randint(0, height - 1)
                if (bx, by) != (0, 0) and (bx, by) != (goal_x, goal_y):
                    boss = Boss(bx, by, cell_size, max_hp=5)
                    print(f"[시스템] 보스 등장! (HP: {boss.hp}) 위치: ({bx}, {by})")
                    break
        
        # 아이템 생성
        debuff_state = DebuffState()
        debuff_items = []
        start_item = spawn_debuff_near_start(grid, width, height, rng, start=(0, 0))
        debuff_items.append(start_item)

        occupied_positions = set()
        occupied_positions.add((0, 0))
        occupied_positions.add((goal_x, goal_y))
        occupied_positions.add((start_item.gx, start_item.gy))
        if boss and boss.is_alive:
            occupied_positions.add((boss.x, boss.y))

        remaining_slots = MAX_DEBUFF_ITEMS - len(debuff_items)
        if remaining_slots < 0: remaining_slots = 0
        target_item_count = min(remaining_slots, int(width * height * 0.05))

        current_added = 0
        while current_added < target_item_count:
            rx = rng.randint(0, width - 1)
            ry = rng.randint(0, height - 1)
            if (rx, ry) not in occupied_positions:
                dtype = rng.choice([DebuffType.SLOW, DebuffType.TIME_LEFT, DebuffType.REVERSE])
                debuff_items.append(DebuffItem(rx, ry, dtype))
                occupied_positions.add((rx, ry))
                current_added += 1

        # 상태 변수
        start_time_ms = pygame.time.get_ticks()
        game_over_message = ""
        running = True
        
        is_paused = False
        pause_start_time = 0
        restart_requested = False

        # [FIX] 에러 해결: 루프 시작 전에 변수를 미리 초기화합니다.
        remaining_time_ms = TIME_LIMIT_SECONDS * 1000

        while running:
            dt = clock.tick(60)
            now_ms = pygame.time.get_ticks()

            # 1. 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    window_surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                
                # 마우스 클릭 처리 (버튼)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 왼쪽 클릭
                        win_w, win_h = window_surface.get_size()
                        scale_x = game_width / win_w
                        scale_y = game_height / win_h
                        mx = event.pos[0] * scale_x
                        my = event.pos[1] * scale_y
                        
                        # 버튼 클릭 확인
                        if pause_btn_rect.collidepoint(mx, my):
                            if not game_over_message:
                                is_paused = not is_paused
                                if is_paused:
                                    pause_start_time = now_ms
                                else:
                                    pause_duration = now_ms - pause_start_time
                                    start_time_ms += pause_duration

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        restart_requested = True
                    
                    elif event.key == pygame.K_ESCAPE:
                        if not game_over_message:
                            is_paused = not is_paused
                            if is_paused:
                                pause_start_time = now_ms
                            else:
                                start_time_ms += (now_ms - pause_start_time)

                    # 플레이어 이동
                    if not is_paused and not game_over_message:
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
                        
                        if event.key == pygame.K_SPACE:
                            if boss and boss.is_alive:
                                boss.take_damage(1)

            if restart_requested:
                break

            # 2. 그리기 (배경 및 게임 요소)
            game_surface.fill((255, 255, 255))
            draw_maze(game_surface, grid, cell_size, goal_x, goal_y)
            draw_debuff_items(game_surface, debuff_items, cell_size)
            if boss and boss.is_alive: boss.draw(game_surface)
            player.draw(game_surface, cell_size)
            
            # [FIX] 여기서 remaining_time_ms를 사용하므로, 위에서 초기화가 필수적임
            draw_debuff_hud(game_surface, debuff_state, now_ms, remaining_time_ms, font)

            # 일시정지 버튼 그리기
            btn_color = (200, 200, 200) if not is_paused else (150, 150, 150)
            pygame.draw.rect(game_surface, btn_color, pause_btn_rect, border_radius=5)
            pygame.draw.rect(game_surface, (50, 50, 50), pause_btn_rect, 2, border_radius=5)
            
            btn_text = "RESUME" if is_paused else "PAUSE"
            text_surf = button_font.render(btn_text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=pause_btn_rect.center)
            game_surface.blit(text_surf, text_rect)

            # 일시정지 화면 처리
            if is_paused:
                overlay = pygame.Surface((game_width, game_height))
                overlay.set_alpha(128)
                overlay.fill((0, 0, 0))
                game_surface.blit(overlay, (0, 0))
                
                # 버튼 다시 그리기 (오버레이 위로)
                pygame.draw.rect(game_surface, btn_color, pause_btn_rect, border_radius=5)
                pygame.draw.rect(game_surface, (50, 50, 50), pause_btn_rect, 2, border_radius=5)
                game_surface.blit(text_surf, text_rect)

                pause_msg = pause_font.render("PAUSED", True, (255, 255, 255))
                pause_msg_rect = pause_msg.get_rect(center=(game_width//2, game_height//2))
                game_surface.blit(pause_msg, pause_msg_rect)

                scaled_surface = pygame.transform.scale(game_surface, window_surface.get_size())
                window_surface.blit(scaled_surface, (0, 0))
                pygame.display.flip()
                continue

            # 3. 게임 로직 (일시정지 아닐 때)
            elapsed_ms = now_ms - start_time_ms
            total_limit_ms = TIME_LIMIT_SECONDS * 1000
            
            # [FIX] 여기서 값이 갱신됩니다. 다음 프레임 그리기에서 이 값을 사용합니다.
            remaining_time_ms = max(0, total_limit_ms - elapsed_ms)
            
            if remaining_time_ms <= 0 and not game_over_message:
                game_over_message = "시간 초과! (Press R)"

            if boss and boss.is_alive and not game_over_message:
                boss.update()
                dist_x = abs(player.pixel_x - boss.pixel_x)
                dist_y = abs(player.pixel_y - boss.pixel_y)
                if dist_x < cell_size / 2 and dist_y < cell_size / 2:
                    game_over_message = "보스와 충돌! (Press R)"

            if debuff_items and not game_over_message:
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

            if not game_over_message:
                if debuff_state.is_slow(now_ms):
                    player.speed = max(1, int(base_speed * debuff_state.slow_multiplier))
                else:
                    player.speed = base_speed
                player.update()

                if player.grid_x == goal_x and player.grid_y == goal_y:
                    game_over_message = "탈출 성공! (Press R)"

            # 4. 최종 화면 갱신 (게임오버 시)
            if game_over_message:
                overlay = pygame.Surface((game_width, game_height))
                overlay.set_alpha(180)
                overlay.fill((255, 255, 255))
                game_surface.blit(overlay, (0, 0))

                text_color = (0, 180, 0) if "성공" in game_over_message else (255, 0, 0)
                msg_surf = timer_font.render(game_over_message, True, text_color)
                msg_rect = msg_surf.get_rect(center=(game_width//2, game_height//2))
                game_surface.blit(msg_surf, msg_rect)
                
                guide_surf = font.render("Press 'R' to Restart", True, (50, 50, 50))
                guide_rect = guide_surf.get_rect(center=(game_width//2, game_height//2 + 40))
                game_surface.blit(guide_surf, guide_rect)

            scaled_surface = pygame.transform.scale(game_surface, window_surface.get_size())
            window_surface.blit(scaled_surface, (0, 0))
            pygame.display.flip()

if __name__ == "__main__":
    main()