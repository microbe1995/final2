# CBAM 프로젝트 대화 요약

## 📋 프로젝트 개요
- **프로젝트명**: CBAM (Carbon Border Adjustment Mechanism)
- **아키텍처**: Microservices Architecture (MSA)
- **백엔드**: FastAPI (Python)
- **데이터베이스**: PostgreSQL (Railway)
- **프론트엔드**: Next.js
- **배포**: Railway

## 🏗️ 시스템 구조
```
Final/
├── service/
│   ├── cbam-service/          # 메인 서비스 (포트 8001)
│   │   └── app/
│   │       ├── domain/        # 도메인별 모듈
│   │       ├── main.py        # FastAPI 앱
│   │       └── ...
│   └── auth-service/          # 인증 서비스
├── gateway/                    # API 게이트웨이
└── src/                       # 프론트엔드
```

## 🔧 주요 도메인 모듈
각 도메인은 DDD 패턴을 따라 다음 구조를 가집니다:
- `entity.py` - SQLAlchemy 엔티티
- `schema.py` - Pydantic 스키마
- `repository.py` - 데이터 접근 계층
- `service.py` - 비즈니스 로직
- `controller.py` - API 엔드포인트
- `__init__.py` - 모듈 내보내기

### 📁 도메인 목록
- `@install/` - 사업장 관리
- `@product/` - 제품 관리
- `@process/` - 공정 관리
- `@edge/` - 엣지 관계
- `@calculation/` - 계산 로직
- `@mapping/` - HS-CN 매핑
- `@matdir/` - 자재 디렉토리
- `@fueldir/` - 연료 디렉토리
- `@processchain/` - 공정 체인
- `@productprocess/` - 제품-공정 관계 (새로 생성)

## 🚨 주요 문제 및 해결 과정

### 1. HTTP 502 오류 (`/api/v1/boundary/install`)
- **문제**: `/api/v1/boundary/install` 엔드포인트에서 HTTP 502 오류 발생
- **해결**: Edge 도메인 기능을 `@calculation/`에서 `@edge/`로 리팩토링

### 2. 데이터베이스 연결 풀 초기화 오류
- **문제**: "데이터베이스 연결 풀이 초기화되지 않았습니다" 오류
- **원인**: Repository 인스턴스가 요청별로 생성되지만 `initialize()` 메서드가 애플리케이션 시작 시 다른 인스턴스에서만 호출됨
- **해결**: 
  - 모든 repository에 robust한 lazy initialization 패턴 구현
  - `_initialization_attempted` 플래그 추가
  - `main.py`의 `lifespan`에서 repository 인스턴스 직접 초기화
  - `matdir_repository.py`와 `fueldir_repository.py`를 `psycopg2`에서 `asyncpg`로 리팩토링

### 3. 307 Temporary Redirect 루프
- **문제**: `/install` 요청이 계속 307 리다이렉트 발생
- **원인**: FastAPI의 기본 리다이렉트 동작과 라우터 설정 충돌
- **해결**:
  - `install_router`를 첫 번째로 등록하여 우선순위 부여
  - CORS 미들웨어의 `allow_methods`를 `["*"]`에서 구체적인 메서드 목록으로 변경
  - `/debug/routes` 디버그 엔드포인트 추가

### 4. ProductProcess 리팩토링
- **요청**: `@calculation/`의 ProductProcess 기능을 `@productprocess/`로 이동
- **과정**:
  1. Railway DB의 `productionroute` 테이블을 `product_process`로 이름 변경
  2. 새로운 `@productprocess/` 도메인 폴더 생성
  3. 모든 관련 코드 (entity, schema, repository, service, controller) 이동
  4. `main.py`에서 새로운 라우터 등록
  5. `@calculation/` 도메인에서 ProductProcess 관련 코드 제거

## 🔄 데이터베이스 스키마 변경
### 테이블 이름 변경 과정
1. **초기 상태**: `product_process` 테이블 존재
2. **첫 번째 변경**: `product_process` → `productionroute` (사용자 요청)
3. **사용자 명확화**: 이름을 `productprocess`로 유지하고 기능만 이동
4. **최종 변경**: `productionroute` → `product_process` (원래 이름으로 복원)

