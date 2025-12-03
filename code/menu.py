import pygame

# ───────── [버튼 위치 계산 헬퍼] ─────────
def get_menu_rects(center_x, center_y, is_paused, game_over_message):
    """
    현재 상태(일시정지/게임오버)에 따라 버튼들의 위치(Rect)를 딕셔너리로 반환합니다.
    이렇게 하면 main.py에서 클릭 판정과 그리기 좌표를 통일할 수 있습니다.
    """
    btn_w, btn_h = 200, 50
    rects = {}

    # 1. Resume (일시정지 상태일 때만)
    if is_paused:
        r_rect = pygame.Rect(0, 0, btn_w, btn_h)
        r_rect.center = (center_x, center_y - 60)
        rects['resume'] = r_rect

    # 2. Restart
    # 일시정지면 중앙, 게임오버면 조금 위 (위치 조정)
    base_y = center_y if is_paused else (center_y - 30)
    restart_rect = pygame.Rect(0, 0, btn_w, btn_h)
    restart_rect.center = (center_x, base_y)
    rects['restart'] = restart_rect

    # 3. Manual
    base_y = (center_y + 60) if is_paused else (center_y + 30)
    manual_rect = pygame.Rect(0, 0, btn_w, btn_h)
    manual_rect.center = (center_x, base_y)
    rects['manual'] = manual_rect

    # 4. Quit
    base_y = (center_y + 120) if is_paused else (center_y + 90)
    quit_rect = pygame.Rect(0, 0, btn_w, btn_h)
    quit_rect.center = (center_x, base_y)
    rects['quit'] = quit_rect

    return rects

# ───────── [버튼 그리기] ─────────
def draw_button(surface, rect, text, font, mouse_pos, base_color=(220, 220, 220), hover_color=(180, 210, 255)):
    is_hover = rect.collidepoint(mouse_pos)
    color = hover_color if is_hover else base_color
    
    # 그림자
    pygame.draw.rect(surface, (50, 50, 50), (rect.x + 2, rect.y + 2, rect.width, rect.height), border_radius=8)
    # 본체
    pygame.draw.rect(surface, color, rect, border_radius=8)
    # 테두리
    pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=8)
    
    txt_surf = font.render(text, True, (0, 0, 0))
    txt_rect = txt_surf.get_rect(center=rect.center)
    surface.blit(txt_surf, txt_rect)
    
    return is_hover

# ───────── [매뉴얼 창 그리기] ─────────
def draw_manual_window(surface, screen_rect, title_font, font, mouse_pos):
    # 반투명 배경
    overlay = pygame.Surface(screen_rect.size)
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0,0))

    panel_w, panel_h = 600, 450
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = screen_rect.center
    
    pygame.draw.rect(surface, (250, 250, 245), panel_rect, border_radius=15)
    pygame.draw.rect(surface, (0, 0, 0), panel_rect, 3, border_radius=15)

    cx = panel_rect.centerx
    y = panel_rect.y + 40
    
    title = title_font.render("- GAME MANUAL -", True, (0, 0, 0))
    surface.blit(title, title.get_rect(center=(cx, y)))
    y += 60

    descriptions = [
        ("GOAL", "Reach the Red Circle (Bottom-Right)"),
        ("MOVE", "Use Arrow Keys (↑ ↓ ← →)"),
        ("BOSS", "Run away from the Red Monster! (Hard Mode)"),
        ("ITEMS", "Avoid these traps:"),
        ("  [BLUE]", "Slow Down (30s)"),
        ("  [PURPLE]", "Reverse Controls (15s)"),
        ("  [RED]", "Time Penalty (-30s)"),
    ]

    for label, desc in descriptions:
        color = (0, 0, 0)
        if "[BLUE]" in label: color = (0, 0, 200)
        elif "[PURPLE]" in label: color = (128, 0, 128)
        elif "[RED]" in label: color = (200, 0, 0)
        
        lbl_surf = font.render(label, True, color)
        desc_surf = font.render(desc, True, (50, 50, 50))
        
        surface.blit(lbl_surf, (panel_rect.x + 50, y))
        surface.blit(desc_surf, (panel_rect.x + 200, y))
        y += 35

    # 닫기 버튼
    btn_w, btn_h = 120, 45
    back_rect = pygame.Rect(0, 0, btn_w, btn_h)
    back_rect.center = (cx, panel_rect.bottom - 50)
    
    draw_button(surface, back_rect, "CLOSE", font, mouse_pos)
    return back_rect