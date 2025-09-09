## 1. 문제 정의 (Problem)
- **배경**: CBAM(Carbon Border Adjustment Mechanism) 제도에 대응하기 위해, 기업은 제품별/공정별 탄소배출량을 산정·검증·보고해야 함. 기존 시스템은 공정 체인의 복잡성, 데이터 단위 불일치, 사업장 간 권한 문제로 인해 정확성과 재현성을 보장하기 어려움.
- **핵심 문제**:
  - 복잡한 공정 연결(공정→제품→공정)에서의 배출량 전파/집계/분배의 일관성 부족
  - 데이터 누락/중복, 순환 참조로 인한 계산 실패 및 규제 보고 리스크
  - 사업장 간(내부/외부) 데이터 편집 권한 관리 미흡
- **성공 기준**:
  - 엣지 변경 시 전체 그래프 재계산을 통한 일관된 결과 제공
  - 제품별 최종 배출량과 공정 단계별 배출량을 신뢰성 있게 산출 및 이력화
  - RBAC 기반 권한 모델로 데이터 무결성 및 감사 가능성 확보

## 2. 솔루션 개요 (Solution)
- **요약**: MSA 기반 CBAM/LCA 솔루션. React Flow 기반 시각적 산정경계 편집기와 FastAPI 백엔드 계산 엔진을 결합하여, 제품-공정-엣지 모델에서 배출량을 실시간 전파/집계/분배한다.
- **핵심 기능**:
  - 제품-공정 관계 설정: 제품별 공정 매핑, 사업장 정보 노출, 권한 제어
  - 산정경계 시각화/편집: 공정/제품 노드, 커스텀 엣지, 읽기 전용(외부 사업장) 처리
  - 배출량 계산 엔진: continue/produce/consume 규칙에 따른 실시간 계산 및 전파
  - 마스터 데이터: 연료/원재료/HS-CN 매핑 테이블로 직접배출 계산과 코드 표준화
  - RBAC/감사: 역할 기반 접근 제어 및 로그/이력 저장

## 3. 아키텍처 (Architecture)
- **전체 구조**
  - Frontend (Next.js 14, React 18, TypeScript, Tailwind, @xyflow/react)
  - Gateway (FastAPI) → `/api/v1/{service}/{path}` 프록시 라우팅
  - Services
    - Auth Service (FastAPI): 인증/권한/RBAC
    - CBAM Service (FastAPI): 설치/제품/공정/엣지/계산/마스터 데이터 도메인
  - PostgreSQL 15 (asyncpg, SQLAlchemy 2)
- **주요 원칙**
  - 데이터 무결성 우선: 누락/중복/순환 참조/단위 불일치 검증
  - 아토믹 디자인 + DDD: 프론트는 컴포넌트 레이어링, 백엔드는 도메인 분리
  - DevOps: Docker Compose, Railway 배포, 중앙 로깅/헬스체크

## 4. 데이터 모델 & 규칙 (Data Model & Rules)
- **핵심 엔터티**: `install`, `product`, `process`, `edge`, `product_process`, `process_attrdir_emission`, `fueldir`, `matdir`, `fuel_master`, `material_master`, `hs_cn_mapping`
- **관계 개요**:
  - Install 1─* Product, Install 1─* Process
  - Product *─* Process (via product_process)
  - Edge: Process↔Process(continue), Process→Product(produce), Product→Process(consume)
- **계산 규칙**:
  - continue: `target.attr_em = source.attr_em + target.attr_em`
  - produce: `product.attr_em = Σ(connected_processes.attr_em)`
  - consume: `to_next_process = product_amount - product_sell - product_eusell`
- **검증/에러 처리**:
  - 필수 데이터 누락, 중복 데이터, 순환 참조, 단위 불일치 시 계산 중단 및 명시적 에러

## 5. 데이터 흐름 (Data Flow)
- **End-to-End**: 사용자 입력 → React Form → `axiosClient` → Next.js rewrites → Gateway → CBAM Service → Service Layer → Repository → PostgreSQL → 응답 반환
- **예시(제품 생성)**: `/api/v1/boundary/product` → Gateway 프록시 → CBAM `/product` → Service/Repository → INSERT → 생성된 제품 엔티티 반환
- **보고/계산**:
  - 엣지 업데이트 시 계산 API 호출 → 공정별/제품별 배출량 재계산 → `process_attrdir_emission`/`product.attr_em` 업데이트 → 이력/로그 기록

## 6. 프론트엔드 UX & 보안 (Frontend UX & Security)
- **UX 설계**:
  - 산정경계 에디터: 노드/엣지 드래그, 자동 라우팅, 큰 그래프 가상화 렌더링
  - 권한 시각화: 외부 사업장 공정은 읽기 전용 스타일 적용
  - 상태 저장/복원: JSON 기반 빠른 로딩, React Query/훅으로 API 연동
- **보안/신뢰성**:
  - JWT 인증, 토큰 만료 시 자동 로그아웃
  - axios 재시도/중복요청 취소/타임아웃으로 네트워크 안정성 강화
  - Gateway CORS 화이트리스트, 서비스 라우팅 통합 로깅

---

### 부록 A. 배포/운영
- Docker Compose: `gateway`, `auth-service`, `cbam-service`, `postgres`
- Railway: 서비스/DB 배포, 환경변수 대시보드 관리
- 모니터링: 구조화 로그, `/health`, 응답시간/에러율 메트릭

### 부록 B. 실행/테스트 가이드
- 설치
  - `cd frontend && pnpm install`
  - `cd service/cbam-service && pip install -r requirements.txt`
- 실행
  - `docker-compose up -d gateway cal-boundary auth-service postgres`
  - `cd frontend && pnpm dev`
- 테스트
  - `cd frontend && pnpm test`
  - `cd service/cbam-service && pytest`

### 부록 C. 규칙 요약
- DB 스키마 임의 변경 금지(프로덕션 DB 우선 확인)
- 기존 기능 우선 재사용, 기능 보존 최우선
- 데이터 중복/누락 방지, 계산 이력화/감사 가능성 확보
