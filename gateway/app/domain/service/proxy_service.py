"""
프록시 서비스 - 서비스 디스커버리 및 프록시 로직
Gateway의 핵심 비즈니스 로직을 담당
"""
import os
import logging
import httpx
from typing import Dict, Any, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from enum import Enum

from app.domain.entity.service_entity import ServiceInfo
from app.domain.repository.service_repository import ServiceRepository

# 로거 설정
logger = logging.getLogger(__name__)

class ServiceType(str, Enum):
    """서비스 타입 Enum"""
    AUTH = "auth"
    DISCOVERY = "discovery"
    USER = "user"

class ProxyService:
    """
    프록시 서비스 클래스
    - 서비스 디스커버리
    - 요청 프록시 처리
    - 서비스 헬스 체크
    """
    
    def __init__(self):
        """프록시 서비스 초기화"""
        self.service_repository = ServiceRepository()
        self.timeout = 30.0
        
    def _get_service_url(self, service_type: ServiceType) -> str:
        """
        서비스 타입에 따른 URL 반환
        
        Args:
            service_type: 서비스 타입
            
        Returns:
            서비스 URL
        """
        if service_type == ServiceType.AUTH:
            return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
        elif service_type == ServiceType.DISCOVERY:
            return os.getenv("DISCOVERY_SERVICE_URL", "http://localhost:8001")
        elif service_type == ServiceType.USER:
            return os.getenv("USER_SERVICE_URL", "http://localhost:8002")
        # fallback
        return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
    
    async def proxy_request(
        self, 
        method: str, 
        service: str, 
        path: str, 
        request: Request
    ) -> JSONResponse:
        """
        HTTP 요청을 대상 서비스로 프록시
        
        Args:
            method: HTTP 메서드 (GET, POST, PUT, DELETE, PATCH)
            service: 대상 서비스명
            path: 요청 경로
            request: HTTP 요청 객체
            
        Returns:
            대상 서비스의 응답
        """
        try:
            # 서비스 타입 검증
            service_type = ServiceType(service)
            base_url = self._get_service_url(service_type)
            
            # 경로 정리 (앞의 슬래시 제거)
            clean_path = path.lstrip('/')
            url = f"{base_url}/{clean_path}"
            
            logger.info(f"➡️  proxy -> {service}: {method} {url}")
            logger.info(f"🔧 base_url: {base_url}, path: {path}, clean_path: {clean_path}")
            
            # 요청 본문 및 헤더 준비
            body = await request.body() if method in ["POST", "PUT", "DELETE", "PATCH"] else None
            headers = self._clean_forward_headers(request.headers)
            params = dict(request.query_params)
            
            # HTTP 클라이언트로 요청 전송
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await self._make_request(
                    client, method, url, headers, body, params
                )
                
                logger.info(f"✅  {service} 응답: {response.status_code}")
                logger.info(f"🔧 응답 헤더: {dict(response.headers)}")
                
                # 응답 반환
                return JSONResponse(
                    content=response.json() if response.content else {},
                    status_code=response.status_code,
                )
                
        except ValueError as e:
            logger.error(f"❌ 잘못된 서비스 타입: {service}")
            return JSONResponse(
                content={"detail": f"지원하지 않는 서비스 타입: {service}"}, 
                status_code=400
            )
        except httpx.TimeoutException:
            logger.error(f"⏰ {service} 서비스 타임아웃")
            return JSONResponse(
                content={"detail": f"{service} 서비스 응답 시간 초과"}, 
                status_code=504
            )
        except httpx.ConnectError:
            logger.error(f"🔌 {service} 서비스 연결 실패")
            return JSONResponse(
                content={"detail": f"{service} 서비스에 연결할 수 없습니다"}, 
                status_code=503
            )
        except Exception as e:
            logger.error(f"❌ {service} 서비스 요청 실패: {str(e)}")
            return JSONResponse(
                content={"detail": f"서비스 요청 처리 중 오류가 발생했습니다: {str(e)}"}, 
                status_code=500
            )
    
    async def _make_request(
        self, 
        client: httpx.AsyncClient, 
        method: str, 
        url: str, 
        headers: dict, 
        body: Optional[bytes], 
        params: dict
    ) -> httpx.Response:
        """
        HTTP 클라이언트를 사용하여 요청 전송
        
        Args:
            client: HTTP 클라이언트
            method: HTTP 메서드
            url: 요청 URL
            headers: 요청 헤더
            body: 요청 본문
            params: 쿼리 파라미터
            
        Returns:
            HTTP 응답
        """
        method_upper = method.upper()
        
        if method_upper == "GET":
            return await client.get(url, headers=headers, params=params)
        elif method_upper == "POST":
            return await client.post(url, content=body, headers=headers, params=params)
        elif method_upper == "PUT":
            return await client.put(url, content=body, headers=headers, params=params)
        elif method_upper == "DELETE":
            return await client.delete(url, content=body, headers=headers, params=params)
        elif method_upper == "PATCH":
            return await client.patch(url, content=body, headers=headers, params=params)
        else:
            raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
    
    def _clean_forward_headers(self, headers: dict) -> dict:
        """
        전달할 헤더 정리 (불필요한 헤더 제거)
        
        Args:
            headers: 원본 헤더
            
        Returns:
            정리된 헤더
        """
        cleaned = dict(headers)
        # 프록시에서 제거해야 할 헤더들
        cleaned.pop("host", None)
        cleaned.pop("content-length", None)
        return cleaned
    
    async def handle_cors_preflight(
        self, 
        request: Request, 
        service: str, 
        path: str
    ) -> JSONResponse:
        """
        CORS preflight 요청 처리
        
        Args:
            request: HTTP 요청 객체
            service: 대상 서비스명
            path: 요청 경로
            
        Returns:
            CORS 헤더가 포함된 응답
        """
        # CORS 설정 가져오기
        allowed_origins = [o.strip() for o in os.getenv("CORS_URL", "").split(",") if o.strip()]
        if not allowed_origins:
            allowed_origins = ["https://lca-final.vercel.app"]
        
        # Origin 확인
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
    
    async def check_all_services_health(self) -> Dict[str, Any]:
        """
        연결된 모든 서비스의 상태 확인
        
        Returns:
            각 서비스의 상태 정보
        """
        services_status = {}
        
        # Auth Service 헬스 체크
        try:
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
                "url": self._get_service_url(ServiceType.AUTH)
            }
        
        return {
            "gateway": "healthy",
            "services": services_status,
            "timestamp": "2024-01-01T00:00:00Z"
        }

# 기존 ServiceProxyFactory 클래스 (호환성을 위해 유지)
class ServiceProxyFactory:
    """기존 코드와의 호환성을 위한 ServiceProxyFactory 클래스"""
    
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
        return os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

    async def request(
        self,
        method: str,
        path: str,
        headers: dict | None = None,
        body: bytes | None = None,
        params: dict | None = None,
    ):
        # 기존 로직 유지
        clean_path = path.lstrip('/')
        url = f"{self.base_url}/{clean_path}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            m = method.upper()
            if m == "GET":
                return await client.get(url, headers=headers, params=params)
            elif m == "POST":
                return await client.post(url, content=body, headers=headers, params=params)
            elif m == "PUT":
                return await client.put(url, content=body, headers=headers, params=params)
            elif m == "DELETE":
                return await client.delete(url, content=body, headers=headers, params=params)
            elif m == "PATCH":
                return await client.patch(url, content=body, headers=headers, params=params)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
