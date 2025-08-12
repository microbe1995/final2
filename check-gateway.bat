@echo off
chcp 65001 >nul

echo 🔍 Gateway 서비스 상태 확인 중...

echo.
echo 📡 Health Check 엔드포인트 테스트:
curl -s http://localhost:8080/health

echo.
echo 📡 API Health Check 엔드포인트 테스트:
curl -s http://localhost:8080/api/v1/health

echo.
echo 📡 Auth Health Check 엔드포인트 테스트:
curl -s http://localhost:8080/api/v1/auth/health

echo.
echo 📡 사용 가능한 엔드포인트 확인:
curl -s http://localhost:8080/docs

echo.
echo ✅ Gateway 서비스 확인 완료!
pause
