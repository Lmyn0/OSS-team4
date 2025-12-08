// assets/boss.js

export class Boss {
  constructor(gridX, gridY, cellSize, maxHP = 5) {
    // 격자 좌표
    this.grid_x = gridX;
    this.grid_y = gridY;

    // 픽셀 좌표 (셀의 왼쪽 위 기준)
    this.cellSize = cellSize;
    this.pixel_x = gridX * cellSize;
    this.pixel_y = gridY * cellSize;

    // 체력
    this.maxHP = maxHP;
    this.hp = maxHP;
    this.isAlive = true;

    // 애니메이션용 타이머
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

    // 펄스 애니메이션 (살짝 커졌다 작아졌다)
    const pulse = Math.sin(this.anim) * 2;

    // 🔥 보스 기본 사이즈: 셀의 90% 정도로 크게
    const baseSize = this.cellSize * 0.9;
    const size     = baseSize + pulse;

    // 셀 안에서 가운데로 오도록 오프셋
    const offset = (this.cellSize - size) / 2;

    const x = this.pixel_x + offset;
    const y = this.pixel_y + offset;

    // 보스 본체 (빨간 정사각형)
    ctx.fillStyle = "rgb(200, 0, 0)";
    ctx.fillRect(x, y, size, size);

    // --- 눈 그리기 ---
    const eyeR       = size / 6;
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
    this.drawHP(ctx, x, y, size);
  }

  // ----- HP 바 -----
  drawHP(ctx, x, y, size) {
    const barMargin = 6;   // 보스와 HP바 사이 간격
    const barHeight = 6;
    const barWidth  = size;

    const barX = x;
    const barY = y - barMargin - barHeight;

    // 배경 (회색)
    ctx.fillStyle = "rgb(50, 50, 50)";
    ctx.fillRect(barX, barY, barWidth, barHeight);

    // 체력 비율
    const ratio = this.hp / this.maxHP;
    const fillWidth = barWidth * ratio;

    // 체력 색상 (30% 이하 빨강)
    ctx.fillStyle = ratio > 0.3 ? "lime" : "red";
    ctx.fillRect(barX, barY, fillWidth, barHeight);
  }
}
