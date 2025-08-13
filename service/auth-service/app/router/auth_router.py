"""
Auth Router - Auth Service
"""
import logging
import json
from fastapi import APIRouter, HTTPException
from domain.model.auth_model import UserCreateModel, UserLoginModel, UserResponseModel
from domain.controller.auth_controller import AuthController

logger = logging.getLogger(__name__)
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# 컨트롤러 인스턴스
auth_controller = AuthController()

@auth_router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "auth"}

@auth_router.post("/register", response_model=UserResponseModel)
async def register_user(user_data: UserCreateModel):
    """사용자 회원가입"""
    logger.info(f"🔵 /register 엔드포인트 호출됨")
    try:
        # 로깅: 라우터에서 받은 회원가입 요청
        logger.info(f"라우터 회원가입 요청: {json.dumps(user_data.dict(), ensure_ascii=False)}")
        
        result = await auth_controller.register_user(user_data)
        logger.info(f"✅ 회원가입 성공: {user_data.email}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 회원가입 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {str(e)}")

@auth_router.post("/login")
async def login_user(user_credentials: UserLoginModel):
    """사용자 로그인"""
    try:
        # 로깅: 라우터에서 받은 로그인 요청
        masked_credentials = {**user_credentials.dict(), 'password': '***'}
        logger.info(f"라우터 로그인 요청: {json.dumps(masked_credentials, ensure_ascii=False)}")
        
        result = await auth_controller.login_user(user_credentials)
        logger.info(f"로그인 성공: {user_credentials.email}")
        return result
        
    except Exception as e:
        logger.error(f"로그인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"로그인 실패: {str(e)}")
