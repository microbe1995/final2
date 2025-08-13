"""
인증 서비스
"""
import os
import logging
import hashlib
import secrets
from typing import Optional

from domain.entity.user_entity import UserEntity
from domain.model.auth_model import UserCreateModel, UserLoginModel
from domain.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)

class AuthService:
    """인증 서비스 클래스"""
    
    def __init__(self):
        self.user_repository = UserRepository()
    
    def _hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        try:
            salt, hash_value = hashed.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return hash_obj.hex() == hash_value
        except Exception as e:
            logger.error(f"비밀번호 검증 중 오류: {e}")
            return False
    
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
        
        # 비밀번호 해싱
        password_hash = self._hash_password(user_data.password)
        
        # 사용자 엔티티 생성
        user = UserEntity(
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash,
            full_name=user_data.full_name,
            is_active=True
        )
        
        # 저장
        saved_user = self.user_repository.save(user)
        logger.info(f"회원가입 성공: {saved_user.email}")
        
        return saved_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """사용자 인증"""
        logger.info(f"로그인 시도: {email}")
        
        # 사용자 조회
        user = self.user_repository.find_by_email(email)
        if not user:
            logger.warning(f"사용자 없음: {email}")
            return None
        
        # 비밀번호 확인
        if not self._verify_password(password, user.password_hash):
            logger.warning(f"비밀번호 불일치: {email}")
            return None
        
        logger.info(f"로그인 성공: {email}")
        return "success"
