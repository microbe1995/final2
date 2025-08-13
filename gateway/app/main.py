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

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://lca-final.vercel.app").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(",")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "Accept,Accept-Language,Content-Language,Content-Type,Authorization,X-Requested-With,Origin,Access-Control-Request-Method,Access-Control-Request-Headers").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=[m.strip() for m in CORS_ALLOW_METHODS if m.strip()],
    allow_headers=[h.strip() for h in CORS_ALLOW_HEADERS if h.strip()],
    expose_headers=["*"],
    max_age=86400,
)

@app.options("/{path:path}")
async def any_options(path: str):
    response = Response(content="OK", status_code=200)
    origin = (CORS_ORIGINS[0] or "").strip() if CORS_ORIGINS else ""
    response.headers["Access-Control-Allow-Origin"] = origin or ""
    response.headers["Access-Control-Allow-Methods"] = ", ".join(CORS_ALLOW_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(CORS_ALLOW_HEADERS)
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    response.headers["Access-Control-Max-Age"] = "86400"
    return response

@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response

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