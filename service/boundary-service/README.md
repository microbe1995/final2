# Cal_boundary 서비스

## 🚀 서비스 개요

Cal_boundary 서비스는 도형, 화살표, Canvas 등의 HTTP API를 제공하는 FastAPI 애플리케이션입니다.

## 🏗️ 주요 기능

### 1. 도형 관리 (Shapes)
- 도형 생성, 수정, 삭제
- 도형 타입별 분류 및 관리
- 도형 검색 및 통계

### 2. 화살표 관리 (Arrows)
- 화살표 생성, 수정, 삭제
- 화살표 타입별 분류 및 관리
- 화살표 연결 및 배치 생성

### 3. Canvas 관리 (Canvas)
- Canvas 생성, 수정, 삭제
- Canvas 내 도형 및 화살표 배치
- Canvas 템플릿 및 가져오기/내보내기
- Canvas 병합 및 복제

### 4. 🆕 CBAM 산정경계 설정 (CBAM Boundary)
- **기업 정보 검증**: 기업명, 사업자등록번호, 연락처 등 검증
- **CBAM 제품 검증**: HS 코드, CN 코드 기반 CBAM 대상 여부 확인
- **생산 공정 검증**: 공정 정보 및 흐름 검증
- **보고 기간 검증**: 역년/회계연도/국내제도 기간 검증
- **산정경계 설정**: CBAM 대상 제품 생산을 위한 경계 설정
- **배출원 및 소스 스트림 식별**: CO2 배출원과 탄소 함유 물질 식별
- **데이터 할당 계획**: 공유 자원의 공정별 할당 계획 수립
- **종합 분석**: 전체 과정에 대한 종합적인 분석 및 권장사항 제공

## 📁 프로젝트 구조

```
app/
├── domain/
│   ├── controller/          # HTTP API 컨트롤러
│   │   ├── shape_controller.py
│   │   ├── arrow_controller.py
│   │   ├── canvas_controller.py
│   │   └── cbam_controller.py      # 🆕 CBAM 컨트롤러
│   ├── entity/              # 데이터베이스 엔티티
│   │   ├── shape_entity.py
│   │   ├── arrow_entity.py
│   │   ├── canvas_entity.py
│   │   └── cbam_entity.py          # 🆕 CBAM 엔티티
│   ├── schema/              # Pydantic 스키마
│   │   ├── shape_schema.py
│   │   ├── arrow_schema.py
│   │   ├── canvas_schema.py
│   │   └── cbam_schema.py          # 🆕 CBAM 스키마
│   └── service/             # 비즈니스 로직
│       ├── shape_service.py
│       ├── arrow_service.py
│       ├── canvas_service.py
│       └── cbam_service.py          # 🆕 CBAM 서비스
├── common/                  # 공통 유틸리티
└── main.py                 # 메인 애플리케이션
```

## 🔌 API 엔드포인트

### 기본 API
- `GET /health` - 서비스 상태 확인
- `GET /docs` - Swagger API 문서 (개발 모드)

### 도형 API
- `POST /shapes` - 도형 생성
- `GET /shapes` - 도형 목록 조회
- `PUT /shapes/{id}` - 도형 수정
- `DELETE /shapes/{id}` - 도형 삭제

### 화살표 API
- `POST /arrows` - 화살표 생성
- `GET /arrows` - 화살표 목록 조회
- `PUT /arrows/{id}` - 화살표 수정
- `DELETE /arrows/{id}` - 화살표 삭제

### Canvas API
- `POST /canvas` - Canvas 생성
- `GET /canvas` - Canvas 목록 조회
- `PUT /canvas/{id}` - Canvas 수정
- `DELETE /canvas/{id}` - Canvas 삭제

### 🆕 CBAM 산정경계 설정 API
- `POST /api/v1/cbam/company/validate` - 기업 정보 검증
- `POST /api/v1/cbam/products/validate` - CBAM 제품 검증
- `GET /api/v1/cbam/products/hs-codes` - CBAM 대상 HS 코드 목록
- `POST /api/v1/cbam/products/check-target` - CBAM 대상 여부 확인
- `POST /api/v1/cbam/processes/validate` - 생산 공정 검증
- `POST /api/v1/cbam/processes/flow-analysis` - 공정 흐름 분석
- `POST /api/v1/cbam/periods/validate` - 보고 기간 검증
- `GET /api/v1/cbam/periods/templates` - 보고 기간 템플릿
- `POST /api/v1/cbam/boundary/create` - 산정경계 설정 생성
- `POST /api/v1/cbam/boundary/emission-sources` - 배출원 식별
- `POST /api/v1/cbam/boundary/source-streams` - 소스 스트림 식별
- `POST /api/v1/cbam/allocation/create-plan` - 데이터 할당 계획 생성
- `POST /api/v1/cbam/analysis/comprehensive` - 종합 분석
- `GET /api/v1/cbam/health` - CBAM 서비스 상태 확인
- `GET /api/v1/cbam/info` - CBAM 서비스 정보

