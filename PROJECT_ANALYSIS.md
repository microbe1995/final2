# 🏗️ GreenSteel MSA 프로젝트 상세 분석 문서

## 📋 프로젝트 개요

GreenSteel은 **Next.js + TypeScript + React + FastAPI + PostgreSQL**을 기반으로 한 **마이크로서비스 아키텍처(MSA)** 프로젝트입니다. CBAM(Carbon Border Adjustment Mechanism) 및 LCA(Life Cycle Assessment) 기능을 제공하는 ESG 관리 플랫폼입니다.

---

## 🏛️ 아키텍처 구조

### **전체 시스템 구조**
```
Frontend (Next.js, Port 3000)
    ↓ HTTP 요청
Gateway (FastAPI, Port 8080)
    ↓ 라우팅
Services (FastAPI, Port 8000-8001)
    ↓ 데이터 접근
PostgreSQL (Port 5432)
```

### **MSA 서비스 구성**
- **Frontend**: Next.js 14 + TypeScript + React 18 + Tailwind CSS
- **Gateway**: FastAPI 기반 API Gateway (라우팅 및 인증)
- **Auth Service**: 사용자 인증 및 권한 관리 (Port 8000)
- **CBAM Service**: CBAM 계산 및 경계 관리 (Port 8001)
- **Database**: PostgreSQL 15 + SQLAlchemy ORM

---

## 🎯 현재 구현된 기능들

### **1. 🔐 인증 시스템 (Auth Service)**

#### **구현된 기능:**
- **회원가입/로그인**: JWT 토큰 기반 인증
- **토큰 갱신**: 자동 토큰 갱신 메커니즘
- **권한 관리**: 사용자별 접근 권한 제어
- **세션 관리**: 로컬 스토리지 기반 세션 유지

#### **기술 스택:**
- FastAPI + SQLAlchemy
- JWT 토큰 인증
- PostgreSQL 사용자 테이블
- Pydantic 스키마 검증

### **2. 🏭 CBAM 시스템 (CBAM Service)**

#### **2.1 사업장 관리 (Install Management)**

**구현된 기능:**
- ✅ **사업장 생성/수정/삭제**: CRUD 작업 완전 구현
- ✅ **보고기간 설정**: `reporting_year` 필드로 연도별 관리
- ✅ **사업장 목록 조회**: 페이지네이션 및 정렬 지원
- ✅ **사업장별 제품 관리**: 계층적 데이터 구조

**데이터 모델:**
```sql
install 테이블:
- id (Primary Key)
- install_name (사업장명)
- reporting_year (보고기간)
- created_at, updated_at (타임스탬프)
```

#### **2.2 제품 관리 (Product Management)**

**구현된 기능:**
- ✅ **제품 생성/수정/삭제**: 사업장별 제품 CRUD
- ✅ **제품 분류**: 단순제품/복합제품 카테고리
- ✅ **제품 기간 관리**: `prostart_period`, `proend_period`
- ✅ **제품 수량 관리**: `product_amount`, `product_sell`, `product_eusell`
- ✅ **CN 코드 관리**: CBAM 대상 제품 식별용
- ✅ **계층적 구조**: Install → Product 관계

**데이터 모델:**
```sql
product 테이블:
- id (Primary Key)
- install_id (Foreign Key → install.id)
- product_name (제품명)
- product_category (단순제품/복합제품)
- prostart_period, proend_period (기간)
- product_amount (제품 수량)
- product_cncode (CN 코드)
- goods_name, aggrgoods_name (품목명)
- product_sell, product_eusell (판매량)
- created_at, updated_at
```

#### **2.3 공정 관리 (Process Management)**

**구현된 기능:**
- ✅ **공정 생성/수정/삭제**: 제품별 공정 CRUD
- ✅ **공정 기간 관리**: `start_period`, `end_period` (선택적)
- ✅ **계층적 구조**: Install → Product → Process
- ✅ **크로스 사업장 공정**: 다른 사업장의 공정도 표시 가능

**데이터 모델:**
```sql
process 테이블:
- id (Primary Key)
- product_id (Foreign Key → product.id)
- process_name (공정명)
- start_period, end_period (기간, NULL 허용)
- created_at, updated_at
```

#### **2.4 공정 입력 데이터 관리 (Process Input)**

**구현된 기능:**
- ✅ **입력 데이터 CRUD**: 원료, 연료, 전력 사용량 관리
- ✅ **배출량 계산**: 직접/간접 배출량 자동 계산
- ✅ **입력 유형 분류**: 원료/연료/전력/기타
- ✅ **계산 공식**: `amount × factor × oxy_factor`

