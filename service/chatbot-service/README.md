# Chatbot Service

## 개요
GreenSteel MSA 시스템의 챗봇 서비스입니다. 사용자와의 대화형 인터페이스를 제공합니다.

## 기능
- 사용자 메시지 처리
- 자연어 처리
- 대화 컨텍스트 관리
- 응답 생성

## 기술 스택
- FastAPI
- Python 3.11+
- Uvicorn
- Pydantic

## 실행 방법
```bash
cd service/chatbot-service
python main.py
```

## API 엔드포인트
- `POST /chat` - 챗봇 대화 처리
- `GET /health` - 헬스 체크

## 포트
- 기본 포트: 8002 