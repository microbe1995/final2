FROM python:3.11-slim

ARG CACHEBUST=1
ARG BUILD_DATE=unknown
ARG GIT_COMMIT=unknown

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c 'curl -fsS http://127.0.0.1:${PORT:-8080}/health || exit 1'

CMD sh -c 'uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}'