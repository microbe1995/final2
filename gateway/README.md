# Gateway Service

API Gateway 서비스로, 모든 마이크로서비스에 대한 진입점 역할을 합니다.

## 주요 기능

### 1. 인증 (Authentication)
- **회원가입**: `/api/v1/auth/register` - 사용자 회원가입
- **로그인**: `/api/v1/auth/login` - 사용자 로그인
- **로컬 테스트**: `/api/v1/auth/register/local`, `/api/v1/auth/login/local`

### 2. 로깅 시스템
- **JSON 형태 로그**: 모든 로그가 JSON 형태로 출력되어 도커 로그에서 쉽게 확인 가능
- **구조화된 로깅**: 요청/응답 데이터, 오류 정보 등이 체계적으로 기록
- **도커 로그 통합**: `docker logs` 명령어로 모든 로그 확인 가능

### 3. 프록시 기능
- 동적 라우팅을 통한 마이크로서비스 프록시
- GET, POST, PUT, PATCH, DELETE 메서드 지원
- 파일 업로드 지원

## API 엔드포인트

### 인증 관련
```
POST /api/v1/auth/register      # 외부 서비스 회원가입
POST /api/v1/auth/login         # 외부 서비스 로그인
POST /api/v1/auth/register/local # 로컬 회원가입 (테스트용)
POST /api/v1/auth/login/local   # 로컬 로그인 (테스트용)
GET  /api/v1/auth/health        # 인증 서비스 상태 확인
```

### 프록시
```
GET  /api/v1/{service}/{path}   # GET 요청 프록시
POST /api/v1/{service}/{path}   # POST 요청 프록시
PUT  /api/v1/{service}/{path}   # PUT 요청 프록시
PATCH /api/v1/{service}/{path}  # PATCH 요청 프록시
DELETE /api/v1/{service}/{path} # DELETE 요청 프록시
```

## 로깅 예시

### 회원가입 요청 로그
```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "level": "INFO",
  "logger": "gateway.app.router.auth_router",
  "message": "라우터 회원가입 요청: {\"email\": \"test@example.com\", \"username\": \"testuser\", \"full_name\": \"테스트 사용자\"}",
  "module": "auth_router",
  "function": "register",
  "line": 45
}
```

### 회원가입 성공 응답 로그
```json
{
  "timestamp": "2024-01-01T00:00:01.000Z",
  "level": "INFO",
  "logger": "gateway.app.domain.auth.service.auth_service",
  "message": "회원가입 성공: {\"id\": \"uuid-here\", \"email\": \"test@example.com\", \"username\": \"testuser\", \"full_name\": \"테스트 사용자\", \"created_at\": \"2024-01-01T00:00:01.000Z\", \"message\": \"회원가입이 성공적으로 완료되었습니다.\"}",
  "module": "auth_service",
  "function": "register_user",
  "line": 78
}
```

## 실행 방법

### 도커로 실행
```bash
docker-compose up gateway
```

### 로컬 실행
```bash
cd gateway
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## 테스트

### 테스트 스크립트 실행
```bash
cd gateway
python test_auth.py
```

### API 문서 확인
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## 도커 로그 확인

```bash
# 전체 로그 확인
docker-compose logs gateway

# 실시간 로그 확인
docker-compose logs -f gateway

# 특정 서비스 로그만 확인
docker logs greensteel-gateway-1
```

## 환경 변수

- `PORT`: 서비스 포트 (기본값: 8080)
- `AUTH_SERVICE_URL`: 인증 서비스 URL
- `USER_SERVICE_URL`: 사용자 서비스 URL 