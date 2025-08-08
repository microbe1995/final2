"""
인증 서비스
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from domain.entity.user_entity import UserEntity
from domain.model.auth_model import UserCreateModel, UserLoginModel, TokenModel, TokenDataModel
from domain.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)

class AuthService:
    """인증 서비스 클래스"""
    
    def __init__(self):
        self.user_repository = UserRepository()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # JWT 설정
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """비밀번호 해시화"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenDataModel]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if email is None or user_id is None:
                return None
            
            return TokenDataModel(email=email, user_id=user_id)
        except JWTError:
            return None
    
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
        
        # 비밀번호 해시화
        hashed_password = self.get_password_hash(user_data.password)
        
        # 사용자 엔티티 생성
        user = UserEntity(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
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
            logger.warning(f"사용자를 찾을 수 없음: {email}")
            return None
        
        # 비밀번호 검증
        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"비밀번호 불일치: {email}")
            return None
        
        # 활성 상태 확인
        if not user.is_active:
            logger.warning(f"비활성 사용자: {email}")
            return None
        
        # 토큰 생성
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"로그인 성공: {email}")
        return access_token
    
    async def get_current_user(self, token: str) -> Optional[UserEntity]:
        """현재 사용자 조회"""
        token_data = self.verify_token(token)
        if token_data is None:
            return None
        
        user = self.user_repository.find_by_email(token_data.email)
        if user is None:
            return None
        
        return user
    
    def create_token_response(self, access_token: str) -> TokenModel:
        """토큰 응답 생성"""
        return TokenModel(
            access_token=access_token,
            token_type="bearer"
        )
    
    def create_user_response(self, user: UserEntity) -> dict:
        """사용자 응답 생성"""
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
