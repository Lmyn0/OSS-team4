// ------------------------------------
// 1. 캔버스 및 격자 무늬 로직
// ------------------------------------
const canvas = document.getElementById('mazeCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas(){
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.max(1, Math.floor(window.devicePixelRatio || 1));
  
  canvas.width = Math.floor(rect.width * dpr);
  canvas.height = Math.floor(rect.height * dpr);
  
  ctx.setTransform(dpr,0,0,dpr,0,0);
  
  drawPlaceholder();
}

function drawPlaceholder(){
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  const w = canvas.width / dpr; // 논리적 너비
  const h = canvas.height / dpr; // 논리적 높이
  
  const cell = 30; // 격자 크기 (30px)
  
  ctx.clearRect(0,0,w,h);
  
  // ⭐️ [수정된 부분]: 갈색 배경을 캔버스에 직접 채워줍니다.
  // CSS 변수 대신 하드코딩된 값 #654C40을 사용합니다.
  const darkBrown = '#654C40'; 
  ctx.fillStyle = darkBrown;
  ctx.fillRect(0,0,w,h);
  
  // ⭐️ [수정된 부분]: 격자 선 색상을 더 잘 보이도록 조정합니다.
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'; // 투명도를 0.08에서 0.2로 높임
  ctx.lineWidth = 1; 

  // 세로선 그리기 (갈색 사각형 크기에 맞춰서)
  for(let x=0; x<=w; x+=cell){
    ctx.beginPath(); 
    ctx.moveTo(x, 0); 
    ctx.lineTo(x, h); 
    ctx.stroke();
  }
  
  // 가로선 그리기
  for(let y=0; y<=h; y+=cell){
    ctx.beginPath(); 
    ctx.moveTo(0, y); 
    ctx.lineTo(w, y); 
    ctx.stroke();
  }

  // Label
  ctx.fillStyle = '#fff';
  ctx.font = '20px Galmuri7, monospace';
  ctx.textAlign = 'center';
  ctx.fillText('✅ 미로 생성 대기 중 (Cell Size: ' + cell + 'px) ✅', w/2, h/2);
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas(); // 초기 로드 시 캔버스 크기 조정 및 그리기

// ------------------------------------
// 2. 버튼 클릭 기능 로직
// ------------------------------------
document.getElementById('btnClose').addEventListener('click', () => {
    alert('창을 닫습니다. (브라우저 보안 정책상 실제 창은 닫히지 않을 수 있습니다.)');
    try {
        window.close(); 
    } catch (e) {
        console.log("창 닫기 실패:", e);
    }
});

document.getElementById('btnMaximize').addEventListener('click', () => {
    alert('ㅁ 버튼 클릭: 최대화/복원 기능 구현 예정');
});

document.getElementById('btnMinimize').addEventListener('click', () => {
    alert('ㅡ 버튼 클릭: 최소화 기능 구현 예정');
});
