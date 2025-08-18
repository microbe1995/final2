"""
데이터베이스 모델 - SQLAlchemy 기반
PostgreSQL 연결을 위한 테이블 스키마 정의

주요 기능:
- 사용자 테이블 스키마 정의
- 자동 UUID 생성
- 타임스탬프 자동 관리
- 인덱스 및 제약조건 설정
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
from datetime import datetime
# 원래 엔티티
# ============================================================================
# 🗄️ SQLAlchemy Base 클래스
# ============================================================================

Base = declarative_base()

# ============================================================================
# 👥 사용자 데이터베이스 모델
# ============================================================================

class UserDB(Base):
    """사용자 데이터베이스 모델"""
    __tablename__ = "users"
    
    # 기본 필드
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # 상태 및 시간 필드
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        """문자열 표현"""
        return f"<UserDB(id={self.id}, email={self.email}, full_name={self.full_name})>"
    
    def to_dict(self):
        """딕셔너리 변환 (비밀번호 제외)"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
