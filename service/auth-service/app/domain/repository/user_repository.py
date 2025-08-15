"""
사용자 저장소 - 사용자 정보의 데이터 접근 로직
인증 서비스에서 사용자 정보를 저장하고 조회
"""
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import uuid

from app.domain.entity.user_entity import User, UserCredentials

# 로거 설정
logger = logging.getLogger(__name__)

class UserRepository:
    """
    사용자 정보 저장소 클래스
    - 사용자 정보 저장/조회/수정
    - 사용자 인증 정보 검증
    - 임시 메모리 기반 저장 (향후 PostgreSQL로 확장)
    """
    
    def __init__(self):
        """사용자 저장소 초기화"""
        # 메모리 기반 저장소 (향후 데이터베이스로 확장 가능)
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, str] = {}  # email -> user_id 매핑
        self._users_by_username: Dict[str, str] = {}  # username -> user_id 매핑
        
        logger.info("✅ 사용자 저장소 초기화 완료")
    
    async def create_user(self, user: User) -> Optional[User]:
        """
        새로운 사용자 생성
        
        Args:
            user: 생성할 사용자 정보
            
        Returns:
            생성된 사용자 정보 (성공 시), None (실패 시)
        """
        try:
            # 사용자 ID 생성
            user.id = str(uuid.uuid4())
            user.created_at = datetime.now()
            user.updated_at = datetime.now()
            
            # 중복 검사
            if await self.get_user_by_email(user.email):
                logger.warning(f"❌ 이메일 중복: {user.email}")
                return None
            
            if await self.get_user_by_username(user.username):
                logger.warning(f"❌ 사용자명 중복: {user.username}")
                return None
            
            # 사용자 저장
            self._users[user.id] = user
            self._users_by_email[user.email] = user.id
            self._users_by_username[user.username] = user.id
            
            logger.info(f"✅ 사용자 생성 성공: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"❌ 사용자 생성 실패: {str(e)}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        사용자 ID로 사용자 정보 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 정보 (있으면), None (없으면)
        """
        return self._users.get(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자 정보 조회
        
        Args:
            email: 이메일 주소
            
        Returns:
            사용자 정보 (있으면), None (없으면)
        """
        user_id = self._users_by_email.get(email)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        사용자명으로 사용자 정보 조회
        
        Args:
            username: 사용자명
            
        Returns:
            사용자 정보 (있으면), None (없으면)
        """
        user_id = self._users_by_username.get(username)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def authenticate_user(self, credentials: UserCredentials) -> Optional[User]:
        """
        사용자 인증
        
        Args:
            credentials: 사용자 인증 정보
            
        Returns:
            인증된 사용자 정보 (성공 시), None (실패 시)
        """
        try:
            user = await self.get_user_by_email(credentials.email)
            if not user:
                logger.warning(f"❌ 사용자 없음: {credentials.email}")
                return None
            
            # 비밀번호 검증 (실제로는 해시 비교)
            if user.password_hash == credentials.password:  # 임시 구현
                user.update_last_login()
                logger.info(f"✅ 사용자 인증 성공: {credentials.email}")
                return user
            else:
                logger.warning(f"❌ 비밀번호 불일치: {credentials.email}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 사용자 인증 실패: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """
        사용자 정보 업데이트
        
        Args:
            user_id: 사용자 ID
            update_data: 업데이트할 데이터
            
        Returns:
            업데이트된 사용자 정보 (성공 시), None (실패 시)
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"❌ 사용자 없음: {user_id}")
                return None
            
            # 업데이트 가능한 필드들
            allowed_fields = ['full_name', 'is_active']
            for field, value in update_data.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            user.update_modified_time()
            logger.info(f"✅ 사용자 정보 업데이트 성공: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"❌ 사용자 정보 업데이트 실패: {str(e)}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """
        사용자 삭제
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"❌ 사용자 없음: {user_id}")
                return False
            
            # 관련 매핑 제거
            if user.email in self._users_by_email:
                del self._users_by_email[user.email]
            if user.username in self._users_by_username:
                del self._users_by_username[user.username]
            
            # 사용자 제거
            del self._users[user_id]
            
            logger.info(f"✅ 사용자 삭제 성공: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 사용자 삭제 실패: {str(e)}")
            return False
    
    async def get_all_users(self) -> List[User]:
        """
        모든 사용자 정보 조회
        
        Returns:
            사용자 정보 목록
        """
        return list(self._users.values())
    
    async def get_users_count(self) -> int:
        """
        등록된 사용자 수 조회
        
        Returns:
            사용자 수
        """
        return len(self._users)
    
    async def search_users(self, query: str) -> List[User]:
        """
        사용자 검색
        
        Args:
            query: 검색 쿼리
            
        Returns:
            검색 결과 사용자 목록
        """
        results = []
        query_lower = query.lower()
        
        for user in self._users.values():
            if (query_lower in user.username.lower() or 
                query_lower in user.email.lower() or 
                query_lower in user.full_name.lower()):
                results.append(user)
        
        return results
