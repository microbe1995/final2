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
# DB 연결지점 
# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.domain.user.user_schema import User
from app.domain.user.user_entity import UserDB
from app.common.database.database import database

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 📚 사용자 저장소 클래스
# ============================================================================

class UserRepository:
    """
    사용자 데이터 저장소
    
    주요 기능:
    - 사용자 생성/조회/수정/삭제
    - 이메일/사용자명으로 사용자 검색
    - 사용자 인증
    - PostgreSQL 및 메모리 저장소 지원
    """
    
    def __init__(self, use_database: bool = True):
        """
        사용자 저장소 초기화
        
        Args:
            use_database: PostgreSQL 사용 여부 (기본값: True)
        """
        self.use_database = use_database
        
        # 메모리 저장소는 항상 초기화 (fallback용)
        self._users: dict = {}
        self._users_by_email: dict = {}
        
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} 데이터베이스 저장소 사용")
    
    # ============================================================================
    # 🔐 사용자 인증 메서드
    # ============================================================================
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        사용자 인증
        
        Args:
            email: 사용자 이메일
            password: 사용자 비밀번호
            
        Returns:
            Optional[User]: 인증된 사용자 또는 None
        """
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None
            
            # 비밀번호 해싱 후 비교
            import hashlib
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            if user.password_hash == hashed_password:
                logger.info(f"✅ 사용자 인증 성공: {email}")
                return user
            else:
                logger.warning(f"❌ 비밀번호 불일치: {email}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 사용자 인증 실패: {email} - {str(e)}")
            return None
    
    # ============================================================================
    # 📝 사용자 CRUD 메서드
    # ============================================================================
    
    async def create_user(self, user: User) -> User:
        """
        사용자 생성
        
        Args:
            user: 생성할 사용자 정보
            
        Returns:
            User: 생성된 사용자 정보
        """
        try:
            if self.use_database:
                return await self._create_user_db(user)
            else:
                return await self._create_user_memory(user)
        except Exception as e:
            logger.error(f"❌ 사용자 생성 실패: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        사용자 ID로 사용자 조회
        
        Args:
            user_id: 조회할 사용자 ID
            
        Returns:
            Optional[User]: 사용자 정보 또는 None
        """
        try:
            if self.use_database:
                return await self._get_user_by_id_db(user_id)
            else:
                return self._users.get(user_id)
        except Exception as e:
            logger.error(f"❌ 사용자 ID 조회 실패: {user_id} - {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자 조회
        
        Args:
            email: 조회할 이메일
            
        Returns:
            Optional[User]: 사용자 정보 또는 None
        """
        try:
            if self.use_database:
                return await self._get_user_by_email_db(email)
            else:
                return self._users_by_email.get(email)
        except Exception as e:
            logger.error(f"❌ 이메일 조회 실패: {email} - {str(e)}")
            return None
    
    async def update_user(self, user: User) -> User:
        """
        사용자 정보 업데이트
        
        Args:
            user: 업데이트할 사용자 정보
            
        Returns:
            User: 업데이트된 사용자 정보
        """
        try:
            if self.use_database:
                return await self._update_user_db(user)
            else:
                return await self._update_user_memory(user)
        except Exception as e:
            logger.error(f"❌ 사용자 업데이트 실패: {user.id} - {str(e)}")
            raise
    
    async def delete_user(self, user_id: str) -> bool:
        """
        사용자 삭제
        
        Args:
            user_id: 삭제할 사용자 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if self.use_database:
                return await self._delete_user_db(user_id)
            else:
                return await self._delete_user_memory(user_id)
        except Exception as e:
            logger.error(f"❌ 사용자 삭제 실패: {user_id} - {str(e)}")
            return False
    
    # ============================================================================
    # 🔍 사용자 검색 메서드
    # ============================================================================
    
    async def get_all_users(self) -> List[User]:
        """
        모든 사용자 조회
        
        Returns:
            List[User]: 사용자 목록
        """
        try:
            if self.use_database:
                return await self._get_all_users_db()
            else:
                return list(self._users.values())
        except Exception as e:
            logger.error(f"❌ 모든 사용자 조회 실패: {str(e)}")
            return []
    
    async def search_users(self, query: str) -> List[User]:
        """
        사용자 검색
        
        Args:
            query: 검색 쿼리
            
        Returns:
            List[User]: 검색된 사용자 목록
        """
        try:
            if self.use_database:
                return await self._search_users_db(query)
            else:
                return [
                    user for user in self._users.values()
                    if query.lower() in user.username.lower() or 
                       query.lower() in user.email.lower() or
                       (user.full_name and query.lower() in user.full_name.lower())
                ]
        except Exception as e:
            logger.error(f"❌ 사용자 검색 실패: {query} - {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드
    # ============================================================================
    
    async def _create_user_db(self, user: User) -> User:
        """PostgreSQL에 사용자 생성"""
        try:
            session = await database.get_async_session()
            try:
                user_db = UserDB(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    password_hash=user.password_hash,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                )
                
                session.add(user_db)
                await session.commit()
                await session.refresh(user_db)
                
                logger.info(f"✅ PostgreSQL 사용자 생성 성공: {user.email}")
                return user
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 사용자 생성 실패: {str(e)}")
            raise
    
    async def _get_user_by_id_db(self, user_id: str) -> Optional[User]:
        """PostgreSQL에서 사용자 ID로 조회"""
        try:
            session = await database.get_async_session()
            try:
                result = await session.execute(
                    text("SELECT * FROM users WHERE id = :user_id"),
                    {"user_id": user_id}
                )
                user_data = result.fetchone()
                
                if user_data:
                    return User(
                        id=user_data.id,
                        email=user_data.email,
                        full_name=user_data.full_name,
                        password_hash=user_data.password_hash,
                        is_active=user_data.is_active,
                        created_at=user_data.created_at,
                        updated_at=user_data.updated_at,
                        last_login=user_data.last_login
                    )
                return None
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 사용자 ID 조회 실패: {str(e)}")
            return None
    
    async def _get_user_by_email_db(self, email: str) -> Optional[User]:
        """PostgreSQL에서 이메일로 사용자 조회"""
        try:
            session = await database.get_async_session()
            try:
                result = await session.execute(
                    text("SELECT * FROM users WHERE email = :email"),
                    {"email": email}
                )
                user_data = result.fetchone()
                
                if user_data:
                    return User(
                        id=user_data.id,
                        email=user_data.email,
                        full_name=user_data.full_name,
                        password_hash=user_data.password_hash,
                        is_active=user_data.is_active,
                        created_at=user_data.created_at,
                        updated_at=user_data.updated_at,
                        last_login=user_data.last_login
                    )
                return None
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 이메일 조회 실패: {str(e)}")
            return None
    
    async def _update_user_db(self, user: User) -> User:
        """PostgreSQL에서 사용자 정보 업데이트"""
        try:
            session = await database.get_async_session()
            try:
                await session.execute(
                    text("""
                        UPDATE users 
                        SET email = :email, full_name = :full_name,
                            password_hash = :password_hash, is_active = :is_active,
                            updated_at = :updated_at, last_login = :last_login
                        WHERE id = :id
                    """),
                    {
                        "id": user.id,
                        "email": user.email,
                        "full_name": user.full_name,
                        "password_hash": user.password_hash,
                        "is_active": user.is_active,
                        "updated_at": user.updated_at,
                        "last_login": user.last_login
                    }
                )
                await session.commit()
                
                logger.info(f"✅ PostgreSQL 사용자 업데이트 성공: {user.email}")
                return user
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 사용자 업데이트 실패: {str(e)}")
            raise
    
    async def _delete_user_db(self, user_id: str) -> bool:
        """PostgreSQL에서 사용자 삭제"""
        try:
            session = await database.get_async_session()
            try:
                result = await session.execute(
                    text("DELETE FROM users WHERE id = :user_id"),
                    {"user_id": user_id}
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 사용자 삭제 성공: {user_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 사용자 삭제 실패: 사용자를 찾을 수 없음 {user_id}")
                    return False
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 사용자 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_users_db(self) -> List[User]:
        """PostgreSQL에서 모든 사용자 조회"""
        try:
            session = await database.get_async_session()
            try:
                result = await session.execute(text("SELECT * FROM users"))
                users_data = result.fetchall()
                
                users = []
                for user_data in users_data:
                    user = User(
                        id=user_data.id,
                        email=user_data.email,
                        full_name=user_data.full_name,
                        password_hash=user_data.password_hash,
                        is_active=user_data.is_active,
                        created_at=user_data.created_at,
                        updated_at=user_data.updated_at,
                        last_login=user_data.last_login
                    )
                    users.append(user)
                
                return users
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 모든 사용자 조회 실패: {str(e)}")
            return []
    
    async def _search_users_db(self, query: str) -> List[User]:
        """PostgreSQL에서 사용자 검색"""
        try:
            session = await database.get_async_session()
            try:
                search_pattern = f"%{query}%"
                result = await session.execute(
                    text("""
                        SELECT * FROM users 
                        WHERE email ILIKE :query OR full_name ILIKE :query
                    """),
                    {"query": search_pattern}
                )
                users_data = result.fetchall()
                
                users = []
                for user_data in users_data:
                    user = User(
                        id=user_data.id,
                        email=user_data.email,
                        full_name=user_data.full_name,
                        password_hash=user_data.password_hash,
                        is_active=user_data.is_active,
                        created_at=user_data.created_at,
                        updated_at=user_data.updated_at,
                        last_login=user_data.last_login
                    )
                    users.append(user)
                
                return users
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 사용자 검색 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_user_memory(self, user: User) -> User:
        """메모리에 사용자 생성"""
        self._users[user.id] = user
        self._users_by_email[user.email] = user
        
        logger.info(f"✅ 메모리 사용자 생성: {user.email}")
        return user
    
    async def _update_user_memory(self, user: User) -> User:
        """메모리에서 사용자 정보 업데이트"""
        if user.id in self._users:
            old_user = self._users[user.id]
            
            # 이전 이메일 인덱스 제거
            if old_user.email in self._users_by_email:
                del self._users_by_email[old_user.email]
            
            # 새 정보로 업데이트
            self._users[user.id] = user
            self._users_by_email[user.email] = user
            
            logger.info(f"✅ 메모리 사용자 업데이트 성공: {user.email}")
            return user
        else:
            raise ValueError(f"사용자를 찾을 수 없습니다: {user.id}")
    
    async def _delete_user_memory(self, user_id: str) -> bool:
        """메모리에서 사용자 삭제"""
        if user_id in self._users:
            user = self._users[user_id]
            
            # 인덱스에서 제거
            if user.email in self._users_by_email:
                del self._users_by_email[user.email]
            
            # 메인 저장소에서 제거
            del self._users[user_id]
            
            logger.info(f"✅ 메모리 사용자 삭제 성공: {user_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 사용자 삭제 실패: 사용자를 찾을 수 없음 {user_id}")
            return False
