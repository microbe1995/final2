# CBAM/LCA 프로젝트 - 상세 구현 가이드

## 📋 프로젝트 개요

이 프로젝트는 CBAM(Carbon Border Adjustment Mechanism) 배출량 산정을 위한 종합적인 LCA(Life Cycle Assessment) 솔루션입니다. MSA(Microservice Architecture) 기반으로 구축되어 있으며, 노드 기반의 시각적 프로세스 플로우 에디터를 통해 복잡한 공정 체인을 관리하고 배출량을 계산합니다.

## 🏗️ 시스템 아키텍처

### 전체 구조
```
Frontend (Next.js 14, Port 3000)
    ↓
Gateway (FastAPI, Port 8080)
    ↓
Services:
├── Auth Service (Port 8000) - 사용자 인증 및 권한 관리
└── CBAM Service (Port 8001) - 핵심 비즈니스 로직
    ↓
PostgreSQL Database (Port 5432)
```

### 기술 스택
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, @xyflow/react
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.0, asyncpg
- **Database**: PostgreSQL 15
- **DevOps**: Docker & Docker Compose, GitHub Actions
- **Package Manager**: pnpm

## 🎯 핵심 기능

### 1. 제품-공정 관계 설정
- **제품 선택**: 드롭다운으로 제품 선택
- **공정 목록 표시**: 선택된 제품의 전체 공정 목록
- **사업장 정보**: "사업장명의 공정명" 형태로 표시
- **권한 관리**: 체크박스로 "사용 가능" 설정
- **관계 관리**: 공정 추가/제거 기능

### 2. 산정경계 설정
- **사업장별 제품 생산**: 특정 사업장에서 제품 생산 시
- **사전 설정 공정**: 미리 정의된 공정 목록에서 선택
- **외부 사업장 공정**: 읽기 전용으로 표시, 사용은 가능하지만 편집 불가

### 3. 배출량 계산 엔진
- **노드 기반 계산**: Process, Product, Edge를 통한 연결
- **자동 전파**: 공정 간 배출량 자동 계산 및 전파
- **실시간 업데이트**: 엣지 변경 시 전체 그래프 재계산

## 📁 프로젝트 구조

### Frontend (`/frontend`)
```
src/
├── app/                    # Next.js 14 App Router
│   ├── (protected)/       # 인증 필요 페이지
│   │   ├── cbam/         # CBAM 관련 페이지
│   │   │   ├── install/  # 사업장 관리
│   │   │   ├── process/  # 공정 관리
│   │   │   └── process-manager/ # 산정경계 설정
│   │   ├── lca/          # LCA 분석
│   │   ├── dashboard/    # 대시보드
│   │   └── settings/     # 설정
│   └── (public)/         # 공개 페이지
├── components/            # React 컴포넌트
│   ├── atomic/           # 아토믹 디자인 패턴
│   │   ├── atoms/        # 기본 UI 요소
│   │   ├── molecules/    # 단순 조합
│   │   ├── organisms/    # 복잡한 조합
│   │   └── templates/    # 페이지 레이아웃
│   ├── cbam/            # CBAM 전용 컴포넌트
│   └── common/          # 공통 컴포넌트
├── hooks/                # 커스텀 React 훅
├── lib/                  # 유틸리티 및 설정
└── types/                # TypeScript 타입 정의
```

### Backend Services (`/service`)
```
service/
├── auth-service/         # 인증 서비스
│   ├── app/
│   │   ├── domain/      # 도메인 로직
│   │   ├── router/      # API 라우터
│   │   └── common/      # 공통 기능
│   └── requirements.txt
└── cbam-service/        # CBAM 핵심 서비스
    ├── app/
    │   ├── domain/      # 도메인별 모듈
    │   │   ├── install/     # 사업장 관리
    │   │   ├── product/     # 제품 관리
    │   │   ├── process/     # 공정 관리
    │   │   ├── edge/        # 엣지 관리
    │   │   ├── calculation/ # 배출량 계산
    │   │   ├── matdir/      # 직접재료 배출량
    │   │   ├── fueldir/     # 직접연료 배출량
    │   │   └── mapping/     # HS-CN 매핑
    │   └── main.py
    └── requirements.txt
```

