# Final Project

## 🚀 프로젝트 개요

이 프로젝트는 마이크로서비스 아키텍처를 기반으로 한 CBAM(Carbon Border Adjustment Mechanism) 시스템입니다.

## 🏗️ 아키텍처

```
프론트엔드 (Next.js) → Gateway (FastAPI) → Auth Service (FastAPI)
     ↓                    ↓                    ↓
  localhost:3000    localhost:8080      localhost:8000
```

## 📁 프로젝트 구조

```
LCA_final-main/
├── frontend/                 # Next.js 프론트엔드
│   └── src/
│       ├── app/             # Next.js App Router
│       │   ├── process-flow/ # 공정도 관리 (React Flow)
│       │   │   └── page.tsx # 메인 페이지 + API 서비스 통합
│       │   ├── login/       # 로그인 페이지
│       │   ├── register/    # 회원가입 페이지
│       │   └── profile/     # 프로필 관리 페이지
│       └── components/      # 아토믹 디자인 패턴
│           ├── atoms/       # 최소 단위 컴포넌트
│           ├── molecules/   # atoms의 조합
│           ├── organisms/   # molecules의 조합
│           └── templates/   # 페이지 레이아웃
├── gateway/                  # API Gateway (FastAPI)
├── service/
│   ├── auth-service/        # 인증 서비스 (FastAPI)
│   └── Cal_boundary/        # 공정도 관리 서비스 (FastAPI)
├── docker-compose.yml       # Docker Compose 설정
├── start-dev.bat           # 개발 환경 시작
└── stop-dev.bat            # 개발 환경 중지
```

## 🔄 데이터 흐름

### 회원가입 흐름
1. **프론트엔드** (`/register`): 사용자 입력 수집
2. **Gateway** (`/api/v1/auth/register`): CORS 처리 및 라우팅
3. **Auth Service** (`/auth/register`): 실제 회원 생성 로직

### API 엔드포인트
- **Gateway**: `http://localhost:8080/api/v1/{service}/{path}`
- **Auth Service**: `http://localhost:8000/auth/{endpoint}`

## 🚀 빠른 시작

### 1. 개발 환경 시작
```bash
# Windows
start-dev.bat

# 또는 수동으로
docker-compose up --build -d
```

### 2. 서비스 접속
- **프론트엔드**: http://localhost:3000
- **Gateway**: http://localhost:8080
- **Auth Service**: http://localhost:8000

### 3. API 문서
- **Gateway API Docs**: http://localhost:8080/docs
- **Auth Service API Docs**: http://localhost:8000/docs

### 4. 개발 환경 중지
```bash
# Windows
stop-dev.bat

# 또는 수동으로
docker-compose down
```

## 🔧 환경 변수

### **프론트엔드 환경변수**
프론트엔드 루트에 `.env.local` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# API 기본 URL (게이트웨이)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080/api/v1

# Cal_boundary 서비스 직접 URL (개발용)
NEXT_PUBLIC_CAL_BOUNDARY_URL=http://localhost:8001

# 개발 모드
NODE_ENV=development
NEXT_PUBLIC_DEBUG_MODE=true
```

### **백엔드 환경변수**

#### Gateway
- `PORT`: 8080 (기본값)
- `AUTH_SERVICE_URL`: http://localhost:8000 (기본값)
- `CAL_BOUNDRY_URL`: http://localhost:8001 (기본값)
- `CORS_URL`: http://localhost:3000 (기본값)

#### Auth Service
- `PORT`: 8000 (기본값)
- `DATABASE_URL`: PostgreSQL 연결 문자열

#### Cal_boundary Service
- `PORT`: 8001 (기본값)
- `DEBUG_MODE`: true (개발용)

## 📝 주요 기능

### 회원가입
- 이메일, 사용자명, 비밀번호, 전체 이름 입력
- 비밀번호 해싱 및 저장
- 중복 이메일/사용자명 검증

### 로그인
- 이메일/비밀번호 인증
- JWT 토큰 발급 (향후 구현 예정)

## 🐛 문제 해결

### 서비스가 시작되지 않는 경우
1. Docker가 실행 중인지 확인
2. 포트 충돌 확인 (3000, 8080, 8000)
3. `docker-compose logs`로 로그 확인

### CORS 오류가 발생하는 경우
1. Gateway의 CORS 설정 확인
2. 프론트엔드 origin이 허용 목록에 포함되어 있는지 확인

## 📚 기술 스택

- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+
- **Container**: Docker, Docker Compose
- **Database**: 메모리 기반 (향후 PostgreSQL 추가 예정)

## 🤝 기여 방법

1. 이슈 생성 또는 기존 이슈 확인
2. 기능 브랜치 생성
3. 코드 작성 및 테스트
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 
