# difficulty.py
import sys
import pygame

FONT_NAME = "malgungothic"  # 폰트 없으면 None으로 fallback
MENU_FONT_SIZE = 25

class Difficulty:
    def __init__(self, width, height, cell, time_limit):
        self.width = width
        self.height = height
        self.cell = cell
        self.time_limit = time_limit

# 셀 크기를 60, 50으로 대폭 늘립니다.
# (EASY: 20x20, 셀 60px, 창 1200x1200)
EASY = Difficulty(width=20, height=20, cell=60, time_limit=180) 
# (HARD: 30x30, 셀 50px, 창 1500x1500)
HARD = Difficulty(width=30, height=30, cell=50, time_limit=300) 

def _draw_button(screen, rect, text, font, color=(200,200,200), text_color=(0,0,0)):
    # ... (이하 동일) ...
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0,0,0), rect, 2)
    surf = font.render(text, True, text_color)
    screen.blit(surf, surf.get_rect(center=rect.center))

def select_difficulty():
    # ... (이하 동일) ...
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("미로 게임 - 난이도 선택")

    try:
        font = pygame.font.SysFont(FONT_NAME, MENU_FONT_SIZE)
    except:
        font = pygame.font.SysFont(None, MENU_FONT_SIZE)

    b1 = pygame.Rect(200, 120, 200, 70)
    b2 = pygame.Rect(200, 220, 200, 70)
    clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))
        _draw_button(screen, b1, "난이도 : 쉬움 (20x20)", font) 
        _draw_button(screen, b2, "난이도 : 어려움 (30x30)", font)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b1.collidepoint(e.pos): return EASY
                if b2.collidepoint(e.pos): return HARD
        clock.tick(60)