### Gateway (`/gateway`)
- **역할**: 모든 API 요청의 중앙 라우팅
- **경로**: `/api/v1/{service}/{path}` 형식
- **서비스 구분**: 
  - Auth: `/auth/` prefix
  - CBAM: `/api/` prefix

## 🔧 핵심 구현 원칙

### 1. 데이터 할당 로직 (dataallocation.mdc)
```typescript
// 공정→공정 (edge_kind = "continue")
// source.attr_em이 target으로 누적 전달
target.attr_em = source.attr_em + target.attr_em

// 공정→제품 (edge_kind = "produce")
// product.attr_em = sum(connected_processes.attr_em)

// 제품→공정 (edge_kind = "consume")
// to_next_process = product_amount - product_sell - product_eusell
// 여러 공정으로 소비될 경우 생산량 비율에 따라 분배
```

### 2. 개발 규칙 (rule1.mdc)
- **DB 스키마 변경 금지**: Railway PostgreSQL DB 스키마 확인 후 진행
- **기존 기능 활용**: 새로 만들지 말고 기존 기능에서 수정
- **기능 보존**: 기존 기능을 해치지 않아야 함

### 3. 아토믹 디자인 패턴
- **atoms**: 기본 UI 요소 (Button, Input, ProcessNode, ProductNode)
- **molecules**: 단순 조합 (ProcessSelector, ProductSelector)
- **organisms**: 복잡한 조합 (ProcessManager, InputManager)
- **templates**: 페이지 레이아웃 (LcaLayout, ReportPageTemplate)

## 🚀 주요 기능 구현 방법

### 1. 제품-공정 관계 설정

#### Frontend 구현 (`/cbam/install` 페이지)
```typescript
// 탭 기반 인터페이스
const [activeTab, setActiveTab] = useState<'install' | 'product-process'>('install');

// 제품-공정 관계 상태 관리
const [productProcessRelations, setProductProcessRelations] = useState<Map<number, any[]>>(new Map());

// 공정 추가/제거 함수
const handleAddProcessToProduct = async (productId: number, processId: number) => {
  await axiosClient.post(apiEndpoints.cbam.productProcess.create, {
    product_id: productId,
    process_id: processId
  });
};
```

#### Backend API 엔드포인트
```typescript
// API 경로 구조
cbam: {
  productProcess: {
    create: '/api/v1/cbam/productprocess',
    delete: (id: number) => `/api/v1/cbam/productprocess/${id}`
  }
}
```

### 2. 산정경계 설정

#### ProcessManager 컴포넌트
```typescript
// React Flow 기반 시각적 에디터
import { ReactFlow, ReactFlowProvider } from '@xyflow/react';

// 커스텀 노드 타입
const nodeTypes: NodeTypes = {
  process: ProcessNode,
  product: ProductNode
};

// 커스텀 엣지 타입
const edgeTypes: EdgeTypes = { custom: CustomEdge };
```

#### 권한 관리
```typescript
// 외부 사업장 공정 읽기 전용 처리
const isExternalProcess = data.install_id !== data.current_install_id;
const effectiveVariant = isExternalProcess ? 'readonly' : finalVariant;

// 읽기 전용 스타일
const readonlyStyles = 'bg-gray-100 border-gray-400 text-gray-600 opacity-75';
```

### 3. 배출량 계산 엔진

#### 계산 로직
```python
# Python 백엔드 (cbam-service)
class EmissionCalculationService:
    async def propagate_emissions(self, process_chain_id: int):
        """전체 프로세스 체인의 배출량을 계산하고 전파"""
        
        # 1. 공정→공정 전파 (continue)
        for edge in continue_edges:
            target.attr_em += source.attr_em
            
        # 2. 공정→제품 집계 (produce)
        for product in products:
            product.attr_em = sum(connected_processes.attr_em)
            
        # 3. 제품→공정 분배 (consume)
        for consume_edge in consume_edges:
            to_next_process = product_amount - product_sell - product_eusell
            target.mat_amount = to_next_process
            target.attr_em += product.attr_em
```

## 📊 데이터베이스 스키마

### 핵심 테이블
- **install**: 사업장 정보
- **product**: 제품 정보
- **process**: 공정 정보
- **edge**: 공정 간 연결 관계
- **productprocess**: 제품-공정 관계
- **processchain**: 프로세스 체인 정보

