from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.common.db import get_db
from app.common.settings import settings
from app.common.security import get_current_user
from app.domain.entities.user import User

def get_settings():
    """설정 의존성"""
    return settings

def get_current_user_depends(
    db: Session = Depends(get_db),
    token: str = Depends(get_current_user)
) -> User:
    """현재 사용자 의존성"""
    user = get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
