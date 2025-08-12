"""
Auth Router - Auth Service (JWT 제거 버전)
"""
from fastapi import APIRouter
from domain.model.auth_model import UserCreateModel, UserLoginModel, UserResponseModel
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

@auth_router.post("/login")
async def login_user(user_credentials: UserLoginModel):
    """사용자 로그인 (JWT 제거)"""
    return await auth_controller.login_user(user_credentials)
