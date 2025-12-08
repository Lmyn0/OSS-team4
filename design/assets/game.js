// assets/game.js

import { Boss } from "./boss.js";
import { drawMaze, drawDebuffItems, updateHUD } from "./renderer.js";
import { generateMaze, N, S, E, W } from "./maze.js";
import { Player } from "./player.js"; // player.js의 두 눈 구조 클래스를 import
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

    // ===== 2. 난이도 / 보드 크기 설정 =====
    const params = new URLSearchParams(window.location.search);

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

    const maxCellW = Math.floor(boardRect.width  / width);
    const maxCellH = Math.floor(boardRect.height / height);
    const cellSize = Math.min(difficulty.cell, maxCellW, maxCellH);

    const mazeWidth  = width  * cellSize;
    const mazeHeight = height * cellSize;

    canvas.width  = mazeWidth;
    canvas.height = mazeHeight;
    canvas.style.width  = mazeWidth  + "px";
    canvas.style.height = mazeHeight + "px";

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

    const player = new Player(0, 0, cellSize, "#FF00FF", baseSpeed);
    actorsEl.appendChild(player.el);

    // 도착 지점
    const goalX = width  - 1;
    const goalY = height - 1;

    // ===== 4.5. 보스 생성 (HARD 모드에서만) =====
    let boss = null;

    if (difficulty === HARD) {
        const bx = Math.floor(width / 2);
        const by = Math.floor(height / 2);
        boss = new Boss(bx, by, cellSize, 5);
        // Boss 엘리먼트는 Boss 클래스 내부에서 생성되므로, 여기서 actorsEl에 추가하는 코드는 불필요함
        // 만약 Boss가 DOM 요소를 사용한다면, 여기서 actorsEl.appendChild(boss.el)를 호출해야 함. 
        // 현재는 Boss가 캔버스에 그려진다고 가정하고 DOM 추가는 생략함.
        console.log("💀 HARD MODE → Boss Spawned at", bx, by, "cellSize", cellSize);
    } else {
        console.log("🙂 NOT HARD → no boss");
    }

    // ===== 5. 디버프 상태 / 아이템 상수 및 초기화 =====
    const SLOW_DURATION_MS      = 30_000;
    const REVERSE_DURATION_MS = 15_000;
    const TIME_LEFT_MS          = 30_000;
    const MAX_DEBUFF_ITEMS      = 25;

    const debuffState = new DebuffState(
        SLOW_DURATION_MS,
        REVERSE_DURATION_MS,
        0.5
    );
    let debuffItems = [];

    // 시작 지점 근처 아이템 생성
    const startItem = spawnDebuffNearStart(
        grid,
        width,
        height,
        Math.random,
        [0, 0]
    );
    debuffItems.push(startItem);

    // 기타 랜덤 아이템 생성
    const occupied = new Set();
    function posKey(x, y) {
        return `${x},${y}`;
    }
    occupied.add(posKey(0, 0));
    occupied.add(posKey(goalX, goalY));
    occupied.add(posKey(startItem.gx, startItem.gy));

    let remainingSlots = MAX_DEBUFF_ITEMS - debuffItems.length;
    if (remainingSlots < 0) remainingSlots = 0;

    const totalCells      = width * height;
    const percentBased    = Math.floor(totalCells * 0.05);
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

    // ===== 6. 시간 관련 변수 =====
    const totalLimitMs  = TIME_LIMIT_SECONDS * 1000;
    let startTimeMs     = performance.now();
    let remainingTimeMs = totalLimitMs;

    // ===== 7. 키보드 입력 처리 =====
    const keysDown = new Set();

    window.addEventListener("keydown", (e) => {
        keysDown.add(e.key);

        if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) {
            e.preventDefault();
        }

        // 보스 공격 처리 (스페이스바)
        if (e.key === " ") {
            if (boss && boss.isAlive) {
                const dx = Math.abs(player.grid_x - boss.grid_x);
                const dy = Math.abs(player.grid_y - boss.grid_y);

                // 인접한 셀에 있을 때만 공격 가능
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

    const DIRS = {
        up:    { dx: 0,  dy: -1, bit: N },
        down:  { dx: 0,  dy:  1, bit: S },
        left:  { dx: -1, dy:  0, bit: W },
        right: { dx: 1,  dy:  0, bit: E },
    };

    function handleMovement(nowMs) {
        if (player.moving_direction !== null) return;

        const reverse = debuffState.is_reverse(nowMs);

        let keyUp      = "ArrowUp";
        let keyDownK = "ArrowDown";
        let keyLeft    = "ArrowLeft";
        let keyRight = "ArrowRight";

        // 방향 반전 디버프 적용
        if (reverse) {
            keyUp      = "ArrowDown";
            keyDownK = "ArrowUp";
            keyLeft    = "ArrowRight";
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
    let gameOver      = false;
    let gameOverMessage = "";

    function loop() {
        const nowMs = performance.now();
        let shouldStopLoop = false; // 루프 중단 여부 플래그

        if (!gameOver) {
            const elapsedMs = nowMs - startTimeMs;
            remainingTimeMs = Math.max(0, totalLimitMs - elapsedMs);

            // 1차 시간 초과 체크 및 게임 오버 처리
            if (remainingTimeMs <= 0) {
                gameOver      = true;
                gameOverMessage = "시간 초과!";
                shouldStopLoop = true; 
                // 즉시 lose.html로 리디렉션
                const diffParam = dKey || "easy";
                window.location.href = "lose.html?d=" + encodeURIComponent(diffParam);
            }

            // 속도 디버프 적용
            if (debuffState.is_slow(nowMs)) {
                player.speed = Math.max(
                    1,
                    Math.floor(baseSpeed * debuffState.slow_multiplier)
                );
            } else {
                player.speed = baseSpeed;
            }

            handleMovement(nowMs);

            // 아이템 획득 처리
            if (debuffItems.length > 0) {
                const nextItems = [];

                for (const it of debuffItems) {
                    const picked =
                        player.grid_x === it.gx && player.grid_y === it.gy;

                    if (!picked) {
                        nextItems.push(it);
                        continue;
                    }

                    // 아이템 효과 적용
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

            // 보스 업데이트 (예외 처리 포함)
            if (boss && boss.isAlive && typeof boss.update === "function") {
                try {
                    boss.update();
                } catch (e) {
                    console.error("Boss update error:", e);
                }
            }

            // 플레이어 업데이트
            player.update();

            // 승리 조건 체크
            if (player.grid_x === goalX && player.grid_y === goalY) {
                gameOver = true;
                shouldStopLoop = true;
                console.log("🎉 YOU WIN!");
                // 팝업이나 리디렉션 처리
                setTimeout(() => {
                    window.location.href = "/win";
                }, 300); 
            }
        }

        // 그리기 (게임 오버 여부와 관계없이 마지막 상태를 그림)
        drawMaze(ctx, grid, cellSize, goalX, goalY);
        drawDebuffItems(ctx, debuffItems, cellSize);

        if (boss && boss.isAlive && typeof boss.draw === "function") {
            try {
                boss.draw(ctx);
            } catch (e) {
                console.error("Boss draw error:", e);
            }
        }

        player.draw(cellSize);
        updateHUD(hudEl, debuffState, nowMs, remainingTimeMs);

        // 🚨 다음 프레임 요청: 게임 오버 상태가 아닐 때만 요청하며, 시간 초과 시 리디렉션 되었으므로 여기는 실행되지 않음
        if (!gameOver && !shouldStopLoop) {
            requestAnimationFrame(loop);
        }
    }

    loop();
});