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
    const isUIOpened = pauseOverlay.style.display === 'flex';

    if (!isUIOpened) {
        // 🔹 1) UI: 메뉴 열기
        pauseOverlay.style.display = 'flex';
        document.body.classList.add('paused');
        console.log("Pause menu OPEN");

        // 🔹 2) 게임 로직: 일시정지
        if (window.gameInstance && typeof window.gameInstance.pause === 'function') {
            window.gameInstance.pause();
            console.log("Game state set to PAUSED.");
        } else {
            console.warn("window.gameInstance.pause()를 찾지 못했습니다.");
        }

    } else {
        // 🔹 1) UI: 메뉴 닫기
        pauseOverlay.style.display = 'none';
        document.body.classList.remove('paused');
        console.log("Pause menu CLOSE");

        // 🔹 2) 게임 로직: 재개
        if (window.gameInstance && typeof window.gameInstance.resume === 'function') {
            window.gameInstance.resume();
            console.log("Game state set to RUNNING.");
        } else {
            console.warn("window.gameInstance.resume()를 찾지 못했습니다.");
        }
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

    // 5. 🚨 QUIT 버튼: start.html로 이동
    document.getElementById('quitBtn').addEventListener('click', () => {
    console.log("QUIT button pressed. Going to START screen.");
    window.location.href = 'start.html';   // 🔥 첫 화면 파일명!
    });


});