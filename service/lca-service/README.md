# LCA Service

## 개요
GreenSteel MSA 시스템의 LCA(Life Cycle Assessment) 서비스입니다. 제품의 전 과정 환경영향평가를 수행합니다.

## 기능
- LCA 분석
- 환경영향 평가
- 데이터베이스 관리
- 결과 시각화
- 비교 분석

## 기술 스택
- FastAPI
- Python 3.11+
- Uvicorn
- Pydantic
- Brightway2 (LCA 계산)
- Matplotlib (시각화)

## 실행 방법
```bash
cd service/lca-service
python main.py
```

## API 엔드포인트
- `POST /analyze` - LCA 분석 수행
- `POST /compare` - 비교 분석
- `GET /databases` - 데이터베이스 조회
- `GET /results` - 결과 조회
- `GET /health` - 헬스 체크

## 포트
- 기본 포트: 8005 