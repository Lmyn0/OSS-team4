// maze.js

// 방향 상수 (Python과 동일한 값)
export const N = 1, S = 2, E = 4, W = 8;
export const DX = { [E]: 1, [W]: -1, [N]: 0, [S]: 0 };
export const DY = { [E]: 0, [W]: 0, [N]: -1, [S]: 1 };
export const OPPOSITE = { [E]: W, [W]: E, [N]: S, [S]: N };

// 간단한 시드 난수 생성기 (Python random.Random(seed) 대신)
function mulberry32(a) {
  return function() {
    let t = a += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

class Tree {
  constructor() {
    this.parent = null;
  }
  root() {
    return this.parent ? this.parent.root() : this;
  }
  connected(other) {
    return this.root() === other.root();
  }
  connect(other) {
    other.root().parent = this;
  }
}

export function generateMaze(width, height, seed = null) {
  const grid = Array.from({ length: height }, () =>
    Array.from({ length: width }, () => 0)
  );
  const sets = Array.from({ length: height }, () =>
    Array.from({ length: width }, () => new Tree())
  );

  // 랜덤 생성기
  let rng = Math.random;
  if (seed !== null && seed !== undefined) {
    rng = mulberry32(seed >>> 0);
  }

  const edges = [];
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (y > 0) edges.push({ x, y, dir: N });
      if (x > 0) edges.push({ x, y, dir: W });
    }
  }

  // 셔플
  for (let i = edges.length - 1; i > 0; i--) {
    const j = (rng() * (i + 1)) | 0;
    [edges[i], edges[j]] = [edges[j], edges[i]];
  }

  // Kruskal
  while (edges.length > 0) {
    const { x, y, dir } = edges.pop();
    const nx = x + DX[dir];
    const ny = y + DY[dir];

    const set1 = sets[y][x];
    const set2 = sets[ny][nx];

    if (!set1.connected(set2)) {
      set1.connect(set2);
      grid[y][x] |= dir;
      grid[ny][nx] |= OPPOSITE[dir];
    }
  }

  return grid; // grid[y][x]는 Python과 동일한 비트 구조
}
