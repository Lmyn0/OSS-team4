# 🧩 Kruskal 알고리즘 기반 미로 생성 게임  


## 📖 프로젝트 개요  
이 프로젝트는 **Kruskal 알고리즘**을 사용하여 매번 **랜덤한 미로**를 생성하고,  
플레이어가 **방향키를 이용해 출발점에서 도착점까지 이동**하는 2D 미로 게임입니다.

난이도 선택 기능을 제공하여 미로의 크기와 셀 크기가 달라지도록 구현했습니다.



## 🚀 주요 기능

### 🔹 1. Kruskal 알고리즘 기반 미로 생성
- 미로의 각 셀을 **독립된 집합(Union-Find)** 으로 관리  
- 임의의 벽을 선택해 허물면서 셀을 연결  
- **사이클이 생기지 않도록** Union-Find로 검사  
- 모든 벽 처리가 끝나면 **완전한 미로 구조** 생성

---

### 🔹 2. 플레이어 이동 시스템
- `Player` 클래스는 현재 위치 `(x, y)` 를 저장  
- 각 방향 **(N, S, E, W)** 에 벽이 없는 경우에만 이동 가능  
- 방향키 입력으로 실제 미로 내부를 탐색할 수 있음  

---

### 🔹 3. 난이도 조절 기능
| 난이도 | 미로 크기 |
|--------|-----------|
| **쉬움(Easy)** | 20 x 20 |
| **어려움(Hard)** | 30 x 30 |

난이도에 따라 **게임 난이도 및 플레이 감각이 달라지는 구조**입니다.



## 📂 프로젝트 구조 

```text
OSS-TEAM4/
 ├─ app/
 │   └─ app.py                 # 서버 실행 또는 메인 엔트리
 │
 ├─ code/                      # (파이썬 파일)
 │
 ├─ design/                    # UI/UX 디자인 관련 자료
 │   └─assets/
 │      ├─ background.css         # 전체 배경 스타일
 │      ├─ frame.css              # 프레임 및 공통 UI 스타일
 │      ├─ player.css             # 플레이어 관련 스타일
 │      │
 │      ├─ background.js          # 배경 렌더링 스크립트
 │      ├─ boss.js                # 보스(또는 특수 엔티티) 로직
 │      ├─ debuff.js              # 디버프 효과 처리
 │      ├─ difficulty.js          # 난이도 선택 및 설정
 │      ├─ game.js                # 전체 게임 진행 로직
 │      ├─ maze.js                # Kruskal 알고리즘 기반 미로 생성
 │      ├─ player.js              # 플레이어 이동 및 상태 관리
 │      └─ renderer.js            # 화면/캔버스 렌더링
 │ 
 │  └── background.html            # 배경 화면 페이지
        ├─ level.html                 # 난이도 선택 화면
        ├─ lose.html                  # 패배 화면
        ├─ manual.html                # 게임 설명/매뉴얼 페이지
        ├─ start.html                 # 시작 화면
        ├─ win.html                   # 승리 화면
        │
        ├─ Component 1.png            # UI 구성 요소 이미지
        ├─ Component 2.png
        ├─ Component 3.png
        └─ zeroexit.png               # 종료/버튼 등 이미지
```
---

## ▶️ 실행 방법

### 1. 프로젝트를 클론합니다.
   ```bash
   git clone https://github.com/your-repo/OSS-TEAM4.git
   cd OSS-TEAM4/app
   ```

### 2. app.py 파일을 실행합니다.
   ```bash 
   python app.py
   ```
### 3. 실행 후 터미널에 출력되는 주소(URL)를 확인합니다.
    ```bash
    * Running on http://127.0.0.1:5000/
    ```
### 4. 해당 주소를 브라우저 주소창에 복사하여 접속합니다.  

---

## 🛠 Tech Stack

| 기술 | 아이콘 | 설명 |
|------|--------|--------|
| Python | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40"/> | 서버 실행(app.py), 게임 구동 환경 제공 |
| HTML | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" width="40"/> | 게임 화면 구성 및 UI 구조 설계 |
| CSS | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" width="40"/> | UI 스타일링, 애니메이션, 디자인 요소 적용 |
| JavaScript | <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" width="40"/> | 미로 생성 알고리즘, 렌더링, 플레이어 이동 등 핵심 게임 로직 |



## 👥 팀원 소개 (TEAM 4)

| 프로필 | 이름 | 역할 |
|--------|------|--------|
| <img src="https://github.com/Lmyn0.png" width="60" height="60"/> | [이민호](https://github.com/Lmyn0) <br> <img src="https://cdnjs.cloudflare.com/ajax/libs/simple-icons/3.13.0/github.svg" width="18"/> | 팀장 / 게임 로직 개발 |
| <img src="https://github.com/heeveonm.png" width="60" height="60"/> | [문희연](https://github.com/heeveonm) <br> <img src="https://cdnjs.cloudflare.com/ajax/libs/simple-icons/3.13.0/github.svg" width="18"/> | UI/UX |
| <img src="https://github.com/nodevvice.png" width="60" height="60"/> | [심예정](https://github.com/nodevvice) <br> <img src="https://cdnjs.cloudflare.com/ajax/libs/simple-icons/3.13.0/github.svg" width="18"/> | 게임 로직 개발 |
