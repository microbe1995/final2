# GreenSteel MSA 시스템 테스트 가이드

## 🚀 전체 시스템 실행

### 1. 의존성 설치

```bash
# 프론트엔드 의존성 설치
cd frontend
npm install

# 게이트웨이 의존성 설치
cd ../gateway
pip install -r requirements.txt

# 메시지 서비스 의존성 설치
cd ../service/message-service
pip install -r requirements.txt
```

### 2. 서비스 실행

#### 방법 1: 개별 실행
```bash
# 1. 메시지 서비스 시작 (터미널 1)
cd service/message-service
python main.py

# 2. 게이트웨이 시작 (터미널 2)
cd gateway
python main.py

# 3. 프론트엔드 시작 (터미널 3)
cd frontend
npm run dev
```

#### 방법 2: 스크립트 실행
```bash
# 실행 권한 부여
chmod +x start-services.sh

# 모든 서비스 시작
./start-services.sh
```

## 🧪 테스트 시나리오

### 1. 프론트엔드 테스트
1. 브라우저에서 `http://localhost:3000` 접속
2. 메시지 입력 필드에 텍스트 입력
3. "메시지 전송" 버튼 클릭
4. 성공/실패 응답 확인

### 2. API 직접 테스트
```bash
# 게이트웨이 헬스 체크
curl http://localhost:8000/health

# 메시지 서비스 직접 테스트
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d '{"message": "테스트 메시지", "timestamp": "2024-01-01T12:00:00", "user_id": "test_user"}'

# 게이트웨이를 통한 메시지 처리
curl -X POST http://localhost:8000/message-service/process \
  -H "Content-Type: application/json" \
  -d '{"message": "게이트웨이 테스트", "timestamp": "2024-01-01T12:00:00", "user_id": "test_user"}'
```

### 3. 로그 확인
각 서비스의 터미널에서 실시간 로그를 확인할 수 있습니다:

- **메시지 서비스**: 상세한 처리 로그와 터미널 출력
- **게이트웨이**: 프록시 및 라우팅 로그
- **프론트엔드**: 브라우저 개발자 도구 콘솔

## 📊 예상 로그 출력

### 메시지 서비스 로그
```
================================================================================
🎯 MESSAGE SERVICE - 메시지 처리 완료
================================================================================
📥 입력 메시지: 안녕하세요!
✨ 처리된 메시지: 안녕하세요!
🆔 메시지 ID: msg_a1b2c3d4e5f6
⏰ 처리 시간: 2024-01-01T12:00:00.123456
👤 사용자 ID: test_user
================================================================================
```

### 게이트웨이 로그
```
================================================================================
📋 GATEWAY 메시지 처리 요약
================================================================================
📥 입력 메시지: 안녕하세요!
⏰ 요청 시간: 2024-01-01T12:00:00
👤 사용자 ID: test_user
✅ 처리 성공: True
🆔 메시지 ID: msg_a1b2c3d4e5f6
⏰ 처리 완료: 2024-01-01T12:00:00.123456
📊 서비스 응답: {'status': 'success', 'message_id': 'msg_a1b2c3d4e5f6', ...}
================================================================================
```

## 🔧 문제 해결

### 1. 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001
netstat -tulpn | grep :3000

# 프로세스 종료
kill -9 <PID>
```

### 2. 의존성 문제
```bash
# Python 가상환경 사용 권장
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. CORS 문제
- 게이트웨이의 CORS 설정 확인
- 프론트엔드 API 호출 URL 확인

## 📚 API 문서

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **메시지 서비스 API**: http://localhost:8001/docs

## 🎯 성공 기준

✅ **정상 동작 확인 사항:**
1. 프론트엔드에서 메시지 입력 및 전송
2. 게이트웨이를 통한 요청 라우팅
3. 메시지 서비스에서 메시지 처리
4. 터미널에 상세한 로그 출력
5. 프론트엔드에 성공 응답 표시
6. JSON 스키마 검증 통과 