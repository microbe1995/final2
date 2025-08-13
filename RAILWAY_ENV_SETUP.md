# Railway 환경변수 설정 가이드

## 🚂 Gateway 서비스 환경변수

### 필수 환경변수
```
FRONT_ORIGIN=https://lca-final.vercel.app
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS,PATCH
CORS_ALLOW_HEADERS=Accept,Accept-Language,Content-Language,Content-Type,Authorization,X-Requested-With,Origin,Access-Control-Request-Method,Access-Control-Request-Headers
PORT=8080
```

### 선택적 환경변수
```
RAILWAY_ENVIRONMENT=production
PYTHONPATH=/app
```

## 🌐 Vercel 환경변수

### 필수 환경변수
```
NEXT_PUBLIC_API_URL=https://gateway-production-22ef.up.railway.app
NEXT_PUBLIC_API_BASE_URL=https://gateway-production-22ef.up.railway.app/api/v1
```

### 선택적 환경변수
```
IS_RAILWAY_DEPLOYED=true
CURRENT_ENVIRONMENT=railway
```

## ⚠️ 주의사항

1. **공백 제거**: Railway UI에서 환경변수 값 뒤에 공백이 있으면 안됩니다
2. **쉼표 구분**: CORS_ALLOW_METHODS와 CORS_ALLOW_HEADERS는 쉼표로 구분
3. **Origin 정확성**: FRONT_ORIGIN은 정확히 Vercel 도메인과 일치해야 함

## 🔧 설정 순서

1. Railway에서 Gateway 서비스 환경변수 설정
2. Vercel에서 Frontend 환경변수 설정
3. Railway 재배포
4. Vercel 재배포
5. CORS 테스트

## 📊 로그 확인

### Railway Deploy 로그에서 확인할 내용:
```
🔧 CORS 설정 확인:
  - FRONT_ORIGIN: 'https://lca-final.vercel.app'
  - CORS_ALLOW_CREDENTIALS: True
  - ALLOWED_METHODS: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
  - ALLOWED_HEADERS: ['Accept', 'Accept-Language', 'Content-Language', 'Content-Type', 'Authorization', 'X-Requested-With', 'Origin', 'Access-Control-Request-Method', 'Access-Control-Request-Headers']
```

### CORS 프로브 로그에서 확인할 내용:
```
CORS_PROBE origin='https://lca-final.vercel.app' acr-method='POST' acr-headers='content-type,authorization' path=/api/v1/auth/register method=OPTIONS
```
