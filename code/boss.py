import pygame
import math

class Boss:
    def __init__(self, x, y, cell_size, max_hp=5):
        # 1. 요청하신 속성 추가
        self.x = x          # 셀 좌표 x
        self.y = y          # 셀 좌표 y
        self.max_hp = max_hp
        self.hp = max_hp
        self.is_alive = True

        # 기존 렌더링용 변수 유지
        self.cell_size = cell_size
        self.pixel_x = x * cell_size
        self.pixel_y = y * cell_size
        
        # 애니메이션용 변수
        self.anim_timer = 0

    def take_damage(self, amount):
        """데미지를 입는 함수"""
        if not self.is_alive:
            return

        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def update(self):
        """살아있을 때만 애니메이션 재생"""
        if self.is_alive:
            self.anim_timer += 0.1

    def draw(self, surface):
        # 죽었으면 그리지 않음
        if not self.is_alive:
            return

        # 1. 보스 본체 그리기 (기존 코드와 동일)
        pulse = math.sin(self.anim_timer) * 2
        rect_size = self.cell_size - 8 + pulse
        offset = (self.cell_size - rect_size) / 2
        
        rect = pygame.Rect(
            self.pixel_x + offset, 
            self.pixel_y + offset, 
            rect_size, 
            rect_size
        )
        
        pygame.draw.rect(surface, (200, 0, 0), rect, border_radius=5)
        
        # 눈 그리기
        eye_radius = rect_size / 6
        eye_offset_x = rect_size * 0.25
        eye_offset_y = rect_size * 0.3
        
        pygame.draw.circle(surface, (255, 255, 0), (int(rect.x + eye_offset_x), int(rect.y + eye_offset_y)), int(eye_radius))
        pygame.draw.circle(surface, (255, 255, 0), (int(rect.right - eye_offset_x), int(rect.y + eye_offset_y)), int(eye_radius))

        # 2. HP 바 그리기 (머리 위)
        self._draw_health_bar(surface)

    def _draw_health_bar(self, surface):
        bar_width = self.cell_size
        bar_height = 6
        bar_x = self.pixel_x
        bar_y = self.pixel_y - 10  # 보스 머리 위 10픽셀

        # 체력 비율 계산
        ratio = self.hp / self.max_hp
        fill_width = int(bar_width * ratio)

        # 배경 (검은색)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect)

        # 체력 (초록색 ~ 빨간색 그라데이션 대신 단순 초록/빨강 처리)
        color = (0, 255, 0) if ratio > 0.3 else (255, 0, 0)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(surface, color, fill_rect)