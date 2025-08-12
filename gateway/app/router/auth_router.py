"""
Auth Router - Gateway Service
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Auth Service URL
AUTH_SERVICE_URL = "http://auth-service:8001"

@auth_router.get("/health")
async def auth_health():
    """Auth Service 헬스 체크"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/health")
            return {"status": "auth service healthy", "auth_service": response.json()}
    except Exception as e:
        logger.error(f"Auth service health check failed: {e}")
        raise HTTPException(status_code=503, detail="Auth service unavailable")

@auth_router.post("/login")
async def login(credentials: Dict[str, Any]):
    """사용자 로그인"""
    try:
        logger.info(f"로그인 요청: {credentials.get('email', 'unknown')}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/login",
                json=credentials,
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info(f"로그인 성공: {credentials.get('email', 'unknown')}")
                return response.json()
            else:
                logger.warning(f"로그인 실패: {credentials.get('email', 'unknown')} - {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get('detail', '로그인에 실패했습니다.')
                )
                
    except httpx.TimeoutException:
        logger.error("Auth service timeout")
        raise HTTPException(status_code=504, detail="Auth service timeout")
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="로그인 처리 중 오류가 발생했습니다.")

@auth_router.post("/register")
async def register(user_data: Dict[str, Any]):
    """사용자 회원가입"""
    try:
        logger.info(f"회원가입 요청: {user_data.get('email', 'unknown')}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/register",
                json=user_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info(f"회원가입 성공: {user_data.get('email', 'unknown')}")
                return response.json()
            else:
                logger.warning(f"회원가입 실패: {user_data.get('email', 'unknown')} - {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get('detail', '회원가입에 실패했습니다.')
                )
                
    except httpx.TimeoutException:
        logger.error("Auth service timeout")
        raise HTTPException(status_code=504, detail="Auth service timeout")
    except Exception as e:
        logger.error(f"Register error: {e}")
        raise HTTPException(status_code=500, detail="회원가입 처리 중 오류가 발생했습니다.")




