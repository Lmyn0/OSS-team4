// debuff.js (최종 버전: Reverse 5초 기본값 설정)

import { N, S, E, W, DX, DY } from "./maze.js";

// =====================================================
// DebuffType (Python Enum 대응)
// =====================================================
export const DebuffType = {
  SLOW: "SLOW",          // 플레이어 속도 감소
  REVERSE: "REVERSE",    // 조작 반전
  TIME_LEFT: "TIME_LEFT" // 남은 게임 시간 차감
};

// =====================================================
// DebuffItem
// =====================================================
export class DebuffItem {
  constructor(gx, gy, dtype) {
    this.gx = gx;
    this.gy = gy;
    this.dtype = dtype;
  }
}

// =====================================================
// DebuffState (지속 시간 및 배율 관리)
// =====================================================
export class DebuffState {
  constructor(
    slowDurationMs = 15000,
    reverseDurationMs = 5000, // 🚨 수정: REVERSE 지속 5초로 변경
    slowMultiplier = 0.1      // 🚨 SLOW 배율 0.1 (더 느리게)
  ) {
    this.slow_duration_ms = slowDurationMs;
    this.reverse_duration_ms = reverseDurationMs;

    this.slow_until_ms = 0;
    this.reverse_until_ms = 0;

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

// =====================================================
// BFS: 특정 경로가 존재하는지 확인
// =====================================================
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

        if (
          0 <= nx && nx < w &&
          0 <= ny && ny < h &&
          !seen[ny][nx]
        ) {
          seen[ny][nx] = true;
          q.push([nx, ny]);
        }
      }
    }
  }
  return false;
}

// =====================================================
// Helper: 배열에서 랜덤 선택
// =====================================================
function choice(arr, rng) {
  const idx = Math.floor(rng() * arr.length);
  return arr[idx];
}

// =====================================================
// Debuff Spawn: 출발지점 근처에 무작위 배치
// =====================================================
export function spawnDebuffNearStart(grid, w, h, rng, start = [0, 0]) {
  const [sx, sy] = start;
  const neighbors = [];
  const cell = grid[sy][sx];

  // 출발지에서 실제 이동 가능한 방향만 후보
  for (const d of [N, S, E, W]) {
    const nx = sx + DX[d];
    const ny = sy + DY[d];

    if (0 <= nx && nx < w && 0 <= ny && ny < h) {
      if (cell & d) {
        neighbors.push([nx, ny]);
      }
    }
  }

  // 사방막힘 방지용 fallback
  let candidates = neighbors;
  if (candidates.length === 0) {
    if (h > 1) {
      candidates = [[0, 1]];
    } else if (w > 1) {
      candidates = [[1, 0]];
    } else {
      candidates = [[0, 0]];
    }
  }

  const [gx, gy] = choice(candidates, rng);
  const dtype = choice(
    [DebuffType.SLOW, DebuffType.TIME_LEFT, DebuffType.REVERSE],
    rng
  );

  return new DebuffItem(gx, gy, dtype);
}

// =====================================================
// Debuff 적용 (pickup 시)
// =====================================================
export function applyDebuffOnPickup(
  nowMs,
  state,
  item,
  remainingTimeMs,
  penaltyMs = 30000
) {
  // SLOW: 기존 지속시간과 비교 후 연장
  if (item.dtype === DebuffType.SLOW) {
    const base = Math.max(nowMs, state.slow_until_ms);
    state.slow_until_ms = base + state.slow_duration_ms;
    return remainingTimeMs;
  }

  // REVERSE: 기존 reverse_until_ms와 비교하여 연장
  if (item.dtype === DebuffType.REVERSE) {
    const base = Math.max(nowMs, state.reverse_until_ms);
    state.reverse_until_ms = base + state.reverse_duration_ms;
    return remainingTimeMs;
  }

  // TIME_LEFT: 남은 시간 패널티 적용
  if (item.dtype === DebuffType.TIME_LEFT) {
    return Math.max(0, remainingTimeMs - penaltyMs);
  }

  return remainingTimeMs;
}
