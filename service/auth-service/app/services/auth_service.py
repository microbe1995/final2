"""
인증 서비스 로직
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.user import User, UserCreate

logger = logging.getLogger(__name__)

class AuthService:
    """인증 서비스 클래스"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
        
        # 메모리 기반 사용자 저장소
        self.users: Dict[str, User] = {}
        self.users_by_email: Dict[str, str] = {}  # email -> user_id
        self.users_by_username: Dict[str, str] = {}  # username -> user_id
        
        # 테스트 사용자 생성
        self._create_test_user()
    
    def _create_test_user(self):
        """테스트 사용자 생성"""
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=self.get_password_hash("test123"),
            is_active=True,
            created_at=datetime.utcnow()
        )
        self.users[test_user.id] = test_user
        self.users_by_email[test_user.email] = test_user.id
        self.users_by_username[test_user.username] = test_user.id
        logger.info("테스트 사용자 생성: test@example.com / test123")
    
    def _get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        user_id = self.users_by_email.get(email)
        return self.users.get(user_id) if user_id else None
    
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        user_id = self.users_by_username.get(username)
        return self.users.get(user_id) if user_id else None
    
    def _save_user(self, user: User) -> User:
        """사용자 저장"""
        self.users[user.id] = user
        self.users_by_email[user.email] = user.id
        self.users_by_username[user.username] = user.id
        return user
    
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
        logger.info(f"🔥 회원가입 요청 받음: 이메일={user_data.email}, 사용자명={user_data.username}")
        
        # 이메일 중복 확인
        existing_user = self._get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"❌ 이메일 중복: {user_data.email}")
            raise ValueError("이미 존재하는 이메일입니다.")
        
        # 사용자명 중복 확인
        existing_username = self._get_user_by_username(user_data.username)
        if existing_username:
            logger.warning(f"❌ 사용자명 중복: {user_data.username}")
            raise ValueError("이미 존재하는 사용자명입니다.")
        
        # 비밀번호 해시화
        hashed_password = self.get_password_hash(user_data.password)
        logger.info(f"🔒 비밀번호 해시 생성 완료: {user_data.email}")
        
        # 사용자 생성
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # 메모리에 저장
        created_user = self._save_user(user)
        logger.info(f"✅ 새 사용자 생성 완료: {created_user.email} (ID: {created_user.id})")
        logger.info(f"📊 현재 총 사용자 수: {len(self.users)}명")
        return created_user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """사용자 인증 및 토큰 생성"""
        logger.info(f"🔑 로그인 시도: {email}")
        
        user = self._get_user_by_email(email)
        if not user:
            logger.warning(f"❌ 존재하지 않는 사용자: {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"❌ 비활성 사용자 로그인 시도: {email}")
            return None
        
        if not self.verify_password(password, user.hashed_password):
            logger.warning(f"❌ 잘못된 비밀번호: {email}")
            return None
        
        # JWT 토큰 생성
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"✅ 사용자 인증 성공: {email}")
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
        
        user = self._get_user_by_email(email)
        if user is None:
            logger.warning(f"토큰의 사용자가 존재하지 않음: {email}")
            return None
        
        return user
