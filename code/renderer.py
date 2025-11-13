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
