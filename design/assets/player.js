// assets/player.js
export class Player {
  constructor(gridX, gridY, cellSize, color = "#d9d9d9", baseSpeed = 2) {
    this.grid_x = gridX;
    this.grid_y = gridY;
    this.cellSize = cellSize;

    this.color = color;
    this.speed = baseSpeed;
    this.baseSpeed = baseSpeed;

    // 현재 픽셀 위치 (셀 중앙 기준)
    this.pixel_x = gridX * cellSize + cellSize / 2;
    this.pixel_y = gridY * cellSize + cellSize / 2;
    this.target_x = this.pixel_x;
    this.target_y = this.pixel_y;

    // 이동 중인지 여부 (null이면 정지)
    this.moving_direction = null;  // dir 객체 그대로 저장

    // DOM 엘리먼트 생성 (player.css에서 스타일 입힘)
    this.el = document.createElement("div");
    this.el.className = "player";
    this.el.style.background = this.color;

    const eye = document.createElement("div");
    eye.className = "eye";
    this.el.appendChild(eye);

    this.updateDom();
  }

  // DOM 위치 갱신
  updateDom() {
    this.el.style.left = `${this.pixel_x}px`;
    this.el.style.top  = `${this.pixel_y}px`;
  }

  /**
   * 이동 시작 시도
   * @param {number[][]} grid - 미로 격자 (각 셀은 비트 플래그)
   * @param {{dx:number, dy:number, bit:number}} dir - 방향 객체
   * @param {number} cellSize - 한 칸 픽셀 크기
   */
  start_move(grid, dir, cellSize) {
    // 이미 이동 중이면 무시
    if (this.moving_direction !== null) return;

    const nx = this.grid_x + dir.dx;
    const ny = this.grid_y + dir.dy;

    // 맵 밖으로 나가면 이동 불가
    if (ny < 0 || ny >= grid.length) return;
    if (nx < 0 || nx >= grid[0].length) return;

    // 현재 셀에서 그 방향으로 길이 열려 있는지 확인
    const cell = grid[this.grid_y][this.grid_x];

    // cell의 해당 비트가 0이면 = 길 없음(벽)
    if ((cell & dir.bit) === 0) {
      return;
    }

    // 실제 그리드 좌표 업데이트
    this.grid_x = nx;
    this.grid_y = ny;

    // 도착해야 할 픽셀 좌표(셀 중앙)
    this.target_x = this.grid_x * cellSize + cellSize / 2;
    this.target_y = this.grid_y * cellSize + cellSize / 2;

    // 이동 중 상태로 전환
    this.moving_direction = dir;
  }

  // 한 프레임마다 호출
  update() {
    if (this.moving_direction === null) {
      this.updateDom();
      return;
    }

    const dx = this.target_x - this.pixel_x;
    const dy = this.target_y - this.pixel_y;
    const dist = Math.hypot(dx, dy);

    if (dist <= this.speed) {
      // 도착
      this.pixel_x = this.target_x;
      this.pixel_y = this.target_y;
      this.moving_direction = null;
    } else {
      // 속도 비율만큼 이동
      this.pixel_x += (dx / dist) * this.speed;
      this.pixel_y += (dy / dist) * this.speed;
    }

    this.updateDom();
  }

  // 캔버스에 직접 그리는 건 없고 DOM만 쓰는 구조라 비워둠
  draw(cellSize) {
    // 필요하면 나중에 캔버스 기반 이펙트 추가 가능
  }
}
