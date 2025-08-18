"""
인증 컨트롤러 - HTTP 요청/응답 처리
인증 서비스의 HTTP 엔드포인트를 담당

주요 기능:
- 사용자 회원가입 (/auth/register)
- 사용자 로그인 (/auth/login)
- 사용자 정보 조회 (/auth/user/{user_id})
- 사용자 정보 수정 (/auth/user/{user_id})
- 사용자 삭제 (/auth/user/{user_id})
- 서비스 헬스 체크 (/auth/health)
- 에러 처리 및 로깅
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from app.domain.user.user_service import AuthService
from app.domain.user.user_repository import UserRepository
from app.domain.user.user_schema import (
    UserRegistrationRequest,
    UserLoginRequest,
    UserUpdateRequest,
    PasswordChangeRequest,
    UserDeleteRequest,
    AuthResponse,
    UserResponse,
    MessageResponse,
)

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🚀 라우터 생성
# ============================================================================

auth_router = APIRouter(prefix="/auth", tags=["인증"])

# ============================================================================
# 🔧 의존성 주입
# ============================================================================

def get_user_repository() -> UserRepository:
    """사용자 저장소 의존성 주입"""
    try:
        repository = UserRepository()
        logger.info("✅ UserRepository 의존성 주입 성공")
        return repository
    except Exception as e:
        logger.error(f"❌ UserRepository 의존성 주입 실패: {str(e)}")
        raise

def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    """인증 서비스 의존성 주입"""
    try:
        service = AuthService(user_repository)
        logger.info("✅ AuthService 의존성 주입 성공")
        return service
    except Exception as e:
        logger.error(f"❌ AuthService 의존성 주입 실패: {str(e)}")
        raise

# 전역 변수로 현재 로그인한 사용자 ID 저장 (임시 구현)
_current_user_id = None

def get_current_user_id() -> str:
    """현재 인증된 사용자 ID 반환 (임시 구현)"""
    global _current_user_id
    if _current_user_id is None:
        # TODO: JWT 토큰에서 실제 사용자 ID 추출
        # 현재는 테스트용으로 하드코딩된 값 반환
        _current_user_id = "test-user-id-12345"
    return _current_user_id

def set_current_user_id(user_id: str):
    """현재 로그인한 사용자 ID 설정"""
    global _current_user_id
    _current_user_id = user_id

# ============================================================================
# 🔍 디버깅 엔드포인트
# ============================================================================

@auth_router.get("/debug/users", response_model=dict)
async def debug_users(auth_service: AuthService = Depends(get_auth_service)):
    """데이터베이스에 저장된 사용자 목록 조회 (디버깅용)"""
    try:
        logger.info("🔍 디버깅: 사용자 목록 조회 요청")
        
        # 모든 사용자 조회
        users = await auth_service.get_all_users()
        
        # 사용자 정보 정리 (비밀번호 제외)
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            })
        
        logger.info(f"✅ 디버깅: {len(user_list)}명의 사용자 발견")
        return {
            "total_users": len(user_list),
            "users": user_list
        }
        
    except Exception as e:
        logger.error(f"❌ 디버깅: 사용자 목록 조회 실패 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 목록 조회 실패: {str(e)}"
        )

@auth_router.get("/debug/db-status", response_model=dict)
async def debug_database_status():
    """데이터베이스 연결 상태 확인 (디버깅용)"""
    try:
        logger.info("🔍 디버깅: 데이터베이스 상태 확인 요청")
        
        from app.common.database.database import database
        
        # 데이터베이스 연결 상태 확인
        db_status = {
            "database_url_set": bool(database.database_url),
            "database_url_preview": database.database_url[:50] + "..." if database.database_url else None,
            "engine_available": bool(database.engine),
            "async_engine_available": bool(database.async_engine),
            "railway_environment": os.getenv("RAILWAY_ENVIRONMENT") == "true",
            "railway_project_id": os.getenv("RAILWAY_PROJECT_ID"),
            "railway_service_id": os.getenv("RAILWAY_SERVICE_ID")
        }
        
        # 테이블 존재 여부 확인
        if database.engine:
            try:
                with database.engine.connect() as conn:
                    result = conn.execute(text("SELECT COUNT(*) FROM users"))
                    user_count = result.scalar()
                    db_status["users_table_exists"] = True
                    db_status["total_users"] = user_count
            except Exception as e:
                db_status["users_table_exists"] = False
                db_status["table_error"] = str(e)
        else:
            db_status["users_table_exists"] = False
            db_status["table_error"] = "엔진이 사용할 수 없음"
        
        logger.info(f"✅ 디버깅: 데이터베이스 상태 확인 완료")
        return db_status
        
    except Exception as e:
        logger.error(f"❌ 디버깅: 데이터베이스 상태 확인 실패 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터베이스 상태 확인 실패: {str(e)}"
        )

# ============================================================================
# 📝 회원가입 엔드포인트
# ============================================================================

@auth_router.post("/register", response_model=AuthResponse)
async def register_user(request: UserRegistrationRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    사용자 회원가입
    
    - **email**: 사용자 이메일 (고유 식별자)
    - **full_name**: 사용자 실명
    - **password**: 비밀번호 (최소 6자)
    - **confirm_password**: 비밀번호 확인
    
    Returns:
        - user: 생성된 사용자 정보
        - token: 인증 토큰
    """
    try:
        logger.info(f"🔐 회원가입 요청: {request.email}")
        
        user, token = await auth_service.register_user(request)
        
        logger.info(f"✅ 회원가입 성공: {request.email}")
        
        # 현재 로그인한 사용자 ID 저장
        set_current_user_id(user.id)
        
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            ),
            token=token
        )
        
    except ValueError as e:
        logger.warning(f"❌ 회원가입 실패: {request.email} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ 회원가입 오류: {request.email} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 중 오류가 발생했습니다"
        )

