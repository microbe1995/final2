# Python 환경 설정 가이드

## 🐍 Python 가상환경 설정

### 1. 가상환경 생성
```bash
# 프로젝트 루트 디렉토리에서
python -m venv venv
```

### 2. 가상환경 활성화
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 의존성 설치
```bash
# 루트 의존성 설치
pip install -r requirements.txt

# Auth Service 의존성 설치
cd service/auth-service
pip install -r requirements.txt

# Gateway 의존성 설치
cd ../../gateway
pip install -r requirements.txt
```

## 🚀 빠른 설치 (Windows)
```bash
# install_dependencies.bat 파일 실행
install_dependencies.bat
```

## 🔧 VS Code 설정

### Python 인터프리터 설정
1. `Ctrl + Shift + P` → "Python: Select Interpreter"
2. 생성한 가상환경 선택: `./venv/Scripts/python.exe`

### 설정 파일 생성 (.vscode/settings.json)
```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true
}
```

## 📦 설치되는 패키지들

### Core Packages
- `fastapi==0.104.1` - 웹 프레임워크
- `uvicorn[standard]==0.24.0` - ASGI 서버
- `python-dotenv==1.0.0` - 환경변수 관리

### Auth Service Packages
- `python-jose[cryptography]==3.3.0` - JWT 토큰
- `passlib[bcrypt]==1.7.4` - 비밀번호 해싱
- `email-validator==2.1.0` - 이메일 검증
- `sqlalchemy==2.0.27` - ORM
- `psycopg2-binary==2.9.10` - PostgreSQL 드라이버
- `asyncpg==0.29.0` - 비동기 PostgreSQL
- `bcrypt==4.1.2` - 비밀번호 암호화

## ✅ 확인 방법
```bash
# 설치된 패키지 확인
pip list

# Python에서 import 테스트
python -c "import fastapi; print('FastAPI 설치 완료')"
python -c "import uvicorn; print('Uvicorn 설치 완료')"
```
