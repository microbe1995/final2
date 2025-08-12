"""
인증 서비스 (JWT 제거 버전)
"""
import os
import logging
from typing import Optional

from domain.entity.user_entity import UserEntity
from domain.model.auth_model import UserCreateModel, UserLoginModel
from domain.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)

class AuthService:
    """인증 서비스 클래스 (JWT 제거)"""
    
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def create_user(self, user_data: UserCreateModel) -> UserEntity:
        """사용자 생성"""
        logger.info(f"회원가입 요청: {user_data.email}")
        
        # 이메일 중복 확인
        if self.user_repository.exists_by_email(user_data.email):
            logger.warning(f"이메일 중복: {user_data.email}")
            raise ValueError("이미 존재하는 이메일입니다.")
        
        # 사용자명 중복 확인
        if self.user_repository.exists_by_username(user_data.username):
            logger.warning(f"사용자명 중복: {user_data.username}")
            raise ValueError("이미 존재하는 사용자명입니다.")
        
        # 사용자 엔티티 생성 (비밀번호는 평문으로 저장 - 개발용)
        user = UserEntity(
            email=user_data.email,
            username=user_data.username,
            hashed_password=user_data.password,  # 개발용으로 평문 저장
            is_active=True
        )
        
        # 저장
        saved_user = self.user_repository.save(user)
        logger.info(f"회원가입 성공: {saved_user.email}")
        
        return saved_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """사용자 인증 (JWT 제거)"""
        logger.info(f"로그인 시도: {email}")
        
        # 사용자 조회
        user = self.user_repository.find_by_email(email)
        if not user:
            logger.warning(f"사용자 없음: {email}")
            return None
        
        # 비밀번호 확인 (개발용으로 평문 비교)
        if user.hashed_password != password:
            logger.warning(f"비밀번호 불일치: {email}")
            return None
        
        logger.info(f"로그인 성공: {email}")
        return "success"  # JWT 대신 간단한 성공 메시지
