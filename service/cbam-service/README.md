# CBAM Service

## 개요
GreenSteel MSA 시스템의 CBAM(Carbon Border Adjustment Mechanism) 서비스입니다. 탄소국경조정메커니즘 관련 계산과 분석을 제공합니다.

## 기능
- CBAM 계산
- 탄소 배출량 분석
- 국경 조정 세금 계산
- CBAM 인증서 관리
- 데이터 검증

## 기술 스택
- FastAPI
- Python 3.11+
- Uvicorn
- Pydantic
- NumPy (수치 계산)
- Pandas (데이터 처리)

## 실행 방법
```bash
cd service/cbam-service
python main.py
```

## API 엔드포인트
- `POST /calculate` - CBAM 계산
- `POST /validate` - 데이터 검증
- `GET /certificates` - 인증서 조회
- `GET /health` - 헬스 체크

## 포트
- 기본 포트: 8004 