# ============================================================================
# 🗄️ 공통 데이터베이스 Base 클래스
# ============================================================================

"""
모든 도메인에서 공통으로 사용할 SQLAlchemy Base 클래스

SQLAlchemy 2.0 호환성을 위해 DeclarativeBase를 사용합니다.
각 도메인별로 개별 Base를 생성하는 대신 공통 Base를 사용하여
메타데이터 충돌을 방지합니다.
"""

from typing import Any
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

# ============================================================================
# 🗄️ 데이터베이스 기본 엔티티
# ============================================================================

class DatabaseBase(Base):
    """데이터베이스 기본 엔티티"""
    
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(Text(36), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# 공통 Base 인스턴스 (모든 도메인에서 사용)
# Base = DatabaseBase

# 공통 필드를 가진 Base 클래스 (필요 시 사용)
class TimestampMixin:
    """생성/수정 시간 공통 필드"""
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class IdentityMixin:
    """ID 공통 필드"""
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
