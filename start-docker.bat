@echo off
echo ============================================================================
echo 🚀 GreenSteel Docker 서비스 시작
echo ============================================================================

echo.
echo 📋 서비스 정보:
echo   • Gateway: http://localhost:8080
echo   • Auth Service: http://localhost:8000
echo   • Cal Boundary: http://localhost:8001
echo   • Frontend: http://localhost:3000
echo   • PostgreSQL: localhost:5432
echo.

echo 🔧 Docker Compose 실행 중...
docker-compose up -d

echo.
echo ✅ 모든 서비스가 시작되었습니다!
echo.
echo 📊 서비스 상태 확인:
echo   docker-compose ps
echo.
echo 📝 로그 확인:
echo   docker-compose logs -f
echo.
echo 🛑 서비스 중지:
echo   docker-compose down
echo.

pause