**데이터 모델:**
```sql
process_input 테이블:
- id (Primary Key)
- process_id (Foreign Key → process.id)
- input_name (입력명)
- input_type (원료/연료/전력/기타)
- input_amount (입력량)
- factor (배출계수)
- oxy_factor (산화계수)
- direm (직접배출량)
- indirem (간접배출량)
- created_at, updated_at
```

### **3. 🎨 프론트엔드 UI/UX**

#### **3.1 아토믹 디자인 시스템**

**구현된 컴포넌트:**

**Atoms (기본 UI 요소):**
- ✅ **Button**: 다양한 스타일과 상태 지원
- ✅ **Input**: 폼 입력 필드
- ✅ **DataTable**: 데이터 테이블 표시
- ✅ **StatusBadge**: 상태 표시 배지
- ✅ **ProgressBar**: 진행률 표시
- ✅ **SectionTitle**: 섹션 제목
- ✅ **HandleStyles**: ReactFlow 핸들 스타일
- ✅ **CustomEdge**: 커스텀 엣지 스타일

**Molecules (단순 조합):**
- ✅ **InfoCard**: 정보 카드
- ✅ **ProductInfoGrid**: 제품 정보 그리드
- ✅ **ReportGenerationForm**: 보고서 생성 폼
- ✅ **ReportStatusList**: 보고서 상태 목록
- ✅ **TabGroup**: 탭 그룹

**Organisms (복잡한 조합):**
- ✅ **LCAAnalysisSection**: LCA 분석 섹션
- ✅ **LCAResultsSection**: LCA 결과 섹션
- ✅ **ProductInfoSection**: 제품 정보 섹션
- ✅ **ReportHeader**: 보고서 헤더
- ✅ **ReportSidebar**: 보고서 사이드바

**Templates (페이지 레이아웃):**
- ✅ **ReportPageTemplate**: 보고서 페이지 템플릿
- ✅ **LCALayout**: LCA 레이아웃
- ✅ **ErrorBoundary**: 에러 경계

#### **3.2 ReactFlow 기반 시각화**

**구현된 기능:**
- ✅ **ProductNode**: 제품 노드 컴포넌트
- ✅ **ProcessNode**: 공정 노드 컴포넌트 (크로스 사업장 지원)
- ✅ **CustomEdge**: 커스텀 엣지 연결
- ✅ **다중 캔버스**: 사업장별 독립적인 캔버스
- ✅ **크로스 사업장 공정**: 외부 사업장 공정 회색 표시
- ✅ **드래그 앤 드롭**: 노드 위치 자유 이동
- ✅ **연결 관리**: 노드 간 엣지 연결/해제

**특별 기능:**
- **읽기 전용 외부 공정**: 다른 사업장의 공정은 회색으로 표시, 데이터 편집 불가
- **위치 이동 가능**: 외부 공정도 드래그로 위치 조정 가능
- **시각적 구분**: 현재 사업장 vs 외부 사업장 공정 명확히 구분

#### **3.3 페이지 구조**

**CBAM 모듈:**
```
/cbam/
├── page.tsx (메인 대시보드)
├── install/
│   ├── page.tsx (사업장 관리)
│   └── [id]/
│       └── products/
│           └── page.tsx (제품별 공정 관리)
├── process-manager/
│   └── page.tsx (산정경계설정 - ReactFlow)
└── calculation/
    └── page.tsx (계산 관리)
```

**LCA 모듈:**
```
/lca/
├── page.tsx (LCA 대시보드)
├── scope/
│   └── page.tsx (프로젝트 스코프)
├── lci/
│   └── page.tsx (생명주기 인벤토리)
├── lcia/
│   └── page.tsx (생명주기 영향평가)
├── interpretation/
│   └── page.tsx (결과 해석)
└── report/
    └── page.tsx (보고서 생성)
```

### **4. 🔧 백엔드 API**

#### **4.1 Gateway (API Gateway)**

**구현된 기능:**
- ✅ **서비스 라우팅**: `/api/v1/{service}/{path}` 형식
- ✅ **인증 미들웨어**: JWT 토큰 검증
- ✅ **CORS 설정**: 프론트엔드와의 통신 허용
- ✅ **에러 핸들링**: 통합 에러 응답
- ✅ **로깅**: 요청/응답 로깅

**라우팅 구조:**
```
/api/v1/auth/* → Auth Service (Port 8000)
/api/v1/boundary/* → CBAM Service (Port 8001)
```

#### **4.2 CBAM Service API**