### 관계 구조
```
Install (사업장)
├── Product (제품)
│   ├── Process (공정) - 직접 연결
│   └── Edge (연결) - 간접 연결
└── Process (공정) - 직접 생성
```

## 🔐 권한 시스템

### 사용자 역할
- **super_admin**: 시스템 전체 관리
- **company_admin**: 기업 내 모든 권한
- **manager**: 팀 관리 및 데이터 편집
- **user**: 기본 데이터 조회 및 편집
- **viewer**: 데이터 조회만 가능

### 권한 관리
```python
# permissions.py
def has_permission(user_permissions: dict, required_permission: str) -> bool:
    if "*" in user_permissions.get("permissions", []):
        return True
    return user_permissions.get(required_permission, False)
```

## 🧪 테스트 및 개발

### 개발 환경 설정
```bash
# 1. 의존성 설치
cd frontend && pnpm install
cd service/cbam-service && pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# Railway DB 연결 정보 설정

# 3. Docker 서비스 실행
docker-compose up -d gateway cal-boundary auth-service postgres

# 4. Frontend 개발 서버
cd frontend && pnpm dev
```

### 테스트 실행
```bash
# Frontend 테스트
cd frontend && pnpm test

# Backend 테스트
cd service/cbam-service && pytest
```

## 📈 성능 최적화

### React Flow 최적화
- **노드 렌더링**: 가상화를 통한 대규모 다이어그램 처리
- **엣지 라우팅**: 자동 라우팅 알고리즘으로 복잡한 연결 처리
- **상태 관리**: JSON 기반 상태 저장/복원으로 빠른 로딩

### 백엔드 최적화
- **비동기 처리**: SQLAlchemy async/await 패턴
- **배치 처리**: 대량 데이터 처리 시 배치 연산
- **캐싱**: 자주 사용되는 계산 결과 캐싱

## 🚨 에러 처리

### 프론트엔드 에러 처리
```typescript
// axiosClient.ts - 재시도 로직
const retryRequest = async (config: AxiosRequestConfig, retries: number = 3) => {
  try {
    return await axiosInstance(config);
  } catch (error) {
    if (retries > 0 && error.response?.status >= 500) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return retryRequest(config, retries - 1);
    }
    throw error;
  }
};
```

### 백엔드 에러 처리
```python
# 계산 중단 조건
if missing_data:
    raise CalculationError("필수 데이터 누락")
if duplicate_data:
    raise CalculationError("중복 데이터 발견")
if circular_reference:
    raise CalculationError("순환 참조 위반")
```

## 🔄 배포 및 운영

### Railway 배포
- **데이터베이스**: Railway PostgreSQL 사용
- **서비스**: Docker 컨테이너로 배포
- **환경 변수**: Railway 대시보드에서 관리

### 모니터링
- **로그**: 구조화된 로깅 시스템
- **헬스체크**: `/health` 엔드포인트로 서비스 상태 확인
- **메트릭**: API 응답 시간 및 에러율 모니터링

## 📚 추가 리소스

### 마스터 데이터
- **fuel_master.xlsx**: 연료 마스터 데이터
- **material_master.xlsx**: 원재료 마스터 데이터
- **hs_cn_mapping.xlsx**: HS-CN 코드 매핑
- **dummy_db.xlsx**: 테스트용 더미 데이터

### API 문서
- **Gateway**: `http://localhost:8080/docs`
- **Auth Service**: `http://localhost:8000/docs`
- **CBAM Service**: `http://localhost:8001/docs`

## 🤝 기여 가이드

### 코드 스타일
- **TypeScript**: 엄격한 타입 체크 사용
- **Python**: PEP 8 스타일 가이드 준수
- **컴포넌트**: 아토믹 디자인 패턴 준수
- **테스트**: 새로운 기능에 대한 테스트 코드 작성

### 커밋 메시지
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 업데이트
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 코드 추가/수정
chore: 빌드 프로세스 또는 보조 도구 변경
```

이 README를 통해 프로젝트의 전체 구조와 구현 방법을 이해하고, 동일한 기능을 다시 구현할 수 있습니다. 각 섹션은 실제 코드와 연관되어 있으며, 개발 시 참고할 수 있는 구체적인 예시를 포함하고 있습니다.
