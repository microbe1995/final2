FROM python:3.11-slim

ARG CACHEBUST=1
ARG BUILD_DATE=unknown
ARG GIT_COMMIT=unknown

WORKDIR /app

# 시스템 패키지 설치 및 정리
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Python 환경 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080

# 의존성 설치 (레이어 캐싱 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사 (필요한 파일만)
COPY app/ .

EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c 'curl -fsS http://127.0.0.1:${PORT:-8080}/health || exit 1'

# 애플리케이션 실행
CMD sh -c 'uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}'