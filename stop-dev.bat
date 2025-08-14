@echo off
echo ========================================
echo LCA Final 개발 환경 중지
echo ========================================
echo.

echo 🛑 Docker Compose 서비스 중지 중...
docker-compose down

echo.
echo 🧹 컨테이너 및 네트워크 정리 중...
docker system prune -f

echo.
echo ✅ 모든 서비스가 중지되었습니다!
echo.
pause
