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

# [추가] 분리한 메뉴 파일 임포트
import menu 

SLOW_DURATION_MS = 30_000       
REVERSE_DURATION_MS = 15_000    
TIME_LEFT_MS = 15_000          

MAX_DEBUFF_ITEMS = 25

def main():
    difficulty = select_difficulty()
    width, height, cell_size = difficulty.width, difficulty.height, difficulty.cell
    TIME_LIMIT_SECONDS = difficulty.time_limit

    pygame.init()
    
    font = pygame.font.SysFont("arial", 22)
    title_font = pygame.font.SysFont("arial", 35, bold=True)
    hud_font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()

    game_width = width * cell_size
    game_height = height * cell_size

    window_surface = pygame.display.set_mode((game_width, game_height), pygame.RESIZABLE)
    pygame.display.set_caption("Maze Game") 
    game_surface = pygame.Surface((game_width, game_height))

    # 우상단 일시정지(메뉴) 버튼 영역
    pause_btn_rect = pygame.Rect(game_width - 80, 10, 70, 30)

    while True: # 세션 루프
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

        boss = None 
        if getattr(difficulty, 'name', '') in ["Hard", "어려움"]:
            while True:
                bx = rng.randint(0, width - 1)
                by = rng.randint(0, height - 1)
                if (bx, by) != (0, 0) and (bx, by) != (goal_x, goal_y):
                    boss = Boss(bx, by, cell_size, max_hp=5)
                    break
        
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

        start_time_ms = pygame.time.get_ticks()
        remaining_time_ms = TIME_LIMIT_SECONDS * 1000
        game_over_message = ""
        running = True
        
        is_paused = False
        pause_start_time = 0
        show_manual = False

        while running:
            dt = clock.tick(60)
            now_ms = pygame.time.get_ticks()

            win_w, win_h = window_surface.get_size()
            scale_x = game_width / win_w
            scale_y = game_height / win_h
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pos = (mouse_x * scale_x, mouse_y * scale_y)

            is_menu_mode = is_paused or (game_over_message != "")

            # ───────── 1. 이벤트 처리 ─────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    window_surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: running = False
                    
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        if show_manual: show_manual = False
                        elif not game_over_message:
                            is_paused = not is_paused
                            if is_paused: pause_start_time = now_ms
                            else: start_time_ms += (now_ms - pause_start_time)
                    
                    if not is_menu_mode and not show_manual:
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
                        
                        if event.key == pygame.K_SPACE and boss and boss.is_alive:
                            boss.take_damage(1)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 좌클릭
                        
                        # (A) 매뉴얼 닫기
                        if show_manual:
                            # 닫기 버튼 위치를 단순 계산 (그리기 로직과 맞춤)
                            cx, cy = game_width // 2, game_height // 2
                            back_rect = pygame.Rect(0, 0, 120, 45)
                            back_rect.center = (cx, cy + 225 - 50)
                            if back_rect.collidepoint(mouse_pos):
                                show_manual = False

                        # (B) 메뉴 모드일 때 (버튼 로직을 menu.py의 get_menu_rects로 통합!)
                        elif is_menu_mode:
                            cx, cy = game_width // 2, game_height // 2
                            # [핵심] menu.py에서 버튼 위치를 받아옴 -> 좌표 불일치 해결!
                            rects = menu.get_menu_rects(cx, cy, is_paused, game_over_message)
                            
                            if 'resume' in rects and rects['resume'].collidepoint(mouse_pos):
                                is_paused = False
                                start_time_ms += (now_ms - pause_start_time)
                            
                            elif 'restart' in rects and rects['restart'].collidepoint(mouse_pos):
                                running = False
                            
                            elif 'manual' in rects and rects['manual'].collidepoint(mouse_pos):
                                show_manual = True
                            
                            elif 'quit' in rects and rects['quit'].collidepoint(mouse_pos):
                                pygame.quit(); sys.exit()

                        # (C) 게임 중
                        else:
                            if pause_btn_rect.collidepoint(mouse_pos):
                                is_paused = True
                                pause_start_time = now_ms

            if not running: break

            # ───────── 2. 게임 상태 업데이트 ─────────
            if not is_menu_mode and not show_manual:
                elapsed_ms = now_ms - start_time_ms
                total_limit_ms = TIME_LIMIT_SECONDS * 1000
                remaining_time_ms = max(0, total_limit_ms - elapsed_ms)
                
                if remaining_time_ms <= 0: game_over_message = "TIME OVER"
                
                if boss and boss.is_alive:
                    boss.update()
                    if abs(player.pixel_x - boss.pixel_x) < cell_size/2 and abs(player.pixel_y - boss.pixel_y) < cell_size/2:
                        game_over_message = "CAUGHT BY BOSS"

                if debuff_items:
                    next_items = []
                    for it in debuff_items:
                        if (player.grid_x, player.grid_y) == (it.gx, it.gy):
                            if it.dtype == DebuffType.SLOW: debuff_state.slow_until_ms = max(now_ms, debuff_state.slow_until_ms) + SLOW_DURATION_MS
                            elif it.dtype == DebuffType.REVERSE: debuff_state.reverse_until_ms = max(now_ms, debuff_state.reverse_until_ms) + REVERSE_DURATION_MS
                            elif it.dtype == DebuffType.TIME_LEFT:
                                elapsed_ms = now_ms - start_time_ms
                                remaining_time_ms = max(0, total_limit_ms - elapsed_ms)

                                # 30초 감소
                                new_remaining_ms = max(0, remaining_time_ms - TIME_LEFT_MS)

                                # start_time_ms 를 다시 계산해서 타이머 일관성 유지
                                new_elapsed_ms = total_limit_ms - new_remaining_ms
                                start_time_ms = now_ms - new_elapsed_ms

                                # 디버깅용 갱신
                                remaining_time_ms = new_remaining_ms
                        else: next_items.append(it)
                    debuff_items = next_items

                if debuff_state.is_slow(now_ms): player.speed = max(1, int(base_speed * debuff_state.slow_multiplier))
                else: player.speed = base_speed
                player.update()
                
                if player.grid_x == goal_x and player.grid_y == goal_y:
                    game_over_message = "STAGE CLEAR!"


            # ───────── 3. 화면 그리기 ─────────
            game_surface.fill((255, 255, 255))
            draw_maze(game_surface, grid, cell_size, goal_x, goal_y)
            draw_debuff_items(game_surface, debuff_items, cell_size)
            if boss and boss.is_alive: boss.draw(game_surface)
            player.draw(game_surface, cell_size)
            draw_debuff_hud(game_surface, debuff_state, now_ms, remaining_time_ms, hud_font)

            # 우상단 일시정지 버튼
            if not is_menu_mode and not show_manual:
                menu.draw_button(game_surface, pause_btn_rect, "MENU", font, mouse_pos)

            # 오버레이 (메뉴 or 매뉴얼)
            if is_menu_mode or show_manual:
                overlay = pygame.Surface((game_width, game_height))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                game_surface.blit(overlay, (0, 0))

                cx, cy = game_width // 2, game_height // 2

                if show_manual:
                    # [메뉴 파일 사용] 매뉴얼 창 그리기
                    menu.draw_manual_window(game_surface, pygame.Rect(0,0,game_width,game_height), title_font, font, mouse_pos)
                
                else:
                    # 타이틀
                    if game_over_message:
                        t_txt = game_over_message
                        t_col = (0, 255, 0) if "CLEAR" in game_over_message else (255, 80, 80)
                    else:
                        t_txt = "PAUSED"
                        t_col = (255, 255, 255)
                    
                    t_surf = title_font.render(t_txt, True, t_col)
                    game_surface.blit(t_surf, t_surf.get_rect(center=(cx, cy - 120)))

                    # [핵심] menu.py에서 좌표 받아와서 그리기 -> 좌표 일치!
                    rects = menu.get_menu_rects(cx, cy, is_paused, game_over_message)
                    
                    if 'resume' in rects:
                        menu.draw_button(game_surface, rects['resume'], "RESUME", font, mouse_pos)
                    
                    if 'restart' in rects:
                        menu.draw_button(game_surface, rects['restart'], "RESTART", font, mouse_pos)
                    
                    if 'manual' in rects:
                        menu.draw_button(game_surface, rects['manual'], "MANUAL", font, mouse_pos)
                        
                    if 'quit' in rects:
                        menu.draw_button(game_surface, rects['quit'], "QUIT", font, mouse_pos)

            scaled_surface = pygame.transform.scale(game_surface, window_surface.get_size())
            window_surface.blit(scaled_surface, (0, 0))
            pygame.display.flip()

if __name__ == "__main__":
    main()