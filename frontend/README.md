# Frontend - Next.js PWA Application

MSA(Microservice Architecture) 구조의 프론트엔드 애플리케이션입니다.

## 🏗️ 아키텍처

### MSA 구조
- **Frontend**: Next.js + TypeScript + React
- **API Gateway**: FastAPI 기반 게이트웨이 (포트 8080)
- **Microservices**: 인증, 사용자 관리 등 개별 서비스

### API 통신 구조
```
Frontend → API Gateway (8080) → Microservices
```

## 🚀 주요 기능

### 1. 인증 시스템
- **회원가입**: 사용자명, 이메일, 비밀번호, 전체 이름
- **로그인**: 이메일/비밀번호 기반 인증
- **상태 관리**: Zustand를 통한 전역 상태 관리

### 2. API 통신
- **Axios**: HTTP 클라이언트
- **인터셉터**: 요청/응답 로깅 및 오류 처리
- **타입 안전성**: TypeScript 인터페이스

### 3. PWA (Progressive Web App)
- 오프라인 지원
- 설치 가능
- 푸시 알림 (향후 구현)

## 🛠️ 기술 스택

- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI Library**: React 18
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS
- **PWA**: next-pwa

## 📁 프로젝트 구조

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── login/          # 로그인 페이지
│   │   ├── register/       # 회원가입 페이지
│   │   ├── dashboard/      # 대시보드
│   │   └── cbam/          # CBAM 관련 페이지
│   ├── components/         # 재사용 가능한 컴포넌트
│   ├── lib/               # 유틸리티 및 API 클라이언트
│   │   ├── api.ts         # Axios 인스턴스 및 인터셉터
│   │   ├── auth.ts        # 인증 관련 API 함수
│   │   └── config.ts      # API 설정
│   ├── store/             # Zustand 상태 관리
│   │   └── authStore.ts   # 인증 상태 관리
│   └── types/             # TypeScript 타입 정의
├── public/                # 정적 파일
└── package.json           # 의존성 관리
```

## 🔧 개발 환경 설정

### 1. 의존성 설치
```bash
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

### 3. 빌드
```bash
npm run build
npm start
```

## 🌐 API Gateway 연동

### 환경 변수
```bash
# .env.local (선택사항)
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080/api/v1
```

### API 엔드포인트
- **회원가입**: `POST /api/v1/auth/register/local`
- **로그인**: `POST /api/v1/auth/login/local`
- **헬스체크**: `GET /api/v1/auth/health`

## 📱 PWA 기능

### 매니페스트
- `public/manifest.json`에서 PWA 설정
- 아이콘, 테마 색상, 표시 모드 등

### 서비스 워커
- `public/sw.js`에서 오프라인 캐싱
- 백그라운드 동기화 (향후 구현)

## 🔍 개발 도구

### TypeScript
```bash
npm run type-check
```

### ESLint
```bash
npm run lint
```

## 🚀 배포

### Vercel
- GitHub main 브랜치에 푸시하면 자동 배포
- 환경 변수는 Vercel 대시보드에서 설정

### Docker
```bash
docker build -t frontend .
docker run -p 3000:3000 frontend
```

## 🔗 연관 서비스

- **API Gateway**: `http://localhost:8080`
- **Auth Service**: `http://localhost:8000`
- **User Service**: `http://localhost:8002`

## 📚 참고 문서

- [Next.js Documentation](https://nextjs.org/docs)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PWA Documentation](https://web.dev/progressive-web-apps/)
