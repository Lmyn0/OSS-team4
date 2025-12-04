// assets/boss.js

export class Boss {
  constructor(gridX, gridY, cellSize, maxHP = 5) {
    // 격자 좌표
    this.grid_x = gridX;
    this.grid_y = gridY;

    // 픽셀 좌표
    this.cellSize = cellSize;
    this.pixel_x = gridX * cellSize;
    this.pixel_y = gridY * cellSize;

    // 체력
    this.maxHP = maxHP;
    this.hp = maxHP;
    this.isAlive = true;

    // 애니메이션
    this.anim = 0;
  }

  // ----- 데미지 -----
  takeDamage(amount) {
    if (!this.isAlive) return;
    this.hp -= amount;

    if (this.hp <= 0) {
      this.hp = 0;
      this.isAlive = false;
    }
  }

  // ----- 업데이트 -----
  update() {
    if (this.isAlive) {
      this.anim += 0.1;
    }
  }

  // ----- 그리기 -----
  draw(ctx) {
    if (!this.isAlive) return;

    // 펄스 애니메이션
    const pulse = Math.sin(this.anim) * 2;
    const size = this.cellSize - 8 + pulse;
    const offset = (this.cellSize - size) / 2;

    const x = this.pixel_x + offset;
    const y = this.pixel_y + offset;

    // 보스 본체
    ctx.fillStyle = "rgb(200, 0, 0)";
    ctx.fillRect(x, y, size, size);

    // --- 눈 ---
    const eyeR = size / 6;
    const eyeOffsetX = size * 0.25;
    const eyeOffsetY = size * 0.3;

    ctx.fillStyle = "yellow";

    // 왼쪽 눈
    ctx.beginPath();
    ctx.arc(x + eyeOffsetX, y + eyeOffsetY, eyeR, 0, Math.PI * 2);
    ctx.fill();

    // 오른쪽 눈
    ctx.beginPath();
    ctx.arc(x + size - eyeOffsetX, y + eyeOffsetY, eyeR, 0, Math.PI * 2);
    ctx.fill();

    // HP 바
    this.drawHP(ctx);
  }

  // ----- HP 바 -----
  drawHP(ctx) {
    const barWidth = this.cellSize;
    const barHeight = 6;
    const barX = this.pixel_x;
    const barY = this.pixel_y - 10;

    // 배경
    ctx.fillStyle = "rgb(50, 50, 50)";
    ctx.fillRect(barX, barY, barWidth, barHeight);

    // 체력 비율
    const ratio = this.hp / this.maxHP;
    const fillWidth = barWidth * ratio;

    // 색상 (30% 이하 빨강)
    ctx.fillStyle = ratio > 0.3 ? "lime" : "red";
    ctx.fillRect(barX, barY, fillWidth, barHeight);
  }
}
