# Auth Service

GreenSteel 프로젝트의 인증 마이크로서비스입니다.

## 기능
- 사용자 로그인/로그아웃
- JWT 토큰 발급 및 검증
- 사용자 권한 관리
- 비밀번호 암호화

## 기술 스택
- FastAPI
- SQLAlchemy
- JWT
- bcrypt

## 실행 방법
```bash
cd service/auth-service
pip install -r requirements.txt
python main.py
```

## API 엔드포인트
- `POST /auth/login` - 로그인
- `POST /auth/register` - 회원가입
- `POST /auth/logout` - 로그아웃
- `GET /auth/verify` - 토큰 검증 