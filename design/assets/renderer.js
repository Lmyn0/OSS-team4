// renderer.js
import { N, S, E, W } from "./maze.js";

/**
 * drawMaze(ctx, grid, cellSize, goal_x, goal_y)
 * - Python draw_maze() 1:1 변환
 */
export function drawMaze(ctx, grid, cellSize, goalX, goalY) {
  const h = grid.length;
  const w = grid[0].length;

  // 배경 흰색
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, w * cellSize, h * cellSize);

  ctx.strokeStyle = "#000000";
  ctx.lineWidth = 2;

  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const cx = x * cellSize;
      const cy = y * cellSize;
      const cell = grid[y][x];

      // 위쪽 벽
      if (!(cell & N)) {
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + cellSize, cy);
        ctx.stroke();
      }
      // 왼쪽 벽
      if (!(cell & W)) {
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx, cy + cellSize);
        ctx.stroke();
      }
      // 아래쪽 벽
      if (!(cell & S)) {
        ctx.beginPath();
        ctx.moveTo(cx, cy + cellSize);
        ctx.lineTo(cx + cellSize, cy + cellSize);
        ctx.stroke();
      }
      // 오른쪽 벽
      if (!(cell & E)) {
        ctx.beginPath();
        ctx.moveTo(cx + cellSize, cy);
        ctx.lineTo(cx + cellSize, cy + cellSize);
        ctx.stroke();
      }
    }
  }

  // 골(빨간 원)
  const gx = goalX * cellSize + cellSize / 2;
  const gy = goalY * cellSize + cellSize / 2;
  const radius = Math.max(6, cellSize / 3);

  ctx.fillStyle = "red";
  ctx.beginPath();
  ctx.arc(gx, gy, radius, 0, Math.PI * 2);
  ctx.fill();
}
/**
 * drawDebuffItems(ctx, items, cellSize)
 * - Python draw_debuff_items() 1:1 변환
 */
export function drawDebuffItems(ctx, items, cellSize) {
  for (const it of items) {
    const cx = it.gx * cellSize + cellSize / 2;
    const cy = it.gy * cellSize + cellSize / 2;
    const r = Math.max(6, cellSize / 3);

    // 속이 찬 검은 원
    ctx.fillStyle = "#000000";
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();

    // 회색 테두리
    ctx.strokeStyle = "rgb(180,180,180)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }
}
/**
 * updateHUD(hudElement, debuffState, nowMs, remainingMs)
 * - Python draw_debuff_hud()와 동일한 정보 표시
 * - HTML DOM으로 HUD를 만든다
 */
export function updateHUD(hudEl, debuffState, nowMs, remainingMs) {
  const lines = [];

  // 전체 남은 시간
  const totalSec = Math.max(0, Math.floor(remainingMs / 1000));
  lines.push([ "TIME LEFT", totalSec + "s" ]);

  // 슬로우
  if (debuffState.is_slow(nowMs)) {
    const sec = debuffState.time_left(nowMs, debuffState.slow_until_ms);
    lines.push([ "SLOW", sec + "s" ]);
  }

  // 역방향
  if (debuffState.is_reverse(nowMs)) {
    const sec = debuffState.time_left(nowMs, debuffState.reverse_until_ms);
    lines.push([ "REVERSE", sec + "s" ]);
  }

  // HTML로 표시
  hudEl.innerHTML = ""; // 초기화

  for (let i = 0; i < lines.length; i++) {
    const [label, value] = lines[i];

    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.justifyContent = "space-between";
    row.style.marginBottom = "4px";

    const labelSpan = document.createElement("span");
    const valueSpan = document.createElement("span");

    if (i === 0) labelSpan.style.color = "yellow";
    else labelSpan.style.color = "rgb(255,180,180)";

    valueSpan.style.color = "rgb(200,220,255)";

    labelSpan.textContent = label + ":";
    valueSpan.textContent = value;

    row.appendChild(labelSpan);
    row.appendChild(valueSpan);

    hudEl.appendChild(row);
  }
}
