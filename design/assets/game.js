// assets/game.js (최종 버전: Hard 모드 Slow 배율 0.5 적용 및 최소 속도 제한 1 보장)

import { Boss } from "./boss.js";
// 🚨 수정: drawAttackItems 함수를 import에 추가
import { drawMaze, drawDebuffItems, drawAttackItems, updateHUD } from "./renderer.js"; 
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
    // ===== 1. DOM 요소 준비 (생략) =====
    const canvas    = document.getElementById("gridCanvas");
    const ctx       = canvas.getContext("2d");
    const hudEl     = document.getElementById("hud");
    const actorsEl  = document.getElementById("actors");
    const boardEl   = document.getElementById("board");

    if (!canvas || !ctx || !hudEl || !actorsEl || !boardEl) {
        console.error("필수 DOM 요소(gridCanvas, hud, actors, board)를 찾지 못했습니다.");
        return;
    }

    // ===== 2. 난이도 / 보드 크기 설정 (생략) =====
    const params = new URLSearchParams(window.location.search);
    const dKey =
        params.get("d") ||
        params.get("mode") ||
        params.get("difficulty") ||
        params.get("level");

    const difficulty = selectDifficultyFromKey(dKey); 
    const width                 = difficulty.width;
    const height                = difficulty.height;
    const TIME_LIMIT_SECONDS = difficulty.time_limit;

    const boardRect = boardEl.getBoundingClientRect();
    const maxCellW = Math.floor(boardRect.width     / width);
    const maxCellH = Math.floor(boardRect.height / height);
    const cellSize = Math.min(difficulty.cell, maxCellW, maxCellH);

    const mazeWidth     = width     * cellSize;
    const mazeHeight = height * cellSize;

    canvas.width    = mazeWidth;
    canvas.height = mazeHeight;
    canvas.style.width  = mazeWidth     + "px";
    canvas.style.height = mazeHeight + "px";

    const offsetX = (boardRect.width    - mazeWidth)    / 2;
    const offsetY = (boardRect.height - mazeHeight) / 2;

    canvas.style.left   = offsetX + "px";
    canvas.style.top    = offsetY + "px";
    actorsEl.style.left = offsetX + "px";
    actorsEl.style.top  = offsetY + "px";

    // ===== 3. 미로 생성 (생략) =====
    const seed = (Date.now() & 0xffffffff) >>> 0;
    const grid = generateMaze(width, height, seed);

    // ===== 4. 플레이어 생성 (생략) =====
    const baseSpeed = Math.max(1, Math.floor(cellSize / 8));
    const player = new Player(0, 0, cellSize, "#FF00FF", baseSpeed);
    actorsEl.appendChild(player.el);

    // 도착 지점
    const goalX = width     - 1;
    const goalY = height - 1;

    // ===== 4.5. 보스 및 공격 아이템 초기화 =====
    let boss = null;
    let attackCharges = 0; // 🚨 공격 횟수 초기화
    let attackItems = [];  // 🚨 공격 아이템 위치 목록

    if (difficulty === HARD) {
        const bx = Math.floor(width / 2);
        const by = Math.floor(height / 2);
        boss = new Boss(bx, by, cellSize, 5);
        console.log("💀 HARD MODE → Boss Spawned at", bx, by, "cellSize", cellSize);
    } else {
        console.log("🙂 NOT HARD → no boss");
    }

    // ===== 5. 디버프 상태 / 아이템 상수 및 초기화 =====
    const TIME_LEFT_PENALTY_MS = 15000; // 시간 페널티 (기존값 유지)
    const MAX_DEBUFF_ITEMS   = 25;

    // 🚨 [수정된 로직] 난이도에 따라 Slow 배율 설정
    let slowMultiplier = 0.1; // EASY/NORMAL 기본 배율 (debuff.js의 기본값)
    const reverseDurationMs = 15000; // debuff.js에서 설정된 15초
    const slowDurationMs = 15000; // debuff.js에서 설정된 15초

    if (difficulty === HARD) {
        // 🚨 최종 수정: HARD 모드 SLOW 배율을 0.5로 설정
        slowMultiplier = 0.5; 
    }

    // DebuffState 생성: 설정한 Slow 배율을 전달하여 초기화
    const debuffState = new DebuffState(slowDurationMs, reverseDurationMs, slowMultiplier); 
    let debuffItems = [];

    // 시작 지점 근처 디버프 아이템 생성 (생략)
    const startItem = spawnDebuffNearStart(
        grid,
        width,
        height,
        Math.random,
        [0, 0]
    );
    debuffItems.push(startItem);

    // 기타 랜덤 아이템 생성을 위한 Set
    const occupied = new Set();
    function posKey(x, y) {
        return `${x},${y}`;
    }
    occupied.add(posKey(0, 0));
    occupied.add(posKey(goalX, goalY));
    occupied.add(posKey(startItem.gx, startItem.gy));

    // 디버프 아이템 랜덤 배치 (생략)
    let remainingSlots = MAX_DEBUFF_ITEMS - debuffItems.length;
    if (remainingSlots < 0) remainingSlots = 0;

    const totalCells        = width * height;
    const percentBased  = Math.floor(totalCells * 0.05);
    const targetDebuffCount = Math.min(remainingSlots, percentBased);

    let addedDebuff = 0;
    while (addedDebuff < targetDebuffCount) {
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
            addedDebuff++;
        }
    }

    // 🚨 3. 공격 아이템 스폰 로직 추가 (HARD 모드에서만, 랜덤 위치)
    if (difficulty === HARD) {
        const ATTACK_ITEM_COUNT = 5; 
        
        let addedAttack = 0;
        while (addedAttack < ATTACK_ITEM_COUNT) {
            const rx = Math.floor(Math.random() * width);
            const ry = Math.floor(Math.random() * height);
            if (!occupied.has(posKey(rx, ry))) {
                attackItems.push({ gx: rx, gy: ry }); // 공격 아이템 위치 저장
                occupied.add(posKey(rx, ry));
                addedAttack++;
            }
        }
    }

    console.log(`디버프 아이템 총 ${debuffItems.length}개 배치됨.`);
    if (difficulty === HARD) {
        console.log(`공격 아이템 총 ${attackItems.length}개 배치됨.`);
    }


    // ===== 6. 시간 관련 변수 및 PAUSE 기능 추가 =====
    const totalLimitMs  = TIME_LIMIT_SECONDS * 1000;
    let startTimeMs         = performance.now();
    let remainingTimeMs = totalLimitMs;
    
    let isPaused = false; 
    let animationFrameId = null;
    let nowMs = 0;

    const gameInstance = {
        pause: () => {
            isPaused = true;
            console.log("Game state set to PAUSED.");
        },
        resume: () => {
            if (isPaused) {
                const pauseDurationMs = performance.now() - nowMs;
                startTimeMs += pauseDurationMs;
                isPaused = false;
                console.log("Game state set to RUNNING.");
                requestAnimationFrame(loop); 
            }
        },
    };
    
    window.gameInstance = gameInstance;


    // ===== 7. 키보드 입력 처리 =====
    const keysDown = new Set();

    window.addEventListener("keydown", (e) => {
        if (isPaused && e.key !== 'Escape') return; 
        
        keysDown.add(e.key);

        if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) {
            e.preventDefault();
        }

        // 🚨 5. SPACE 공격 로직 수정 (HARD 모드, 공격 횟수, 인접 여부 확인)
        if (e.key === " " && !isPaused) { 
            if (difficulty === HARD && boss && boss.isAlive && attackCharges > 0) {
                const px = player.grid_x;
                const py = player.grid_y;
                const bx = boss.grid_x; 
                const by = boss.grid_y;
                
                const dx = Math.abs(px - bx);
                const dy = Math.abs(py - by);

                // 인접 셀 (상하좌우) 또는 동일 셀에 있을 때 공격 가능 (파이썬 로직 반영)
                if ((dx === 0 && dy === 0) || dx + dy === 1) { 
                    boss.takeDamage(1);
                    attackCharges -= 1; // 공격 횟수 차감
                    console.log(`Boss HP: ${boss.hp}/${boss.maxHP}, Charges Left: ${attackCharges}`);
                }
            }
        }
    });

    window.addEventListener("keyup", (e) => {
        keysDown.delete(e.key);
    });

    const DIRS = {
        up:     { dx: 0,    dy: -1, bit: N },
        down:   { dx: 0,    dy:     1, bit: S },
        left:   { dx: -1, dy:   0, bit: W },
        right: { dx: 1,     dy:     0, bit: E },
    };

    function handleMovement(nowMs) {
        if (player.moving_direction !== null) return;

        const reverse = debuffState.is_reverse(nowMs);
        
        let keyUp       = "ArrowUp";
        let keyDownK = "ArrowDown";
        let keyLeft     = "ArrowLeft";
        let keyRight = "ArrowRight";

        if (reverse) {
            keyUp       = "ArrowDown";
            keyDownK = "ArrowUp";
            keyLeft     = "ArrowRight";
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
    let gameOver        = false;
    let gameOverMessage = "";

    function loop(timestamp) {
        nowMs = timestamp;
        
        if (isPaused) {
            // 일시 정지 중에는 그리기만 업데이트
            drawMaze(ctx, grid, cellSize, goalX, goalY);
            if (difficulty === HARD) drawAttackItems(ctx, attackItems, cellSize); // 🚨 공격 아이템 그리기
            drawDebuffItems(ctx, debuffItems, cellSize);
            if (boss && boss.isAlive && typeof boss.draw === "function") boss.draw(ctx);
            player.draw(cellSize);
            updateHUD(hudEl, debuffState, nowMs, remainingTimeMs, attackCharges); // 🚨 attackCharges 전달
            return; 
        }
        
        // 로직 업데이트
        if (!gameOver) {
            const elapsedMs = nowMs - startTimeMs;
            remainingTimeMs = Math.max(0, totalLimitMs - elapsedMs);

            // 시간 초과 체크
            if (remainingTimeMs <= 0) {
                gameOver        = true;
                const diffParam = dKey || "easy";
                window.location.href = "lose.html?d=" + encodeURIComponent(diffParam);
                return; 
            }

            // 속도 디버프 적용 (SLOW 15초 반영)
            if (debuffState.is_slow(nowMs)) {
                // 🚨 최종 수정: Math.max(1, ...)를 다시 추가하여 최소 속도를 1로 보장합니다.
                player.speed = Math.max(
                    1,
                    Math.floor(baseSpeed * debuffState.slow_multiplier)
                );
            } else {
                player.speed = baseSpeed;
            }

            handleMovement(nowMs);

            // 4. 공격 아이템 획득 로직 추가 (HARD 모드에서만)
            if (difficulty === HARD && attackItems.length > 0) {
                const nextAttackItems = [];

                for (const it of attackItems) {
                    const picked =
                        player.grid_x === it.gx && player.grid_y === it.gy;

                    if (picked) {
                        attackCharges += 1; // 🚨 공격 횟수 증가
                    } else {
                        nextAttackItems.push(it);
                    }
                }
                attackItems = nextAttackItems;
            }

            // 디버프 아이템 획득 처리 (기존 로직 유지)
            if (debuffItems.length > 0) {
                const nextItems = [];
                for (const it of debuffItems) {
                    const picked = player.grid_x === it.gx && player.grid_y === it.gy;
                    if (!picked) {
                        nextItems.push(it);
                        continue;
                    }
                    
                    // 아이템 효과 적용 (SLOW 15초 반영)
                    if (it.dtype === DebuffType.SLOW) {
                        debuffState.slow_until_ms = Math.max(nowMs, debuffState.slow_until_ms) + debuffState.slow_duration_ms; 
                    } else if (it.dtype === DebuffType.REVERSE) {
                        debuffState.reverse_until_ms = Math.max(nowMs, debuffState.reverse_until_ms) + debuffState.reverse_duration_ms; 
                    } else if (it.dtype === DebuffType.TIME_LEFT) {
                        const newRemaining = Math.max(0, remainingTimeMs - TIME_LEFT_PENALTY_MS);
                        const elapsedAfter = totalLimitMs - newRemaining;
                        startTimeMs             = nowMs - elapsedAfter;
                        remainingTimeMs         = newRemaining;
                    }
                }
                debuffItems = nextItems;
            }

            // 보스 업데이트 (생략)
            if (boss && boss.isAlive && typeof boss.update === "function") {
                try {
                    boss.update();
                } catch (e) {
                    console.error("Boss update error:", e);
                }
            }

            // 플레이어 업데이트
            player.update();

            // 🚨 승리 조건 체크 (수정된 로직)
            if (player.grid_x === goalX && player.grid_y === goalY) {
                
                // Hard 모드이고 보스가 살아있다면 승리 불가능
                const bossMustBeDefeated = (difficulty === HARD && boss && boss.isAlive);
                
                if (bossMustBeDefeated) {
                    // 보스가 살아있다면 통과하지 못하고 메시지만 출력
                    console.log("Boss is alive! Must defeat the boss first.");
                } else {
                    // Easy/Normal 모드이거나, Hard 모드에서 보스가 사망했을 경우 승리
                    gameOver = true;
                    console.log("🎉 YOU WIN!");
                    setTimeout(() => {
                        window.location.href = `win.html?d=${encodeURIComponent(dKey || 'easy')}`;
                    }, 300); 
                    return; // 게임 루프 종료
                }
            }
        }

        // 그리기
        drawMaze(ctx, grid, cellSize, goalX, goalY);
        
        // 🚨 6. 공격 아이템 그리기 호출 (HARD 모드에서만)
        if (difficulty === HARD) {
            // drawAttackItems 함수가 assets/renderer.js에 구현되어 있어야 함
            if (typeof drawAttackItems === 'function') {
                drawAttackItems(ctx, attackItems, cellSize);
            }
        }

        drawDebuffItems(ctx, debuffItems, cellSize);

        if (boss && boss.isAlive && typeof boss.draw === "function") {
            try {
                boss.draw(ctx);
            } catch (e) {
                console.error("Boss draw error:", e);
            }
        }

        player.draw(cellSize);
        
        // 🚨 7. updateHUD 호출 시 attackCharges 전달 (renderer.js의 함수 시그니처 수정 필요)
        updateHUD(hudEl, debuffState, nowMs, remainingTimeMs, attackCharges);

        // 다음 프레임 요청
        animationFrameId = requestAnimationFrame(loop);
    }

    animationFrameId = requestAnimationFrame(loop);
});