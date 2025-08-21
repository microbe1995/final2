# 🚀 Vercel CLI를 사용한 수동 배포 가이드

## 문제 상황

GitHub 자동 배포가 작동하지 않아 Vercel CLI를 사용한 수동 배포가 필요합니다.

## 📋 사전 준비

### 1. Vercel CLI 설치

```bash
npm install -g vercel
```

### 2. Vercel 로그인

```bash
vercel login
```

### 3. 프로젝트 설정

```bash
cd frontend
vercel
```

## 🛠️ 배포 단계

### 1단계: 프로젝트 초기화

```bash
cd frontend
vercel --yes
```

### 2단계: 프로덕션 배포

```bash
vercel --prod
```

### 3단계: 환경 변수 설정

```bash
vercel env add NEXT_PUBLIC_APP_NAME
vercel env add NODE_ENV
# 기타 필요한 환경 변수 추가
```

### 4단계: 도메인 설정

```bash
vercel domains add greensteel.site
```

## 🔧 문제 해결

### 빌드 오류 발생 시

```bash
# 로컬에서 빌드 테스트
pnpm run build

# 오류 수정 후 재배포
vercel --prod
```

### 환경 변수 문제

```bash
# 환경 변수 확인
vercel env ls

# 환경 변수 수정
vercel env rm [변수명]
vercel env add [변수명]
```

### 도메인 연결 문제

```bash
# 도메인 상태 확인
vercel domains ls

# DNS 설정 확인
vercel domains inspect greensteel.site
```

## 📊 배포 상태 확인

### 배포 목록 확인

```bash
vercel ls
```

### 특정 배포 상세 정보

```bash
vercel inspect [배포ID]
```

### 로그 확인

```bash
vercel logs [배포ID]
```

## 🚀 자동화 스크립트

### 배포 스크립트 생성

```bash
# deploy.sh
#!/bin/bash
echo "🚀 GreenSteel 프론트엔드 배포 시작..."

# 의존성 설치
echo "📦 의존성 설치 중..."
pnpm install --frozen-lockfile

# 린팅 및 타입 체크
echo "🔍 코드 검사 중..."
pnpm run lint
pnpm run type-check

# 테스트 실행
echo "🧪 테스트 실행 중..."
pnpm run test

# 빌드
echo "🏗️ 애플리케이션 빌드 중..."
pnpm run build

# Vercel 배포
echo "🚀 Vercel에 배포 중..."
vercel --prod --yes

echo "✅ 배포 완료!"
```

### 실행 권한 부여

```bash
chmod +x deploy.sh
./deploy.sh
```

## 📝 환경 변수 설정

### 필수 환경 변수

```bash
NODE_ENV=production
NEXT_PUBLIC_APP_NAME=GreenSteel
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### 선택적 환경 변수

```bash
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=https://...
```

## 🔍 문제 진단

### 1. 빌드 로그 확인

```bash
vercel logs --follow
```

### 2. 함수 로그 확인

```bash
vercel logs --functions
```

### 3. 에러 로그 확인

```bash
vercel logs --error
```

## 📞 지원

### Vercel 지원

- [Vercel 문서](https://vercel.com/docs)
- [Vercel Discord](https://discord.gg/vercel)
- [Vercel GitHub](https://github.com/vercel/vercel)

### 문제 해결 순서

1. 로컬 빌드 테스트
2. Vercel 로그 확인
3. 환경 변수 검증
4. Vercel 지원팀 문의

---

**생성 시간**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**목적**: Vercel CLI를 사용한 수동 배포 가이드
