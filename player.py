# player.py
import pygame
from maze import DX, DY  # 공통 델타 재사용

PLAYER_COLOR = (255, 0, 0)

class Player:
    def __init__(self, x, y, color=PLAYER_COLOR):
        self.x = x
        self.y = y
        self.color = color

    def move(self, grid, direction):
        """해당 방향으로 길이 뚫려 있으면 이동"""
        cell_bits = grid[self.y][self.x]
        if cell_bits & direction:
            self.x += DX[direction]
            self.y += DY[direction]

    def draw(self, surface, cell_size):
        cx = self.x * cell_size + cell_size // 2
        cy = self.y * cell_size + cell_size // 2
        pygame.draw.circle(surface, self.color, (cx, cy), cell_size // 3)
