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

# Railway 환경 감지 및 import 경로 결정
def get_auth_router():
    """Railway 환경에 따라 적절한 import 경로 선택"""
    # Railway 환경 감지 (더 확실한 방법)
    is_railway = (
        os.getenv("RAILWAY_ENVIRONMENT") == "true" or
        os.getenv("RAILWAY_STATIC_URL") is not None or
        os.getenv("PORT") is not None or
        os.getenv("RAILWAY_PROJECT_ID") is not None or
        os.getenv("RAILWAY_SERVICE_ID") is not None
    )
    
    # 디버깅: 환경 변수 출력
    print(f"🔍 환경 변수 확인:")
    print(f"  - RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
    print(f"  - RAILWAY_STATIC_URL: {os.getenv('RAILWAY_STATIC_URL')}")
    print(f"  - PORT: {os.getenv('PORT')}")
    print(f"  - RAILWAY_PROJECT_ID: {os.getenv('RAILWAY_PROJECT_ID')}")
    print(f"  - RAILWAY_SERVICE_ID: {os.getenv('RAILWAY_SERVICE_ID')}")
    print(f"  - /app/main.py 존재: {os.path.exists('/app/main.py')}")
    print(f"  - is_railway: {is_railway}")
    
    # Railway 환경이거나 Docker 컨테이너 내부라면 절대 경로 사용
    if is_railway or os.path.exists("/app/main.py"):
        print(f"🚂 Railway/Docker 환경 감지됨 - 절대 경로 import 사용")
        # Railway/Docker 환경: 절대 경로로 import (app. 접두사 없음)
        try:
            from router.auth_router import auth_router
            print(f"✅ 절대 경로 import 성공: router.auth_router")
            return auth_router
        except ImportError as e:
            print(f"❌ 절대 경로 import 실패: {e}")
            # fallback: 상대 경로 시도
            from .router.auth_router import auth_router
            print(f"✅ 상대 경로 import 성공: .router.auth_router")
            return auth_router
    else:
        print(f"🏠 로컬 개발 환경 감지됨 - 상대 경로 import 사용")
        # 로컬 개발 환경: 상대 경로로 import
        try:
            from .router.auth_router import auth_router
            print(f"✅ 상대 경로 import 성공: .router.auth_router")
            return auth_router
        except ImportError as e:
            print(f"❌ 상대 경로 import 실패: {e}")
            # fallback: 절대 경로 시도 (app. 접두사 없음)
            from router.auth_router import auth_router
            print(f"✅ 절대 경로 import 성공: router.auth_router")
            return auth_router

# auth_router 가져오기
auth_router = get_auth_router()

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
        "https://lca-final.vercel.app",  # Vercel 프론트엔드 (정확한 도메인)
        "https://*.vercel.app",   # 모든 Vercel 도메인
        "https://vercel.app",     # Vercel 메인 도메인
        "*",  # 모든 프론트엔드 도메인 허용 (개발용)
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Vercel 서브도메인 정규식
    allow_credentials=True,  # HttpOnly 쿠키 사용을 위해 필수
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # 명시적 메서드 허용
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],  # 모든 응답 헤더 노출
    max_age=86400,  # CORS preflight 캐시 시간 (24시간)
)

gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])
gateway_router.include_router(auth_router)
app.include_router(gateway_router)

# CORS 디버깅을 위한 미들웨어 추가
@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    """CORS 요청 디버깅을 위한 미들웨어"""
    # 요청 정보 로깅
    logger.info(f"🌐 CORS 요청: {request.method} {request.url}")
    logger.info(f"🌐 Origin: {request.headers.get('origin', 'No Origin')}")
    logger.info(f"🌐 User-Agent: {request.headers.get('user-agent', 'No User-Agent')}")
    
    # 응답 처리
    response = await call_next(request)
    
    # CORS 헤더 확인
    cors_headers = {
        'Access-Control-Allow-Origin': response.headers.get('access-control-allow-origin'),
        'Access-Control-Allow-Methods': response.headers.get('access-control-allow-methods'),
        'Access-Control-Allow-Headers': response.headers.get('access-control-allow-headers'),
    }
    logger.info(f"🌐 CORS 응답 헤더: {cors_headers}")
    
    return response

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

# Railway 배포를 위한 uvicorn 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 