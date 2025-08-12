# 🚄 Railway 배포 가이드

## 📋 개요
이 프로젝트는 **두 개의 별도 서비스**로 구성되어 있습니다:
- **Frontend**: Next.js 웹 애플리케이션
- **Gateway**: Python FastAPI 백엔드 서비스

## 🏗️ Railway 프로젝트 설정

### 1️⃣ Frontend 서비스 생성

**새 서비스 추가** → **GitHub Repository** 선택

**설정:**
- **Name**: `lca-frontend`
- **Source Directory**: `frontend`
- **Build Command**: `pnpm install && pnpm run build`
- **Start Command**: `pnpm start`
- **Environment Variables**:
  ```
  NODE_ENV=production
  NEXT_PUBLIC_API_URL=https://your-gateway-url.railway.app
  ```

### 2️⃣ Gateway 서비스 생성

**새 서비스 추가** → **GitHub Repository** 선택

**설정:**
- **Name**: `lca-gateway`
- **Source Directory**: `gateway`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
- **Environment Variables**:
  ```
  PORT=8080
  RAILWAY_ENVIRONMENT=true
  ```

## 🔧 서비스 연결

### Frontend → Gateway 연결
1. Gateway 서비스 URL 복사
2. Frontend 서비스의 환경변수에 설정:
   ```
   NEXT_PUBLIC_API_URL=https://your-gateway-url.railway.app
   ```

### CORS 설정
Gateway 서비스의 `main.py`에서 Frontend 도메인 허용:
```python
allow_origins=[
    "https://your-frontend-url.railway.app",
    # ... 기타 도메인
]
```

## 🚀 배포 순서

1. **Gateway 서비스 먼저 배포**
2. **Frontend 서비스 배포** (Gateway URL 환경변수 설정 후)
3. **연결 테스트**

## 📝 문제 해결

### Gateway 서비스 오류
- **ModuleNotFoundError**: `uvicorn app.main:app` 명령어 확인
- **포트 충돌**: `PORT=8080` 환경변수 설정 확인

### Frontend 서비스 오류
- **API 연결 실패**: `NEXT_PUBLIC_API_URL` 환경변수 확인
- **빌드 실패**: Node.js 버전 확인 (22.x 필요)

## 🔗 유용한 링크

- [Railway 공식 문서](https://docs.railway.app/)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Next.js 배포 가이드](https://nextjs.org/docs/deployment)
