# CBAM 솔루션 - 상세 기능 가이드

## 📋 솔루션 개요

CBAM(Carbon Border Adjustment Mechanism) 배출량 산정을 위한 종합적인 솔루션입니다. 이 시스템은 노드 기반의 시각적 프로세스 플로우 에디터를 통해 복잡한 공정 체인을 관리하고, 실시간으로 배출량을 계산하며, 규제 보고를 위한 정확한 데이터를 제공합니다.

## 🏗️ 시스템 아키텍처

### 전체 구조
```
Frontend (Next.js 14, Port 3000)
    ↓
Gateway (FastAPI, Port 8080)
    ↓
Services:
├── Auth Service (Port 8000) - 사용자 인증 및 권한 관리
└── CBAM Service (Port 8001) - 핵심 CBAM 비즈니스 로직
    ↓
PostgreSQL Database (Port 5432)
```

### 기술 스택
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, @xyflow/react
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.0, asyncpg
- **Database**: PostgreSQL 15
- **DevOps**: Docker & Docker Compose, GitHub Actions
- **Package Manager**: pnpm

## 🎯 CBAM 핵심 기능

### 1. 제품-공정 관계 설정 및 관리

#### 제품 선택 및 공정 연결
- **제품 선택**: 드롭다운을 통한 제품 선택 인터페이스
- **공정 목록 표시**: 선택된 제품의 전체 공정 목록 시각화
- **사업장 정보 표시**: "사업장명의 공정명" 형태로 명확한 정보 제공
- **권한 관리**: 체크박스 기반 "사용 가능" 설정으로 접근 제어
- **관계 관리**: 공정 추가/제거를 통한 유연한 제품-공정 관계 관리

#### 구현 위치
- **Frontend**: `/cbam/install` 페이지의 "제품-공정 관계 설정" 탭
- **Backend**: `productprocess` 도메인을 통한 관계 관리 API
- **Database**: `productprocess` 테이블을 통한 관계 저장

### 2. 산정경계 설정 및 시각화

#### React Flow 기반 프로세스 에디터
- **노드 타입**: Process(공정), Product(제품), Edge(연결)
- **시각적 편집**: 드래그 앤 드롭으로 노드 배치 및 연결
- **실시간 업데이트**: 노드 변경 시 즉시 반영
- **자동 레이아웃**: ELK 알고리즘을 통한 최적화된 노드 배치

#### 사업장별 권한 관리
- **내부 사업장 공정**: 편집 가능한 공정 관리
- **외부 사업장 공정**: 읽기 전용으로 표시, 사용은 가능하지만 편집 불가
- **권한 시각화**: 색상 및 스타일로 권한 수준 구분

#### 구현 위치
- **Frontend**: `/cbam/process-manager` 페이지
- **Components**: `ProcessManager`, `ProcessNode`, `ProductNode`
- **Hooks**: `useProcessManager`, `useProcessCanvas`

### 3. 배출량 계산 엔진

#### 데이터 할당 로직 (dataallocation.mdc 기반)

##### 공정→공정 연결 (edge_kind = "continue")
```typescript
// source.attr_em이 target으로 누적 전달
target.attr_em = source.attr_em + target.attr_em
```
- **용도**: 공정 간 배출량 전파
- **계산**: 이전 공정의 배출량을 다음 공정에 누적
- **적용**: 전체 프로세스 체인의 배출량 추적

##### 공정→제품 연결 (edge_kind = "produce")
```typescript
// product.attr_em = sum(connected_processes.attr_em)
```
- **용도**: 제품별 총 배출량 집계
- **계산**: 연결된 모든 공정의 배출량 합계
- **적용**: 최종 제품의 탄소 발자국 계산

##### 제품→공정 연결 (edge_kind = "consume")
```typescript
// to_next_process = product_amount - product_sell - product_eusell
// target.mat_amount = to_next_process
// target.attr_em += product.attr_em
```
- **용도**: 제품 소비를 통한 다음 공정 입력량 계산
- **계산**: 생산량 - 판매량 - EU판매량 = 다음 공정 입력량
- **적용**: 제품의 전구물질 배출량을 다음 공정에 귀속

