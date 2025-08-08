"""
사용자 데이터 저장소
"""
import logging
from typing import Optional, List
from datetime import datetime
from models.user import User
from database.db import get_db

logger = logging.getLogger(__name__)

class UserRepository:
    """사용자 데이터 저장소 클래스"""
    
    def __init__(self):
        pass
    
    async def create_user(self, user: User) -> User:
        """사용자 생성"""
        db = await get_db()
        created_user = await db.create_user(user)
        logger.info(f"사용자 생성 완료: {created_user.email}")
        return created_user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        db = await get_db()
        user = await db.get_user_by_id(user_id)
        if user:
            logger.debug(f"사용자 조회 성공 (ID): {user_id}")
        else:
            logger.debug(f"사용자를 찾을 수 없음 (ID): {user_id}")
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        db = await get_db()
        user = await db.get_user_by_email(email)
        if user:
            logger.debug(f"사용자 조회 성공 (이메일): {email}")
        else:
            logger.debug(f"사용자를 찾을 수 없음 (이메일): {email}")
        return user
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 사용자 조회"""
        db = await get_db()
        user = await db.get_user_by_username(username)
        if user:
            logger.debug(f"사용자 조회 성공 (사용자명): {username}")
        else:
            logger.debug(f"사용자를 찾을 수 없음 (사용자명): {username}")
        return user
    
    async def update_user(self, user_id: str, updates: dict) -> Optional[User]:
        """사용자 정보 업데이트"""
        db = await get_db()
        updates["updated_at"] = datetime.utcnow()
        updated_user = await db.update_user(user_id, updates)
        if updated_user:
            logger.info(f"사용자 정보 업데이트 완료: {user_id}")
        else:
            logger.warning(f"사용자 정보 업데이트 실패: {user_id}")
        return updated_user
    
    async def update_user_last_activity(self, user_id: str) -> bool:
        """사용자 마지막 활동 시간 업데이트"""
        try:
            await self.update_user(user_id, {"updated_at": datetime.utcnow()})
            return True
        except Exception as e:
            logger.error(f"사용자 활동 시간 업데이트 실패: {str(e)}")
            return False
    
    async def deactivate_user(self, user_id: str) -> bool:
        """사용자 비활성화"""
        try:
            updated_user = await self.update_user(user_id, {"is_active": False})
            if updated_user:
                logger.info(f"사용자 비활성화 완료: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"사용자 비활성화 실패: {str(e)}")
            return False
    
    async def activate_user(self, user_id: str) -> bool:
        """사용자 활성화"""
        try:
            updated_user = await self.update_user(user_id, {"is_active": True})
            if updated_user:
                logger.info(f"사용자 활성화 완료: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"사용자 활성화 실패: {str(e)}")
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """사용자 삭제"""
        db = await get_db()
        result = await db.delete_user(user_id)
        if result:
            logger.info(f"사용자 삭제 완료: {user_id}")
        else:
            logger.warning(f"사용자 삭제 실패: {user_id}")
        return result
    
    async def get_all_users(self) -> List[User]:
        """모든 사용자 조회"""
        db = await get_db()
        users = await db.get_all_users()
        logger.debug(f"전체 사용자 조회: {len(users)}명")
        return users
    
    async def count_users(self) -> int:
        """사용자 수 조회"""
        users = await self.get_all_users()
        return len(users)
