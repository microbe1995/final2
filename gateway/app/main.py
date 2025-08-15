"""
<<<<<<< HEAD
Gateway API 메인 파일 - CORS 정리 & 프록시 안정화
"""
from fastapi import FastAPI, Request, APIRouter
=======
Gateway API 메인 파일 - 도메인 구조로 리팩토링
기존 코드를 도메인 레이어로 분리하여 유지보수성 향상
"""
from fastapi import FastAPI, Request
>>>>>>> 2450e54 (gateway main.py 기능 분리)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
<<<<<<< HEAD
import httpx
from enum import Enum
=======

# 도메인 레이어 import
from .domain.controller.proxy_controller import proxy_router
from .domain.service.proxy_service import ProxyService
>>>>>>> 2450e54 (gateway main.py 기능 분리)

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

<<<<<<< HEAD
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
        # 경로 정리 (앞의 슬래시 제거)
        clean_path = path.lstrip('/')
        url = f"{self.base_url}/{clean_path}"
        logger.info(f"➡️  proxy -> {self.service_type.value}: {method} {url}")
        logger.info(f"🔧 base_url: {self.base_url}, path: {path}, clean_path: {clean_path}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
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
                logger.info(f"🔧 응답 헤더: {dict(resp.headers)}")
                return resp
        except httpx.TimeoutException:
            logger.error(f"⏰ {self.service_type.value} 서비스 타임아웃")
            raise Exception(f"{self.service_type.value} 서비스 응답 시간 초과")
        except httpx.ConnectError:
            logger.error(f"🔌 {self.service_type.value} 서비스 연결 실패")
            raise Exception(f"{self.service_type.value} 서비스에 연결할 수 없습니다")
        except Exception as e:
            logger.error(f"❌ {self.service_type.value} 서비스 요청 실패: {str(e)}")
            raise e

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
=======
@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🚀 Gateway API 시작 (도메인 구조 적용)")
    yield
    logger.info("🛑 Gateway API 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final - 도메인 구조로 리팩토링됨",
    version="0.4.0",
>>>>>>> 2450e54 (gateway main.py 기능 분리)
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

<<<<<<< HEAD
# ---- 프록시 라우터 ----
proxy_router = APIRouter(prefix="/api/v1", tags=["Service Proxy"])

# OPTIONS 요청 처리 (CORS preflight)
@proxy_router.options("/{service}/{path:path}")
async def proxy_options(service: str, path: str, request: Request):
    """CORS preflight 요청 처리"""
    origin = request.headers.get("origin")
    if origin in allowed_origins:
        allowed_origin = origin
    else:
        allowed_origin = allowed_origins[0] if allowed_origins else "https://lca-final.vercel.app"
    
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": allowed_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        }
    )

@proxy_router.get("/gateway/health", summary="Gateway 헬스 체크")
async def gateway_health():
    return {"status": "healthy", "service": "gateway", "version": "0.3.1"}

@proxy_router.get("/gateway/services/health", summary="연결된 서비스들의 헬스 체크")
async def services_health():
    """연결된 모든 서비스의 상태를 확인"""
    services_status = {}
    
    try:
        # Auth Service 헬스 체크
        auth_factory = ServiceProxyFactory(service_type=ServiceType.AUTH)
        auth_resp = await auth_factory.request("GET", "health")
        services_status["auth"] = {
            "status": "healthy" if auth_resp.status_code == 200 else "unhealthy",
            "status_code": auth_resp.status_code,
            "url": auth_factory.base_url
        }
    except Exception as e:
        services_status["auth"] = {
            "status": "error",
            "error": str(e),
            "url": auth_factory.base_url if 'auth_factory' in locals() else "unknown"
        }
    
    return {
        "gateway": "healthy",
        "services": services_status,
        "timestamp": "2024-01-01T00:00:00Z"
    }

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
        logger.info(f"📝 POST 프록시 요청: service={service}, path={path}")
        logger.info(f"🔧 요청 헤더: {dict(request.headers)}")
        
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        logger.info(f"📦 요청 본문 크기: {len(body)} bytes")
        
        resp = await factory.request(
            method="POST",
            path=path,
            headers=_clean_forward_headers(request.headers),
            body=body,
            params=dict(request.query_params),
        )
        
        logger.info(f"✅ 프록시 응답 성공: {resp.status_code}")
        return JSONResponse(
            content=resp.json() if resp.content else {},
            status_code=resp.status_code,
        )
    except Exception as e:
        logger.exception(f"❌ POST 프록시 오류: {str(e)}")
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
=======
# ---- 도메인 라우터 등록 ----
# 프록시 컨트롤러의 라우터를 등록
app.include_router(proxy_router)

# ---- 기본 엔드포인트 ----
@app.get("/", summary="Gateway 루트")
async def root():
    """Gateway API 루트 엔드포인트"""
    return {
        "message": "Gateway API - 도메인 구조로 리팩토링됨", 
        "version": "0.4.0",
        "architecture": "Domain-Driven Design",
        "docs": "/docs"
    }

@app.get("/health", summary="Gateway 헬스 체크")
async def health_check_root():
    """Gateway 서비스 상태 확인"""
    return {"status": "healthy", "service": "gateway", "version": "0.4.0"}

# ---- 요청 로깅 미들웨어 ----
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    """모든 HTTP 요청을 로깅하는 미들웨어"""
>>>>>>> 2450e54 (gateway main.py 기능 분리)
    logger.info(f"🌐 {request.method} {request.url.path} origin={request.headers.get('origin','N/A')}")
    response = await call_next(request)
    logger.info(f"🌐 응답: {response.status_code}")
    return response

<<<<<<< HEAD
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
=======
# ---- 예외 처리 핸들러 ----
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 Not Found 예외 처리"""
    logger.error("🚨 404")
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}",
            "method": request.method, 
            "path": request.url.path,
            "architecture": "Domain-Driven Design"
        },
    )

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    """405 Method Not Allowed 예외 처리"""
    logger.error("🚨 405")
    return JSONResponse(
        status_code=405,
        content={
            "detail": f"허용되지 않는 HTTP 메서드입니다. 메서드: {request.method}, URL: {request.url}",
            "method": request.method, 
            "path": request.url.path,
            "architecture": "Domain-Driven Design"
        },
    )

# ---- 애플리케이션 실행 ----
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

# ============================================================================
# 🚫 기존 코드 (참고용으로 보존, 실제로는 사용되지 않음)
# ============================================================================
"""
기존 main.py의 코드를 도메인 구조로 분리한 내용:

1. ServiceProxyFactory 클래스 → domain/service/proxy_service.py로 이동
2. 프록시 라우터 → domain/controller/proxy_controller.py로 이동
3. CORS 처리 → domain/service/proxy_service.py의 handle_cors_preflight로 이동
4. 서비스 헬스 체크 → domain/service/proxy_service.py의 check_all_services_health로 이동

도메인 구조의 장점:
- 관심사 분리 (Separation of Concerns)
- 단일 책임 원칙 (Single Responsibility Principle)
- 코드 재사용성 향상
- 테스트 용이성 향상
- 유지보수성 향상

각 레이어의 역할:
- Controller: HTTP 요청/응답 처리
- Service: 비즈니스 로직 (서비스 디스커버리, 프록시 처리)
- Repository: 데이터 접근 로직 (서비스 정보 관리)
- Entity: 데이터 모델 (서비스 정보, 헬스 체크 결과)
- Schema: 데이터 검증 및 직렬화
"""
>>>>>>> 2450e54 (gateway main.py 기능 분리)