#### 실시간 계산 및 업데이트
- **자동 전파**: 엣지 변경 시 전체 그래프 재계산
- **순환 참조 방지**: DAG 위반 시 에러 반환
- **데이터 검증**: 필수 데이터 누락, 중복 데이터, 단위 불일치 검사
- **이력 관리**: 모든 계산 결과를 DB에 저장하고 로그 기록

#### 구현 위치
- **Backend**: `EmissionCalculationService` 클래스
- **API**: `/api/v1/cbam/calculation/emission/process/calculate`
- **Database**: `calculation_results` 테이블

### 4. 마스터 데이터 관리

#### 연료 마스터 (fuel_master.xlsx)
- **데이터 항목**: 연료명, 영어명, 배출계수, 순발열량
- **용도**: 직접연료 배출량 계산
- **관리**: CRUD 작업을 통한 연료 정보 관리

#### 원재료 마스터 (material_master.xlsx)
- **데이터 항목**: 품목명, 영어명, 탄소계수, 배출계수, CN코드
- **용도**: 직접재료 배출량 계산
- **관리**: HS-CN 코드와 연동된 원재료 정보 관리

#### HS-CN 매핑 (hs_cn_mapping.xlsx)
- **데이터 항목**: HS코드, CN코드, 상품명, 상세분류
- **용도**: 국제 표준 코드 기반 상품 분류
- **관리**: 자동 매핑 및 수동 보정 기능

#### 구현 위치
- **Backend**: `matdir`, `fueldir`, `mapping` 도메인
- **API**: `/api/v1/cbam/matdir/*`, `/api/v1/cbam/fueldir/*`, `/api/v1/cbam/mapping/*`
- **Database**: `fuels`, `materials`, `mapping` 테이블

### 5. 사용자 권한 및 인증 시스템

#### 역할 기반 접근 제어 (RBAC)
- **super_admin**: 시스템 전체 관리 권한
- **company_admin**: 기업 내 모든 CBAM 관련 권한
- **manager**: 팀 관리 및 데이터 편집 권한
- **user**: 기본 데이터 조회 및 편집 권한
- **viewer**: 데이터 조회만 가능

#### 권한별 기능 접근
- **데이터 편집**: 내부 사업장 데이터만 편집 가능
- **데이터 조회**: 모든 사업장 데이터 조회 가능
- **계산 실행**: 권한이 있는 사용자만 배출량 계산 실행
- **보고서 생성**: 권한에 따른 보고서 접근 제어

#### 구현 위치
- **Backend**: `auth-service`의 `permissions.py`
- **Frontend**: `CommonShell` 컴포넌트를 통한 권한 검증
- **API**: 모든 CBAM API에 권한 검증 미들웨어 적용

## 📁 프로젝트 구조 (CBAM 중심)

### Frontend (`/frontend`)
```
src/
├── app/(protected)/cbam/    # CBAM 관련 페이지
│   ├── install/             # 사업장 및 제품-공정 관계 관리
│   ├── process/             # 공정 관리
│   └── process-manager/     # 산정경계 설정 (React Flow)
├── components/cbam/          # CBAM 전용 컴포넌트
│   ├── ProcessManager.tsx   # 프로세스 관리 메인 컴포넌트
│   ├── InputManager.tsx     # 입력 데이터 관리
│   ├── InstallSelector.tsx  # 사업장 선택기
│   ├── ProductSelector.tsx  # 제품 선택기
│   └── ProcessSelector.tsx  # 공정 선택기
└── hooks/                   # CBAM 관련 커스텀 훅
    ├── useProcessManager.ts # 프로세스 관리 로직
    ├── useProcessCanvas.ts  # React Flow 캔버스 관리
    └── useReactFlowAPI.ts   # React Flow API 연동
```

### Backend Services (`/service`)
```
service/
├── cbam-service/            # CBAM 핵심 서비스
│   ├── app/domain/
│   │   ├── install/         # 사업장 관리
│   │   ├── product/         # 제품 관리
│   │   ├── process/         # 공정 관리
│   │   ├── edge/            # 엣지 관리
│   │   ├── calculation/     # 배출량 계산
│   │   ├── matdir/          # 직접재료 배출량
│   │   ├── fueldir/         # 직접연료 배출량
│   │   └── mapping/         # HS-CN 매핑
│   └── main.py
└── auth-service/            # 인증 및 권한 관리
    ├── app/common/
    │   ├── permissions.py   # 권한 정의
    │   └── security.py      # 보안 설정
    └── main.py
```

