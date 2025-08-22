# 🚀 배포 환경변수 설정 가이드

MSA 구조에 맞는 환경변수 설정 방법입니다.

## 🏗️ 아키텍처 구조

```
Frontend (Vercel) 
    ↓
Gateway (Railway) 
    ↓
Services (Railway)
    ├── Auth Service
    └── Cal_boundary Service
```

## 🔧 Railway 환경변수 설정

### Gateway Service
```bash
# 서비스 URL 설정
AUTH_SERVICE_URL=https://auth-service-production-d30b.up.railway.app
CAL_BOUNDARY_URL=https://lcafinal-production.up.railway.app

# CORS 설정 (프론트엔드만 허용)
CORS_URL=https://lca-final.vercel.app

# 포트 설정
PORT=8080
```

### Auth Service
```bash
# CORS 설정 (게이트웨이만 허용)
CORS_URL=https://gateway-production-22ef.up.railway.app

# 데이터베이스 및 기타 설정
DATABASE_URL=postgresql://...
SECRET_KEY=your_secret_key
```

### Cal_boundary Service
```bash
# CORS 설정 필요없음 (내부 서비스)
# 데이터베이스 및 기타 설정만 필요
DATABASE_URL=postgresql://...
```

## 🌐 Vercel 환경변수 설정

### Frontend (Next.js)
```bash
# Gateway를 통한 API 접근
NEXT_PUBLIC_API_BASE_URL=https://gateway-production-22ef.up.railway.app
NEXT_PUBLIC_GATEWAY_URL=https://gateway-production-22ef.up.railway.app

# 직접 서비스 접근용 (특별한 경우만)
NEXT_PUBLIC_CAL_BOUNDARY_URL=lcafinal-production.up.railway.app

# 기타 설정
NODE_ENV=production
NEXT_PUBLIC_APP_NAME=GreenSteel
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## 🔗 API 라우팅 구조

### 프론트엔드 요청 흐름
```
Frontend → Gateway → Service

예시:
GET /api/v1/auth/login
├── Frontend: axios.get('/api/v1/auth/login') 
├── Gateway: https://gateway-production-22ef.up.railway.app/api/v1/auth/login
└── Auth Service: https://auth-service-production-d30b.up.railway.app/api/v1/login
```

### Gateway 라우팅 규칙
```bash
# Auth Service
/api/v1/auth/{path} → AUTH_SERVICE_URL/api/v1/{path}

# Cal_boundary Service  
/api/v1/boundary/{path} → CAL_BOUNDARY_URL/api/{path}
/api/v1/countries/{path} → CAL_BOUNDARY_URL/api/{path}
```

## ✅ 설정 검증 방법

### 1. Gateway 헬스체크
```bash
curl https://gateway-production-22ef.up.railway.app/health
```

### 2. Auth Service 헬스체크 (Gateway 통해)
```bash
curl https://gateway-production-22ef.up.railway.app/api/v1/auth/health
```

### 3. CORS 테스트
```bash
# 프론트엔드에서 요청
curl -H "Origin: https://lca-final.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     https://gateway-production-22ef.up.railway.app/api/v1/auth/login
```

## 🚨 주의사항

### ❌ 하지 말아야 할 것
1. 프론트엔드에서 서비스에 직접 접근
2. 서비스에서 프론트엔드 CORS 허용
3. 게이트웨이를 우회한 API 호출

### ✅ 해야 할 것
1. 모든 API 요청은 게이트웨이를 통해
2. 게이트웨이에서만 프론트엔드 CORS 허용
3. 서비스는 게이트웨이만 신뢰

## 🔄 로컬 개발 환경

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
NEXT_PUBLIC_GATEWAY_URL=http://localhost:8080
```

### Gateway
```bash
AUTH_SERVICE_URL=http://localhost:8000
CAL_BOUNDARY_URL=http://localhost:8001
CORS_URL=http://localhost:3000
```

### Services
```bash
# Auth Service
CORS_URL=http://localhost:8080

# Cal_boundary Service  
# CORS 설정 불필요
```
