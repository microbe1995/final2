# Report Service

## 개요
GreenSteel MSA 시스템의 리포트 생성 서비스입니다. ESG, LCA, CBAM 관련 보고서를 생성합니다.

## 기능
- ESG 보고서 생성
- LCA 분석 보고서
- CBAM 보고서
- PDF/Excel 형식 지원
- 보고서 템플릿 관리

## 기술 스택
- FastAPI
- Python 3.11+
- Uvicorn
- Pydantic
- ReportLab (PDF 생성)
- OpenPyXL (Excel 처리)

## 실행 방법
```bash
cd service/report-service
python main.py
```

## API 엔드포인트
- `POST /generate/esg` - ESG 보고서 생성
- `POST /generate/lca` - LCA 보고서 생성
- `POST /generate/cbam` - CBAM 보고서 생성
- `GET /health` - 헬스 체크

## 포트
- 기본 포트: 8003 