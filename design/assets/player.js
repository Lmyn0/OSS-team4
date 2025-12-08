// assets/player.js - 최종 수정본 (순수한 원형 캐릭터 + 랜덤 색상)

import { HARD, selectDifficultyFromKey } from "./difficulty.js";

// 🆕 랜덤 16진수 색상 코드를 생성하는 함수
const generateRandomColor = () => {
    // # 다음에 6자리의 랜덤 16진수를 생성합니다.
    return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
};

export class Player {
    constructor(
        gridX,
        gridY,
        cellSize,
        // 🚨 color 매개변수 제거
        baseSpeed = 2
    ) {
        this.grid_x = gridX;
        this.grid_y = gridY;
        this.cellSize = cellSize;
        
        // 🚨 🆕 랜덤 색상 설정
        this.color = generateRandomColor(); 
        
        this.speed = baseSpeed;
        this.baseSpeed = baseSpeed;

        // 1. 📏 난이도에 따른 플레이어 크기 조정 (난이도 로직 유지)
        const dKey = new URLSearchParams(window.location.search).get("d");
        const difficulty = selectDifficultyFromKey(dKey); 

        let margin;
        if (difficulty === HARD) {
            margin = 2; // HARD 모드: 최소 마진 (2px)
        } else {
            margin = Math.max(2, Math.round(cellSize * 0.15)); // EASY 모드: 마진 적용
        }

        this.size = this.cellSize - margin;

        // 현재 픽셀 위치 (셀 중앙)
        this.pixel_x = gridX * cellSize + cellSize / 2;
        this.pixel_y = gridY * cellSize + cellSize / 2;
        this.target_x = this.pixel_x;
        this.target_y = this.pixel_y;

        this.moving_direction = null;

        // DOM element 생성 (순수한 몸체만)
        this.el = document.createElement("div");
        this.el.className = "player";
        
        // 🚨 🆕 랜덤 색상 적용
        this.el.style.background = this.color;
        
        this.el.style.width = `${this.size}px`;
        this.el.style.height = `${this.size}px`;

        this.updateDom();
    }

    // DOM 위치 업데이트 (셀 중앙 기준)
    updateDom() {
        this.el.style.left = `${this.pixel_x}px`;
        this.el.style.top = `${this.pixel_y}px`;
    }

    // --- 이동 로직 유지 ---
    
    // 이동 시작 시도
    start_move(grid, dir, cellSize) {
        if (this.moving_direction !== null) return;

        const nx = this.grid_x + dir.dx;
        const ny = this.grid_y + dir.dy;

        // 범위 체크 및 벽 체크 로직은 동일
        if (ny < 0 || ny >= grid.length) return;
        if (nx < 0 || nx >= grid[0].length) return;

        const cell = grid[this.grid_y][this.grid_x];
        if ((cell & dir.bit) === 0) {
            return;
        }

        this.grid_x = nx;
        this.grid_y = ny;

        this.target_x = this.grid_x * cellSize + cellSize / 2;
        this.target_y = this.grid_y * cellSize + cellSize / 2;

        this.moving_direction = dir;
    }

    // 매 프레임 호출
    update() {
        if (this.moving_direction === null) {
            this.updateDom();
            return;
        }

        const dx = this.target_x - this.pixel_x;
        const dy = this.target_y - this.pixel_y;
        const dist = Math.hypot(dx, dy);

        if (dist <= this.speed) {
            this.pixel_x = this.target_x;
            this.pixel_y = this.target_y;
            this.moving_direction = null;
        } else {
            this.pixel_x += (dx / dist) * this.speed;
            this.pixel_y += (dy / dist) * this.speed;
        }

        this.updateDom();
    }

    draw() {}
}