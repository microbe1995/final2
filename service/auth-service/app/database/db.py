"""
데이터베이스 연결 및 초기화
"""
import os
import logging
from typing import Dict, List
from models.user import User

logger = logging.getLogger(__name__)

class InMemoryDB:
    """메모리 기반 임시 데이터베이스 (개발용)"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.users_by_email: Dict[str, str] = {}  # email -> user_id
        self.users_by_username: Dict[str, str] = {}  # username -> user_id
    
    async def create_user(self, user: User) -> User:
        """사용자 생성"""
        self.users[user.id] = user
        self.users_by_email[user.email] = user.id
        self.users_by_username[user.username] = user.id
        logger.info(f"메모리 DB에 사용자 저장: {user.email}")
        return user
    
    async def get_user_by_id(self, user_id: str) -> User:
        """ID로 사용자 조회"""
        return self.users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> User:
        """이메일로 사용자 조회"""
        user_id = self.users_by_email.get(email)
        if user_id:
            return self.users.get(user_id)
        return None
    
    async def get_user_by_username(self, username: str) -> User:
        """사용자명으로 사용자 조회"""
        user_id = self.users_by_username.get(username)
        if user_id:
            return self.users.get(user_id)
        return None
    
    async def update_user(self, user_id: str, updates: dict) -> User:
        """사용자 정보 업데이트"""
        if user_id in self.users:
            user = self.users[user_id]
            for key, value in updates.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            return user
        return None
    
    async def delete_user(self, user_id: str) -> bool:
        """사용자 삭제"""
        if user_id in self.users:
            user = self.users[user_id]
            del self.users[user_id]
            del self.users_by_email[user.email]
            del self.users_by_username[user.username]
            return True
        return False
    
    async def get_all_users(self) -> List[User]:
        """모든 사용자 조회"""
        return list(self.users.values())

# 전역 데이터베이스 인스턴스
_db_instance: InMemoryDB = None

async def get_db() -> InMemoryDB:
    """데이터베이스 인스턴스 반환"""
    global _db_instance
    if _db_instance is None:
        _db_instance = InMemoryDB()
    return _db_instance

async def init_db():
    """데이터베이스 초기화"""
    global _db_instance
    if _db_instance is None:
        _db_instance = InMemoryDB()
        logger.info("메모리 기반 데이터베이스 초기화 완료")
    
    # 테스트 사용자 생성 (개발용)
    if os.getenv("ENVIRONMENT") == "development":
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=pwd_context.hash("test123"),
            is_active=True
        )
        
        existing_user = await _db_instance.get_user_by_email("test@example.com")
        if not existing_user:
            await _db_instance.create_user(test_user)
            logger.info("테스트 사용자 생성: test@example.com / test123")
    
    return _db_instance
