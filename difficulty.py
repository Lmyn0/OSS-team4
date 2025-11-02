# difficulty.py
import sys
import pygame

FONT_NAME = "malgungothic"  # 폰트 없으면 None으로 fallback
MENU_FONT_SIZE = 25

class Difficulty:
    def __init__(self, width, height, cell):
        self.width = width
        self.height = height
        self.cell = cell

EASY = Difficulty(width=15, height=15, cell=40)
HARD = Difficulty(width=20, height=20, cell=30)

def _draw_button(screen, rect, text, font, color=(200,200,200), text_color=(0,0,0)):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0,0,0), rect, 2)
    surf = font.render(text, True, text_color)
    screen.blit(surf, surf.get_rect(center=rect.center))

def select_difficulty():
    """쉬움/HARD 중 선택하여 Difficulty 반환"""
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
        _draw_button(screen, b1, "난이도 : 쉬움", font)
        _draw_button(screen, b2, "난이도 : 어려움", font)
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b1.collidepoint(e.pos): return EASY
                if b2.collidepoint(e.pos): return HARD
        clock.tick(60)
