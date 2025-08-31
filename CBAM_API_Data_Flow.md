# CBAM 시스템 API 데이터 흐름 가이드

## 📋 목차
1. [시스템 아키텍처 개요](#시스템-아키텍처-개요)
2. [전체 데이터 흐름](#전체-데이터-흐름)
3. [구체적인 예시: 제품 생성](#구체적인-예시-제품-생성)
4. [각 컴포넌트별 역할](#각-컴포넌트별-역할)
5. [API 엔드포인트 구조](#api-엔드포인트-구조)
6. [에러 처리 및 로깅](#에러-처리-및-로깅)

---

## 🏗️ 시스템 아키텍처 개요

CBAM(Carbon Border Adjustment Mechanism) 시스템은 마이크로서비스 아키텍처(MSA)를 기반으로 구성되어 있습니다.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Gateway       │    │  CBAM Service   │
│  (Next.js)      │◄──►│  (FastAPI)      │◄──►│  (FastAPI)      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Auth Service   │    │  PostgreSQL    │
                       │  (FastAPI)      │    │  Database      │
                       └─────────────────┘    └─────────────────┘
```

---

## 🔄 전체 데이터 흐름

### 기본 흐름
```
사용자 입력 → React Form → axiosClient → Next.js Rewrites → Gateway → CBAM Service → Service Layer → Repository → Database → 응답 반환
```

### 단계별 설명
1. **사용자 입력**: 프론트엔드 폼에서 데이터 입력
2. **React Form**: 입력 데이터 수집 및 검증
3. **axiosClient**: HTTP 요청 생성 및 인증 토큰 추가
4. **Next.js Rewrites**: 로컬 API 경로를 Gateway로 프록시
5. **Gateway**: 서비스 라우팅 및 요청 전달
6. **CBAM Service**: 비즈니스 로직 처리
7. **Service Layer**: 도메인 비즈니스 로직 실행
8. **Repository**: 데이터베이스 액세스 및 CRUD 작업
9. **Database**: 데이터 영구 저장
10. **응답 반환**: 역방향으로 데이터 전달

---

## 📝 구체적인 예시: 제품 생성

### 1. 프론트엔드 (React/Next.js)

```typescript
// frontend/src/app/(protected)/cbam/install/[id]/products/page.tsx
const handleProductSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  const productData = {
    product_name: "스테인리스강 판재",  // 사용자 입력값
    product_category: "금속제품",
    install_id: installId,
    product_amount: 1000,
    // ... 기타 필드들
  };

  try {
    // axiosClient를 통해 API 호출
    const response = await axiosClient.post(
      apiEndpoints.cbam.product.create,  // '/api/v1/boundary/product'
      productData
    );
    
    console.log('✅ 제품 생성 성공:', response.data);
  } catch (error) {
    console.error('❌ 제품 생성 실패:', error);
  }
};
```

### 2. Axios Client (HTTP 요청 처리)

```typescript
// frontend/src/lib/axiosClient.ts
const axiosClient: AxiosInstance = axios.create({
  baseURL: '', // 상대 경로 사용
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터에서 인증 토큰 추가
axiosClient.interceptors.request.use(config => {
  // 인증 토큰 추가
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});
```

**실제 HTTP 요청:**
```http
POST /api/v1/boundary/product HTTP/1.1
Host: lca-final.vercel.app
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "product_name": "스테인리스강 판재",
  "product_category": "금속제품",
  "install_id": 1,
  "product_amount": 1000
}
```

### 3. Next.js API Routes (프록시)

```typescript
// frontend/next.config.js (rewrites 설정)
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'https://gateway-production-22ef.up.railway.app/api/v1/:path*'
      }
    ]
  }
}
```

**Next.js가 요청을 Gateway로 전달:**
```http
POST https://gateway-production-22ef.up.railway.app/api/v1/boundary/product
```

### 4. Gateway Service (API Gateway)

```python
# gateway/app/main.py
SERVICE_MAP = {
    "boundary": "https://lcafinal-production.up.railway.app",  # CBAM 서비스
    # ... 기타 서비스들
}

async def proxy_request(service: str, path: str, request: Request) -> Response:
    base_url = SERVICE_MAP.get(service)  # "boundary" → CBAM 서비스 URL
    if not base_url:
        return JSONResponse(status_code=404, content={"detail": f"Unknown service: {service}"})

    # MSA 원칙: 각 서비스는 자체 경로 구조를 가져야 함
    normalized_path = path  # "product" (boundary 제거)
    target_url = f"{base_url.rstrip('/')}/{normalized_path}"
    
    # 실제 타겟: https://lcafinal-production.up.railway.app/product
    
    logger.info(f"🔄 프록시 라우팅: {service} -> {target_url}")
    # ... HTTP 요청 전달
```

**Gateway가 요청을 CBAM 서비스로 전달:**
```http
POST https://lcafinal-production.up.railway.app/product
```

### 5. CBAM Service (백엔드)

```python
# service/cbam-service/app/main.py
app.include_router(product_router)  # /product 경로 (prefix 없음)

# service/cbam-service/app/domain/product/product_controller.py
router = APIRouter(tags=["Product"])

@router.post("/", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest):
    """제품 생성"""
    try:
        logger.info(f"📝 제품 생성 요청: {request.product_name}")
        product_service = get_product_service()
        product = await product_service.create_product(request)
        
        logger.info(f"✅ 제품 생성 성공: ID {product.id}")
        return product
    except Exception as e:
        logger.error(f"❌ 제품 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 생성 중 오류가 발생했습니다: {str(e)}")
```

**실제 라우터 경로:**
- **요청받은 경로**: `/product` (POST)
- **처리 함수**: `create_product()`

### 6. Product Service (비즈니스 로직)

```python
# service/cbam-service/app/domain/product/product_service.py
class ProductService:
    async def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        try:
            # 1. 데이터 검증
            if not request.product_name:
                raise ValueError("제품명은 필수입니다")
            
            # 2. Repository를 통한 데이터 저장
            product_repo = ProductRepository()
            product = await product_repo.create_product(request)
            
            # 3. 응답 데이터 변환
            return ProductResponse(
                id=product.id,
                product_name=product.product_name,
                product_category=product.product_category,
                install_id=product.install_id,
                # ... 기타 필드들
            )
        except Exception as e:
            logger.error(f"제품 생성 서비스 오류: {str(e)}")
            raise
```

### 7. Product Repository (데이터 액세스)

```python
# service/cbam-service/app/domain/product/product_repository.py
class ProductRepository:
    async def create_product(self, request: ProductCreateRequest) -> Product:
        async with self.get_session() as session:
            try:
                # 1. 엔티티 생성
                product = Product(
                    product_name=request.product_name,      # "스테인리스강 판재"
                    product_category=request.product_category,  # "금속제품"
                    install_id=request.install_id,         # 1
                    product_amount=request.product_amount, # 1000
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                # 2. 데이터베이스에 저장
                session.add(product)
                await session.commit()
                await session.refresh(product)
                
                logger.info(f"✅ 제품 데이터베이스 저장 성공: ID {product.id}")
                return product
                
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ 제품 데이터베이스 저장 실패: {str(e)}")
                raise
```

### 8. 데이터베이스 (PostgreSQL)

```sql
-- 실제 실행되는 SQL 쿼리
INSERT INTO product (
    product_name, 
    product_category, 
    install_id, 
    product_amount, 
    created_at, 
    updated_at
) VALUES (
    '스테인리스강 판재',  -- 사용자 입력값
    '금속제품', 
    1, 
    1000, 
    '2024-01-15 10:30:00', 
    '2024-01-15 10:30:00'
) RETURNING id, product_name, product_category, install_id, product_amount, created_at, updated_at;
```

**데이터베이스 결과:**
```json
{
  "id": 123,
  "product_name": "스테인리스강 판재",
  "product_category": "금속제품",
  "install_id": 1,
  "product_amount": 1000,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 9. 응답 반환 (역방향)

```python
# Repository → Service → Controller → Gateway → Frontend

# 1. Repository에서 Product 엔티티 반환
# 2. Service에서 ProductResponse로 변환
# 3. Controller에서 HTTP 응답 생성
# 4. Gateway가 응답을 프론트엔드로 전달
# 5. Frontend에서 response.data로 받음
```

**최종 프론트엔드 응답:**
```typescript
// frontend에서 받는 응답
{
  "id": 123,
  "product_name": "스테인리스강 판재",
  "product_category": "금속제품",
  "install_id": 1,
  "product_amount": 1000,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## 🎯 각 컴포넌트별 역할

### Frontend (Next.js)
- **역할**: 사용자 인터페이스 제공, 데이터 입력 및 표시
- **기술**: React, TypeScript, Tailwind CSS
- **주요 기능**: 폼 처리, API 호출, 상태 관리

### Axios Client
- **역할**: HTTP 요청 처리, 인터셉터를 통한 공통 로직 처리
- **주요 기능**: 
  - 인증 토큰 자동 추가
  - 요청 중복 방지
  - 에러 처리 및 재시도
  - CSRF 토큰 관리

### Next.js Rewrites
- **역할**: 로컬 API 경로를 외부 서비스로 프록시
- **장점**: CORS 문제 해결, 개발/프로덕션 환경 통일

### Gateway Service
- **역할**: API 게이트웨이, 서비스 라우팅, 인증/인가
- **주요 기능**:
  - 서비스 디스커버리
  - 요청 라우팅
  - 로깅 및 모니터링
  - CORS 설정

### CBAM Service
- **역할**: CBAM 관련 비즈니스 로직 처리
- **구조**: DDD(Domain-Driven Design) 패턴 적용
- **도메인**: Install, Product, Process, Mapping, Calculation 등

### Service Layer
- **역할**: 도메인 비즈니스 로직 실행
- **특징**: 트랜잭션 관리, 데이터 검증, 비즈니스 규칙 적용

### Repository Layer
- **역할**: 데이터 액세스 추상화
- **기능**: CRUD 작업, 데이터베이스 연결 관리

### Database (PostgreSQL)
- **역할**: 데이터 영구 저장
- **특징**: ACID 트랜잭션, 관계형 데이터 모델

---

## 🌐 API 엔드포인트 구조

### 기본 패턴
```
/api/v1/boundary/{resource}
```

### 주요 리소스별 엔드포인트

#### Install (사업장 관리)
```
GET    /api/v1/boundary/install          # 사업장 목록
POST   /api/v1/boundary/install          # 사업장 생성
GET    /api/v1/boundary/install/{id}     # 사업장 조회
PUT    /api/v1/boundary/install/{id}     # 사업장 수정
DELETE /api/v1/boundary/install/{id}     # 사업장 삭제
GET    /api/v1/boundary/install/names    # 사업장명 목록
```

#### Product (제품 관리)
```
GET    /api/v1/boundary/product          # 제품 목록
POST   /api/v1/boundary/product          # 제품 생성
GET    /api/v1/boundary/product/{id}     # 제품 조회
PUT    /api/v1/boundary/product/{id}     # 제품 수정
DELETE /api/v1/boundary/product/{id}     # 제품 삭제
GET    /api/v1/boundary/product/names    # 제품명 목록
```

#### Process (공정 관리)
```
GET    /api/v1/boundary/process          # 공정 목록
POST   /api/v1/boundary/process          # 공정 생성
GET    /api/v1/boundary/process/{id}     # 공정 조회
PUT    /api/v1/boundary/process/{id}     # 공정 수정
DELETE /api/v1/boundary/process/{id}     # 공정 삭제
```

#### Mapping (HS-CN 매핑)
```
GET    /api/v1/boundary/mapping          # 매핑 목록
POST   /api/v1/boundary/mapping          # 매핑 생성
GET    /api/v1/boundary/mapping/{id}     # 매핑 조회
PUT    /api/v1/boundary/mapping/{id}     # 매핑 수정
DELETE /api/v1/boundary/mapping/{id}     # 매핑 삭제
GET    /api/v1/boundary/mapping/stats    # 매핑 통계
POST   /api/v1/boundary/mapping/batch   # 배치 매핑
```

#### Process Chain (공정 체인)
```
GET    /api/v1/boundary/processchain/chain     # 체인 목록
POST   /api/v1/boundary/processchain/chain     # 체인 생성
GET    /api/v1/boundary/processchain/chain/{id} # 체인 조회
DELETE /api/v1/boundary/processchain/chain/{id} # 체인 삭제
```

#### Edge (엣지 관리)
```
GET    /api/v1/boundary/edge             # 엣지 목록
POST   /api/v1/boundary/edge             # 엣지 생성
GET    /api/v1/boundary/edge/{id}        # 엣지 조회
DELETE /api/v1/boundary/edge/{id}        # 엣지 삭제
```

#### Material Directory (원료 직접배출량)
```
GET    /api/v1/boundary/matdir           # 원료 목록
POST   /api/v1/boundary/matdir           # 원료 생성
GET    /api/v1/boundary/matdir/{id}      # 원료 조회
PUT    /api/v1/boundary/matdir/{id}      # 원료 수정
DELETE /api/v1/boundary/matdir/{id}      # 원료 삭제
POST   /api/v1/boundary/matdir/calculate # 원료 계산
```

#### Fuel Directory (연료 직접배출량)
```
GET    /api/v1/boundary/fueldir          # 연료 목록
POST   /api/v1/boundary/fueldir          # 연료 생성
GET    /api/v1/boundary/fueldir/{id}     # 연료 조회
PUT    /api/v1/boundary/fueldir/{id}     # 연료 수정
DELETE /api/v1/boundary/fueldir/{id}     # 연료 삭제
POST   /api/v1/boundary/fueldir/calculate # 연료 계산
```

---

## 🚨 에러 처리 및 로깅

### 에러 처리 계층

#### 1. Frontend 에러 처리
```typescript
try {
  const response = await axiosClient.post(apiEndpoints.cbam.product.create, productData);
  // 성공 처리
} catch (error: any) {
  // 에러 타입별 처리
  if (error.response?.status === 400) {
    // 클라이언트 에러 (잘못된 입력)
    setToast({ message: '입력 데이터를 확인해주세요.', type: 'error' });
  } else if (error.response?.status === 401) {
    // 인증 에러
    router.push('/login');
  } else if (error.response?.status >= 500) {
    // 서버 에러
    setToast({ message: '서버 오류가 발생했습니다.', type: 'error' });
  } else {
    // 기타 에러
    setToast({ message: '알 수 없는 오류가 발생했습니다.', type: 'error' });
  }
}
```

#### 2. Axios Client 에러 처리
```typescript
// 응답 인터셉터
axiosClient.interceptors.response.use(
  response => response,
  async error => {
    // 5xx 오류나 네트워크 오류 시 재시도
    if (error.response?.status >= 500 || !error.response) {
      const config = error.config;
      if (config && !config._retry) {
        config._retry = true;
        return retryRequest(axiosClient, config);
      }
    }

    // 401 오류 시 토큰 제거 및 로그인 페이지로 이동
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_email');
        window.location.href = '/';
      }
    }

    return Promise.reject(error);
  }
);
```

#### 3. Backend 에러 처리
```python
# Controller 레벨
@router.post("/", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest):
    try:
        product_service = get_product_service()
        product = await product_service.create_product(request)
        return product
    except ValueError as e:
        # 비즈니스 로직 에러
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 시스템 에러
        logger.error(f"제품 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다")

# Service 레벨
async def create_product(self, request: ProductCreateRequest) -> ProductResponse:
    try:
        # 데이터 검증
        if not request.product_name:
            raise ValueError("제품명은 필수입니다")
        
        # 비즈니스 로직 실행
        product = await self.product_repo.create_product(request)
        return ProductResponse.from_orm(product)
    except Exception as e:
        logger.error(f"제품 생성 서비스 오류: {str(e)}")
        raise

# Repository 레벨
async def create_product(self, request: ProductCreateRequest) -> Product:
    async with self.get_session() as session:
        try:
            product = Product(**request.dict())
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product
        except Exception as e:
            await session.rollback()
            logger.error(f"데이터베이스 저장 실패: {str(e)}")
            raise
```

### 로깅 시스템

#### 1. Frontend 로깅
```typescript
// 개발 환경에서 상세 로깅
if (process.env.NODE_ENV === 'development') {
  console.log('🔍 API 요청:', {
    url: apiEndpoints.cbam.product.create,
    data: productData,
    headers: axiosClient.defaults.headers
  });
}
```

#### 2. Backend 로깅
```python
# 요청/응답 로깅
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 요청 로깅
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    # 응답 처리
    response = await call_next(request)
    
    # 응답 로깅
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response

# 도메인별 로깅
logger.info(f"📝 제품 생성 요청: {request.product_name}")
logger.info(f"✅ 제품 생성 성공: ID {product.id}")
logger.error(f"❌ 제품 생성 실패: {str(e)}")
```

---

## 📊 성능 최적화 및 모니터링

### 1. 요청 중복 방지
```typescript
// axiosClient.ts
const pendingRequests = new Map<string, AbortController>();

const generateRequestKey = (config: AxiosRequestConfig): string => {
  const { method, url, data, params } = config;
  return `${method?.toUpperCase() || 'GET'}:${url}:${JSON.stringify(data || {})}:${JSON.stringify(params || {})}`;
};

// 요청 인터셉터에서 중복 요청 취소
if (pendingRequests.has(requestKey)) {
  const controller = pendingRequests.get(requestKey);
  if (controller) {
    controller.abort();
  }
}
```

### 2. 재시도 로직
```typescript
const retryRequest = async (
  axiosInstance: AxiosInstance,
  config: AxiosRequestConfig,
  retries: number = 3
): Promise<AxiosResponse> => {
  try {
    return await axiosInstance(config);
  } catch (error: unknown) {
    const axiosError = error as AxiosError;
    if (
      retries > 0 &&
      ((axiosError.response?.status && axiosError.response.status >= 500) ||
        !axiosError.response)
    ) {
      await new Promise(resolve => setTimeout(resolve, 1000 * (4 - retries)));
      return retryRequest(axiosInstance, config, retries - 1);
    }
    throw error;
  }
};
```

### 3. 타임아웃 설정
```typescript
const axiosClient: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 30000, // 30초
  headers: {
    'Content-Type': 'application/json',
  },
});
```

---

## 🔐 보안 고려사항

### 1. 인증 및 인가
- JWT 토큰 기반 인증
- 토큰 만료 시 자동 로그아웃
- API 요청마다 인증 토큰 검증

### 2. CORS 설정
```python
# Gateway CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lca-final.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 3. 입력 데이터 검증
```python
# Pydantic 스키마를 통한 자동 검증
class ProductCreateRequest(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100)
    product_category: str = Field(..., min_length=1, max_length=50)
    install_id: int = Field(..., gt=0)
    product_amount: float = Field(..., gt=0)
```

---

## 📚 결론

CBAM 시스템은 MSA 아키텍처를 기반으로 각 서비스가 독립적으로 동작하면서도 Gateway를 통해 통합된 API를 제공합니다. 

**주요 특징:**
- **확장성**: 각 도메인별로 독립적인 서비스 운영
- **유지보수성**: 명확한 책임 분리와 계층 구조
- **보안성**: Gateway를 통한 중앙화된 인증/인가
- **모니터링**: 각 단계별 상세한 로깅과 에러 처리

**데이터 흐름의 핵심:**
1. **프론트엔드**: 사용자 입력 처리 및 API 호출
2. **Gateway**: 서비스 라우팅 및 요청 전달
3. **백엔드**: 비즈니스 로직 처리 및 데이터 저장
4. **응답**: 역방향으로 데이터 전달 및 사용자에게 결과 표시

이러한 구조를 통해 CBAM 시스템은 안정적이고 확장 가능한 서비스를 제공할 수 있습니다.
