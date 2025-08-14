"""
Gateway API 메인 파일 - 서비스 팩토리 패턴 적용
"""
from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
import logging
import sys
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

# CORS 설정 - 모든 출처 허용 (보안 약화)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

logger.info("🔧 CORS 설정: 모든 출처 허용")

# --- 프록시 라우터 정의 ---
proxy_router = APIRouter(prefix="/e/v2", tags=["Service Proxy"])

@proxy_router.get("/gateway/health", summary="Gateway 헬스 체크 엔드포인트")
async def health_check():
    """Gateway가 정상적으로 실행 중인지 확인하는 엔드포인트"""
    logger.info("🔧 Gateway 헬스 체크 요청 수신")
    return {"status": "healthy!", "service": "gateway", "version": "0.3.0"}

@proxy_router.options("/{service}/{path:path}", summary="OPTIONS 프록시")
async def proxy_options(service: ServiceType, path: str, request: Request):
    """OPTIONS 요청을 처리합니다 (CORS preflight)."""
    logger.info(f"🔧 OPTIONS 프록시 요청: service={service.value}, path={path}")
    
    return Response(
        status_code=200,
        headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
            'Access-Control-Allow-Headers': '*'
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
        
        # 응답 생성 (CORS 헤더 추가)
        response_headers = dict(response.headers)
        response_headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
            'Access-Control-Allow-Headers': '*'
        })
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=response_headers
        )
        
    except Exception as e:
        logger.error(f"GET 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

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
        
        # 응답 생성 (CORS 헤더 추가)
        response_headers = dict(response.headers)
        response_headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
            'Access-Control-Allow-Headers': '*'
        })
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=response_headers
        )
        
    except Exception as e:
        logger.error(f"POST 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

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
        
        # 응답 생성 (CORS 헤더 추가)
        response_headers = dict(response.headers)
        response_headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
            'Access-Control-Allow-Headers': '*'
        })
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=response_headers
        )
        
    except Exception as e:
        logger.error(f"PUT 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

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
        
        # 응답 생성 (CORS 헤더 추가)
        response_headers = dict(response.headers)
        response_headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
            'Access-Control-Allow-Headers': '*'
        })
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=response_headers
        )
        
    except Exception as e:
        logger.error(f"DELETE 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

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
        
        # 응답 생성 (CORS 헤더 추가)
        response_headers = dict(response.headers)
        response_headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
            'Access-Control-Allow-Headers': '*'
        })
        
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code,
            headers=response_headers
        )
        
    except Exception as e:
        logger.error(f"PATCH 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# 요청 로깅 미들웨어
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 요청: {request.method} {request.url.path}")
    logger.info(f"🌐 Origin: {request.headers.get('origin', 'N/A')}")
    
    response = await call_next(request)
    
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# CORS 헤더를 모든 응답에 추가하는 미들웨어
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    
    # 모든 응답에 CORS 헤더 추가
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

# 프록시 라우터 등록 (먼저 등록)
app.include_router(proxy_router)

# 기본 엔드포인트들 (나중에 등록)
@app.get("/")
async def root():
    return {"message": "Gateway API - 서비스 팩토리 패턴 적용", "version": "0.3.0"}

@app.get("/health")
async def health_check():
    """Gateway 직접 헬스 체크 엔드포인트"""
    logger.info("🔧 Gateway 직접 헬스 체크 요청 수신")
    return {"status": "healthy", "service": "gateway", "version": "0.3.0"}

logger.info("🔧 Gateway API 서비스 설정 완료")

# 404 에러 핸들러 추가
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error(f"🚨 404 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 Origin: {request.headers.get('origin', 'N/A')}")
    
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}",
            "method": request.method,
            "path": request.url.path
        }
    )

# 405 에러 핸들러 추가
@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    logger.error(f"🚨 405 Method Not Allowed 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 Origin: {request.headers.get('origin', 'N/A')}")
    
    return JSONResponse(
        status_code=405,
        content={
            "detail": f"허용되지 않는 HTTP 메서드입니다. 메서드: {request.method}, URL: {request.url}",
            "method": request.method,
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port) 