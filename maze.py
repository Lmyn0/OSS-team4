import random

class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dir = [(x+1, y),(x-1, y),(x, y+1),(x, y-1)]
        random.shuffle(self.dir)

    def get_cur_pos(self):
        return self.x, self.y
    def get_next_pos(self):
        return self.dir.pop()
def make_maze(size):
    rooms = [[Room(x,y) for x in range(size)] for y in range(size)]
    maze = [['■' for _ in range(size*2+1)] for _ in range(size*2+1)]

    visited = []

    def make(cur_room):
        cx,cy = cur_room.get_cur_pos()
        visited.append((cx,cy))
        maze[cy*2+1][cx*2+1] = '·'
        while cur_room.dir:
            nx, ny = cur_room.get_next_pos()
            if 0 <= nx < size and 0 <= ny < size:
                if(nx,ny) not in visited:
                    wall_x = (2*cx+1 + 2*nx+1)//2
                    wall_y = (2*cy+1 + 2*ny+1)//2
                    maze[wall_y][wall_x] = '·'
                    make(rooms[ny][nx])

    make(rooms[0][0])

    maze[1][0] = ' '
    maze[-2][-1] = ' '
    return maze

def save_maze(maze, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for y in range(len(maze)):
            for x in range(len(maze)):
                file.write(maze[y][x])
            file.write('\n')
def print_maze(maze):
    for row in maze:
        print(''.join(row))

if __name__ == '__main__':
    maze = make_maze(8)
    print_maze(maze)
    save_maze(maze, 'maze.txt')