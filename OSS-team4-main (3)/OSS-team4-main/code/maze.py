import random

# Directions
N, S, E, W = 1, 2, 4, 8
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {E: W, W: E, N: S, S: N}

class Tree:
    def __init__(self):
        self.parent = None

    def root(self):
        return self.parent.root() if self.parent else self

    def connected(self, other):
        return self.root() is other.root()

    def connect(self, other):
        other.root().parent = self

def generate_maze(width, height, seed=None):
    rand = random.Random(seed)
    grid = [[0 for _ in range(width)] for _ in range(height)]
    sets = [[Tree() for _ in range(width)] for _ in range(height)]

    edges = []
    for y in range(height):
        for x in range(width):
            if y > 0: edges.append((x, y, N))
            if x > 0: edges.append((x, y, W))

    rand.shuffle(edges)

    while edges:
        x, y, direction = edges.pop()
        nx, ny = x + DX[direction], y + DY[direction]
        set1, set2 = sets[y][x], sets[ny][nx]

        if not set1.connected(set2):
            set1.connect(set2)
            grid[y][x] |= direction
            grid[ny][nx] |= OPPOSITE[direction]

    return grid