### Gateway (`/gateway`)
- **역할**: CBAM API 요청의 중앙 라우팅
- **경로**: `/api/v1/cbam/{path}` 형식
- **서비스 구분**: 
  - CBAM: `/api/v1/cbam/*`
  - Auth: `/auth/*`

## 🔧 핵심 구현 원칙

### 1. 데이터 할당 로직 (dataallocation.mdc)
- **규제 보고 목적**: 엣지 변경 시마다 전체 그래프 재계산
- **API 응답**: 공정 단계별 emission 값과 최종 제품 emission 값 제공
- **DB 업데이트**: 계산 결과를 DB에 업데이트하고 이력(log) 기록
- **에러 처리**: 필수 데이터 누락, 중복 데이터, 순환 참조, 단위 불일치 검사

### 2. 개발 규칙 (rule1.mdc)
- **DB 스키마 변경 금지**: Railway PostgreSQL DB 스키마 확인 후 진행
- **기존 기능 활용**: 새로 만들지 말고 기존 기능에서 수정
- **기능 보존**: 기존 기능을 해치지 않아야 함

### 3. 아토믹 디자인 패턴
- **atoms**: ProcessNode, ProductNode, Button, Input
- **molecules**: ProcessSelector, ProductSelector
- **organisms**: ProcessManager, InputManager
- **templates**: 페이지 레이아웃 및 구조

## 🚀 주요 기능 구현 방법

### 1. 제품-공정 관계 설정

#### Frontend 구현
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

#### Backend API
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

## 📊 데이터베이스 스키마 (CBAM 중심)

### 핵심 테이블
- **install**: 사업장 정보
- **product**: 제품 정보
- **process**: 공정 정보
- **edge**: 공정 간 연결 관계
- **productprocess**: 제품-공정 관계
- **processchain**: 프로세스 체인 정보
- **fuels**: 연료 마스터 데이터
- **materials**: 원재료 마스터 데이터
- **mapping**: HS-CN 코드 매핑
- **calculation_results**: 배출량 계산 결과

### 관계 구조
```
Install (사업장)
├── Product (제품)
│   ├── Process (공정) - 직접 연결
│   └── Edge (연결) - 간접 연결
└── Process (공정) - 직접 생성

Edge (연결)
├── source_process (출발 공정)
├── target_process (도착 공정)
└── edge_kind (continue/produce/consume)
```

## 🔐 권한 시스템

### 사용자 역할별 CBAM 접근 권한
- **super_admin**: 모든 CBAM 기능 접근 가능
- **company_admin**: 기업 내 CBAM 데이터 관리 및 계산 실행
- **manager**: 팀 단위 CBAM 데이터 편집 및 계산 실행
- **user**: 기본 CBAM 데이터 조회 및 편집
- **viewer**: CBAM 데이터 조회만 가능

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
feat: 새로운 CBAM 기능 추가
fix: CBAM 관련 버그 수정
docs: CBAM 문서 업데이트
style: CBAM 코드 스타일 변경
refactor: CBAM 코드 리팩토링
test: CBAM 테스트 코드 추가/수정
chore: CBAM 빌드 프로세스 또는 보조 도구 변경
```

## 🎯 CBAM 솔루션의 핵심 가치

1. **규제 준수**: CBAM 규정에 맞는 정확한 배출량 계산
2. **시각적 관리**: React Flow를 통한 직관적인 프로세스 관리
3. **실시간 계산**: 엣지 변경 시 즉시 전체 시스템 재계산
4. **권한 관리**: 사업장별 데이터 접근 및 편집 권한 제어
5. **확장성**: MSA 아키텍처를 통한 유연한 시스템 확장
6. **데이터 무결성**: 순환 참조 방지 및 데이터 검증을 통한 신뢰성 확보

이 CBAM 솔루션을 통해 기업은 복잡한 공정 체인의 탄소 배출량을 정확하게 계산하고, 규제 요구사항을 충족하며, 지속가능한 경영을 위한 의사결정을 지원받을 수 있습니다.
