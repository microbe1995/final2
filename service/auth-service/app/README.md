# Auth Service (Minimal)

심플한 인증 서비스 - 회원가입, 로그인, 로그아웃 기능을 제공합니다.

## 🚀 기능

- **회원가입**: 이메일 중복 체크, 비밀번호 bcrypt 해시 저장
- **로그인**: 이메일/비밀번호 검증, JWT 액세스 토큰 발급
- **로그아웃**: 인증된 사용자 로그아웃 (토큰 무효화 없음)
- **프로필 조회**: 현재 인증된 사용자 정보 조회

## 🏗️ 아키텍처

- **FastAPI**: 현대적인 Python 웹 프레임워크
- **SQLAlchemy 2.x**: ORM 및 데이터베이스 관리
- **PostgreSQL**: 프로덕션 데이터베이스 (SQLite 폴백 지원)
- **JWT**: JSON Web Token 기반 인증
- **bcrypt**: 안전한 비밀번호 해싱

## 📁 디렉터리 구조

```
service/auth_service/app/
├── core/           # 핵심 설정, 로깅, 보안
├── api/            # API 라우트 (컨트롤러)
├── models/         # 데이터베이스 모델
├── schemas/        # Pydantic 스키마
├── main.py         # 애플리케이션 진입점
├── requirements.txt # Python 의존성
├── Dockerfile      # Docker 이미지 빌드
└── README.md       # 이 파일
```

## 🚀 빠른 시작

### 1. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
SERVICE_NAME=auth-service
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
JWT_SECRET=your-secret-key-here
JWT_ALG=HS256
ACCESS_EXPIRES_MIN=30
ALLOWED_ORIGINS=https://greensteel.site,https://www.greensteel.site
ALLOWED_ORIGIN_REGEX=^https://.*\.vercel\.app$|^https://.*\.up\.railway\.app$
LOG_LEVEL=INFO
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

### 4. Docker로 실행

```bash
docker build -t auth-service .
docker run -p 8081:8081 --env-file .env auth-service
```

## 📚 API 문서

### 인증 엔드포인트

#### POST /auth/register

사용자 회원가입

**요청 본문:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "홍길동"
}
```

**응답 (201):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "홍길동",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login

사용자 로그인

**요청 본문:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**응답 (200):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /auth/logout

사용자 로그아웃 (인증 필요)

**헤더:**

```
Authorization: Bearer <access_token>
```

**응답 (204):** No Content

#### GET /auth/me

현재 사용자 프로필 조회 (인증 필요)

**헤더:**

```
Authorization: Bearer <access_token>
```

**응답 (200):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "홍길동",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 시스템 엔드포인트

#### GET /health

헬스 체크

**응답 (200):**

```json
{
  "status": "ok",
  "name": "auth-service",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### GET /favicon.ico

파비콘 (204 No Content)

## 🔧 설정

### 환경 변수

| 변수명                 | 설명                      | 기본값                                                |
| ---------------------- | ------------------------- | ----------------------------------------------------- |
| `SERVICE_NAME`         | 서비스 이름               | `auth-service`                                        |
| `DATABASE_URL`         | 데이터베이스 연결 URL     | SQLite 폴백                                           |
| `JWT_SECRET`           | JWT 시크릿 키             | 자동 생성                                             |
| `JWT_ALG`              | JWT 알고리즘              | `HS256`                                               |
| `ACCESS_EXPIRES_MIN`   | 액세스 토큰 만료 시간(분) | `30`                                                  |
| `ALLOWED_ORIGINS`      | 허용된 CORS 오리진        | `https://greensteel.site,https://www.greensteel.site` |
| `ALLOWED_ORIGIN_REGEX` | 허용된 CORS 오리진 정규식 | Vercel/Railway 앱                                     |
| `LOG_LEVEL`            | 로그 레벨                 | `INFO`                                                |

### 데이터베이스

- **PostgreSQL**: 프로덕션 환경 (Railway 등)
- **SQLite**: 개발 환경 (DATABASE_URL이 비어있을 때)

## 🐳 Docker

### 빌드

```bash
docker build -t auth-service .
```

### 실행

```bash
docker run -p 8081:8081 --env-file .env auth-service
```

### 포트

- **컨테이너 내부**: 8081
- **게이트웨이**: 8080 (다른 포트 사용)

## 🔒 보안

- **비밀번호**: bcrypt로 해시 저장
- **JWT**: HS256 알고리즘, 30분 만료
- **CORS**: 지정된 오리진만 허용
- **로깅**: 민감한 정보 자동 마스킹

## 📝 로깅

- **요청/응답**: 모든 API 호출 로깅
- **민감 정보**: password, token 등 자동 마스킹
- **로그 레벨**: INFO 기본값

## 🚨 예외 처리

- **400**: 잘못된 요청 데이터
- **401**: 인증 실패
- **409**: 이메일 중복
- **500**: 서버 내부 오류

## 🔄 확장 가능성

- **토큰 블랙리스트**: 로그아웃 시 토큰 무효화
- **리프레시 토큰**: 액세스 토큰 갱신
- **역할 기반 접근 제어**: 사용자 권한 관리
- **이메일 인증**: 계정 활성화

## 📞 지원

문제가 발생하면 로그를 확인하고 GitHub 이슈를 생성해주세요.