### 임시 스크립트들
- `rename_table.py` - 테이블 이름 변경
- `check_tables.py` - 테이블 존재 확인
- `drop_productionroute_table.py` - 충돌 테이블 삭제

## 💻 기술적 세부사항

### 데이터베이스 연결
- **비동기**: `asyncpg` 사용
- **연결 풀**: `asyncpg.create_pool`로 관리
- **초기화**: 애플리케이션 시작 시 또는 첫 사용 시 lazy initialization

### 코드 품질
- **절대 경로**: 모든 import에서 절대 경로 사용 (사용자 요구사항)
- **DDD 패턴**: 모든 새로운 코드에서 Domain-Driven Design 원칙 적용
- **MSA 준수**: Microservices Architecture 패턴 엄격히 준수

### 에러 처리
- **로깅**: 구조화된 로깅으로 디버깅 지원
- **예외 처리**: 각 계층에서 적절한 예외 처리 및 로깅
- **사용자 친화적**: 한국어 에러 메시지 제공

## 📝 주요 파일 변경사항

### 새로 생성된 파일
- `app/domain/productprocess/productprocess_entity.py`
- `app/domain/productprocess/productprocess_schema.py`
- `app/domain/productprocess/productprocess_repository.py`
- `app/domain/productprocess/productprocess_service.py`
- `app/domain/productprocess/productprocess_controller.py`
- `app/domain/productprocess/__init__.py`

### 수정된 파일
- `app/main.py` - ProductProcess 라우터 등록 및 import 경로 수정
- `app/domain/calculation/` - ProductProcess 관련 코드 제거

### 삭제된 파일
- 임시 데이터베이스 관리 스크립트들

## 🚀 배포 및 실행

### Railway 배포
- **cbam-service**: 포트 8001
- **auth-service**: 별도 포트
- **데이터베이스**: Railway PostgreSQL

### 로컬 실행
```bash
cd service/cbam-service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔍 문제 해결 방법론

### 1. 체계적 분석
- 코드베이스 전체 검색으로 기존 기능 중복 방지
- 파일 경로와 import 타입 (상대 vs 절대) 상세 분석
- 각 도메인 폴더 내 파일들의 의존성 관계 파악

### 2. 점진적 수정
- 한 번에 하나의 문제에 집중
- 각 수정 후 기능 검증
- 롤백 가능한 방식으로 접근

### 3. 사용자 피드백 반영
- 요구사항 명확화를 위한 적극적 질문
- 사용자 선호사항에 따른 방향 조정
- 명확한 설명과 함께 수정 제안

## 📚 주요 학습 내용

### FastAPI 관련
- Lifespan 이벤트를 통한 애플리케이션 초기화
- 라우터 등록 순서의 중요성
- CORS 미들웨어 설정의 세밀한 조정

### 데이터베이스 관련
- `asyncpg` vs `psycopg2` 선택 기준
- 비동기 연결 풀 관리 패턴
- 테이블 스키마 변경 시 주의사항

### 아키텍처 관련
- DDD 패턴의 실제 적용
- MSA에서의 모듈 분리 원칙
- 순환 참조 방지 방법

## 🎯 향후 개선 방향

### 코드 품질
- 단위 테스트 추가
- API 문서화 개선
- 에러 처리 표준화

### 성능 최적화
- 데이터베이스 쿼리 최적화
- 연결 풀 크기 조정
- 캐싱 전략 수립

### 모니터링
- 로그 집계 및 분석
- 성능 메트릭 수집
- 알림 시스템 구축

## 💡 핵심 교훈

1. **점진적 리팩토링**: 큰 변경을 한 번에 하지 말고 단계별로 진행
2. **사용자 요구사항 명확화**: 개발 전에 정확한 요구사항 파악
3. **테스트 기반 개발**: 각 단계마다 기능 검증
4. **문서화**: 변경사항과 해결 과정을 상세히 기록
5. **아키텍처 일관성**: DDD와 MSA 원칙을 일관되게 적용

---

*이 문서는 CBAM 프로젝트 개발 과정에서 발생한 주요 문제들과 해결 과정을 정리한 것입니다. 다른 AI 어시스턴트가 프로젝트 맥락을 이해하고 연속성 있는 개발을 진행할 수 있도록 작성되었습니다.*
