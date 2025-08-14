"""
Gateway API 메인 파일 - CORS 정리 & 프록시 안정화
"""
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import httpx
from enum import Enum

# 환경 변수 로드 (.env는 로컬에서만 사용, Railway에선 대시보드 변수 사용)
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gateway_api")

# --- 서비스 타입 Enum ---
class ServiceType(str, Enum):
    AUTH = "auth"
    DISCOVERY = "discovery"
    USER = "user"

# --- 서비스 프록시 팩토리 ---
class ServiceProxyFactory:
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
        self.base_url = self._get_service_url()

    def _get_service_url(self) -> str:
        if self.service_type == ServiceType.AUTH:
            return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
        elif self.service_type == ServiceType.DISCOVERY:
            return os.getenv("DISCOVERY_SERVICE_URL", "http://localhost:8001")
        elif self.service_type == ServiceType.USER:
            return os.getenv("USER_SERVICE_URL", "http://localhost:8002")
        # fallback
        return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

    async def request(
        self,
        method: str,
        path: str,
        headers: dict | None = None,
        body: bytes | None = None,
        params: dict | None = None,
    ):
        url = f"{self.base_url}/{path}"
        logger.info(f"➡️  proxy -> {self.service_type.value}: {method} {url}")
        async with httpx.AsyncClient() as client:
            m = method.upper()
            if m == "GET":
                resp = await client.get(url, headers=headers, params=params)
            elif m == "POST":
                resp = await client.post(url, content=body, headers=headers, params=params)
            elif m == "PUT":
                resp = await client.put(url, content=body, headers=headers, params=params)
            elif m == "DELETE":
                resp = await client.delete(url, content=body, headers=headers, params=params)
            elif m == "PATCH":
                resp = await client.patch(url, content=body, headers=headers, params=params)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            logger.info(f"✅  {self.service_type.value} 응답: {resp.status_code}")
            return resp

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 시작")
    yield
    logger.info("🛑 Gateway API 종료")

# FastAPI 앱
app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final",
    version="0.3.1",
    docs_url="/docs",
    lifespan=lifespan,
)

# ---- CORS 설정 (환경변수 기반) ----
# Railway Variables 예시:
# CORS_URL = https://lca-final.vercel.app
allowed_origins = [o.strip() for o in os.getenv("CORS_URL", "").split(",") if o.strip()]
if not allowed_origins:
    # 안전한 기본값(필요 시 바꿔도 됨)
    allowed_origins = ["https://lca-final.vercel.app"]

allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
allow_methods = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(",")]
allow_headers = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,    # "*" 금지 (credentials true일 때 규칙 위반)
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

logger.info(f"🔧 CORS origins={allowed_origins}, credentials={allow_credentials}")

# ---- 프록시 라우터 ----
proxy_router = APIRouter(prefix="/e/v2", tags=["Service Proxy"])

@proxy_router.get("/gateway/health", summary="Gateway 헬스 체크")
async def gateway_health():
    return {"status": "healthy", "service": "gateway", "version": "0.3.1"}

def _clean_forward_headers(h: dict) -> dict:
    h = dict(h)
    h.pop("host", None)
    h.pop("content-length", None)
    return h

@proxy_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(service: ServiceType, path: str, request: Request):
    try:
        factory = ServiceProxyFactory(service_type=service)
        resp = await factory.request(
            method="GET",
            path=path,
            headers=_clean_forward_headers(request.headers),
            params=dict(request.query_params),
        )
        return JSONResponse(
            content=resp.json() if resp.content else {},
            status_code=resp.status_code,
        )
    except Exception as e:
        logger.exception("GET 프록시 오류")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

@proxy_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(service: ServiceType, path: str, request: Request):
    try:
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        resp = await factory.request(
            method="POST",
            path=path,
            headers=_clean_forward_headers(request.headers),
            body=body,
            params=dict(request.query_params),
        )
        return JSONResponse(
            content=resp.json() if resp.content else {},
            status_code=resp.status_code,
        )
    except Exception as e:
        logger.exception("POST 프록시 오류")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

@proxy_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: ServiceType, path: str, request: Request):
    try:
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        resp = await factory.request(
            method="PUT",
            path=path,
            headers=_clean_forward_headers(request.headers),
            body=body,
            params=dict(request.query_params),
        )
        return JSONResponse(
            content=resp.json() if resp.content else {},
            status_code=resp.status_code,
        )
    except Exception as e:
        logger.exception("PUT 프록시 오류")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

@proxy_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: ServiceType, path: str, request: Request):
    try:
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        resp = await factory.request(
            method="DELETE",
            path=path,
            headers=_clean_forward_headers(request.headers),
            body=body,
            params=dict(request.query_params),
        )
        return JSONResponse(
            content=resp.json() if resp.content else {},
            status_code=resp.status_code,
        )
    except Exception as e:
        logger.exception("DELETE 프록시 오류")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

@proxy_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: ServiceType, path: str, request: Request):
    try:
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        resp = await factory.request(
            method="PATCH",
            path=path,
            headers=_clean_forward_headers(request.headers),
            body=body,
            params=dict(request.query_params),
        )
        return JSONResponse(
            content=resp.json() if resp.content else {},
            status_code=resp.status_code,
        )
    except Exception as e:
        logger.exception("PATCH 프록시 오류")
        return JSONResponse(content={"detail": f"Error processing request: {str(e)}"}, status_code=500)

# 요청 로깅(참고용)
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 {request.method} {request.url.path} origin={request.headers.get('origin','N/A')}")
    response = await call_next(request)
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# 라우터 등록
app.include_router(proxy_router)

# 기본 엔드포인트
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.3.1"}

@app.get("/health")
async def health_check_root():
    return {"status": "healthy", "service": "gateway", "version": "0.3.1"}

# 404
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error("🚨 404")
    return JSONResponse(
        status_code=404,
        content={"detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}",
                 "method": request.method, "path": request.url.path},
    )

# 405
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
