@echo off
echo ========================================
echo GreenSteel MSA 서비스 실행
echo ========================================

echo.
echo 가상환경 활성화 중...
call venv\Scripts\activate

echo.
echo 서비스를 선택하세요:
echo 1. Gateway Service (포트 8080)
echo 2. Auth Service (포트 8001)
echo 3. 모든 서비스 (별도 터미널에서 실행)
echo 4. 종료

set /p choice="선택 (1-4): "

if "%choice%"=="1" (
    echo.
    echo Gateway Service를 시작합니다...
    cd gateway
    python app/main.py
) else if "%choice%"=="2" (
    echo.
    echo Auth Service를 시작합니다...
    cd service\auth-service
    python app/main.py
) else if "%choice%"=="3" (
    echo.
    echo 모든 서비스를 별도 터미널에서 실행합니다...
    echo.
    echo 터미널 1 (Gateway):
    echo cd gateway ^&^& python app/main.py
    echo.
    echo 터미널 2 (Auth Service):
    echo cd service\auth-service ^&^& python app/main.py
    echo.
    pause
) else if "%choice%"=="4" (
    echo 종료합니다.
    exit
) else (
    echo 잘못된 선택입니다.
    pause
)
