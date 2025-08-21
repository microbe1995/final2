# 🔍 DataSearch Domain

CBAM 데이터 검색 도메인 - 작은 도메인 모듈

## 📁 구조

```
datasearch/
├── datasearch_entity.py     # 엔티티
├── datasearch_schema.py     # 스키마
├── datasearch_service.py    # 서비스
├── datasearch_repository.py # 리포지토리
├── datasearch_controller.py # 컨트롤러
└── __init__.py              # 패키지
```

## 🚀 사용법

```python
from datasearch import datasearch_router

app.include_router(datasearch_router, prefix="/api")
```

## API

- GET `/data/hscode/search` - HS코드 검색
- POST `/data/country/search` - 국가 검색
- GET `/data/fuels/search` - 연료 검색
- GET `/data/materials/search` - 원료 검색
- GET `/data/precursors/search` - 전구물질 검색
