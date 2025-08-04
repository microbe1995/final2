#!/bin/bash

echo "🚀 GreenSteel MSA 시스템 시작 중..."

# 1. 메시지 서비스 시작
echo "📡 메시지 서비스 시작 중..."
cd service/message-service
python main.py &
MESSAGE_SERVICE_PID=$!
cd ../..

# 2. 게이트웨이 시작
echo "🌐 API Gateway 시작 중..."
cd gateway
python main.py &
GATEWAY_PID=$!
cd ..

# 3. 프론트엔드 시작
echo "🎨 프론트엔드 시작 중..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ 모든 서비스가 시작되었습니다!"
echo ""
echo "📊 서비스 상태:"
echo "  • 메시지 서비스: http://localhost:8001"
echo "  • API Gateway: http://localhost:8000"
echo "  • 프론트엔드: http://localhost:3000"
echo ""
echo "📚 API 문서:"
echo "  • Swagger UI: http://localhost:8000/docs"
echo "  • ReDoc: http://localhost:8000/redoc"
echo ""
echo "🛑 서비스 중지하려면 Ctrl+C를 누르세요."

# 프로세스 종료 처리
trap 'echo "🛑 서비스 종료 중..."; kill $MESSAGE_SERVICE_PID $GATEWAY_PID $FRONTEND_PID; exit' INT

# 프로세스 대기
wait 