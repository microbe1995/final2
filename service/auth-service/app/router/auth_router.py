"""
Auth Service 라우터 - 모든 인증 관련 엔드포인트
"""
from fastapi import APIRouter, Request
import logging

logger = logging.getLogger("auth_service_router")

# Auth 라우터 생성
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

@auth_router.get("/")
async def root():
    """루트 엔드포인트"""
    logger.info("🔵 /auth 엔드포인트 호출됨")
    return {
        "message": "Auth Service Router", 
        "version": "1.0.0", 
        "status": "running",
        "docs": "/docs",
        "mode": "sub-router"
    }

@auth_router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    logger.info("🔵 /auth/health 엔드포인트 호출됨")
    return {"status": "healthy", "service": "auth", "mode": "sub-router"}

@auth_router.get("/register")
async def register_page():
    """회원가입 페이지 정보"""
    logger.info("🔵 /auth/register 페이지 정보 요청됨")
    return {
        "message": "회원가입 페이지",
        "endpoint": "POST /auth/register",
        "service": "auth-service"
    }

@auth_router.get("/login")
async def login_page():
    """로그인 페이지 정보"""
    logger.info("🔵 /auth/login 페이지 정보 요청됨")
    return {
        "message": "로그인 페이지", 
        "endpoint": "POST /auth/login",
        "service": "auth-service"
    }

@auth_router.post("/register")
async def register_user(request: Request):
    """사용자 회원가입 - 직접 요청 또는 Gateway에서 프록시된 요청"""
    logger.info("🔵 /auth/register 엔드포인트 호출됨")
    
    try:
        # JSON 데이터 파싱
        user_data = await request.json()
        logger.info(f"🔵 받은 데이터: {user_data}")
        
        # 간단한 응답 (실제로는 데이터베이스 처리)
        username = user_data.get('username', 'unknown')
        email = user_data.get('email', 'unknown')
        full_name = user_data.get('full_name', 'unknown')
        
        logger.info(f"✅ 회원가입 성공: {email}")
        return {
            "message": "회원가입 성공",
            "user": {
                "username": username,
                "email": email,
                "full_name": full_name,
                "id": "temp_id_123"  # 임시 ID
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ 회원가입 실패: {str(e)}")
        return {"error": f"회원가입 실패: {str(e)}", "status": "error"}

@auth_router.post("/login")
async def login_user(request: Request):
    """사용자 로그인 - 직접 요청 또는 Gateway에서 프록시된 요청"""
    logger.info("🔵 /auth/login 엔드포인트 호출됨")
    
    try:
        # JSON 데이터 파싱
        user_credentials = await request.json()
        logger.info(f"🔵 받은 데이터: {user_credentials}")
        
        # 간단한 응답 (실제로는 인증 처리)
        email = user_credentials.get('email', 'unknown')
        
        logger.info(f"✅ 로그인 성공: {email}")
        return {
            "message": "로그인 성공",
            "user": {
                "email": email,
                "token": "temp_token_123"  # 임시 토큰
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ 로그인 실패: {str(e)}")
        return {"error": f"로그인 실패: {str(e)}", "status": "error"}

# 추가 인증 관련 엔드포인트들
@auth_router.get("/profile")
async def get_profile():
    """사용자 프로필 정보 (예시)"""
    logger.info("🔵 /auth/profile 엔드포인트 호출됨")
    return {
        "message": "사용자 프로필",
        "endpoint": "GET /auth/profile",
        "service": "auth-service"
    }

@auth_router.post("/logout")
async def logout():
    """사용자 로그아웃 (예시)"""
    logger.info("🔵 /auth/logout 엔드포인트 호출됨")
    return {
        "message": "로그아웃 성공",
        "status": "success"
    }

@auth_router.get("/verify")
async def verify_token():
    """토큰 검증 (예시)"""
    logger.info("🔵 /auth/verify 엔드포인트 호출됨")
    return {
        "message": "토큰 검증",
        "endpoint": "GET /auth/verify",
        "service": "auth-service"
    }
