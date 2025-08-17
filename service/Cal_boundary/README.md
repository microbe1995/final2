# 🎨 Cal_boundary 서비스

## 📋 서비스 개요

**Cal_boundary**는 Canvas 기반의 드래그 앤 드롭 도형/화살표 배치 기능을 제공하는 마이크로 서비스입니다.

## 🚀 주요 기능

### **도형 그리기**
- **사각형**: 크기 조절 가능한 직사각형
- **원**: 반지름 조절 가능한 원형
- **삼각형**: 다양한 각도의 삼각형

### **화살표 그리기**
- **직선 화살표**: 시작점과 끝점 연결
- **곡선 화살표**: 베지어 곡선 기반
- **양방향 화살표**: 양쪽 끝에 화살표

### **인터랙티브 기능**
- **드래그 앤 드롭**: 마우스로 도형 이동
- **크기 조절**: 모서리 핸들로 크기 변경
- **회전**: 도형 회전 기능
- **실시간 편집**: 텍스트, 색상, 스타일 변경

## 🏗️ 아키텍처

```
Cal_boundary/
├── app/
│   ├── domain/
│   │   ├── entity/      # 도형, 화살표 엔티티
│   │   ├── schema/      # API 요청/응답 스키마
│   │   ├── service/     # 비즈니스 로직
│   │   ├── controller/  # HTTP 엔드포인트
│   │   └── repository/  # 데이터 접근 계층
│   ├── common/          # 공통 유틸리티
│   └── main.py         # 애플리케이션 진입점
├── tests/               # 테스트 코드
├── requirements.txt     # Python 의존성
├── Dockerfile          # Docker 이미지
└── README.md           # 프로젝트 문서
```

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.11
- **데이터베이스**: PostgreSQL, SQLAlchemy
- **이미지 처리**: Pillow, NumPy
- **컨테이너**: Docker
- **포트**: 8001

## 🚀 실행 방법

### **Docker로 실행**
```bash
# 이미지 빌드
docker build -t cal-boundary .

# 컨테이너 실행
docker run -p 8001:8001 cal-boundary
```

### **로컬 실행**
```bash
# 의존성 설치
pip install -r requirements.txt

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 📡 API 엔드포인트

### **도형 관리**
- `POST /shapes` - 새 도형 생성
- `GET /shapes` - 모든 도형 조회
- `PUT /shapes/{id}` - 도형 수정
- `DELETE /shapes/{id}` - 도형 삭제

### **화살표 관리**
- `POST /arrows` - 새 화살표 생성
- `GET /arrows` - 모든 화살표 조회
- `PUT /arrows/{id}` - 화살표 수정
- `DELETE /arrows/{id}` - 화살표 삭제

### **Canvas 관리**
- `POST /canvas` - 새 Canvas 생성
- `GET /canvas/{id}` - Canvas 조회
- `PUT /canvas/{id}` - Canvas 수정
- `DELETE /canvas/{id}` - Canvas 삭제

## 🔧 환경 변수

```env
# 데이터베이스
DATABASE_URL=postgresql://user:password@localhost:5432/cal_boundary

# 서비스 설정
SERVICE_PORT=8001
SERVICE_NAME=cal-boundary

# 로깅
LOG_LEVEL=INFO
```

## 📝 사용 예시

### **도형 생성**
```python
import requests

# 사각형 생성
shape_data = {
    "type": "rectangle",
    "x": 100,
    "y": 100,
    "width": 200,
    "height": 150,
    "color": "#3B82F6",
    "stroke_width": 2
}

response = requests.post("http://localhost:8001/shapes", json=shape_data)
```

### **화살표 생성**
```python
# 화살표 생성
arrow_data = {
    "type": "straight",
    "start_x": 50,
    "start_y": 50,
    "end_x": 250,
    "end_y": 200,
    "color": "#EF4444",
    "stroke_width": 3
}

response = requests.post("http://localhost:8001/arrows", json=arrow_data)
```

## 🧪 테스트

```bash
# 테스트 실행
pytest tests/

# 특정 테스트 실행
pytest tests/test_shapes.py -v
```

## 📊 모니터링

- **Health Check**: `GET /health`
- **Metrics**: `GET /metrics`
- **API 문서**: `GET /docs`

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## �� 라이선스

MIT License