# ============================================================================
# 🔑 로그인 엔드포인트
# ============================================================================

@auth_router.post("/login", response_model=AuthResponse)
async def login_user(request: UserLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """
    사용자 로그인
    
    - **email**: 사용자 이메일
    - **password**: 사용자 비밀번호
    
    Returns:
        - user: 사용자 정보
        - token: 인증 토큰
    """
    try:
        logger.info(f"🔑 로그인 요청: {request.email}")
        
        user, token = await auth_service.login_user(request)
        
        logger.info(f"✅ 로그인 성공: {request.email}")
        
        # 현재 로그인한 사용자 ID 저장
        set_current_user_id(user.id)
        
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            ),
            token=token
        )
        
    except ValueError as e:
        logger.warning(f"❌ 로그인 실패: {request.email} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ 로그인 오류: {request.email} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 중 오류가 발생했습니다"
        )

# ============================================================================
# ✏️ 회원 정보 관리 엔드포인트
# ============================================================================

@auth_router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    request: UserUpdateRequest,
    user_id: str = Depends(get_current_user_id),  # 인증 의존성 적용
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    회원 정보 수정
    
    - **full_name**: 새 전체 이름 (선택사항)
    - **email**: 새 이메일 (선택사항, 중복 체크 포함)
    """
    try:
        logger.info(f"✏️ 회원 정보 수정 요청: {user_id}")
        
        user = await auth_service.update_user_info(user_id, request)
        
        logger.info(f"✅ 회원 정보 수정 성공: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        
    except ValueError as e:
        logger.warning(f"❌ 회원 정보 수정 실패: {user_id} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ 회원 정보 수정 오류: {user_id} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원 정보 수정 중 오류가 발생했습니다"
        )

@auth_router.put("/password", response_model=MessageResponse)
async def change_password(
    request: PasswordChangeRequest,
    user_id: str = Depends(get_current_user_id),  # 인증 의존성 적용
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    비밀번호 변경
    
    - **current_password**: 현재 비밀번호
    - **new_password**: 새 비밀번호 (최소 6자)
    - **confirm_new_password**: 새 비밀번호 확인
    """
    try:
        logger.info(f"🔑 비밀번호 변경 요청: {user_id}")
        
        success = await auth_service.change_password(user_id, request)
        
        if success:
            logger.info(f"✅ 비밀번호 변경 성공: {user_id}")
            return MessageResponse(
                message="비밀번호가 성공적으로 변경되었습니다"
            )
        else:
            logger.warning(f"❌ 비밀번호 변경 실패: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호 변경에 실패했습니다"
            )
        
    except ValueError as e:
        logger.warning(f"❌ 비밀번호 변경 실패: {user_id} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ 비밀번호 변경 오류: {user_id} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="비밀번호 변경 중 오류가 발생했습니다"
        )

# ============================================================================
# 🗑️ 회원 탈퇴 엔드포인트
# ============================================================================

@auth_router.delete("/profile", response_model=MessageResponse)
async def delete_user_profile(
    request: UserDeleteRequest,
    user_id: str = Depends(get_current_user_id),  # 인증 의존성 적용
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    회원 탈퇴
    
    - **password**: 계정 삭제를 위한 비밀번호 확인
    """
    try:
        logger.info(f"🗑️ 회원 탈퇴 요청: {user_id}")
        
        await auth_service.delete_user(user_id, request)
        
        logger.info(f"✅ 회원 탈퇴 성공: {user_id}")
        
        return MessageResponse(
            message="계정이 성공적으로 삭제되었습니다"
        )
        
    except ValueError as e:
        logger.warning(f"❌ 회원 탈퇴 실패: {user_id} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ 회원 탈퇴 오류: {user_id} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원 탈퇴 중 오류가 발생했습니다"
        )

# ============================================================================
# 🔍 사용자 정보 조회 엔드포인트
# ============================================================================

@auth_router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    user_id: str = Depends(get_current_user_id),  # 인증 의존성 적용
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    회원 정보 조회
    """
    try:
        logger.info(f"🔍 회원 정보 조회 요청: {user_id}")
        
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        logger.info(f"✅ 회원 정보 조회 성공: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 회원 정보 조회 오류: {user_id} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원 정보 조회 중 오류가 발생했습니다"
        )

# ============================================================================
# 🔍 중복 체크 엔드포인트
# ============================================================================

@auth_router.get("/check/email/{email}")
async def check_email_availability(
    email: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    이메일 중복 체크
    
    - **email**: 확인할 이메일 주소
    
    Returns:
        - available: true (사용 가능) / false (이미 사용 중)
        - message: 상태 메시지
    """
    try:
        logger.info(f"🔍 이메일 중복 체크 요청: {email}")
        
        # 이메일 유효성 검증 (Pydantic 2.x 호환)
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            logger.warning(f"⚠️ 이메일 형식 오류: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="올바른 이메일 형식이 아닙니다"
            )
        
        # 중복 확인 (AuthService를 통해)
        existing_user = await auth_service.user_repository.get_user_by_email(email)
        
        if existing_user:
            logger.info(f"❌ 이메일 중복: {email}")
            return {
                "available": False,
                "message": f"이메일 '{email}'은 이미 사용 중입니다"
            }
        else:
            logger.info(f"✅ 이메일 사용 가능: {email}")
            return {
                "available": True,
                "message": f"이메일 '{email}'은 사용 가능합니다"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 이메일 중복 체크 오류: {email} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="이메일 중복 체크 중 오류가 발생했습니다"
        )

# ============================================================================
# 🏥 헬스 체크 엔드포인트
# ============================================================================

@auth_router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "auth-service"}
