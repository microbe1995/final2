"""
사용자 엔티티
"""
from datetime import datetime
from typing import Optional
import uuid

class UserEntity:
    """사용자 엔티티 클래스"""
    
    def __init__(
        self,
        email: str,
        username: str,
        hashed_password: str,
        is_active: bool = True,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.email = email
        self.username = username
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserEntity':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            id=data.get("id"),
            email=data["email"],
            username=data["username"],
            hashed_password=data["hashed_password"],
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )
    
    def update(self, **kwargs):
        """엔티티 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"UserEntity(id={self.id}, email={self.email}, username={self.username})"
