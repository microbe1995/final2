"""
Gateway API 메인 파일 - CORS 정리 & 프록시 안정화 (완성본)
"""
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response as FastAPIResponse, JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import httpx
from enum import Enum

# ──────────────────────────────────────────────────────────────────────────────
# 환경 변수 로드 (.env는 로컬에서만 사용, Railway는 대시보드 변수를 사용)
# ──────────────────────────────────────────────────────────────────────────────
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# 로깅
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gateway_api")

# ──────────────────────────────────────────────────────────────────────────────
# 서비스 타입
# ──────────────────────────────────────────────────────────────────────────────
class ServiceType(str, Enum):
    AUTH = "auth"
    DISCOVERY = "discovery"
    USER = "user"

# ──────────────────────────────────────────────────────────────────────────────
# 서비스 프록시 팩토리
#   ⚠️ 각 서비스 URL은 "서비스 prefix까지 포함"하도록 환경변수에 넣어주세요.
#   예) AUTH_SERVICE_URL = http://auth-service.railway.internal:8000/api/v1/auth
# ──────────────────────────────────────────────────────────────────────────────
class ServiceProxyFactory:
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
        self.base_url = self._get_service_url()  # prefix 포함 URL

    def _get_service_url(self) -> str:
        st = self.service_type
        if st == ServiceType.AUTH:
            return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000/api/v1/auth")
        if st == ServiceType.DISCOVERY:
            return os.getenv("DISCOVERY_SERVICE_URL", "http://localhost:8001/api/v1/discovery")
        if st == ServiceType.USER:
            return os.getenv("USER_SERVICE_URL", "http://localhost:8002/api/v1/user")
        # fallback
        return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000/api/v1/auth")

    async def request(
        self,
        method: str,
        path: str,
        headers: dict | None = None,
        body: bytes | None = None,
        params: dict | None = None,
    ):
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        logger.info(f"➡️  proxy -> {self.service_type.value}: {method.upper()} {url}")

        async with httpx.AsyncClient() as client:
            m = method.upper()
            if m == "GET":
                resp = await client.get(url, headers=headers, params=params)
            elif m == "POST":
                resp = await client.post(url, headers=headers, content=body, params=params)
            elif m == "PUT":
                resp = await client.put(url, headers=headers, content=body, params=params)
            elif m == "DELETE":
                resp = await client.delete(url, headers=headers, content=body, params=params)
            elif m == "PATCH":
                resp = await client.patch(url, headers=headers, content=body, params=params)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")

        # 에러면 upstream 본문을 로그에 남겨 디버깅 용이
        if resp.status_code >= 400:
            preview = resp.text[:1000] if resp.text else "<empty body>"
            logger.error(f"⛔ upstream {self.service_type.value} {resp.status_code}: {preview}")

        return resp

# ──────────────────────────────────────────────────────────────────────────────
# 앱 & CORS
# ──────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 시작")
    yield
    logger.info("🛑 Gateway API 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final",
    version="0.4.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# CORS (환경변수 기반)
# Railway 변수 예) CORS_URL=https://lca-final.vercel.app
allowed_origins = [o.strip() for o in os.getenv("CORS_URL", "").split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = ["https://lca-final.vercel.app"]

allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
allow_methods = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(",")]
allow_headers = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,    # "*" 금지(credential true일 때 규칙 위반)
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

logger.info(f"🔧 CORS origins={allowed_origins}, credentials={allow_credentials}")

# ──────────────────────────────────────────────────────────────────────────────
# 공통 유틸
# ──────────────────────────────────────────────────────────────────────────────
def _clean_forward_headers(h: dict) -> dict:
    h = dict(h)
    h.pop("host", None)
    h.pop("content-length", None)
    return h

def _passthrough_response(resp: httpx.Response) -> FastAPIResponse:
    headers = {}
    ct = resp.headers.get("content-type")
    if ct:
        headers["content-type"] = ct
    return FastAPIResponse(content=resp.content, status_code=resp.status_code, headers=headers)

# ──────────────────────────────────────────────────────────────────────────────
# 프록시 라우터 (/api/v1 …)
#   프런트는 다음처럼 호출:
#   POST https://<gateway>/api/v1/auth/register
# ──────────────────────────────────────────────────────────────────────────────
router_v1 = APIRouter(prefix="/api/v1", tags=["Service Proxy v1"])

@router_v1.get("/gateway/health")
async def gateway_health_v1():
    return {"status": "healthy", "service": "gateway", "version": "0.4.0"}

@router_v1.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_v1(service: ServiceType, path: str, request: Request):
    factory = ServiceProxyFactory(service_type=service)
    body = await request.body()
    resp = await factory.request(
        method=request.method,
        path=path,
        headers=_clean_forward_headers(request.headers),
        body=body if request.method not in ("GET", "HEAD") else None,
        params=dict(request.query_params),
    )
    return _passthrough_response(resp)

# ──────────────────────────────────────────────────────────────────────────────
# 호환 라우터 (/e/v2 …)  — 필요 없으면 이 블록 삭제해도 됨
# ──────────────────────────────────────────────────────────────────────────────
router_v2 = APIRouter(prefix="/e/v2", tags=["Service Proxy v2 (compat)"])

@router_v2.get("/gateway/health")
async def gateway_health_v2():
    return {"status": "healthy", "service": "gateway", "version": "0.4.0"}

@router_v2.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_v2(service: ServiceType, path: str, request: Request):
    factory = ServiceProxyFactory(service_type=service)
    body = await request.body()
    resp = await factory.request(
        method=request.method,
        path=path,
        headers=_clean_forward_headers(request.headers),
        body=body if request.method not in ("GET", "HEAD") else None,
        params=dict(request.query_params),
    )
    return _passthrough_response(resp)

# ──────────────────────────────────────────────────────────────────────────────
# 요청 로깅(참고용)
# ──────────────────────────────────────────────────────────────────────────────
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 {request.method} {request.url.path} origin={request.headers.get('origin','N/A')}")
    response = await call_next(request)
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# ──────────────────────────────────────────────────────────────────────────────
# 라우터 등록 & 기본 엔드포인트
# ──────────────────────────────────────────────────────────────────────────────
app.include_router(router_v1)
app.include_router(router_v2)

@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.4.0"}

@app.get("/health")
async def health_check_root():
    return {"status": "healthy", "service": "gateway", "version": "0.4.0"}

# 404 / 405
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error("🚨 404")
    return JSONResponse(
        status_code=404,
        content={"detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}",
                 "method": request.method, "path": request.url.path},
    )

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    logger.error("🚨 405")
    return JSONResponse(
        status_code=405,
        content={"detail": f"허용되지 않는 HTTP 메서드입니다. 메서드: {request.method}, URL: {request.url}",
                 "method": request.method, "path": request.url.path},
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
