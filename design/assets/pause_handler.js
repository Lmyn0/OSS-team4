/**
 * assets/pause_handler.js
 * 게임 중 ESC 키를 눌러 일시 정지 메뉴를 제어하고 버튼 기능을 처리합니다.
 */

document.addEventListener("DOMContentLoaded", () => {
    const pauseOverlay = document.getElementById('pauseOverlay');
    
    // pauseOverlay가 없으면 스크립트 실행 중지
    if (!pauseOverlay) return;

    // 초기 상태: 메뉴 숨기기
    pauseOverlay.style.display = 'none';
    
    // 현재 난이도 키를 가져오는 함수 (RESTART에 필요)
    const getDifficultyKey = () => {
        const params = new URLSearchParams(window.location.search);
        return params.get("d") || "easy";
    };

    /**
     * 일시 정지 메뉴를 토글하고 게임 상태를 제어합니다.
     * (게임 정지/재개 로직은 background.html의 게임 모듈이 제공해야 함)
     */
    function togglePause() {
        const isPaused = pauseOverlay.style.display === 'flex';
        
        if (!isPaused) {
            pauseOverlay.style.display = 'flex'; // 메뉴 표시
            document.body.classList.add('paused');
            // 💡 게임 일시 정지 로직 (예: gameInstance.pause())을 여기에 추가합니다.
            console.log("Game Paused");
        } else {
            pauseOverlay.style.display = 'none'; // 메뉴 숨김
            document.body.classList.remove('paused');
            // 💡 게임 재개 로직 (예: gameInstance.resume())을 여기에 추가합니다.
            console.log("Game Resumed");
        }
    }

    // 1. ESC 키 이벤트 리스너: 메뉴 토글
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            e.preventDefault(); 
            togglePause();
        }
    });

    // 2. RESUME 버튼: 일시 정지 해제
    document.getElementById('resumeBtn').addEventListener('click', () => {
        togglePause();
    });

    // 3. RESTART 버튼: 게임 재시작 (난이도 유지)
    document.getElementById('restartBtn').addEventListener('click', () => {
        const dKey = getDifficultyKey();
        window.location.href = `background.html?d=${encodeURIComponent(dKey)}`;
    });

    // 4. MANUAL 버튼: manual.html로 이동
    document.getElementById('manualBtn').addEventListener('click', () => {
        window.location.href = 'manual.html'; 
    });

    // 5. 🚨 QUIT 버튼: 게임 상태를 그대로 유지하고 현재 화면에 머무름 (수정된 부분)
    document.getElementById('quitBtn').addEventListener('click', () => {
        // 사용자의 요청: 게임의 상태를 그대로 멈춘 채 현재 화면에 머물도록 합니다.
        // 현재 pauseOverlay.style.display는 이미 'flex' 상태이며, 게임은 일시 정지 상태입니다.
        console.log("QUIT button pressed. Remaining on the paused screen per user request.");
        // 아무런 추가 동작(화면 이동) 없이 현재 화면을 유지합니다.
    });
});