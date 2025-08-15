# Auth Service Dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /CBAM

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Auth 서비스 요구사항 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Auth 서비스 코드 복사 (현재 폴더 구조 그대로 유지)
COPY . .

# app 폴더로 작업 디렉토리 변경
WORKDIR /CBAM/app


# 포트 노출 (Auth Service는 8000 포트 고정)
EXPOSE 8000

# 환경 변수 설정
ENV PYTHONPATH=/CBAM
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# 헬스 체크 (8000 포트 사용)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
