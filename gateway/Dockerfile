# Gateway Service Dockerfile - gateway 폴더 구조 기반
FROM python:3.11-slim

# 🚨 강력한 캐시 무효화를 위한 ARG 추가
ARG CACHEBUST=1
ARG BUILD_DATE=unknown

# 작업 디렉토리 설정
WORKDIR /app

# 🚨 캐시 무효화를 위한 강제 재빌드 레이어
RUN echo "Cache bust: $(date) - CACHEBUST=${CACHEBUST} - BUILD_DATE=${BUILD_DATE}" > /tmp/cache_bust.txt && \
    echo "강제 재빌드: $(date)" && \
    cat /tmp/cache_bust.txt && \
    rm /tmp/cache_bust.txt

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Python 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 🚨 캐시 무효화를 위한 추가 레이어
RUN echo "Python 환경 설정: $(date) - CACHEBUST=${CACHEBUST}" > /tmp/python_setup.txt && \
    rm /tmp/python_setup.txt

# 요구사항 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🚨 캐시 무효화를 위한 추가 레이어
RUN echo "Requirements 설치 완료: $(date) - CACHEBUST=${CACHEBUST}" > /tmp/requirements_done.txt && \
    rm /tmp/requirements_done.txt

# 애플리케이션 코드 복사 (gateway/app/ 폴더의 내용을 /app/에 직접 복사)
COPY app/ .

# 🚨 캐시 무효화를 위한 최종 확인
RUN echo "애플리케이션 코드 복사 완료: $(date) - CACHEBUST=${CACHEBUST}" > /tmp/app_copy_done.txt && \
    echo "=== 파일 구조 확인 ===" && ls -la && \
    echo "=== main.py 존재 확인 ===" && test -f main.py && echo "✅ main.py exists" || echo "❌ main.py not found" && \
    cat /tmp/app_copy_done.txt && \
    rm /tmp/app_copy_done.txt

# 포트 설정
EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# uvicorn으로 실행 (수정된 경로)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]