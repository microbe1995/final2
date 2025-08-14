"""
Gateway API 메인 파일 - 서비스 팩토리 패턴 적용
"""
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
import logging
import sys
import json
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import httpx
from enum import Enum

# 환경 변수 로드
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gateway_api")

# --- 서비스 타입 Enum 정의 ---
class ServiceType(str, Enum):
    """서비스 타입을 정의하는 Enum"""
    AUTH = "auth"
    DISCOVERY = "discovery"
    USER = "user"

# --- 서비스 프록시 팩토리 클래스 정의 ---
class ServiceProxyFactory:
    """서비스별 프록시 요청을 처리하는 팩토리 클래스"""
    
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
        self.base_url = self._get_service_url()
    
    def _get_service_url(self) -> str:
        """서비스 타입에 따른 URL 반환"""
        if self.service_type == ServiceType.AUTH:
            return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
        elif self.service_type == ServiceType.DISCOVERY:
            return os.getenv("DISCOVERY_SERVICE_URL", "http://localhost:8001")
        elif self.service_type == ServiceType.USER:
            return os.getenv("USER_SERVICE_URL", "http://localhost:8002")
        else:
            return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
    
    async def request(
        self,
        method: str,
        path: str,
        headers: dict = None,
        body: bytes = None,
        params: dict = None
    ):
        """서비스로 요청을 전달"""
        url = f"{self.base_url}/{path}"
        logger.info(f"🎯 {self.service_type.value} 서비스로 요청: {method} {url}")
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, content=body, headers=headers, params=params)
            elif method.upper() == "PUT":
                response = await client.put(url, content=body, headers=headers, params=params)
            elif method.upper() == "DELETE":
                response = await client.delete(url, content=body, headers=headers, params=params)
            elif method.upper() == "PATCH":
                response = await client.patch(url, content=body, headers=headers, params=params)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            
            logger.info(f"✅ {self.service_type.value} 서비스 응답: {response.status_code}")
            return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final - 서비스 팩토리 패턴 적용",
    version="0.3.0",
    docs_url="/docs",
    lifespan=lifespan
)

# Auth Service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
logger.info(f"🔧 Auth Service URL: {AUTH_SERVICE_URL}")

# CORS 설정 - 환경변수 기반
CORS_URL = os.getenv("CORS_URL")
if not CORS_URL:
    CORS_URL = "https://lca-final.vercel.app"
    logger.warning("⚠️ CORS_URL 환경변수가 설정되지 않아 기본값 사용")

FRONT_ORIGIN = CORS_URL.strip()
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "Accept,Accept-Language,Content-Language,Content-Type,Authorization,X-Requested-With,Origin,Access-Control-Request-Method,Access-Control-Request-Headers")

# 메서드와 헤더를 리스트로 변환
ALLOWED_METHODS = [m.strip() for m in CORS_ALLOW_METHODS.split(",") if m.strip()]
ALLOWED_HEADERS = [h.strip() for h in CORS_ALLOW_HEADERS.split(",") if h.strip()]