**사업장 관리:**
- `GET /api/v1/boundary/install` - 사업장 목록
- `POST /api/v1/boundary/install` - 사업장 생성
- `GET /api/v1/boundary/install/{id}` - 사업장 조회
- `PUT /api/v1/boundary/install/{id}` - 사업장 수정
- `DELETE /api/v1/boundary/install/{id}` - 사업장 삭제

**제품 관리:**
- `GET /api/v1/boundary/product` - 제품 목록
- `POST /api/v1/boundary/product` - 제품 생성
- `GET /api/v1/boundary/product/{id}` - 제품 조회
- `PUT /api/v1/boundary/product/{id}` - 제품 수정
- `DELETE /api/v1/boundary/product/{id}` - 제품 삭제

**공정 관리:**
- `GET /api/v1/boundary/process` - 공정 목록
- `POST /api/v1/boundary/process` - 공정 생성
- `GET /api/v1/boundary/process/{id}` - 공정 조회
- `PUT /api/v1/boundary/process/{id}` - 공정 수정
- `DELETE /api/v1/boundary/process/{id}` - 공정 삭제

**공정 입력 데이터:**
- `GET /api/v1/boundary/process-input` - 입력 데이터 목록
- `POST /api/v1/boundary/process-input` - 입력 데이터 생성
- `GET /api/v1/boundary/process-input/{id}` - 입력 데이터 조회
- `PUT /api/v1/boundary/process-input/{id}` - 입력 데이터 수정
- `DELETE /api/v1/boundary/process-input/{id}` - 입력 데이터 삭제

### **5. 🗄️ 데이터베이스 구조**

#### **5.1 테이블 관계**

```sql
install (사업장)
├── id (PK)
├── install_name
├── reporting_year
└── created_at, updated_at

product (제품)
├── id (PK)
├── install_id (FK → install.id)
├── product_name
├── product_category
├── prostart_period, proend_period
├── product_amount
├── product_cncode
├── goods_name, aggrgoods_name
├── product_sell, product_eusell
└── created_at, updated_at

process (공정)
├── id (PK)
├── product_id (FK → product.id)
├── process_name
├── start_period, end_period
└── created_at, updated_at

process_input (공정 입력 데이터)
├── id (PK)
├── process_id (FK → process.id)
├── input_name
├── input_type
├── input_amount
├── factor
├── oxy_factor
├── direm (직접배출량)
├── indirem (간접배출량)
└── created_at, updated_at
```

#### **5.2 제약 조건**
- **Foreign Key**: 계층적 데이터 무결성 보장
- **NOT NULL**: 필수 필드 보장
- **Index**: 조회 성능 최적화
- **Timestamp**: 생성/수정 시간 자동 관리

### **6. 🚀 배포 및 인프라**

#### **6.1 Docker 컨테이너화**
- ✅ **Frontend**: Next.js 컨테이너
- ✅ **Gateway**: FastAPI 컨테이너
- ✅ **Auth Service**: 인증 서비스 컨테이너
- ✅ **CBAM Service**: CBAM 서비스 컨테이너
- ✅ **PostgreSQL**: 데이터베이스 컨테이너

#### **6.2 배포 환경**
- **Vercel**: 프론트엔드 배포
- **Railway**: 백엔드 서비스 및 데이터베이스 배포
- **GitHub Actions**: CI/CD 파이프라인

### **7. 🔒 보안 기능**

#### **7.1 인증 및 권한**
- ✅ **JWT 토큰**: 안전한 인증 메커니즘
- ✅ **토큰 갱신**: 자동 토큰 갱신
- ✅ **세션 관리**: 로컬 스토리지 기반
- ✅ **API 보호**: 인증된 요청만 허용

#### **7.2 데이터 보호**
- ✅ **입력 검증**: Pydantic 스키마 검증
- ✅ **SQL 인젝션 방지**: SQLAlchemy ORM 사용
- ✅ **CORS 설정**: 허용된 도메인만 접근
- ✅ **에러 핸들링**: 민감한 정보 노출 방지

### **8. 📊 성능 최적화**

#### **8.1 프론트엔드**
- ✅ **React.memo**: 불필요한 리렌더링 방지
- ✅ **useCallback/useMemo**: 성능 최적화
- ✅ **코드 스플리팅**: Next.js 자동 코드 분할
- ✅ **이미지 최적화**: Next.js Image 컴포넌트

#### **8.2 백엔드**
- ✅ **데이터베이스 인덱스**: 조회 성능 최적화
- ✅ **연결 풀링**: 데이터베이스 연결 효율성
- ✅ **비동기 처리**: FastAPI 비동기 지원
- ✅ **캐싱**: 자주 사용되는 데이터 캐싱

