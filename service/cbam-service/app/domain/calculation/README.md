# 🧮 Calculation Domain

CBAM 계산 도메인 - 작은 도메인 모듈

## 📁 구조

```
calculation/
├── calculation_entity.py     # 엔티티
├── calculation_schema.py     # 스키마
├── calculation_service.py    # 서비스 
├── calculation_repository.py # 리포지토리
├── calculation_controller.py # 컨트롤러
└── __init__.py              # 패키지
```

## 🚀 사용법

```python
from calculation import calculation_router

app.include_router(calculation_router, prefix="/api")
```

## API

- POST `/calc/fuel/calculate` - 연료 계산
- POST `/calc/material/calculate` - 원료 계산  
- GET `/calc/precursor/user/{user_id}` - 전구물질 조회
- POST `/calc/precursor/save-batch` - 전구물질 저장
- POST `/calc/cbam` - CBAM 종합 계산