// difficulty.js

// Python Difficulty 클래스 그대로 변환
export class Difficulty {
  constructor(width, height, cell, timeLimit) {
    this.width = width;      // 미로 가로 칸 수
    this.height = height;    // 미로 세로 칸 수
    this.cell = cell;        // 셀 크기 (픽셀)
    this.time_limit = timeLimit; // 제한 시간 (초)
  }
}

// EASY 난이도
// (EASY: 20x20, 셀 60px, 창 1200x1200)
export const EASY = new Difficulty(20, 20, 60, 180);

// HARD 난이도
// (HARD: 30x30, 셀 50px, 창 1500x1500)
export const HARD = new Difficulty(30, 30, 50, 300);

/**
 * selectDifficultyFromKey(key)
 * - Python의 select_difficulty() 대신,
 *   문자열 키(easy / hard / 1 / 2 ...)로 난이도 리턴
 *
 *   예)
 *   "easy", "low", "1"  → EASY
 *   "hard", "high", "2" → HARD
 *   그 외 / undefined   → 기본 EASY
 */
export function selectDifficultyFromKey(key) {
  if (!key) return EASY;
  const k = String(key).toLowerCase();

  if (["easy", "low", "1"].includes(k)) {
    return EASY;
  }
  if (["hard", "high", "2"].includes(k)) {
    return HARD;
  }

  // 기본값
  return EASY;
}
