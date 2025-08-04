# Report Service

## 개요
GreenSteel MSA 시스템의 리포트 서비스입니다. ESG/LCA/CBAM 리포트 업로드 및 관리를 제공합니다.

## 기능
- 리포트 파일 업로드 (PDF)
- 리포트 목록 조회
- 리포트 파일 조회
- 리포트 관리

## 기술 스택
- FastAPI
- Python 3.11+
- Uvicorn
- Pydantic

## 실행 방법
```bash
cd service/report-service
python main.py
```

## API 엔드포인트
- `POST /report/upload/` - 리포트 파일 업로드
- `GET /report/list/` - 리포트 목록 조회
- `GET /report/{filename}` - 특정 리포트 조회
- `GET /health` - 헬스 체크

## 포트
- 기본 포트: 8003

## Docker 실행
```bash
docker build -t report-service .
docker run -p 8003:8003 report-service
``` 