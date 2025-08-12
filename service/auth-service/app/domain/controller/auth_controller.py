"""
인증 컨트롤러 (JWT 제거 버전)
"""
from fastapi import HTTPException, status
import logging

from domain.model.auth_model import UserCreateModel, UserLoginModel, UserResponseModel
from domain.service.auth_service import AuthService

logger = logging.getLogger(__name__)

class AuthController:
    """인증 컨트롤러 클래스 (JWT 제거)"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    async def register_user(self, user_data: UserCreateModel) -> UserResponseModel:
        """사용자 회원가입"""
        try:
            logger.info(f"회원가입 요청: {user_data.email}")
            
            # 사용자 생성
            user = await self.auth_service.create_user(user_data)
            
            # 응답 생성
            response_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            
            logger.info(f"회원가입 성공: {user.email}")
            return UserResponseModel(**response_data)
            
        except ValueError as e:
            logger.error(f"회원가입 실패: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"회원가입 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다.")
    
    async def login_user(self, user_credentials: UserLoginModel) -> dict:
        """사용자 로그인 (JWT 제거)"""
        try:
            logger.info(f"로그인 시도: {user_credentials.email}")
            
            # 사용자 인증
            result = await self.auth_service.authenticate_user(
                user_credentials.email, 
                user_credentials.password
            )
            
            if not result:
                logger.warning(f"로그인 실패: {user_credentials.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="이메일 또는 비밀번호가 올바르지 않습니다."
                )
            
            logger.info(f"로그인 성공: {user_credentials.email}")
            return {"message": "로그인 성공", "status": "success"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"로그인 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다.")
