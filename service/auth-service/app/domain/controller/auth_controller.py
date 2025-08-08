"""
인증 컨트롤러
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from domain.model.auth_model import UserCreateModel, UserLoginModel, UserResponseModel, TokenModel
from domain.service.auth_service import AuthService

logger = logging.getLogger(__name__)
security = HTTPBearer()

class AuthController:
    """인증 컨트롤러 클래스"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    async def register_user(self, user_data: UserCreateModel) -> UserResponseModel:
        """사용자 회원가입"""
        try:
            logger.info(f"회원가입 요청: {user_data.email}")
            
            # 사용자 생성
            user = await self.auth_service.create_user(user_data)
            
            # 응답 생성
            response_data = self.auth_service.create_user_response(user)
            logger.info(f"회원가입 성공: {user.email}")
            
            return UserResponseModel(**response_data)
            
        except ValueError as e:
            logger.error(f"회원가입 실패: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"회원가입 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다.")
    
    async def login_user(self, user_credentials: UserLoginModel) -> TokenModel:
        """사용자 로그인"""
        try:
            logger.info(f"로그인 시도: {user_credentials.email}")
            
            # 사용자 인증
            access_token = await self.auth_service.authenticate_user(
                user_credentials.email, 
                user_credentials.password
            )
            
            if not access_token:
                logger.warning(f"로그인 실패: {user_credentials.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="이메일 또는 비밀번호가 올바르지 않습니다.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 토큰 응답 생성
            token_response = self.auth_service.create_token_response(access_token)
            logger.info(f"로그인 성공: {user_credentials.email}")
            
            return token_response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"로그인 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다.")
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponseModel:
        """현재 사용자 정보 조회"""
        try:
            logger.info("현재 사용자 정보 조회 요청")
            
            # 토큰에서 사용자 조회
            user = await self.auth_service.get_current_user(credentials.credentials)
            
            if not user:
                logger.warning("유효하지 않은 토큰")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 응답 생성
            response_data = self.auth_service.create_user_response(user)
            logger.info(f"사용자 정보 조회 성공: {user.email}")
            
            return UserResponseModel(**response_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"사용자 정보 조회 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="사용자 정보 조회 중 오류가 발생했습니다.")
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """JWT 토큰 검증"""
        try:
            logger.info("토큰 검증 요청")
            
            # 토큰 검증
            token_data = self.auth_service.verify_token(credentials.credentials)
            
            if not token_data:
                logger.warning("토큰 검증 실패")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # 사용자 존재 확인
            user = await self.auth_service.get_current_user(credentials.credentials)
            if not user:
                logger.warning("토큰에 해당하는 사용자가 없음")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="유효하지 않은 토큰입니다.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            logger.info(f"토큰 검증 성공: {user.email}")
            return {
                "valid": True,
                "user_id": user.id,
                "email": user.email,
                "username": user.username
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"토큰 검증 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="토큰 검증 중 오류가 발생했습니다.")
