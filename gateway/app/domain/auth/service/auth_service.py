import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib
import secrets

from ..entity.auth_entity import User
from ..model.auth_model import UserRegisterRequest, UserRegisterResponse

logger = logging.getLogger(__name__)

class AuthService:
    """인증 서비스"""
    
    def __init__(self):
        # 임시 사용자 저장소 (실제로는 데이터베이스 사용)
        self.users: Dict[str, User] = {}
        logger.info("AuthService 초기화 완료")
    
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
    
    def register_user(self, user_data: UserRegisterRequest) -> UserRegisterResponse:
        """사용자 회원가입"""
        try:
            # 로깅: 회원가입 요청 데이터
            logger.info(f"회원가입 요청 시작: {json.dumps(user_data.dict(), ensure_ascii=False)}")
            
            # 이메일 중복 확인
            if any(user.email == user_data.email for user in self.users.values()):
                logger.warning(f"이메일 중복: {user_data.email}")
                raise ValueError("이미 등록된 이메일입니다.")
            
            # 사용자명 중복 확인
            if any(user.username == user_data.username for user in self.users.values()):
                logger.warning(f"사용자명 중복: {user_data.username}")
                raise ValueError("이미 사용 중인 사용자명입니다.")
            
            # 비밀번호 해싱
            password_hash = self._hash_password(user_data.password)
            
            # 사용자 엔티티 생성
            user = User(
                email=user_data.email,
                username=user_data.username,
                password_hash=password_hash,
                full_name=user_data.full_name
            )
            
            # 사용자 저장
            self.users[user.id] = user
            
            # 응답 생성
            response = UserRegisterResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                created_at=user.created_at,
                message="회원가입이 성공적으로 완료되었습니다."
            )
            
            # 로깅: 회원가입 성공 응답
            logger.info(f"회원가입 성공: {json.dumps(response.dict(), ensure_ascii=False)}")
            
            return response
            
        except ValueError as ve:
            logger.error(f"회원가입 검증 오류: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"회원가입 처리 중 오류: {str(e)}")
            raise
    
    def login_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """사용자 로그인"""
        try:
            logger.info(f"로그인 시도: {email}")
            
            # 사용자 찾기
            user = next((u for u in self.users.values() if u.email == email), None)
            if not user:
                logger.warning(f"존재하지 않는 이메일: {email}")
                return None
            
            # 비밀번호 검증
            if not self._verify_password(password, user.password_hash):
                logger.warning(f"잘못된 비밀번호: {email}")
                return None
            
            # 로그인 성공
            logger.info(f"로그인 성공: {email}")
            return {
                "user": user.to_dict(),
                "message": "로그인이 성공했습니다."
            }
            
        except Exception as e:
            logger.error(f"로그인 처리 중 오류: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return next((u for u in self.users.values() if u.email == email), None) 