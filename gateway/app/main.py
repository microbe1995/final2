"""
Gateway API 메인 파일 (단일 파일 통합 버전)
- CORS 설정
- 헬스 체크
- 범용 프록시(/api/v1/{service}/{path})
- 서비스 디스커버리 기능(환경변수 기반)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import httpx

# 환경 변수 로드 (.env는 로컬에서만 사용)
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gateway_api")

# 서비스 맵 구성 (환경 변수 기반)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
CAL_BOUNDARY_URL = os.getenv("CAL_BOUNDARY_URL", "http://cal-boundary:8001")

SERVICE_MAP = {
    "auth": AUTH_SERVICE_URL,
    # 기본 키
    "boundary": CAL_BOUNDARY_URL,
    # 프론트엔드 호환용 별칭
    "cal-boundary": CAL_BOUNDARY_URL,
    "cal_boundary": CAL_BOUNDARY_URL,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 시작 (단일 파일 통합)")
    logger.info(f"🔗 SERVICE_MAP: {SERVICE_MAP}")
    yield
    logger.info("🛑 Gateway API 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final - 단일 파일 통합 버전",
    version="0.5.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# CORS 설정
allowed_origins = [o.strip() for o in os.getenv("CORS_URL", "").split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = [
        "https://lca-final.vercel.app",
        "http://localhost:3000",
    ]
allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
allow_methods = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(",")]
allow_headers = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

logger.info(f"🔧 CORS origins={allowed_origins}, credentials={allow_credentials}")

# 프록시 유틸리티
async def proxy_request(service: str, path: str, request: Request) -> Response:
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        return JSONResponse(status_code=404, content={"detail": f"Unknown service: {service}"})

    # 서비스별 경로 정규화 (내부 서비스 라우터 prefix와 정렬)
    normalized_path = path
    if service == "auth":
        # auth-service는 내부 라우터가 "/auth" prefix를 사용하므로 보정
        if normalized_path and not normalized_path.startswith("auth/") and normalized_path != "auth":
            normalized_path = f"auth/{normalized_path}"
    elif service == "boundary" or service == "cal-boundary" or service == "cal_boundary":
        # boundary-service는 내부에서 "/api" prefix를 사용하므로 보정
        if normalized_path and not normalized_path.startswith("api/"):
            normalized_path = f"api/{normalized_path}"

    target_url = f"{base_url.rstrip('/')}/{normalized_path}"
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    params = dict(request.query_params)
    body = await request.body()

    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                params=params,
                content=body,
            )
        except httpx.RequestError as e:
            logger.error(f"Upstream request error: {e}")
            return JSONResponse(status_code=502, content={"detail": "Bad Gateway", "error": str(e)})

    response_headers = {k: v for k, v in resp.headers.items() if k.lower() not in {"content-encoding", "transfer-encoding", "connection"}}
    return Response(content=resp.content, status_code=resp.status_code, headers=response_headers, media_type=resp.headers.get("content-type"))

# 범용 프록시 라우트 (메인 라우팅 역할)
@app.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(service: str, path: str, request: Request):
    return await proxy_request(service, path, request)

# 헬스 체크
@app.get("/health", summary="Gateway 헬스 체크")
async def health_check_root():
    return {"status": "healthy", "service": "gateway", "version": "0.5.0"}

# 요청 로깅
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 {request.method} {request.url.path} origin={request.headers.get('origin','N/A')}")
    response = await call_next(request)
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# 예외 처리
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error("🚨 404")
    return JSONResponse(status_code=404, content={"detail": f"Not Found: {request.url}", "path": request.url.path})

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    logger.error("🚨 405")
    return JSONResponse(status_code=405, content={"detail": f"Method Not Allowed: {request.method} {request.url}"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
