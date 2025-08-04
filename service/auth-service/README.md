# Auth Service

## 개요
GreenSteel MSA 시스템의 인증 및 리포트 서비스입니다. 사용자 인증과 리포트 업로드 기능을 제공합니다.

## 기능
- 사용자 인증 (회원가입, 로그인, 로그아웃)
- 사용자 정보 관리
- 리포트 파일 업로드
- ID 중복 확인

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
- `POST /report-auth/auth/register/` - 회원가입
- `POST /report-auth/auth/login/` - 로그인
- `POST /report-auth/auth/logout/` - 로그아웃
- `POST /report-auth/auth/check-id/` - ID 중복확인

### 사용자 정보
- `GET /report-auth/user/me/` - 내 정보 조회
- `PUT /report-auth/user/update/` - 내 정보 수정
- `GET /report-auth/user/info/` - 사용자 정보 조회
- `GET /report-auth/user/{user_id}/` - 특정 사용자 정보 조회

### 리포트
- `POST /report-auth/report/` - 리포트 파일 업로드

### 헬스 체크
- `GET /health` - 헬스 체크

## 포트
- 기본 포트: 8001

## Docker 실행
```bash
docker build -t auth-service .
docker run -p 8001:8001 auth-service
``` 