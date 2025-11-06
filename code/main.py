# main.py
import sys
import pygame
import random
from difficulty import select_difficulty
from maze import generate_maze, N, S, E, W
from player import Player
from renderer import draw_maze, draw_debuff_items
from debuff import (
    DebuffType, DebuffState, spawn_debuff_near_start,
    update_debuffs
)

def main():
    difficulty = select_difficulty()
    width, height, cell_size = difficulty.width, difficulty.height, difficulty.cell
    
    TIME_LIMIT_SECONDS = difficulty.time_limit 

    seed = random.randint(0, 999999)
    rng = random.Random(seed)
    grid = generate_maze(width, height, seed)

    pygame.init()

    # 1. 고정된 게임 표면 크기 계산
    game_width = width * cell_size
    game_height = height * cell_size

    # 2. 실제 창(Window)을 RESIZABLE 플래그와 함께 생성
    window_surface = pygame.display.set_mode((game_width, game_height), pygame.RESIZABLE)
    pygame.display.set_caption(f"Kruskal Maze with Player (seed={seed})")

    # 3. 게임 로직이 그려질 내부 표면(Surface) 생성
    game_surface = pygame.Surface((game_width, game_height))

    clock = pygame.time.Clock()
    timer_font = pygame.font.SysFont(None, 40) 

    base_speed = max(1, cell_size // 8)
    player = Player(0, 0, speed=cell_size // 8) 
    player.pixel_x = player.grid_x * cell_size
    player.pixel_y = player.grid_y * cell_size
    player.target_pixel_x = player.pixel_x
    player.target_pixel_y = player.pixel_y

    goal_x, goal_y = width - 1, height - 1 
    debuff_state = DebuffState()
    debuff_items = [spawn_debuff_near_start(grid, width, height, rng, start=(0,0))]

    start_time = pygame.time.get_ticks() 
    game_over_message = "" 
    running = True
    
    while running:
        # 시간 계산
        current_time = pygame.time.get_ticks()
        now = current_time
        elapsed_seconds = (current_time - start_time) / 1000
        remaining_time = TIME_LIMIT_SECONDS - elapsed_seconds

        if remaining_time <= 0:
            remaining_time = 0
            running = False
            game_over_message = "시간 초과!"

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 4. 창 크기 조절 이벤트(VIDEORESIZE) 처리
            elif event.type == pygame.VIDEORESIZE:
                # 새 크기로 window_surface를 다시 설정
                window_surface = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            
            elif event.type == pygame.KEYDOWN:
                if debuff_state.is_reverse(now):
                    if event.key == pygame.K_UP:    player.start_move(grid, S, cell_size)
                    elif event.key == pygame.K_DOWN:  player.start_move(grid, N, cell_size)
                    elif event.key == pygame.K_LEFT:  player.start_move(grid, E, cell_size)
                    elif event.key == pygame.K_RIGHT: player.start_move(grid, W, cell_size)
                else:
                    if event.key == pygame.K_UP:       player.start_move(grid, N, cell_size)
                    elif event.key == pygame.K_DOWN:   player.start_move(grid, S, cell_size)
                    elif event.key == pygame.K_LEFT:   player.start_move(grid, W, cell_size)
                    elif event.key == pygame.K_RIGHT:  player.start_move(grid, E, cell_size)
 
        if debuff_items:
            remaining = []
            for it in debuff_items:
                if (player.grid_x, player.grid_y) == (it.gx, it.gy):
                    duration_ms = 30000
                    if it.dtype == DebuffType.SLOW:
                        debuff_state.slow_until_ms = now + duration_ms
                    elif it.dtype == DebuffType.WALL_SHIFT:
                        debuff_state.wallshift_perminent = True
                        debuff_state.wallshift_until_ms = 0
                        debuff_state._last_shift_ms = 0
                    elif it.dtype == DebuffType.REVERSE:
                        debuff_state.reverse_until_ms = now + 30000
                else:
                    remaining.append(it)
            debuff_items = remaining

        update_debuffs(now, debuff_state, grid, width, height, start=(0,0), goal=(goal_x, goal_y), rng=rng)

        if debuff_state.is_slow(now):
            player.speed = max(1, int(base_speed * debuff_state.slow_multiplier))
        else:
            player.speed = base_speed

        # 플레이어 상태 업데이트
        player.update() 

        # 승리 조건 확인
        if player.grid_x == goal_x and player.grid_y == goal_y:
            running = False
            game_over_message = "GAME OVER!"

        # --- 5. 그리기 ---
        game_surface.fill((255, 255, 255))
        # 미로와 목표지점 그리기
        draw_maze(game_surface, grid, cell_size, goal_x, goal_y)
        draw_debuff_items(game_surface, debuff_items, cell_size)

        # 플레이어 그리기
        player.draw(game_surface, cell_size) 

        # 타이머 텍스트 그리기
        timer_text = f"Time: {int(remaining_time)}"
        timer_surf = timer_font.render(timer_text, True, (0, 0, 0)) 
        game_surface.blit(timer_surf, (10, 10)) # game_surface에 blit

        # --- 6. 화면 업데이트 (스케일링) ---
        
        # game_surface를 window_surface의 현재 크기에 맞게 스케일링
        scaled_surface = pygame.transform.scale(game_surface, window_surface.get_size())
        
        # 스케일링된 표면을 실제 창에 그리기
        window_surface.blit(scaled_surface, (0, 0))
        
        pygame.display.flip() 
        
        clock.tick(60)

    # 게임 오버 화면
    if game_over_message:
        # 게임 오버 메시지도 game_surface에 그림
        msg_surf = timer_font.render(game_over_message, True, (0, 0, 0))
        msg_rect = msg_surf.get_rect(center=game_surface.get_rect().center)
        
        # 덮어쓰기 위해 회색 배경을 game_surface에 그림
        game_surface.fill((220, 220, 220)) 
        game_surface.blit(msg_surf, msg_rect)

        # 스케일링하여 window_surface에 표시
        scaled_surface = pygame.transform.scale(game_surface, window_surface.get_size())
        window_surface.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        
        pygame.time.wait(3000) 

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
