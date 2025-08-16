"""
프록시 컨트롤러 - HTTP 요청/응답 처리 및 프록시 로직
Gateway의 핵심 기능인 서비스 프록시를 담당

주요 기능:
- CORS preflight 요청 처리
- Gateway 헬스 체크
- 연결된 서비스들의 헬스 체크
- HTTP 메서드별 프록시 처리 (GET, POST, PUT, DELETE, PATCH)
- 에러 처리 및 로깅
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

from app.domain.service.proxy_service import ProxyService
from app.domain.schema.proxy_schema import ProxyRequest, ProxyResponse

# ============================================================================
# 🔧 로거 설정 및 기본 구성
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🚪 프록시 라우터 생성
# ============================================================================

# 프록시 라우터 생성
proxy_router = APIRouter(prefix="/api/v1", tags=["Service Proxy"])

# ============================================================================
# 🔌 의존성 주입
# ============================================================================

def get_proxy_service() -> ProxyService:
    """프록시 서비스 의존성 주입"""
    return ProxyService()

# ============================================================================
# 🌐 CORS preflight 요청 처리
# ============================================================================

@proxy_router.options("/{service}/{path:path}")
async def proxy_options(
    service: str, 
    path: str, 
    request: Request,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    CORS preflight 요청 처리
    
    Args:
        service: 대상 서비스명 (auth, user 등)
        path: 요청 경로
        request: HTTP 요청 객체
        proxy_service: 프록시 서비스 인스턴스
    
    Returns:
        CORS 헤더가 포함된 응답
    """
    try:
        return await proxy_service.handle_cors_preflight(request, service, path)
    except Exception as e:
        logger.error(f"❌ CORS preflight 처리 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="CORS 처리 중 오류가 발생했습니다")

# ============================================================================
# 🏥 헬스 체크 엔드포인트
# ============================================================================

@proxy_router.get("/gateway/health", summary="Gateway 헬스 체크")
async def gateway_health():
    """Gateway 서비스 상태 확인"""
    return {"status": "healthy", "service": "gateway", "version": "0.3.1"}

@proxy_router.get("/gateway/services/health", summary="연결된 서비스들의 헬스 체크")
async def services_health(proxy_service: ProxyService = Depends(get_proxy_service)):
    """
    연결된 모든 서비스의 상태를 확인
    
    Returns:
        각 서비스의 상태 정보
    """
    try:
        return await proxy_service.check_all_services_health()
    except Exception as e:
        logger.error(f"❌ 서비스 헬스 체크 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="서비스 상태 확인 중 오류가 발생했습니다")

# ============================================================================
# 🔄 HTTP 메서드별 프록시 처리
# ============================================================================

@proxy_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(
    service: str, 
    path: str, 
    request: Request,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    GET 요청 프록시 처리
    
    Args:
        service: 대상 서비스명
        path: 요청 경로
        request: HTTP 요청 객체
        proxy_service: 프록시 서비스 인스턴스
    
    Returns:
        대상 서비스의 응답
    """
    try:
        return await proxy_service.proxy_request("GET", service, path, request)
    except Exception as e:
        logger.exception("❌ GET 프록시 오류")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"}, 
            status_code=500
        )

@proxy_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(
    service: str, 
    path: str, 
    request: Request,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    POST 요청 프록시 처리
    
    Args:
        service: 대상 서비스명
        path: 요청 경로
        request: HTTP 요청 객체
        proxy_service: 프록시 서비스 인스턴스
    
    Returns:
        대상 서비스의 응답
    """
    try:
        logger.info(f"📝 POST 프록시 요청: service={service}, path={path}")
        return await proxy_service.proxy_request("POST", service, path, request)
    except Exception as e:
        logger.exception(f"❌ POST 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"}, 
            status_code=500
        )

@proxy_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(
    service: str, 
    path: str, 
    request: Request,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    PUT 요청 프록시 처리
    
    Args:
        service: 대상 서비스명
        path: 요청 경로
        request: HTTP 요청 객체
        proxy_service: 프록시 서비스 인스턴스
    
    Returns:
        대상 서비스의 응답
    """
    try:
        return await proxy_service.proxy_request("PUT", service, path, request)
    except Exception as e:
        logger.exception("❌ PUT 프록시 오류")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"}, 
            status_code=500
        )

@proxy_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(
    service: str, 
    path: str, 
    request: Request,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    DELETE 요청 프록시 처리
    
    Args:
        service: 대상 서비스명
        path: 요청 경로
        request: HTTP 요청 객체
        proxy_service: 프록시 서비스 인스턴스
    
    Returns:
        대상 서비스의 응답
    """
    try:
        return await proxy_service.proxy_request("DELETE", service, path, request)
    except Exception as e:
        logger.exception("❌ DELETE 프록시 오류")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"}, 
            status_code=500
        )

@proxy_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(
    service: str, 
    path: str, 
    request: Request,
    proxy_service: ProxyService = Depends(get_proxy_service)
):
    """
    PATCH 요청 프록시 처리
    
    Args:
        service: 대상 서비스명
        path: 요청 경로
        request: HTTP 요청 객체
        proxy_service: 프록시 서비스 인스턴스
    
    Returns:
        대상 서비스의 응답
    """
    try:
        return await proxy_service.proxy_request("PATCH", service, path, request)
    except Exception as e:
        logger.exception("❌ PATCH 프록시 오류")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"}, 
            status_code=500
        )
