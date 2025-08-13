"""
gateway-router 메인 파일
"""
from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
import logging
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager

print("=" * 60)
print("Gateway API 서비스 시작 - Railway 디버깅 모드")
print("=" * 60)
print(f"작업 디렉토리: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', '설정되지 않음')}")
print("=" * 60)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gateway_api")

if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

def get_auth_router():
    try:
        from router.auth_router import auth_router
        return auth_router
    except ImportError:
        try:
            from app.router.auth_router import auth_router
            return auth_router
        except ImportError:
            r = APIRouter(prefix="/auth", tags=["Authentication"])
            @r.get("/health")
            async def _fallback():
                return {"status": "auth router not available"}
            return r

auth_router = get_auth_router()

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        return json.dumps(log_entry, ensure_ascii=False)

root_logger = logging.getLogger()
root_logger.handlers.clear()
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(JSONFormatter())
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Gateway API 시작")
    yield
    logger.info("Gateway API 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# CORS 설정 - 환경변수 기반
FRONT_ORIGIN = os.getenv("FRONT_ORIGIN", "https://lca-final.vercel.app").strip()
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "Accept,Accept-Language,Content-Language,Content-Type,Authorization,X-Requested-With,Origin,Access-Control-Request-Method,Access-Control-Request-Headers")

# 메서드와 헤더를 리스트로 변환 (공백 제거)
ALLOWED_METHODS = [m.strip() for m in CORS_ALLOW_METHODS.split(",") if m.strip()]
ALLOWED_HEADERS = [h.strip() for h in CORS_ALLOW_HEADERS.split(",") if h.strip()]

# 허용할 origin들을 리스트로 설정 (개발 및 프로덕션 환경 모두 지원)
ALLOWED_ORIGINS = [
    FRONT_ORIGIN,  # 기본 Vercel 프론트엔드
    "http://localhost:3000",  # 로컬 개발
    "http://127.0.0.1:3000",  # 로컬 IP
    "https://lca-final.vercel.app",  # Vercel 프로덕션
    "https://lca-final-git-main-microbe95.vercel.app",  # Vercel 프리뷰
]

# CORS 설정 로그 출력
print(f"🔧 CORS 설정 확인:")
print(f"  - FRONT_ORIGIN: '{FRONT_ORIGIN}'")
print(f"  - ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
print(f"  - CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
print(f"  - ALLOWED_METHODS: {ALLOWED_METHODS}")
print(f"  - ALLOWED_HEADERS: {ALLOWED_HEADERS}")
print("=" * 60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 여러 origin 허용
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["*"],
    max_age=86400,
)

@app.options("/{path:path}")
async def any_options(path: str):
    # 요청의 origin을 확인
    request_origin = request.headers.get("origin")
    
    # origin이 허용된 목록에 있는지 확인
    if request_origin in ALLOWED_ORIGINS:
        allowed_origin = request_origin
    else:
        allowed_origin = FRONT_ORIGIN  # 기본값 사용
    
    response = Response(content="OK", status_code=200)
    response.headers["Access-Control-Allow-Origin"] = allowed_origin
    response.headers["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    response.headers["Access-Control-Max-Age"] = "86400"
    
    # CORS preflight 로깅
    print(f"🔍 CORS OPTIONS 요청 처리:")
    print(f"  - Path: {path}")
    print(f"  - Request Origin: {request_origin}")
    print(f"  - Allowed Origin: {allowed_origin}")
    print(f"  - Methods: {', '.join(ALLOWED_METHODS)}")
    print(f"  - Headers: {', '.join(ALLOWED_HEADERS)}")
    
    return response

@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    # CORS 관련 헤더 로깅
    origin = request.headers.get("origin")
    method = request.method
    path = request.url.path
    
    logger.info(f"🌐 CORS 요청: {method} {path}")
    logger.info(f"  - Origin: {origin}")
    logger.info(f"  - Allowed Origins: {ALLOWED_ORIGINS}")
    
    response = await call_next(request)
    
    # CORS 응답 헤더 확인
    if origin and origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        logger.info(f"✅ CORS 헤더 설정: {origin}")
    else:
        logger.warning(f"⚠️ CORS Origin 미허용: {origin}")
    
    return response

@app.middleware("http")
async def _cors_probe(request: Request, call_next):
    print("CORS_PROBE",
          "origin=", repr(request.headers.get("origin")),
          "acr-method=", repr(request.headers.get("access-control-request-method")),
          "acr-headers=", repr(request.headers.get("access-control-request-headers")),
          "path=", request.url.path,
          "method=", request.method)
    return await call_next(request)

@app.get("/health")
async def health_check():
    return {"status": "healthy!"}

@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0"}

# 중요: auth_router는 prefix="/auth"라고 가정하고 게이트웨이 프리픽스는 "/api/v1"로 단일화
app.include_router(auth_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port) 