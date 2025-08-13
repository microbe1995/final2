"""
사용자 리포지토리
"""
from typing import Optional, List, Dict
from domain.entity.user_entity import UserEntity
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """사용자 리포지토리 클래스"""
    
    def __init__(self):
        # 메모리 기반 저장소 (실제로는 데이터베이스 사용)
        self._users: Dict[str, UserEntity] = {}
        self._users_by_email: Dict[str, str] = {}  # email -> user_id
        self._users_by_username: Dict[str, str] = {}  # username -> user_id
        
        # 테스트 데이터 초기화
        self._initialize_test_data()
    
    def _initialize_test_data(self):
        """테스트 데이터 초기화"""
        test_user = UserEntity(
            email="test@example.com",
            username="testuser",
            password_hash="test123",  # 개발용으로 평문 저장
            full_name="테스트 사용자",
            is_active=True
        )
        
        self.save(test_user)
        logger.info("테스트 사용자 데이터 초기화 완료")
    
    def save(self, user: UserEntity) -> UserEntity:
        """사용자 저장"""
        self._users[user.id] = user
        self._users_by_email[user.email] = user.id
        self._users_by_username[user.username] = user.id
        logger.info(f"사용자 저장 완료: {user.email}")
        return user
    
    def find_by_id(self, user_id: str) -> Optional[UserEntity]:
        """ID로 사용자 조회"""
        return self._users.get(user_id)
    
    def find_by_email(self, email: str) -> Optional[UserEntity]:
        """이메일로 사용자 조회"""
        user_id = self._users_by_email.get(email)
        return self._users.get(user_id) if user_id else None
    
    def find_by_username(self, username: str) -> Optional[UserEntity]:
        """사용자명으로 사용자 조회"""
        user_id = self._users_by_username.get(username)
        return self._users.get(user_id) if user_id else None
    
    def find_all(self) -> List[UserEntity]:
        """모든 사용자 조회"""
        return list(self._users.values())
    
    def update(self, user: UserEntity) -> UserEntity:
        """사용자 업데이트"""
        if user.id in self._users:
            user.update()  # updated_at 자동 설정
            self._users[user.id] = user
            logger.info(f"사용자 업데이트 완료: {user.email}")
        return user
    
    def delete(self, user_id: str) -> bool:
        """사용자 삭제"""
        user = self._users.get(user_id)
        if user:
            del self._users[user_id]
            del self._users_by_email[user.email]
            del self._users_by_username[user.username]
            logger.info(f"사용자 삭제 완료: {user.email}")
            return True
        return False
    
    def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부 확인"""
        return email in self._users_by_email
    
    def exists_by_username(self, username: str) -> bool:
        """사용자명 존재 여부 확인"""
        return username in self._users_by_username
    
    def count(self) -> int:
        """사용자 수 조회"""
        return len(self._users)
