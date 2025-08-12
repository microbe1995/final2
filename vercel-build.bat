@echo off
chcp 65001 >nul

echo 🚀 Vercel 배포 빌드 시작...

REM frontend 디렉토리로 이동
cd frontend

REM 의존성 설치
echo 📦 의존성 설치 중...
call pnpm install

REM 빌드 실행
echo 🔨 Next.js 빌드 중...
call pnpm run build

REM 빌드 결과 확인
if %errorlevel% equ 0 (
    echo ✅ 빌드 성공!
    echo 📁 빌드 결과: frontend\.next\
    echo 🚀 Vercel에 배포할 준비가 완료되었습니다.
) else (
    echo ❌ 빌드 실패!
    pause
    exit /b 1
)

pause
