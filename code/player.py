# player.py
import pygame
from maze import N, S, E, W, DX, DY

class Player:
    def __init__(self, x, y, color=(0, 0, 255), speed=5): 
        # ... (init, start_move, stop_move, update 함수는 이전과 동일) ...
        self.grid_x = x 
        self.grid_y = y
        self.pixel_x = x * 60 # (임시값, main에서 덮어씀)
        self.pixel_y = y * 60 
        self.color = color
        self.speed = speed 

        self.moving_direction = None 
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y
    
    # ... (start_move, stop_move, update 함수는 변경 없음) ...
    def start_move(self, grid, direction, cell_size):
        if self.pixel_x != self.target_pixel_x or self.pixel_y != self.target_pixel_y:
            return
        cell = grid[self.grid_y][self.grid_x]
        if cell & direction: 
            self.moving_direction = direction
            self.grid_x += DX[direction]
            self.grid_y += DY[direction]
            self.target_pixel_x = self.grid_x * cell_size
            self.target_pixel_y = self.grid_y * cell_size
        else:
            self.moving_direction = None 
    def stop_move(self):
        self.moving_direction = None
    def update(self):
        if self.moving_direction is not None:
            if self.pixel_x < self.target_pixel_x:
                self.pixel_x = min(self.pixel_x + self.speed, self.target_pixel_x)
            elif self.pixel_x > self.target_pixel_x:
                self.pixel_x = max(self.pixel_x - self.speed, self.target_pixel_x)
            if self.pixel_y < self.target_pixel_y:
                self.pixel_y = min(self.pixel_y + self.speed, self.target_pixel_y)
            elif self.pixel_y > self.target_pixel_y:
                self.pixel_y = max(self.pixel_y - self.speed, self.target_pixel_y)
            if self.pixel_x == self.target_pixel_x and self.pixel_y == self.target_pixel_y:
                self.moving_direction = None 

    def draw(self, surface, cell_size):
        draw_x = self.pixel_x + cell_size // 2
        draw_y = self.pixel_y + cell_size // 2
        
        pygame.draw.circle(surface, self.color, (draw_x, draw_y), 12)
