"""
인증 서비스 로직
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.user import User, UserCreate
from database.user_repository import UserRepository

logger = logging.getLogger(__name__)

class AuthService:
    """인증 서비스 클래스"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
        self.user_repository = UserRepository()
    
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
    
    async def create_user(self, user_data: UserCreate) -> User:
        """사용자 생성"""
        # 이메일 중복 확인
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("이미 존재하는 이메일입니다.")
        
        # 사용자명 중복 확인
        existing_username = await self.user_repository.get_user_by_username(user_data.username)
        if existing_username:
            raise ValueError("이미 존재하는 사용자명입니다.")
        
        # 비밀번호 해시화
        hashed_password = self.get_password_hash(user_data.password)
        
        # 사용자 생성
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # 데이터베이스에 저장
        created_user = await self.user_repository.create_user(user)
        logger.info(f"새 사용자 생성: {created_user.email}")
        return created_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """사용자 인증 및 토큰 생성"""
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            logger.warning(f"존재하지 않는 사용자: {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"비활성 사용자 로그인 시도: {email}")
            return None
        
        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"잘못된 비밀번호: {email}")
            return None
        
        # JWT 토큰 생성
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"사용자 인증 성공: {email}")
        return access_token
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """토큰으로부터 현재 사용자 정보 조회"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None
        except JWTError as e:
            logger.warning(f"토큰 디코딩 실패: {str(e)}")
            return None
        
        user = await self.user_repository.get_user_by_email(email)
        if user is None:
            logger.warning(f"토큰의 사용자가 존재하지 않음: {email}")
            return None
        
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """사용자 ID로 사용자 조회"""
        return await self.user_repository.get_user_by_id(user_id)
    
    async def update_user_activity(self, user_id: str) -> bool:
        """사용자 활동 시간 업데이트"""
        try:
            await self.user_repository.update_user_last_activity(user_id)
            return True
        except Exception as e:
            logger.error(f"사용자 활동 시간 업데이트 실패: {str(e)}")
            return False
