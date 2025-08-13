# Gateway Service Dockerfile - 근본적 문제 해결
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

# 디버깅: 정확한 문제 파악
RUN echo "=== 1. 현재 작업 디렉토리 ===" && pwd && \
    echo "=== 2. 디렉토리 구조 ===" && ls -la && \
    echo "=== 3. app 디렉토리 내용 ===" && ls -la app/ && \
    echo "=== 4. Python 경로 ===" && python -c "import sys; print('Python path:', sys.path)" && \
    echo "=== 5. Python 버전 ===" && python --version && \
    echo "=== 6. 모듈 import 테스트 ===" && \
    python -c "import app" && echo "✅ app 모듈 import 성공!" && \
    python -c "from app.main import app" && echo "✅ app.main.app import 성공!" && \
    echo "=== 7. 파일 존재 확인 ===" && \
    echo "app/__init__.py exists:" && test -f app/__init__.py && echo "✅ YES" || echo "❌ NO" && \
    echo "app/main.py exists:" && test -f app/main.py && echo "✅ YES" || echo "❌ NO" && \
    echo "=== 8. 파일 내용 확인 ===" && \
    echo "app/__init__.py content:" && head -5 app/__init__.py && \
    echo "app/main.py first few lines:" && head -5 app/main.py

# 포트 설정
EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# uvicorn으로 직접 실행 (문제 정확히 파악)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
