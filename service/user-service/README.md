# User Service

GreenSteel 프로젝트의 사용자 관리 마이크로서비스입니다.

## 기능
- 사용자 프로필 관리
- 사용자 정보 CRUD
- 사용자 설정 관리
- 사용자 활동 로그

## 기술 스택
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis (캐싱)

## 실행 방법
```bash
cd service/user-service
pip install -r requirements.txt
python main.py
```

## API 엔드포인트
- `GET /users/{user_id}` - 사용자 정보 조회
- `PUT /users/{user_id}` - 사용자 정보 수정
- `DELETE /users/{user_id}` - 사용자 삭제
- `GET /users/{user_id}/profile` - 프로필 조회 