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

# Python 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# Gateway 애플리케이션 요구사항 복사
COPY requirements.txt .

# Python 패키지 설치 (캐시 제거)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Gateway 애플리케이션 코드 복사
COPY . .

# 포트 설정
EXPOSE 8080
ENV PORT=8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 실행 명령어 - 직접 Python으로 실행
CMD ["python", "app/main.py"]