### **9. 🧪 테스트 및 품질**

#### **9.1 코드 품질**
- ✅ **TypeScript**: 타입 안전성 보장
- ✅ **ESLint**: 코드 스타일 검사
- ✅ **Prettier**: 코드 포맷팅
- ✅ **Pydantic**: 데이터 검증

#### **9.2 테스트**
- ✅ **Jest**: 프론트엔드 테스트 프레임워크
- ✅ **React Testing Library**: 컴포넌트 테스트
- ✅ **FastAPI TestClient**: 백엔드 API 테스트

---

## 🎯 핵심 비즈니스 로직

### **1. CBAM 계산 로직**
```python
# 직접 배출량 계산
direm = input_amount × factor × oxy_factor

# 간접 배출량 계산
indirem = input_amount × factor × oxy_factor

# 총 배출량
total_emission = direm + indirem
```

### **2. 계층적 데이터 관리**
```
Install (사업장)
├── Product 1 (제품)
│   ├── Process 1 (공정)
│   │   └── Process Input (입력 데이터)
│   └── Process 2 (공정)
│       └── Process Input (입력 데이터)
└── Product 2 (제품)
    └── Process 3 (공정)
        └── Process Input (입력 데이터)
```

### **3. 크로스 사업장 공정 관리**
- **현재 사업장 공정**: 녹색 노드, 편집 가능
- **외부 사업장 공정**: 회색 노드, 읽기 전용, 위치 이동 가능
- **시각적 구분**: 투명도와 색상으로 명확히 구분

---

## 📈 현재 상태 및 향후 계획

### **✅ 완료된 기능**
1. **기본 CRUD**: 모든 엔티티의 생성/조회/수정/삭제
2. **계층적 관리**: Install → Product → Process → Process Input
3. **시각화**: ReactFlow 기반 다이어그램
4. **크로스 사업장**: 외부 사업장 공정 표시
5. **배출량 계산**: 기본적인 배출량 계산 로직
6. **인증 시스템**: JWT 기반 사용자 인증
7. **MSA 구조**: 완전한 마이크로서비스 아키텍처

### **🔄 진행 중인 기능**
1. **CBAM 비즈니스 로직**: 고급 계산 알고리즘
2. **보고서 생성**: 자동 보고서 생성 시스템
3. **데이터 검증**: 고급 데이터 검증 로직

### **📋 향후 계획**
1. **고급 CBAM 계산**: 복잡한 배출량 계산 알고리즘
2. **실시간 모니터링**: 실시간 데이터 업데이트
3. **고급 시각화**: 3D 다이어그램 및 애니메이션
4. **모바일 앱**: React Native 기반 모바일 앱
5. **AI 통합**: 머신러닝 기반 예측 및 분석

---

## 🛠️ 기술적 특징

### **1. 아키텍처 패턴**
- **MSA (Microservices Architecture)**: 서비스 분리 및 독립성
- **DDD (Domain-Driven Design)**: 도메인 중심 설계
- **CQRS**: 명령과 조회 분리
- **Event Sourcing**: 이벤트 기반 데이터 관리

### **2. 개발 패턴**
- **아토믹 디자인**: 컴포넌트 재사용성 극대화
- **단일 책임 원칙**: 각 컴포넌트의 명확한 역할
- **관심사 분리**: 프론트엔드/백엔드 명확히 분리
- **의존성 주입**: 느슨한 결합 구조

### **3. 성능 최적화**
- **React.memo**: 불필요한 리렌더링 방지
- **데이터베이스 인덱스**: 조회 성능 최적화
- **코드 스플리팅**: 번들 크기 최적화
- **캐싱 전략**: 자주 사용되는 데이터 캐싱

---

## 📝 결론

GreenSteel MSA 프로젝트는 **현대적인 웹 개발 기술 스택**과 **견고한 아키텍처 패턴**을 기반으로 구축된 **완전한 ESG 관리 플랫폼**입니다. 

현재 **CBAM의 핵심 기능들이 모두 구현**되어 있으며, **크로스 사업장 공정 관리**와 **시각적 다이어그램**을 통해 복잡한 생산 과정을 직관적으로 관리할 수 있습니다.

**MSA 구조**로 인해 각 서비스가 독립적으로 개발, 배포, 확장 가능하며, **TypeScript**와 **Pydantic**을 통한 **타입 안전성**이 보장되어 있습니다.

이 프로젝트는 **실제 CBAM 규정을 준수**하면서도 **사용자 친화적인 인터페이스**를 제공하는 **프로덕션 레벨의 애플리케이션**입니다.
