@echo off
chcp 65001 >nul

REM MatDir 테스트 실행 스크립트 (Windows)

echo 🧪 MatDir 기능 테스트 시작
echo ================================

REM 환경변수 확인
if "%DATABASE_URL%"=="" (
    echo ❌ DATABASE_URL 환경변수가 설정되지 않았습니다.
    echo Railway 환경변수를 확인하거나 .env 파일을 설정하세요.
    pause
    exit /b 1
)

echo ✅ DATABASE_URL 환경변수 확인됨
echo 🔧 DATABASE_URL: %DATABASE_URL:~0,50%...

REM Python 가상환경 확인 및 활성화
if exist "venv\Scripts\activate.bat" (
    echo 🐍 가상환경 활성화 중...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo 🐍 가상환경 활성화 중...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️ 가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.
)

REM Python 버전 확인
echo 🐍 Python 버전 확인 중...
python --version

REM 필요한 패키지 설치 확인
echo 📦 필요한 패키지 설치 확인 중...
pip install asyncpg

REM 테스트 실행
echo.
echo 🚀 테스트 실행 중...
echo ================================

REM 1. 연결 테스트만 실행
echo 1️⃣ 데이터베이스 연결 테스트
python test_matdir_functionality.py --connection-only

if %ERRORLEVEL% EQU 0 (
    echo ✅ 연결 테스트 성공
    echo.
    
    REM 2. 간단한 기능 테스트
    echo 2️⃣ 간단한 기능 테스트
    python test_matdir_simple.py
    
    if %ERRORLEVEL% EQU 0 (
        echo ✅ 간단한 기능 테스트 성공
        echo.
        
        REM 3. 전체 기능 테스트
        echo 3️⃣ 전체 기능 테스트
        python test_matdir_functionality.py
        
        if %ERRORLEVEL% EQU 0 (
            echo 🎉 모든 테스트 통과!
            pause
            exit /b 0
        ) else (
            echo ❌ 전체 기능 테스트 실패
            pause
            exit /b 1
        )
    ) else (
        echo ❌ 간단한 기능 테스트 실패
        pause
        exit /b 1
    )
) else (
    echo ❌ 연결 테스트 실패
    pause
    exit /b 1
)
