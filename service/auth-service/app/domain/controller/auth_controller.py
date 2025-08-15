"""
인증 컨트롤러 - HTTP 요청/응답 처리
인증 서비스의 HTTP 엔드포인트를 담당
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging

from ..service.auth_service import AuthService
from ..schema.auth_schema import (
    UserRegistrationRequest, UserLoginRequest,
    UserRegistrationResponse, UserLoginResponse,
    ErrorResponse, HealthResponse
)

# 로거 설정
logger = logging.getLogger(__name__)

# 인증 라우터 생성
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# 의존성 주입
def get_auth_service() -> AuthService:
    """인증 서비스 의존성 주입"""
    return AuthService()

@auth_router.post("/register", response_model=UserRegistrationResponse, summary="사용자 회원가입")
async def register_user(
    registration_data: UserRegistrationRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    사용자 회원가입
    
    Args:
        registration_data: 회원가입 요청 데이터
        auth_service: 인증 서비스 인스턴스
    
    Returns:
        회원가입 결과
    """
    try:
        logger.info(f"🔐 회원가입 요청: {registration_data.email}")
        
        # 회원가입 처리
        result = await auth_service.register_user(registration_data)
        
        if result["status"] == "success":
            logger.info(f"✅ 회원가입 성공: {registration_data.email}")
            return UserRegistrationResponse(**result)
        else:
            logger.warning(f"❌ 회원가입 실패: {registration_data.email}")
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "회원가입에 실패했습니다")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 회원가입 처리 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다"
        )

@auth_router.post("/login", response_model=UserLoginResponse, summary="사용자 로그인")
async def login_user(
    login_data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    사용자 로그인
    
    Args:
        login_data: 로그인 요청 데이터
        auth_service: 인증 서비스 인스턴스
    
    Returns:
        로그인 결과
    """
    try:
        logger.info(f"🔐 로그인 요청: {login_data.email}")
        
        # 로그인 처리
        result = await auth_service.login_user(login_data)
        
        if result["status"] == "success":
            logger.info(f"✅ 로그인 성공: {login_data.email}")
            return UserLoginResponse(**result)
        else:
            logger.warning(f"❌ 로그인 실패: {login_data.email}")
            raise HTTPException(
                status_code=401,
                detail=result.get("error", "로그인에 실패했습니다")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 로그인 처리 중 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다"
        )

@auth_router.get("/users/count", summary="등록된 사용자 수 조회")
async def get_users_count(
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    등록된 사용자 수 조회
    
    Args:
        auth_service: 인증 서비스 인스턴스
    
    Returns:
        사용자 수
    """
    try:
        count = await auth_service.get_users_count()
        return {"users_count": count, "status": "success"}
        
    except Exception as e:
        logger.error(f"❌ 사용자 수 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="사용자 수 조회 중 오류가 발생했습니다"
        )

@auth_router.get("/users/search", summary="사용자 검색")
async def search_users(
    query: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    사용자 검색
    
    Args:
        query: 검색 쿼리
        auth_service: 인증 서비스 인스턴스
    
    Returns:
        검색 결과 사용자 목록
    """
    try:
        users = await auth_service.search_users(query)
        return {
            "users": [user.to_dict() for user in users],
            "count": len(users),
            "query": query,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ 사용자 검색 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="사용자 검색 중 오류가 발생했습니다"
        )

@auth_router.get("/health", response_model=HealthResponse, summary="인증 서비스 헬스 체크")
async def health_check():
    """인증 서비스 상태 확인"""
    return HealthResponse(
        status="healthy",
        service="auth",
        version="1.0.0"
    )

@auth_router.get("/", summary="인증 서비스 루트")
async def root():
    """인증 서비스 루트 엔드포인트"""
    return {
        "message": "Auth Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "register": "/auth/register",
            "login": "/auth/login",
            "health": "/auth/health",
            "users_count": "/auth/users/count",
            "users_search": "/auth/users/search"
        }
    }
