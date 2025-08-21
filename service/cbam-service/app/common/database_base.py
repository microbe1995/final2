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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime

class DatabaseBase(DeclarativeBase):
    """모든 엔티티의 공통 Base 클래스"""
    pass

# 공통 Base 인스턴스 (모든 도메인에서 사용)
Base = DatabaseBase

# 공통 필드를 가진 Base 클래스 (필요 시 사용)
class TimestampMixin:
    """생성/수정 시간 공통 필드"""
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class IdentityMixin:
    """ID 공통 필드"""
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