# 허용할 origin들을 리스트로 설정
ALLOWED_ORIGINS = [
    FRONT_ORIGIN,
    "https://lca-final.vercel.app",
    "https://lca-final-9th3dtaxw-microbe95s-projects.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

logger.info(f"🔧 CORS 설정 정보:")
logger.info(f"🔧 CORS_URL: {CORS_URL}")
logger.info(f"🔧 FRONT_ORIGIN: {FRONT_ORIGIN}")
logger.info(f"🔧 ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
logger.info(f"🔧 ALLOWED_METHODS: {ALLOWED_METHODS}")
logger.info(f"🔧 ALLOWED_HEADERS: {ALLOWED_HEADERS}")
logger.info(f"🔧 CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["*"],
    max_age=86400,
)

# CORS 헤더를 응답에 강제로 추가하는 함수
def add_cors_headers(response: Response, request: Request) -> Response:
    """응답에 CORS 헤더를 강제로 추가합니다."""
    origin = request.headers.get("origin")
    
    if origin in ALLOWED_ORIGINS:
        allowed_origin = origin
    else:
        allowed_origin = FRONT_ORIGIN
        logger.warning(f"⚠️ 허용되지 않은 origin: {origin}, 기본값 사용: {allowed_origin}")
    
    response.headers["Access-Control-Allow-Origin"] = allowed_origin
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    response.headers["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
    response.headers["Access-Control-Max-Age"] = "86400"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    logger.info(f"🔧 CORS 헤더 추가: Origin={allowed_origin}, Method={request.method}")
    return response

# --- 프록시 라우터 정의 ---
proxy_router = APIRouter(prefix="/e/v2", tags=["Service Proxy"])

@proxy_router.get("/health", summary="헬스 체크 엔드포인트")
async def health_check():
    """서비스가 정상적으로 실행 중인지 확인하는 엔드포인트"""
    logger.info("🔧 헬스 체크 요청 수신")
    return {"status": "healthy!", "service": "gateway", "version": "0.3.0"}

@proxy_router.options("/{service}/{path:path}", summary="OPTIONS 프록시")
async def proxy_options(service: ServiceType, path: str, request: Request):
    """OPTIONS 요청을 처리합니다 (CORS preflight)."""
    logger.info(f"🔧 OPTIONS 프록시 요청: service={service.value}, path={path}")
    
    origin = request.headers.get('Origin', FRONT_ORIGIN)
    
    return Response(
        status_code=200,
        headers={
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': ', '.join(ALLOWED_METHODS),
            'Access-Control-Allow-Headers': ', '.join(ALLOWED_HEADERS)
        }
    )

@proxy_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(service: ServiceType, path: str, request: Request):
    """GET 요청을 내부 서비스로 프록시합니다."""
    logger.info(f"🎯 GET 프록시 호출: service={service.value}, path={path}")
    
    try:
        factory = ServiceProxyFactory(service_type=service)
        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        response = await factory.request(
            method="GET",
            path=path,
            headers=headers,
            params=dict(request.query_params)
        )
        
        # CORS 헤더가 포함된 응답 생성
        json_response = JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
        return add_cors_headers(json_response, request)
        
    except Exception as e:
        logger.error(f"GET 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

@proxy_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(service: ServiceType, path: str, request: Request):
    """POST 요청을 내부 서비스로 프록시합니다."""
    logger.info(f"🎯 POST 프록시 호출: service={service.value}, path={path}")
    
    try:
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        response = await factory.request(
            method="POST",
            path=path,
            headers=headers,
            body=body,
            params=dict(request.query_params)
        )
        
        # CORS 헤더가 포함된 응답 생성
        json_response = JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
        return add_cors_headers(json_response, request)
        
    except Exception as e:
        logger.error(f"POST 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

@proxy_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: ServiceType, path: str, request: Request):
    """PUT 요청을 내부 서비스로 프록시합니다."""
    logger.info(f"🎯 PUT 프록시 호출: service={service.value}, path={path}")
    
    try:
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        response = await factory.request(
            method="PUT",
            path=path,
            headers=headers,
            body=body,
            params=dict(request.query_params)
        )
        
        # CORS 헤더가 포함된 응답 생성
        json_response = JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
        return add_cors_headers(json_response, request)
        
    except Exception as e:
        logger.error(f"PUT 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

@proxy_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: ServiceType, path: str, request: Request):
    """DELETE 요청을 내부 서비스로 프록시합니다."""
    logger.info(f"🎯 DELETE 프록시 호출: service={service.value}, path={path}")
    
    try:
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        response = await factory.request(
            method="DELETE",
            path=path,
            headers=headers,
            body=body,
            params=dict(request.query_params)
        )
        
        # CORS 헤더가 포함된 응답 생성
        json_response = JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
        return add_cors_headers(json_response, request)
        
    except Exception as e:
        logger.error(f"DELETE 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

@proxy_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: ServiceType, path: str, request: Request):
    """PATCH 요청을 내부 서비스로 프록시합니다."""
    logger.info(f"🎯 PATCH 프록시 호출: service={service.value}, path={path}")
    
    try:
        factory = ServiceProxyFactory(service_type=service)
        body = await request.body()
        headers = dict(request.headers)
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        response = await factory.request(
            method="PATCH",
            path=path,
            headers=headers,
            body=body,
            params=dict(request.query_params)
        )
        
        # CORS 헤더가 포함된 응답 생성
        json_response = JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=dict(response.headers)
        )
        
        return add_cors_headers(json_response, request)
        
    except Exception as e:
        logger.error(f"PATCH 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

# 요청 로깅 미들웨어
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 요청: {request.method} {request.url.path}")
    logger.info(f"🌐 Origin: {request.headers.get('origin', 'N/A')}")
    
    response = await call_next(request)
    
    # CORS 헤더 강제 추가
    response = add_cors_headers(response, request)
    
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# 기본 엔드포인트들
@app.get("/")
async def root():
    return {"message": "Gateway API - 서비스 팩토리 패턴 적용", "version": "0.3.0"}

# 프록시 라우터 등록
app.include_router(proxy_router)

logger.info("🔧 Gateway API 서비스 설정 완료")

# 404 에러 핸들러 추가
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error(f"🚨 404 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 Origin: {request.headers.get('origin', 'N/A')}")
    
    response = JSONResponse(
        status_code=404,
        content={
            "detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}",
            "method": request.method,
            "path": request.url.path
        }
    )
    
    return add_cors_headers(response, request)

# 405 에러 핸들러 추가
@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    logger.error(f"🚨 405 Method Not Allowed 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 Origin: {request.headers.get('origin', 'N/A')}")
    
    response = JSONResponse(
        status_code=405,
        content={
            "detail": f"허용되지 않는 HTTP 메서드입니다. 메서드: {request.method}, URL: {request.url}",
            "method": request.method,
            "path": request.url.path
        }
    )
    
    return add_cors_headers(response, request)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port) 