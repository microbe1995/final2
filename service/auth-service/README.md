# Auth Service

## 개요
GreenSteel MSA 시스템의 인증 서비스입니다. 사용자 인증 및 계정 관리를 제공합니다.

## 기능
- 사용자 인증 (회원가입, 로그인, 로그아웃)
- 사용자 정보 관리
- ID 중복 확인
- JWT 토큰 관리

## 기술 스택
- FastAPI
- Python 3.11+
- Uvicorn
- Pydantic
- SQLAlchemy
- Passlib (비밀번호 해싱)
- Python-Jose (JWT)

## 실행 방법
```bash
cd service/auth-service
python main.py
```

## API 엔드포인트

### 인증 관련
- `POST /auth/register/` - 회원가입
- `POST /auth/login/` - 로그인
- `POST /auth/logout/` - 로그아웃
- `POST /auth/check-id/` - ID 중복확인

### 사용자 정보
- `GET /user/me/` - 내 정보 조회
- `PUT /user/update/` - 내 정보 수정
- `GET /user/info/` - 사용자 정보 조회
- `GET /user/{user_id}/` - 특정 사용자 정보 조회

### 헬스 체크
- `GET /health` - 헬스 체크

## 포트
- 기본 포트: 8001

## Docker 실행
```bash
docker build -t auth-service .
docker run -p 8001:8001 auth-service
``` 