## 🛠️ 기술 스택

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Validation**: Pydantic
- **Logging**: Loguru
- **Documentation**: OpenAPI/Swagger

## 🚀 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서비스 실행
```bash
# 개발 모드
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 3. Docker 실행
```bash
docker build -t cal-boundary .
docker run -p 8001:8001 cal-boundary
```

## 📊 CBAM 산정경계 설정 워크플로우

### 단계 1: 기업 정보 입력 및 검증
1. 기업명, 사업장 주소, 사업자등록번호 등 기본 정보 입력
2. 입력된 정보의 유효성 검증
3. 검증 오류 시 수정 요청

### 단계 2: CBAM 대상 제품 확인
1. 수출 제품의 HS 코드 및 CN 코드 입력
2. CBAM 대상 품목 여부 자동 확인
3. 대상 제품 목록 작성

### 단계 3: 생산 공정 정보 입력
1. 사업장 내 모든 생산 공정 리스트 작성
2. 각 공정별 투입 원료, 연료, 에너지 흐름 정의
3. 공동 사용 유틸리티 설비 식별
4. CBAM 대상/비대상 제품 생산 여부 표시

### 단계 4: 보고 기간 설정
1. 역년, 회계연도, 국내제도 중 선택
2. 12개월 기준 보고 기간 설정
3. 시작일/종료일 및 기간 길이 검증

### 단계 5: 산정경계 설정
1. CBAM 대상 제품 생산 공정 중심으로 경계 설정
2. 개별/통합 경계 유형 선택
3. 포함/제외 공정 명확히 구분
4. 공동 사용 유틸리티 가상 분할 계획

### 단계 6: 배출원 및 소스 스트림 식별
1. CO2 배출원 자동 식별 (연소설비, 화학반응 등)
2. 탄소 함유 물질 (연료, 원료) 식별
3. 전구물질 여부 확인 및 내재 배출량 고려

### 단계 7: 데이터 할당 계획 수립
1. 공유 자원 사용 공정 식별
2. 가동시간, 전력사용량 등 기준 할당 방법 선택
3. 공정별 할당 비율 계산

### 단계 8: 종합 분석 및 권장사항
1. 전체 과정 검증 결과 요약
2. 산정경계 설정 결과 제공
3. 다음 단계 및 권장사항 제시

## 🔍 CBAM 규정 준수 사항

### 철강 부문 특화 기능
- **온실가스 종류**: CO2만 고려 (N2O, PFCs 제외)
- **HS 코드**: 7208-7216 (철강 제품)
- **전구물질**: 소결광, 펠릿, 선철, 용강 등
- **복합제품**: 전구물질 내재 배출량 포함 계산

### 데이터 할당 우선순위
1. **법정계량기** - 가장 높은 신뢰도
2. **자체계량기** - 중간 신뢰도
3. **대체 방법** - 가동시간, 정격용량, 화학양론식 등

### 보고 기간 요구사항
- **최소 기간**: 3개월
- **기본 기간**: 12개월 (역년/회계연도/국내제도)
- **계절적 변동성**: 사업장 운영 특성 반영

## 📈 향후 개발 계획

### 단기 계획 (1-3개월)
- [ ] 데이터베이스 연동 및 영속성 구현
- [ ] 사용자 인증 및 권한 관리
- [ ] API 응답 캐싱 및 성능 최적화

### 중기 계획 (3-6개월)
- [ ] 배출량 계산 엔진 연동
- [ ] 보고서 생성 및 내보내기 기능
- [ ] 다국어 지원 (한국어/영어)

### 장기 계획 (6개월 이상)
- [ ] AI 기반 자동 경계 설정 제안
- [ ] 실시간 모니터링 및 알림 시스템
- [ ] EU CBAM 시스템과의 직접 연동

## 🤝 기여 방법

1. 이슈 생성 또는 기존 이슈 확인
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 코드 작성 및 테스트
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

- **개발팀**: Cal_boundary Development Team
- **이메일**: dev@cal-boundary.com
- **문서**: `/docs` 엔드포인트에서 API 문서 확인 가능
