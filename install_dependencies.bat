@echo off
echo ========================================
echo GreenSteel MSA Python 환경 설정
echo ========================================

echo.
echo 1. Python 가상환경 생성 중...
if not exist "venv" (
    python -m venv venv
    echo 가상환경이 생성되었습니다.
) else (
    echo 가상환경이 이미 존재합니다.
)

echo.
echo 2. 가상환경 활성화 중...
call venv\Scripts\activate

echo.
echo 3. pip 업그레이드 중...
python -m pip install --upgrade pip

echo.
echo 4. 루트 의존성 설치 중...
pip install -r requirements.txt

echo.
echo 5. Auth Service 의존성 설치 중...
cd service\auth-service
pip install -r requirements.txt

echo.
echo 6. Gateway 의존성 설치 중...
cd ..\..\gateway
pip install -r requirements.txt

echo.
echo 7. 개발 도구 설치 중...
cd ..
pip install black isort mypy flake8

echo.
echo ========================================
echo 설치 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. VS Code에서 Python 인터프리터를 ./venv/Scripts/python.exe로 설정
echo 2. .env 파일을 생성하고 환경 변수를 설정
echo 3. 각 서비스를 실행해보세요
echo.
echo Gateway 실행: cd gateway && python app/main.py
echo Auth Service 실행: cd service/auth-service && python app/main.py
echo.
pause
