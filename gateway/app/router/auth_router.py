"""
Auth Router - Gateway Service
"""
import os
import logging
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import httpx

# Railway 환경에서는 절대 경로로 import
if os.getenv("RAILWAY_ENVIRONMENT") == "true":
    from domain.auth.model.auth_model import UserLoginRequest, UserRegisterRequest
else:
    # 로컬 개발 환경에서는 상대 경로로 import
    try:
        from ..domain.auth.model.auth_model import UserLoginRequest, UserRegisterRequest
    except ImportError:
        from domain.auth.model.auth_model import UserLoginRequest, UserRegisterRequest

logger = logging.getLogger(__name__)
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Auth Service URL - Railway 환경에 맞게 수정
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

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
async def login(credentials: UserLoginRequest):
    """사용자 로그인"""
    try:
        # 로깅: 라우터에서 받은 로그인 요청
        masked_credentials = {**credentials.dict(), 'password': '***'}
        logger.info(f"라우터 로그인 요청: {json.dumps(masked_credentials, ensure_ascii=False)}")
        
        # 외부 Auth Service 사용
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/login",
                json=credentials.dict(),
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"외부 서비스 로그인 성공: {credentials.email}")
                return result
            else:
                logger.warning(f"외부 서비스 로그인 실패: {credentials.email} - {response.status_code}")
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
async def register(user_data: UserRegisterRequest):
    """사용자 회원가입 - Auth Service로 위임"""
    try:
        logger.info(f"🔵 /register 엔드포인트 호출됨 (Auth Service로 위임)")
        
        # 외부 Auth Service 사용
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/register",
                json=user_data.dict(),
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"외부 서비스 회원가입 성공: {user_data.email}")
                return result
            else:
                logger.warning(f"외부 서비스 회원가입 실패: {user_data.email} - {response.status_code}")
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




