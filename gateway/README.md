# GreenSteel MSA 프로젝트

GreenSteel은 Next.js + TypeScript + React + Zustand + Axios + PWA + JWT 인증을 기반으로 한 마이크로서비스 아키텍처 프로젝트입니다.

## 🏗️ 프로젝트 구조

```
greensteel/
├── frontend/              # Next.js 프론트엔드 애플리케이션
│   ├── src/               # 소스 코드
│   ├── public/            # 정적 파일 (PWA 매니페스트, 아이콘 등)
│   ├── package.json       # 프론트엔드 의존성
│   └── ...
├── gateway/               # FastAPI API Gateway
│   ├── app/               # 게이트웨이 애플리케이션 코드
│   ├── main.py            # 게이트웨이 메인 파일
│   └── docker-compose.yml # 게이트웨이 도커 설정
├── service/               # 마이크로서비스들
│   ├── auth-service/      # 인증 서비스
│   ├── user-service/      # 사용자 관리 서비스
│   └── esg-service/       # ESG 데이터 서비스
├── document/              # 프로젝트 문서
│   └── README.md          # 상세 문서
├── .github/               # GitHub Actions CI/CD
│   └── workflows/
└── vercel.json            # Vercel 배포 설정
```

## 🚀 기술 스택

### Frontend
- **Next.js 14** - React 프레임워크
- **TypeScript** - 타입 안전성
- **React 18** - UI 라이브러리
- **Zustand** - 상태 관리
- **Axios** - HTTP 클라이언트
- **Tailwind CSS** - 스타일링
- **PWA** - Progressive Web App

### Backend
- **FastAPI** - API Gateway
- **Python** - 백엔드 언어
- **JWT** - 인증 토큰
- **Docker** - 컨테이너화

### DevOps
- **GitHub Actions** - CI/CD
- **Vercel** - 프론트엔드 배포
- **Docker Compose** - 로컬 개발 환경

## 🛠️ 개발 환경 설정

### 1. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```

### 2. 게이트웨이 실행
```bash
cd gateway
pip install -r requirements.txt
python main.py
```

### 3. 서비스 실행
```bash
# 각 서비스 디렉토리에서 실행
cd service/auth-service
python main.py
```

## 📦 배포

### Frontend (Vercel)
- GitHub main 브랜치에 푸시하면 자동 배포
- Vercel 대시보드에서 환경 변수 설정

### Backend (Docker)
```bash
cd gateway
docker-compose up -d
```

## 🔄 CI/CD 파이프라인

1. **코드 푸시** → GitHub
2. **자동 테스트** → GitHub Actions
3. **빌드 검증** → TypeScript, ESLint
4. **자동 배포** → Vercel (Frontend)

## 📚 문서

자세한 문서는 `document/` 폴더를 참조하세요.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 