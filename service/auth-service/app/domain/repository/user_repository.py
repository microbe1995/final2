"""
사용자 저장소 - 사용자 정보의 데이터 접근 로직
인증 서비스에서 사용자 정보를 저장하고 조회

주요 기능:
- 사용자 생성/조회/수정/삭제
- 이메일/사용자명 중복 검사
- 사용자 인증 (로그인)
- PostgreSQL 및 메모리 저장소 지원
- 자동 UUID 생성 및 타임스탬프 관리
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.domain.entity.user_entity import User, UserCredentials
from app.domain.model.db_models import UserDB
from app.common.database.database import database

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 👥 사용자 정보 저장소 클래스
# ============================================================================

class UserRepository:
    """
    사용자 정보 저장소 클래스
    
    주요 기능:
    - 사용자 정보 저장/조회/수정/삭제
    - 사용자 인증 정보 검증
    - PostgreSQL 및 메모리 저장소 지원
    - 자동 UUID 생성 및 타임스탬프 관리
    """
    
    def __init__(self):
        """사용자 저장소 초기화"""
        # 데이터베이스 연결 확인
        self.use_database = database.database_url is not None
        
        # 메모리 기반 저장소 (fallback용으로 항상 초기화)
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, str] = {}  # email -> user_id 매핑
        self._users_by_username: Dict[str, str] = {}  # username -> user_id 매핑
        
        if self.use_database:
            logger.info("✅ PostgreSQL 데이터베이스 저장소 사용")
        else:
            logger.info("⚠️ 메모리 저장소 사용 (DATABASE_URL 미설정)")
    
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
            
            if self.use_database:
                # PostgreSQL 데이터베이스에 저장
                return await self._create_user_db(user)
            else:
                # 메모리 저장소에 저장
                return await self._create_user_memory(user)
                
        except Exception as e:
            logger.error(f"❌ 사용자 생성 실패: {str(e)}")
            return None
    
    async def _create_user_db(self, user: User) -> Optional[User]:
        """PostgreSQL 데이터베이스에 사용자 생성"""
        try:
            # 중복 검사
            if await self.get_user_by_email(user.email):
                logger.warning(f"❌ 이메일 중복: {user.email}")
                return None
            
            if await self.get_user_by_username(user.username):
                logger.warning(f"❌ 사용자명 중복: {user.username}")
                return None
            
            # UserDB 모델로 변환
            user_db = UserDB(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                password_hash=user.password_hash,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
            
            # 데이터베이스에 저장
            session = await database.get_async_session()
            if session:
                try:
                    session.add(user_db)
                    await session.commit()
                    await session.refresh(user_db)
                finally:
                    await session.close()
            else:
                logger.error("❌ 데이터베이스 세션을 가져올 수 없습니다.")
                return None
            
            logger.info(f"✅ PostgreSQL 사용자 생성 성공: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL 사용자 생성 실패: {str(e)}")
            return None
    
    async def _get_user_by_email_db(self, email: str) -> Optional[User]:
        """PostgreSQL에서 이메일로 사용자 조회"""
        try:
            session = await database.get_async_session()
            if session:
                try:
                    result = await session.execute(
                        select(UserDB).where(UserDB.email == email)
                    )
                    user_db = result.scalar_one_or_none()
                    
                    if user_db:
                        # UserDB를 User 엔티티로 변환
                        user = User(
                            id=user_db.id,
                            username=user_db.username,
                            email=user_db.email,
                            full_name=user_db.full_name,
                            password_hash=user_db.password_hash,
                            is_active=user_db.is_active,
                            created_at=user_db.created_at,
                            updated_at=user_db.updated_at,
                            last_login=user_db.last_login
                        )
                        return user
                    return None
                finally:
                    await session.close()
            else:
                logger.error("❌ 데이터베이스 세션을 가져올 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 이메일 조회 실패: {str(e)}")
            return None
    
    async def _get_user_by_username_db(self, username: str) -> Optional[User]:
        """PostgreSQL에서 사용자명으로 사용자 조회"""
        try:
            session = await database.get_async_session()
            if session:
                try:
                    result = await session.execute(
                        select(UserDB).where(UserDB.username == username)
                    )
                    user_db = result.scalar_one_or_none()
                    
                    if user_db:
                        # UserDB를 User 엔티티로 변환
                        user = User(
                            id=user_db.id,
                            username=user_db.username,
                            email=user_db.email,
                            full_name=user_db.full_name,
                            password_hash=user_db.password_hash,
                            is_active=user_db.is_active,
                            created_at=user_db.created_at,
                            updated_at=user_db.updated_at,
                            last_login=user_db.last_login
                        )
                        return user
                    return None
                finally:
                    await session.close()
            else:
                logger.error("❌ 데이터베이스 세션을 가져올 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 사용자명 조회 실패: {str(e)}")
            return None
    
    async def _create_user_memory(self, user: User) -> Optional[User]:
        """메모리 저장소에 사용자 생성"""
        try:
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
            
            logger.info(f"✅ 메모리 사용자 생성 성공: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"❌ 메모리 사용자 생성 실패: {str(e)}")
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
        if self.use_database:
            # PostgreSQL에서 조회
            return await self._get_user_by_email_db(email)
        else:
            # 메모리에서 조회
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
        if self.use_database:
            # PostgreSQL에서 조회
            return await self._get_user_by_username_db(username)
        else:
            # 메모리에서 조회
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
            
            # 비밀번호 해싱 후 비교
            import hashlib
            hashed_password = hashlib.sha256(credentials.password.encode()).hexdigest()
            
            if user.password_hash == hashed_password:
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
