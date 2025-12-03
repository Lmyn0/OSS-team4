from flask import Flask, render_template, request
import subprocess
import os
import sys

# C:\zeroexit
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN_DIR = os.path.join(BASE_DIR, "design")   # HTML/CSS/이미지
CODE_DIR = os.path.join(BASE_DIR, "code")       # 미로 파이썬 코드들

# design 폴더를 템플릿 + 정적파일 폴더 둘 다로 사용
# /frame.css, /zeroexit.png, /assets/game.js 이런 식으로 접근 가능
app = Flask(
    __name__,
    template_folder=DESIGN_DIR,
    static_folder=DESIGN_DIR,
    static_url_path=""
)

# 1. 첫 화면: start.html
@app.route("/")
def start_page():
    return render_template("start.html")

# 2. 난이도 선택 화면: level.html
@app.route("/level")
def level_page():
    return render_template("level.html")

# 3. 게임 화면: background.html (JS 미로 게임)
@app.route("/background")
def background_page():
    return render_template("background.html")

# 4. 파이썬 pygame 버전 게임 실행 (필요하면 사용)
@app.route("/start-game")
def start_game():
    # HTML / JS 에서 ?d=low 또는 ?d=hard 로 보낸다고 가정
    ui_level = request.args.get("d", "low")

    if ui_level == "hard":
        arg = "hard"
    else:
        arg = "low"

    python_exe = sys.executable
    main_path = os.path.join(CODE_DIR, "main.py")
    main_path = os.path.abspath(main_path)

    # python main.py low / hard 실행
    subprocess.Popen([python_exe, main_path, arg])

    return """
    <h2>게임이 실행되었습니다!</h2>
    <p>터미널 창에서 게임을 플레이하세요.</p>
    <a href="/">메인 화면으로 돌아가기</a><br>
    <a href="/background">게임 화면으로 돌아가기</a>
    """

if __name__ == "__main__":
    app.run(debug=True)
