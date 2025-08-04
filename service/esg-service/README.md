# ESG Service

GreenSteel 프로젝트의 ESG 데이터 관리 마이크로서비스입니다.

## 기능
- ESG 데이터 수집 및 분석
- 지속가능성 지표 계산
- ESG 리포트 생성
- 환경 영향 평가

## 기술 스택
- FastAPI
- Pandas
- NumPy
- PostgreSQL
- Redis (캐싱)

## 실행 방법
```bash
cd service/esg-service
pip install -r requirements.txt
python main.py
```

## API 엔드포인트
- `GET /esg/indicators` - ESG 지표 조회
- `POST /esg/calculate` - ESG 점수 계산
- `GET /esg/reports` - ESG 리포트 목록
- `GET /esg/reports/{report_id}` - ESG 리포트 상세 