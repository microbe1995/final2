
import os
import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# 메시지 서비스 관련 import
from app.routers.message_router import router as message_router

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceConfig(BaseModel):
    """서비스 설정 모델"""
    name: str
    base_url: str
    health_check_path: str = "/health"
    timeout: int = 30
    retry_count: int = 3
    circuit_breaker_threshold: int = 5

class GatewaySettings(BaseSettings):
    """게이트웨이 설정"""
    app_name: str = "GreenSteel Gateway"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = int(os.environ.get("PORT", 8000))
    
    # CORS 설정
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # 보안 설정
    trusted_hosts: List[str] = ["*"]
    
    # 서비스 디스커버리 설정
    service_registry_url: Optional[str] = None
    service_registry_refresh_interval: int = 30  # 초
    
    class Config:
        env_file = ".env"

class ServiceRegistry:
    """서비스 레지스트리 관리"""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.service_health: Dict[str, bool] = {}
        self.circuit_breaker_count: Dict[str, int] = {}
    
    def register_service(self, service: ServiceConfig):
        """서비스 등록"""
        self.services[service.name] = service
        self.service_health[service.name] = True
        self.circuit_breaker_count[service.name] = 0
        logger.info(f"서비스 등록: {service.name} -> {service.base_url}")
    
    def get_service(self, service_name: str) -> Optional[ServiceConfig]:
        """서비스 조회"""
        return self.services.get(service_name)
    
    def update_service_health(self, service_name: str, is_healthy: bool):
        """서비스 헬스 상태 업데이트"""
        self.service_health[service_name] = is_healthy
        if not is_healthy:
            self.circuit_breaker_count[service_name] += 1
        else:
            self.circuit_breaker_count[service_name] = 0
    
    def is_service_available(self, service_name: str) -> bool:
        """서비스 사용 가능 여부 확인"""
        service = self.get_service(service_name)
        if not service:
            return False
        
        # Circuit Breaker 체크
        if self.circuit_breaker_count.get(service_name, 0) >= service.circuit_breaker_threshold:
            return False
        
        return self.service_health.get(service_name, False)

