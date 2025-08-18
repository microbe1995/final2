@echo off
echo ============================================================================
echo 🛑 GreenSteel Docker 서비스 중지
echo ============================================================================

echo.
echo 🔧 Docker Compose 중지 중...
docker-compose down

echo.
echo ✅ 모든 서비스가 중지되었습니다!
echo.
echo 🗑️  컨테이너 및 볼륨 정리:
echo   docker-compose down -v
echo.
echo 🧹 이미지 정리:
echo   docker system prune -f
echo.

pause
