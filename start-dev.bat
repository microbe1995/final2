@echo off
echo ========================================
echo LCA Final 개발 환경 시작
echo ========================================
echo.

echo 🚀 Docker Compose로 서비스 시작 중...
docker-compose up --build -d

echo.
echo ⏳ 서비스 시작 대기 중... (10초)
timeout /t 10 /nobreak > nul

echo.
echo 🔍 서비스 상태 확인 중...
docker-compose ps

echo.
echo 🌐 프론트엔드: http://localhost:3000
echo 🔧 Gateway: http://localhost:8080
echo 🔐 Auth Service: http://localhost:8000
echo 📚 Gateway API Docs: http://localhost:8080/docs
echo 🔐 Auth Service API Docs: http://localhost:8000/docs

echo.
echo ✅ 모든 서비스가 시작되었습니다!
echo.
echo 🛑 서비스를 중지하려면: docker-compose down
echo 📊 로그 확인: docker-compose logs -f
echo.
pause
