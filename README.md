# GreenSteel MSA 프로젝트

GreenSteel은 Next.js + TypeScript + React + FastAPI + PostgreSQL을 기반으로 한 마이크로서비스 아키텍처 프로젝트입니다.

## 🏗️ 프로젝트 구조

```
LCA_final-main/
├── frontend/              # Next.js 프론트엔드 애플리케이션
│   ├── src/               # 소스 코드
│   ├── public/            # 정적 파일
│   ├── package.json       # 프론트엔드 의존성
│   └── Dockerfile         # 프론트엔드 Docker 이미지
├── gateway/               # FastAPI API Gateway
│   ├── app/               # 게이트웨이 애플리케이션 코드
│   ├── main.py            # 게이트웨이 메인 파일
│   └── Dockerfile         # 게이트웨이 Docker 이미지
├── service/               # 마이크로서비스들
│   ├── auth-service/      # 인증 서비스
│   │   ├── app/           # 서비스 코드
│   │   └── Dockerfile     # 인증 서비스 Docker 이미지
│   └── Cal_boundary/      # 계산 경계 서비스
│       ├── app/           # 서비스 코드
│       └── Dockerfile     # 계산 경계 서비스 Docker 이미지
├── docker-compose.yml     # Docker Compose 설정
├── start-docker.bat       # Windows Docker 시작 스크립트
├── stop-docker.bat        # Windows Docker 중지 스크립트
└── README.md              # 프로젝트 문서
```

## 🚀 기술 스택

### Frontend
- **Next.js 14** - React 프레임워크
- **TypeScript** - 타입 안전성
- **React 18** - UI 라이브러리
- **Tailwind CSS** - 스타일링
- **PWA** - Progressive Web App

### Backend
- **FastAPI** - API Gateway 및 서비스
- **Python 3.11** - 백엔드 언어
- **PostgreSQL 15** - 데이터베이스
- **SQLAlchemy** - ORM

### DevOps
- **Docker** - 컨테이너화
- **Docker Compose** - 로컬 개발 환경
- **GitHub Actions** - CI/CD

## 🛠️ 개발 환경 설정

### 1. Docker 설치
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치
- Docker Compose가 포함되어 있어야 함

### 2. 프로젝트 클론
```bash
git clone <repository-url>
cd LCA_final-main
```

### 3. Docker 서비스 실행

#### Windows
```bash
# 서비스 시작
start-docker.bat

# 서비스 중지
stop-docker.bat
```

#### Linux/Mac
```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down
```

### 4. 개별 서비스 실행 (개발용)
```bash
# 프론트엔드
cd frontend
npm install
npm run dev

# 게이트웨이
cd gateway
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# 인증 서비스
cd service/auth-service
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 계산 경계 서비스
cd service/Cal_boundary
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 📦 서비스 정보

### 서비스 포트
- **Frontend**: http://localhost:3000
- **Gateway**: http://localhost:8080
- **Auth Service**: http://localhost:8000
- **Cal Boundary**: http://localhost:8001
- **PostgreSQL**: localhost:5432

### API 문서
- **Gateway Swagger**: http://localhost:8080/docs
- **Auth Service Swagger**: http://localhost:8000/docs
- **Cal Boundary Swagger**: http://localhost:8001/docs

## 🔄 개발 워크플로우

1. **코드 수정** → 소스 코드 편집
2. **Docker 재빌드** → `docker-compose build`
3. **서비스 재시작** → `docker-compose up -d`
4. **로그 확인** → `docker-compose logs -f [service-name]`

## 🐛 문제 해결

### 포트 충돌
```bash
# 포트 사용 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8080

# Docker 컨테이너 상태 확인
docker-compose ps
```

### 로그 확인
```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs frontend
docker-compose logs gateway
docker-compose logs auth-service
docker-compose logs cal-boundary
```

### 컨테이너 재시작
```bash
# 특정 서비스 재시작
docker-compose restart frontend

# 전체 재시작
docker-compose restart
```

## 📚 추가 문서

- **Frontend**: `frontend/README.md`
- **Gateway**: `gateway/README.md`
- **Auth Service**: `service/auth-service/README.md`
- **Cal Boundary**: `service/Cal_boundary/README.md`

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 
