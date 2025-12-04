// assets/game.js

import { Boss } from "./boss.js";
import { drawMaze, drawDebuffItems, updateHUD } from "./renderer.js";
import { generateMaze, N, S, E, W } from "./maze.js";
import { Player } from "./player.js";
import {
  DebuffType,
  DebuffState,
  DebuffItem,
  spawnDebuffNearStart,
} from "./debuff.js";
import { EASY, HARD, selectDifficultyFromKey } from "./difficulty.js";

window.addEventListener("DOMContentLoaded", () => {
  // ===== 1. DOM 요소 준비 =====
  const canvas   = document.getElementById("gridCanvas");
  const ctx      = canvas.getContext("2d");
  const hudEl    = document.getElementById("hud");
  const actorsEl = document.getElementById("actors");
  const boardEl  = document.getElementById("board");

  if (!canvas || !ctx || !hudEl || !actorsEl || !boardEl) {
    console.error("필수 DOM 요소(gridCanvas, hud, actors, board)를 찾지 못했습니다.");
    return;
  }

  // ===== 2. 난이도 / 보드 크기 =====
  const params = new URLSearchParams(window.location.search);

  // d=hard, mode=hard, difficulty=hard, level=hard 다 받아주기
  const dKey =
    params.get("d") ||
    params.get("mode") ||
    params.get("difficulty") ||
    params.get("level");

  console.log("[DIFF] raw key =", dKey);

  const difficulty = selectDifficultyFromKey(dKey); // EASY or HARD 객체

  console.log(
    "[DIFF] selected difficulty:",
    difficulty,
    "is HARD?",
    difficulty === HARD
  );

  const width              = difficulty.width;
  const height             = difficulty.height;
  const TIME_LIMIT_SECONDS = difficulty.time_limit;

  const boardRect = boardEl.getBoundingClientRect();

  // 보드 안에 전부 들어가도록 cellSize 결정
  const maxCellW = Math.floor(boardRect.width  / width);
  const maxCellH = Math.floor(boardRect.height / height);
  const cellSize = Math.min(difficulty.cell, maxCellW, maxCellH);

  // 캔버스 실제 크기
  const mazeWidth  = width  * cellSize;
  const mazeHeight = height * cellSize;

  canvas.width  = mazeWidth;
  canvas.height = mazeHeight;
  canvas.style.width  = mazeWidth  + "px";
  canvas.style.height = mazeHeight + "px";

  // 보드 안에서 중앙 정렬
  const offsetX = (boardRect.width  - mazeWidth)  / 2;
  const offsetY = (boardRect.height - mazeHeight) / 2;

  canvas.style.left   = offsetX + "px";
  canvas.style.top    = offsetY + "px";
  actorsEl.style.left = offsetX + "px";
  actorsEl.style.top  = offsetY + "px";

  // ===== 3. 미로 생성 =====
  const seed = (Date.now() & 0xffffffff) >>> 0;
  const grid = generateMaze(width, height, seed);

  // ===== 4. 플레이어 생성 =====
  const baseSpeed = Math.max(1, Math.floor(cellSize / 8));
  const player    = new Player(0, 0, cellSize, "#FF00FF", baseSpeed);
  actorsEl.appendChild(player.el);

  const goalX = width  - 1;
  const goalY = height - 1;

  // ===== 4.5. 보스 생성 (HARD 모드에서만) =====
  let boss = null;

  if (difficulty === HARD) {
    const bx = Math.floor(width / 2);
    const by = Math.floor(height / 2);
    boss = new Boss(bx, by, cellSize, 5);
    console.log("💀 HARD MODE → Boss Spawned at", bx, by, "cellSize", cellSize);
  } else {
    console.log("🙂 NOT HARD → no boss");
  }

  // ===== 5. 디버프 상태 / 아이템 =====
  const SLOW_DURATION_MS    = 30_000;
  const REVERSE_DURATION_MS = 15_000;
  const TIME_LEFT_MS        = 30_000;
  const MAX_DEBUFF_ITEMS    = 25;

  const debuffState = new DebuffState(
    SLOW_DURATION_MS,
    REVERSE_DURATION_MS,
    0.5 // 속도 50%
  );
  let debuffItems = [];

  // 시작점 근처 하나
  const startItem = spawnDebuffNearStart(
    grid,
    width,
    height,
    Math.random,
    [0, 0]
  );
  debuffItems.push(startItem);

  // 이미 사용된 위치 기록
  const occupied = new Set();
  function posKey(x, y) {
    return `${x},${y}`;
  }
  occupied.add(posKey(0, 0));                     // 시작점
  occupied.add(posKey(goalX, goalY));             // 도착점
  occupied.add(posKey(startItem.gx, startItem.gy));

  // 추가 아이템 배치
  let remainingSlots = MAX_DEBUFF_ITEMS - debuffItems.length;
  if (remainingSlots < 0) remainingSlots = 0;

  const totalCells      = width * height;
  const percentBased    = Math.floor(totalCells * 0.05); // 맵 5% 정도
  const targetItemCount = Math.min(remainingSlots, percentBased);

  let added = 0;
  while (added < targetItemCount) {
    const rx = Math.floor(Math.random() * width);
    const ry = Math.floor(Math.random() * height);
    if (!occupied.has(posKey(rx, ry))) {
      const types = [
        DebuffType.SLOW,
        DebuffType.TIME_LEFT,
        DebuffType.REVERSE,
      ];
      const dtype = types[Math.floor(Math.random() * types.length)];
      debuffItems.push(new DebuffItem(rx, ry, dtype));
      occupied.add(posKey(rx, ry));
      added++;
    }
  }

  console.log(`디버프 아이템 총 ${debuffItems.length}개 배치됨.`);

  // ===== 6. 시간 관련 =====
  const totalLimitMs  = TIME_LIMIT_SECONDS * 1000;
  let startTimeMs     = performance.now();
  let remainingTimeMs = totalLimitMs;

  // ===== 7. 키보드 입력 처리 =====
  const keysDown = new Set();

  window.addEventListener("keydown", (e) => {
    keysDown.add(e.key);

    // 방향키 기본 스크롤 방지
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) {
      e.preventDefault();
    }

    // === 스페이스바 공격 ===
    if (e.key === " ") {
      if (boss && boss.isAlive) {
        const dx = Math.abs(player.grid_x - boss.grid_x);
        const dy = Math.abs(player.grid_y - boss.grid_y);

        if (dx + dy <= 1) {
          boss.takeDamage(1);
          console.log(`Boss HP: ${boss.hp}/${boss.maxHP}`);
        }
      }
    }
  });

  window.addEventListener("keyup", (e) => {
    keysDown.delete(e.key);
  });

  // === 방향 벡터 (N,S,E,W 비트 + 이동량) ===
  const DIRS = {
    up:    { dx: 0,  dy: -1, bit: N },
    down:  { dx: 0,  dy:  1, bit: S },
    left:  { dx: -1, dy:  0, bit: W },
    right: { dx: 1,  dy:  0, bit: E },
  };

  function handleMovement(nowMs) {
    if (player.moving_direction !== null) return;

    const reverse = debuffState.is_reverse(nowMs);

    let keyUp    = "ArrowUp";
    let keyDownK = "ArrowDown";
    let keyLeft  = "ArrowLeft";
    let keyRight = "ArrowRight";

    if (reverse) {
      keyUp    = "ArrowDown";
      keyDownK = "ArrowUp";
      keyLeft  = "ArrowRight";
      keyRight = "ArrowLeft";
    }

    let dir = null;

    if (keysDown.has(keyUp)) {
      dir = DIRS.up;
    } else if (keysDown.has(keyDownK)) {
      dir = DIRS.down;
    } else if (keysDown.has(keyLeft)) {
      dir = DIRS.left;
    } else if (keysDown.has(keyRight)) {
      dir = DIRS.right;
    }

    if (dir) {
      player.start_move(grid, dir, cellSize);
    }
  }

  // ===== 8. 게임 루프 =====
  let gameOver        = false;
  let gameOverMessage = "";

  function loop() {
    const nowMs = performance.now();

    if (!gameOver) {
      const elapsedMs = nowMs - startTimeMs;
      remainingTimeMs = Math.max(0, totalLimitMs - elapsedMs);

      if (remainingTimeMs <= 0) {
        gameOver        = true;
        gameOverMessage = "시간 초과!";
      }

      if (debuffState.is_slow(nowMs)) {
        player.speed = Math.max(
          1,
          Math.floor(baseSpeed * debuffState.slow_multiplier)
        );
      } else {
        player.speed = baseSpeed;
      }

      handleMovement(nowMs);

      if (debuffItems.length > 0) {
        const nextItems = [];

        for (const it of debuffItems) {
          const picked =
            player.grid_x === it.gx && player.grid_y === it.gy;

          if (!picked) {
            nextItems.push(it);
            continue;
          }

          if (it.dtype === DebuffType.SLOW) {
            debuffState.slow_until_ms = Math.max(
              nowMs,
              debuffState.slow_until_ms
            ) + SLOW_DURATION_MS;
          } else if (it.dtype === DebuffType.REVERSE) {
            debuffState.reverse_until_ms = Math.max(
              nowMs,
              debuffState.reverse_until_ms
            ) + REVERSE_DURATION_MS;
          } else if (it.dtype === DebuffType.TIME_LEFT) {
            const newRemaining = Math.max(0, remainingTimeMs - TIME_LEFT_MS);
            const elapsedAfter = totalLimitMs - newRemaining;
            startTimeMs        = nowMs - elapsedAfter;
            remainingTimeMs    = newRemaining;
          }
        }

        debuffItems = nextItems;
      }

      if (boss && boss.isAlive) {
        boss.update();
      }

      player.update();

      if (player.grid_x === goalX && player.grid_y === goalY) {
        gameOver = true;
        console.log("🎉 YOU WIN!");
        setTimeout(() => {
          window.location.href = "win.html";
        }, 300);
      }
    }

    // --- 그리기 ---
    drawMaze(ctx, grid, cellSize, goalX, goalY);
    drawDebuffItems(ctx, debuffItems, cellSize);

    if (boss && boss.isAlive) {
      boss.draw(ctx);
    }

    player.draw(cellSize);

updateHUD(hudEl, debuffState, nowMs, remainingTimeMs);

if (remainingTimeMs <= 0) {
  gameOver        = true;
  gameOverMessage = "시간 초과!";

  setTimeout(() => {
    const diffParam = dKey || "easy";
    window.location.href = "lose.html?d=" + encodeURIComponent(diffParam);
  }, 300);
}

// 🔥 여기! requestAnimationFrame 복원
requestAnimationFrame(loop);
}

loop();
});
