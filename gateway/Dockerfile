# Gateway Service Dockerfile - WORKDIR 변경으로 모듈 경로 문제 해결
FROM python:3.11-slim

# 작업 디렉토리를 app으로 설정 (모듈 경로 문제 해결)
WORKDIR /app/app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV RAILWAY_ENVIRONMENT=true

# Gateway 애플리케이션 요구사항 복사
COPY requirements.txt /app/

# Python 패키지 설치 (캐시 제거)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Gateway 애플리케이션 코드 복사 (전체 디렉토리)
COPY . /app/

# 디버깅: 디렉토리 구조 및 Python 경로 확인
RUN echo "=== 현재 작업 디렉토리 ===" && \
    pwd && \
    echo "=== 디렉토리 구조 확인 ===" && \
    ls -la && \
    echo "=== 상위 디렉토리 내용 ===" && \
    ls -la /app/ && \
    echo "=== Python 경로 확인 ===" && \
    python -c "import sys; print('Python path:', sys.path)" && \
    echo "=== 모듈 import 테스트 ===" && \
    python -c "import main; print('✅ main 모듈 import 성공!')" && \
    python -c "from main import app; print('✅ main.app import 성공!')"

# 포트 설정
EXPOSE 8080
ENV PORT=8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 0.0.0.0으로 실행 (Docker 환경에 적합)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