class APIGateway:
    """API Gateway 클래스"""
    
    def __init__(self):
        self.settings = GatewaySettings()
        self.app = FastAPI(
            title=self.settings.app_name,
            description="GreenSteel MSA API Gateway - 모든 마이크로서비스에 대한 통합 API 엔드포인트",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        self.service_registry = ServiceRegistry()
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        self._setup_middleware()
        self._setup_routes()
        self._register_default_services()
    
    def _setup_middleware(self):
        """미들웨어 설정"""
        # CORS 미들웨어
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.cors_origins,
            allow_credentials=self.settings.cors_allow_credentials,
            allow_methods=self.settings.cors_allow_methods,
            allow_headers=self.settings.cors_allow_headers,
        )
        
        # Trusted Host 미들웨어
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=self.settings.trusted_hosts
        )
    
    def _setup_routes(self):
        """라우트 설정"""
        
        # 메시지 서비스 라우터 등록
        self.app.include_router(message_router)
        
        @self.app.get("/", 
                      summary="게이트웨이 상태",
                      description="GreenSteel API Gateway의 기본 상태 정보를 반환합니다.",
                      tags=["Gateway Status"])
        async def root():
            """루트 엔드포인트"""
            return {
                "message": "GreenSteel API Gateway",
                "version": "1.0.0",
                "status": "running",
                "docs": {
                    "swagger": "/docs",
                    "redoc": "/redoc",
                    "openapi": "/openapi.json"
                }
            }
        
        @self.app.get("/health", 
                      summary="헬스 체크",
                      description="게이트웨이와 모든 등록된 서비스의 헬스 상태를 확인합니다.",
                      tags=["Gateway Status"])
        async def health_check():
            """헬스 체크"""
            return {
                "status": "healthy",
                "gateway": "running",
                "services": {
                    name: {
                        "healthy": self.service_registry.is_service_available(name),
                        "circuit_breaker": self.service_registry.circuit_breaker_count.get(name, 0)
                    }
                    for name in self.service_registry.services.keys()
                }
            }
        
        @self.app.get("/services", 
                      summary="등록된 서비스 목록",
                      description="현재 게이트웨이에 등록된 모든 마이크로서비스의 목록과 상태를 반환합니다.",
                      tags=["Gateway Management"])
        async def list_services():
            """등록된 서비스 목록"""
            return {
                "services": [
                    {
                        "name": service.name,
                        "base_url": service.base_url,
                        "healthy": self.service_registry.is_service_available(service.name),
                        "circuit_breaker_count": self.service_registry.circuit_breaker_count.get(service.name, 0)
                    }
                    for service in self.service_registry.services.values()
                ]
            }
        
        @self.app.get("/docs/swagger", 
                      summary="Swagger UI",
                      description="API 문서를 위한 Swagger UI 페이지로 리다이렉트합니다.",
                      tags=["Documentation"])
        async def swagger_redirect():
            """Swagger UI 리다이렉트"""
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/docs")
        
        @self.app.get("/docs/redoc", 
                      summary="ReDoc",
                      description="API 문서를 위한 ReDoc 페이지로 리다이렉트합니다.",
                      tags=["Documentation"])
        async def redoc_redirect():
            """ReDoc 리다이렉트"""
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/redoc")
        
        @self.app.api_route("/{service_name}/{path:path}", 
                           methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
                           summary="서비스 프록시",
                           description="지정된 마이크로서비스로 요청을 프록시합니다. 모든 HTTP 메서드를 지원합니다.",
                           tags=["Service Proxy"])
        async def proxy_request(service_name: str, path: str, request: Request):
            """프록시 요청 처리"""
            return await self._handle_proxy_request(service_name, path, request)
    
    def _register_default_services(self):
        """기본 서비스 등록"""
        default_services = [
            ServiceConfig(
                name="user-service",
                base_url="http://user-service:8001",
                health_check_path="/health"
            ),
            ServiceConfig(
                name="product-service", 
                base_url="http://product-service:8002",
                health_check_path="/health"
            ),
            ServiceConfig(
                name="order-service",
                base_url="http://order-service:8003", 
                health_check_path="/health"
            ),
            ServiceConfig(
                name="payment-service",
                base_url="http://payment-service:8004",
                health_check_path="/health"
            ),
            ServiceConfig(
                name="notification-service",
                base_url="http://notification-service:8005",
                health_check_path="/health"
            )
        ]
        
        for service in default_services:
            self.service_registry.register_service(service)
    
    async def _handle_proxy_request(self, service_name: str, path: str, request: Request):
        """프록시 요청 처리"""
        # 서비스 확인
        if not self.service_registry.is_service_available(service_name):
            raise HTTPException(
                status_code=503,
                detail=f"Service {service_name} is not available"
            )
        
        service = self.service_registry.get_service(service_name)
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service {service_name} not found"
            )
        
        # 타겟 URL 구성
        target_url = urljoin(service.base_url, path)
        
        # 요청 헤더 준비
        headers = dict(request.headers)
        # 호스트 헤더 제거 (타겟 서비스의 호스트로 대체)
        headers.pop("host", None)
        
        # 요청 바디 준비
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # 프록시 요청 전송
        try:
            async with httpx.AsyncClient(timeout=service.timeout) as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=dict(request.query_params)
                )
                
                # 응답 헤더 준비
                response_headers = dict(response.headers)
                response_headers.pop("content-encoding", None)
                response_headers.pop("content-length", None)
                
                # 성공 응답 시 헬스 상태 업데이트
                self.service_registry.update_service_health(service_name, True)
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=response_headers,
                    media_type=response.headers.get("content-type")
                )
                
        except httpx.TimeoutException:
            logger.error(f"Timeout for service {service_name}")
            self.service_registry.update_service_health(service_name, False)
            raise HTTPException(
                status_code=504,
                detail=f"Service {service_name} timeout"
            )
        except httpx.ConnectError:
            logger.error(f"Connection error for service {service_name}")
            self.service_registry.update_service_health(service_name, False)
            raise HTTPException(
                status_code=503,
                detail=f"Service {service_name} connection error"
            )
        except Exception as e:
            logger.error(f"Error proxying to service {service_name}: {str(e)}")
            self.service_registry.update_service_health(service_name, False)
            raise HTTPException(
                status_code=500,
                detail=f"Internal gateway error"
            )
    
    async def start_health_check_loop(self):
        """헬스 체크 루프 시작"""
        while True:
            await self._perform_health_checks()
            await asyncio.sleep(30)  # 30초마다 헬스 체크
    
    async def _perform_health_checks(self):
        """모든 서비스에 대한 헬스 체크 수행"""
        for service_name, service in self.service_registry.services.items():
            try:
                health_url = urljoin(service.base_url, service.health_check_path)
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(health_url)
                    is_healthy = response.status_code == 200
                    self.service_registry.update_service_health(service_name, is_healthy)
                    
                    if not is_healthy:
                        logger.warning(f"Service {service_name} is unhealthy")
                        
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {str(e)}")
                self.service_registry.update_service_health(service_name, False)
    
    async def shutdown(self):
        """게이트웨이 종료"""
        await self.http_client.aclose()

# 게이트웨이 인스턴스 생성
gateway = APIGateway()


# FastAPI 앱 참조
app = gateway.app

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("GreenSteel API Gateway starting...")
    # 헬스 체크 루프 시작
    asyncio.create_task(gateway.start_health_check_loop())

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("GreenSteel API Gateway shutting down...")
    await gateway.shutdown()

# 게이트웨이 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )