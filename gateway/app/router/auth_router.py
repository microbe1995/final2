"""
Auth Router - Gateway Service
"""
import os
import logging
import json
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import httpx

try:
    from ..domain.auth.controller.auth_controller import AuthController
    from ..domain.auth.model.auth_model import UserRegisterRequest, UserRegisterResponse, UserLoginRequest
except ImportError:
    # Docker 환경에서 절대 경로로 import 시도
    from app.domain.auth.controller.auth_controller import AuthController
    from app.domain.auth.model.auth_model import UserRegisterRequest, UserRegisterResponse, UserLoginRequest

logger = logging.getLogger(__name__)
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Auth Service URL - Railway 환경에 맞게 수정
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

# 로컬 인증 컨트롤러 (테스트용)
auth_controller = AuthController()

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
        
        # 로컬 컨트롤러 사용 (테스트용)
        try:
            result = await auth_controller.login_user(credentials.dict())
            logger.info(f"로컬 로그인 성공: {credentials.email}")
            return result
        except Exception as local_error:
            logger.warning(f"로컬 로그인 실패, 외부 서비스 시도: {local_error}")
        
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
    """사용자 회원가입"""
    logger.info(f"🔵 /register 엔드포인트 호출됨")
    return await register_local(user_data)

@auth_router.post("/register/local")
async def register_local(user_data: UserRegisterRequest):
    """사용자 회원가입 (로컬)"""
    logger.info(f"🔵 /register/local 엔드포인트 호출됨")
    try:
        # 로깅: 라우터에서 받은 회원가입 요청
        logger.info(f"라우터 회원가입 요청: {json.dumps(user_data.dict(), ensure_ascii=False)}")
        
        # 로컬 컨트롤러 사용 (테스트용)
        try:
            logger.info(f"🔵 로컬 컨트롤러로 회원가입 시도")
            result = await auth_controller.register_user(user_data)
            logger.info(f"✅ 로컬 회원가입 성공: {user_data.email}")
            return result
        except Exception as local_error:
            logger.error(f"❌ 로컬 회원가입 실패: {str(local_error)}")
            logger.error(f"❌ 에러 타입: {type(local_error).__name__}")
            logger.error(f"❌ 에러 상세: {local_error}")
            raise HTTPException(status_code=500, detail=f"로컬 회원가입 실패: {str(local_error)}")
        
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

@auth_router.post("/register/local")
async def register_local(user_data: UserRegisterRequest):
    """로컬 회원가입 (테스트용)"""
    try:
        logger.info(f"로컬 회원가입 요청: {json.dumps(user_data.dict(), ensure_ascii=False)}")
        result = await auth_controller.register_user(user_data)
        logger.info(f"로컬 회원가입 완료: {json.dumps(result.dict(), ensure_ascii=False)}")
        return result
    except Exception as e:
        logger.error(f"로컬 회원가입 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.post("/login/local")
async def login_local(credentials: UserLoginRequest):
    """로컬 로그인 (테스트용)"""
    try:
        masked_credentials = {**credentials.dict(), 'password': '***'}
        logger.info(f"로컬 로그인 요청: {json.dumps(masked_credentials, ensure_ascii=False)}")
        result = await auth_controller.login_user(credentials.dict())
        if result:
            logger.info(f"로컬 로그인 성공: {credentials.email}")
            return result
        else:
            logger.warning(f"로컬 로그인 실패: {credentials.email}")
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    except Exception as e:
        logger.error(f"로컬 로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




