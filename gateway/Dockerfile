FROM python:3.11-slim

ARG CACHEBUST=1
ARG BUILD_DATE=unknown
ARG GIT_COMMIT=unknown

WORKDIR /CBAM

# Python 환경 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/CBAM
ENV PORT=8080

# 의존성 설치 (레이어 캐싱 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사 (현재 폴더 구조 그대로 유지)
COPY . .

# app 폴더로 작업 디렉토리 변경
WORKDIR /CBAM/app

EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c 'curl -fsS http://127.0.0.1:${PORT:-8080}/health || exit 1'

# 애플리케이션 실행
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}