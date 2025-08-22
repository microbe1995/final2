from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any
import uuid

Base = declarative_base()

# ============================================================================
# 👤 사용자 엔티티
# ============================================================================

class User(Base):
    """사용자 엔티티"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(Text, unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # 사용자 계정 정보
    username = Column(Text, unique=True, index=True, nullable=False, comment="사용자명 (로그인용)")
    hashed_password = Column(Text, nullable=False, comment="해시된 비밀번호")
    
    # 사용자 개인 정보
    full_name = Column(Text, nullable=False, comment="전체 이름")
    email = Column(Text, nullable=True, comment="이메일")
    phone = Column(Text, nullable=True, comment="전화번호")
    department = Column(Text, nullable=True, comment="부서")
    position = Column(Text, nullable=True, comment="직책")
    
    # 사용자 역할 및 상태
    role = Column(Text, nullable=False, default="user", comment="사용자 역할")
    is_active = Column(Boolean, default=True, comment="활성 상태")
    is_verified = Column(Boolean, default=False, comment="이메일 인증 상태")
    
    # 소속 정보
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, comment="소속 기업 ID")
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True, comment="소속 관리자 ID")
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True, comment="마지막 로그인 시간")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "position": self.position,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "company_id": self.company_id,
            "admin_id": self.admin_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
