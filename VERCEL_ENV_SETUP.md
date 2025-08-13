# 🚀 Vercel 환경변수 설정 가이드

## 📋 **Railway Gateway 연결을 위한 필수 환경변수**

### **Vercel 대시보드에서 설정해야 할 환경변수들**

1. **프로젝트 설정** → **Environment Variables** 탭으로 이동

2. **다음 환경변수들을 추가:**

#### **🔗 API Gateway 연결**
```
NEXT_PUBLIC_API_URL=https://your-gateway-url.railway.app
NEXT_PUBLIC_API_BASE_URL=https://your-gateway-url.railway.app/api/v1
```

#### **🚄 Railway 배포 환경**
```
NEXT_PUBLIC_RAILWAY_API_URL=https://your-gateway-url.railway.app
NEXT_PUBLIC_RAILWAY_API_BASE_URL=https://your-gateway-url.railway.app/api/v1
IS_RAILWAY_DEPLOYED=true
```

#### **🌍 환경 구분**
```
CURRENT_ENVIRONMENT=railway
```

## ⚠️ **주의사항**

### **자동 설정되는 환경변수 (설정 불필요)**
- `NODE_ENV`: Vercel에서 자동으로 `production` 설정
- `VERCEL`: Vercel 배포 환경임을 나타내는 플래그

### **설정 불가능한 환경변수**
- `NODE_ENV`는 `next.config.js`에서 직접 설정 불가
- Next.js 예약 환경변수

## 🔧 **설정 방법**

### **1단계: Railway Gateway URL 확인**
- Railway 대시보드에서 Gateway 서비스의 실제 URL 복사
- 예: `https://lca-gateway-production-xxxx.up.railway.app`

### **2단계: Vercel 환경변수 설정**
- Vercel 프로젝트 대시보드 접속
- **Settings** → **Environment Variables**
- 위의 환경변수들을 **Production**, **Preview**, **Development** 모두에 설정

### **3단계: 재배포**
- 환경변수 설정 후 **Redeploy** 클릭
- 또는 Git push로 자동 재배포

## 📱 **환경변수 확인 방법**

### **브라우저 콘솔에서 확인**
```javascript
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('Railway API URL:', process.env.NEXT_PUBLIC_RAILWAY_API_URL);
console.log('NODE_ENV:', process.env.NODE_ENV); // Vercel에서 자동 설정
```

### **Next.js 빌드 시 확인**
```bash
npm run build
# 환경변수가 올바르게 로드되는지 확인
```

## 🚨 **주의사항**

1. **NEXT_PUBLIC_** 접두사 필수
   - 클라이언트 사이드에서 접근 가능한 환경변수
   - 빌드 타임에 주입됨

2. **HTTPS URL 사용**
   - Railway는 HTTPS 제공
   - HTTP는 보안상 차단될 수 있음

3. **CORS 설정 확인**
   - Gateway의 CORS 설정에서 Vercel 도메인 허용 필요

4. **NODE_ENV 설정 금지**
   - `next.config.js`에서 직접 설정 불가
   - Vercel에서 자동으로 `production` 설정

## 🔍 **문제 해결**

### **연결 실패 시 확인사항**
1. Gateway 서비스가 Railway에서 정상 실행 중인지 확인
2. `/health` 엔드포인트 접근 가능한지 확인
3. 환경변수가 올바르게 설정되었는지 확인
4. Vercel 재배포 후 테스트

### **디버깅 명령어**
```bash
# Gateway 상태 확인
curl https://your-gateway-url.railway.app/health

# API 엔드포인트 테스트
curl https://your-gateway-url.railway.app/api/v1/health
```
