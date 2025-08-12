# Gateway Service Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Gateway 애플리케이션 요구사항 복사
COPY app/requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Gateway 애플리케이션 코드 복사
COPY app/ .

# 포트 노출 (Gateway 서비스)
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Gateway 서비스 실행
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
