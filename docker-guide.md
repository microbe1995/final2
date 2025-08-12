# Docker Compose 사용 가이드

## 🚀 서비스 실행

### 전체 서비스 실행
```bash
docker-compose up -d
```

### 특정 서비스만 실행
```bash
# 게이트웨이와 인증 서비스만 실행
docker-compose up -d gateway auth-service postgres

# 프론트엔드만 실행
docker-compose up -d frontend
```

## 📊 서비스 포트

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Frontend | 3000 | Next.js 애플리케이션 |
| Gateway | 8080 | API 게이트웨이 |
| Auth Service | 8001 | 인증 서비스 |
| PostgreSQL | 5432 | 데이터베이스 |
| Redis | 6379 | 캐시 서비스 |

## 🛠️ 개발 환경

### 서비스 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs gateway
docker-compose logs auth-service
```

### 서비스 재시작
```bash
# 특정 서비스 재시작
docker-compose restart gateway

# 모든 서비스 재시작
docker-compose restart
```

### 서비스 중지
```bash
# 모든 서비스 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

## 🔧 환경 변수 설정

`.env` 파일을 생성하여 환경 변수를 설정할 수 있습니다:

```bash
# .env 파일 예시
JWT_SECRET=your-secret-key-here
DATABASE_URL=postgresql://postgres:password@localhost:5432/greensteel
```

## 📝 주의사항

1. **포트 충돌**: 이미 사용 중인 포트가 있다면 `docker-compose.yml`에서 포트를 변경하세요.
2. **데이터베이스**: PostgreSQL 데이터는 `postgres_data` 볼륨에 저장됩니다.
3. **환경 변수**: 프로덕션 환경에서는 `.env` 파일을 사용하여 민감한 정보를 관리하세요.

## 🚨 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# 포트 사용 확인
netstat -an | grep :8080

# 프로세스 종료
sudo kill -9 <PID>
```

### Docker 이미지 재빌드
```bash
# 특정 서비스 재빌드
docker-compose build gateway

# 모든 서비스 재빌드
docker-compose build --no-cache
```
