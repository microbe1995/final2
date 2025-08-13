"""
gateway-router 메인 파일
"""
from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Railway 환경에서는 절대 경로로 import
if os.getenv("RAILWAY_ENVIRONMENT") == "true":
    from .router.auth_router import auth_router
else:
    # 로컬 개발 환경에서는 상대 경로로 import
    try:
        from .router.auth_router import auth_router
    except ImportError:
        from app.router.auth_router import auth_router

# Railway 환경이 아닐 때만 .env 파일 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# JSON 형태의 로그 포맷터 클래스
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 추가 필드가 있는 경우 포함
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
            
        return json.dumps(log_entry, ensure_ascii=False)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 루트 로거 설정
root_logger = logging.getLogger()
root_logger.handlers.clear()

# JSON 포맷터 적용
json_formatter = JSONFormatter()
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(json_formatter)
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger("gateway_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for ausikor.com",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 로컬 접근
        "http://127.0.0.1:3000",  # 로컬 IP 접근
        "http://frontend:3000",   # Docker 내부 네트워크
        "https://lca-final.vercel.app",  # Vercel 프론트엔드
        "https://*.vercel.app",   # 모든 Vercel 도메인
        "*",  # 모든 프론트엔드 도메인 허용 (개발용)
    ],
    allow_credentials=True,  # HttpOnly 쿠키 사용을 위해 필수
    allow_methods=["*"],
    allow_headers=["*"],
)

gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])
gateway_router.include_router(auth_router)
app.include_router(gateway_router)

@app.get("/health", summary="테스트 엔드포인트")
async def health_check():
    return {"status": "healthy!"}

@gateway_router.get("/health", summary="테스트 엔드포인트")
async def gateway_health_check():
    return {"status": "gateway healthy!"}

# 기본 루트 경로
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0"}

# Railway 배포를 위한 uvicorn 호환성
# 직접 실행은 제거하고 uvicorn app.main:app으로 실행 