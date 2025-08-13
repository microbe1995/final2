# Gateway Service Dockerfile - 완전 단순화
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Python 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 요구사항 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 디버깅: 디렉토리 구조 확인
RUN echo "=== 디렉토리 구조 ===" && ls -la && \
    echo "=== app 디렉토리 ===" && ls -la app/ && \
    echo "=== Python 경로 ===" && python -c "import sys; print(sys.path)" && \
    echo "=== 모듈 테스트 ===" && python -c "import app.main; print('✅ app.main import 성공!')"

# 포트 설정
EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# uvicorn 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
