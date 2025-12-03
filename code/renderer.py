import pygame
from maze import N, S, E, W

def draw_maze(surface, grid, cell_size, goal_x, goal_y):
    h = len(grid)
    w = len(grid[0])
    surface.fill((255,255,255))

    for y in range(h):
        for x in range(w):
            cx, cy = x*cell_size, y*cell_size
            cell = grid[y][x]
            if not (cell & N):
                pygame.draw.line(surface,(0,0,0),(cx,cy),(cx+cell_size,cy),2)
            if not (cell & W):
                pygame.draw.line(surface,(0,0,0),(cx,cy),(cx,cy+cell_size),2)
            if not (cell & S):
                pygame.draw.line(surface,(0,0,0),(cx,cy+cell_size),(cx+cell_size,cy+cell_size),2)
            if not (cell & E):
                pygame.draw.line(surface,(0,0,0),(cx+cell_size,cy),(cx+cell_size,cy+cell_size),2)
    
    gx = goal_x * cell_size + cell_size // 2
    gy = goal_y * cell_size + cell_size // 2
    
    radius = max(6, cell_size // 3)
    pygame.draw.circle(surface, (255, 0, 0), (gx, gy), radius)
    
def draw_debuff_items(surface, items, cell_size):
    import pygame
    for it in items:
        cx = it.gx * cell_size + cell_size // 2
        cy = it.gy * cell_size + cell_size // 2
        r = max(6, cell_size // 3)  
        pygame.draw.circle(surface, (0, 0, 0), (cx, cy), r)           
        pygame.draw.circle(surface, (180, 180, 180), (cx, cy), r, 2)
def draw_debuff_hud(surface, debuff_state, now_ms, remaining_time_ms, font, attack_charges):
    """
    surface            : game_surface
    debuff_state       : DebuffState 인스턴스
    now_ms             : pygame.time.get_ticks()
    remaining_time_ms  : 전체 게임 남은 시간 (ms)
    font               : pygame.font.SysFont(None, 24)
    attack_charges     : 남은 공격 아이템 개수 (int)
    """
    lines = []

    # 1) 전체 게임 남은 시간
    total_sec = max(0, int(remaining_time_ms / 1000))
    lines.append(("TIME LEFT", f"{total_sec}s"))

    # 추가. 1.1) 공격 아이템 개수 표시
    lines.append(("ATTACK", f"{attack_charges}x"))
    # 2) 슬로우 디버프 남은 시간
    if debuff_state.is_slow(now_ms):
        sec = debuff_state.time_left(now_ms, debuff_state.slow_until_ms)
        lines.append(("SLOW", f"{sec}s"))

    # 3) 역방향 디버프 남은 시간
    if debuff_state.is_reverse(now_ms):
        sec = debuff_state.time_left(now_ms, debuff_state.reverse_until_ms)
        lines.append(("REVERSE", f"{sec}s"))

    # ───── HUD 그리기 ─────
    padding = 6
    line_h = font.get_height() + 4
    box_w = 200
    box_h = padding * 2 + line_h * len(lines)

    x = surface.get_width() - box_w - 10
    y = 10

    # 반투명 검정 배경
    bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 160))
    surface.blit(bg, (x, y))

    # 텍스트 그리기
    cur_y = y + padding
    for idx, (label, value) in enumerate(lines):
        if idx == 0:
            label_color = (255, 255, 0)     # TIME LEFT 강조
        elif label == "ATTACK":
            label_color = (255, 255, 0)     # ATTACK 강조
        else:
            label_color = (255, 180, 180)   # 디버프 이름
        value_color = (200, 220, 255)

        label_surf = font.render(label + ":", True, label_color)
        value_surf = font.render(value, True, value_color)

        surface.blit(label_surf, (x + padding, cur_y))
        surface.blit(value_surf, (x + padding + 100, cur_y))
        cur_y += line_h