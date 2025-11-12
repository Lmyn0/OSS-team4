<script>
  // 112px 기반을 유지하고, 실제 사용 크기는 SCALE로 제어
  const BASE = 112;
  const SCALE = 0.25; // ← 1/4
  const SIZE = Math.round(BASE * SCALE); // 28

  // 보기 좋은 랜덤 컬러 (HSL)
  function randomColor() {
    const h = Math.floor(Math.random() * 360);
    const s = 70 + Math.floor(Math.random() * 20); // 70~89%
    const l = 55;                                   // 밝기 고정(가독성)
    return `hsl(${h} ${s}% ${l}%)`;
  }

  // 플레이어 생성: parent 내부 (x,y) 위치에 스폰
  function spawnPlayer(parent, x = 0, y = 0) {
    const el = document.createElement('div');
    el.className = 'player';
    el.style.setProperty('--size', SIZE + 'px');
    el.style.left = x + 'px';
    el.style.top  = y + 'px';
    el.style.setProperty('--color', randomColor()); // 생성 즉시 랜덤색

    const eye = document.createElement('div');
    eye.className = 'eye';
    el.appendChild(eye);

    parent.appendChild(el);
    return el;
  }

  // 색만 바꾸고 싶을 때 (맵 변경 이벤트 등에서 호출)
  function recolorPlayer(el) {
    el.style.setProperty('--color', randomColor());
    
  }

  // === 사용 예시 ===
  document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('game-root'); // 보드/콘텐츠 영역
    const player = spawnPlayer(root, 40, 40);          // (40,40)에 스폰

    // 예: 3초 후 색상 변경 (나중에 맵 변경 이벤트에 연결하면 됨)
    setTimeout(() => recolorPlayer(player), 3000);
  });
</script>
