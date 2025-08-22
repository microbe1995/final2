# ============================================================================
# 🐳 Cal_boundary 서비스 Docker 이미지
# ============================================================================

FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /CBAM

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    locales \
    && rm -rf /var/lib/apt/lists/*

# PostgreSQL collation 문제 해결을 위한 로케일 설정
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 마이그레이션 스크립트는 main.py의 lifespan에서 처리됨

# 포트 노출
EXPOSE 8001

# PostgreSQL collation 문제 해결을 위한 환경 변수 설정
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1

# 시작 스크립트 생성 (마이그레이션은 main.py의 lifespan에서 처리)
RUN echo '#!/bin/bash\n\
echo "🚀 CBAM 서비스 시작 중..."\n\
echo "🚀 애플리케이션 시작 (마이그레이션은 자동 처리됨)..."\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8001\n\
' > /CBAM/start.sh && chmod +x /CBAM/start.sh

# 애플리케이션 실행
CMD ["/CBAM/start.sh"]
