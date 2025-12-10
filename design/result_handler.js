// result_handler.js

/**
 * 게임 결과 화면에서 ESC 키를 눌렀을 때 레벨 선택 화면으로 이동합니다.
 */

// ➡️ 목적지 URL: 레벨 선택 화면 (요청에 따라 level.html로 설정)
const MENU_URL = 'level.html'; 

document.addEventListener('keydown', function(event) {
    
    // ESC 키의 keyCode (27) 또는 key 속성 ('Escape') 확인
    if (event.key === 'Escape' || event.keyCode === 27) {
        
        event.preventDefault(); 
        
        console.log("ESC 키가 감지되었습니다. 레벨 선택 화면으로 이동합니다.");
        
        // level.html로 이동
        window.location.href = MENU_URL;
    }
});