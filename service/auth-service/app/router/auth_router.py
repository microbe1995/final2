"""
Auth Router - Auth Service
"""
from fastapi import APIRouter, Depends
from domain.model.auth_model import UserCreateModel, UserLoginModel, UserResponseModel, TokenModel
from domain.controller.auth_controller import AuthController

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
    return await auth_controller.register_user(user_data)

@auth_router.post("/login", response_model=TokenModel)
async def login_user(user_credentials: UserLoginModel):
    """사용자 로그인"""
    return await auth_controller.login_user(user_credentials)

@auth_router.get("/me", response_model=UserResponseModel)
async def get_current_user():
    """현재 사용자 정보 조회"""
    return await auth_controller.get_current_user()

@auth_router.post("/verify-token")
async def verify_token():
    """JWT 토큰 검증"""
    return await auth_controller.verify_token()
