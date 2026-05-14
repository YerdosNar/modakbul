@echo off
setlocal

:: 1. 마스터 디렉터리에 venv 폴더가 없으면 최초 1회 생성
if not exist venv\Scripts\activate.bat (
    echo [System] venv 폴더가 없습니다. 가상환경을 최초 1회 생성합니다...
    python -m venv venv
)

:: 2. 무조건 venv 활성화
echo [System] 가상환경(venv)을 활성화합니다...
call venv\Scripts\activate.bat

:: 3. 패키지 설치 및 서버 실행
echo [System] 패키지 상태를 확인하고 서버를 켭니다...
pip install -r requirements.txt
uvicorn main:app --reload

endlocal