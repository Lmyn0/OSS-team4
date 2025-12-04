// debuff.js
import { N, S, E, W, DX, DY } from "./maze.js";

// Python DebuffType Enum 대응
export const DebuffType = {
  SLOW: "SLOW",        // 플레이어 속도 감소
  REVERSE: "REVERSE",  // 조작 반전
  TIME_LEFT: "TIME_LEFT" // 남은 게임 시간 차감
};

// Python DebuffItem 그대로
export class DebuffItem {
  /**
   * @param {number} gx - 격자 x
   * @param {number} gy - 격자 y
   * @param {string} dtype - DebuffType 중 하나
   */
  constructor(gx, gy, dtype) {
    this.gx = gx;
    this.gy = gy;
    this.dtype = dtype;
  }
}

// Python DebuffState 대응
export class DebuffState {
  /**
   * @param {number} slowDurationMs     - SLOW 지속 시간(ms)
   * @param {number} reverseDurationMs  - REVERSE 지속 시간(ms)
   * @param {number} slowMultiplier     - 속도 배율 (기본 0.5)
   */
  constructor(slowDurationMs = 5000,
              reverseDurationMs = 5000,
              slowMultiplier = 0.5) {

    // 각 디버프 지속 시간
    this.slow_duration_ms = slowDurationMs;
    this.reverse_duration_ms = reverseDurationMs;

    // 현재 효과가 끝나는 시각(ms)
    this.slow_until_ms = 0;
    this.reverse_until_ms = 0;

    // 속도 감소 배율
    this.slow_multiplier = slowMultiplier;
  }

  is_slow(nowMs) {
    return nowMs < this.slow_until_ms;
  }

  is_reverse(nowMs) {
    return nowMs < this.reverse_until_ms;
  }

  time_left(nowMs, untilMs) {
    return Math.max(0, Math.floor((untilMs - nowMs) / 1000));
  }
}

// ===== 경로 유지 확인용 BFS =====
export function hasPath(grid, w, h, sx, sy, gx, gy) {
  const q = [];
  q.push([sx, sy]);

  const seen = Array.from({ length: h }, () =>
    Array.from({ length: w }, () => false)
  );
  seen[sy][sx] = true;

  while (q.length > 0) {
    const [x, y] = q.shift();
    if (x === gx && y === gy) return true;

    const cell = grid[y][x];
    for (const d of [N, S, E, W]) {
      if (cell & d) {
        const nx = x + DX[d];
        const ny = y + DY[d];
        if (0 <= nx && nx < w && 0 <= ny && ny < h && !seen[ny][nx]) {
          seen[ny][nx] = true;
          q.push([nx, ny]);
        }
      }
    }
  }
  return false;
}

// ===== 출발지점 인접 랜덤 스폰 =====
// rng: () => [0,1) 형태의 난수 함수 (예: Math.random 또는 mulberry32)
function choice(arr, rng) {
  const idx = Math.floor(rng() * arr.length);
  return arr[idx];
}

export function spawnDebuffNearStart(grid, w, h, rng, start = [0, 0]) {
  const [sx, sy] = start;
  const neighbors = [];
  const cell = grid[sy][sx];

  for (const d of [N, S, E, W]) {
    const nx = sx + DX[d];
    const ny = sy + DY[d];
    if (0 <= nx && nx < w && 0 <= ny && ny < h) {
      // 출발지점에서 실제로 이동 가능한 방향만 후보
      if (cell & d) {
        neighbors.push([nx, ny]);
      }
    }
  }

  let candidates = neighbors;
  if (candidates.length === 0) {
    // 혹시 출발이 사방막힘이면 임의로 (0,1) 같은 유효칸 배치
    if (h > 1)      candidates = [[0, 1]];
    else if (w > 1) candidates = [[1, 0]];
    else            candidates = [[0, 0]];
  }

  const [gx, gy] = choice(candidates, rng);
  const dtype = choice(
    [DebuffType.SLOW, DebuffType.TIME_LEFT, DebuffType.REVERSE],
    rng
  );
  return new DebuffItem(gx, gy, dtype);
}

// ===== 아이템 픽업 시 효과 적용 =====
export function applyDebuffOnPickup(
  nowMs,
  state,
  item,
  remainingTimeMs,
  penaltyMs = 5000
) {
  /**
   * - SLOW/REVERSE: 남은 지속시간이 있으면 연장되도록 처리
   * - TIME_LEFT   : 남은 전체 시간에서 penaltyMs 차감하여 반환
   * 반환값: 갱신된 remainingTimeMs
   */

  if (item.dtype === DebuffType.SLOW) {
    const base = Math.max(nowMs, state.slow_until_ms);
    state.slow_until_ms = base + state.slow_duration_ms;
    return remainingTimeMs;
  }

  if (item.dtype === DebuffType.REVERSE) {
    const base = Math.max(nowMs, state.reverse_until_ms);
    state.reverse_until_ms = base + state.reverse_duration_ms;
    return remainingTimeMs;
  }

  if (item.dtype === DebuffType.TIME_LEFT) {
    return Math.max(0, remainingTimeMs - penaltyMs);
  }

  return remainingTimeMs;
}
