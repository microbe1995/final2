# ============================================================================
# 🗃️ Database Models - 데이터베이스 모델 기본 클래스
# ============================================================================

"""
데이터베이스 모델의 기본 클래스

SQLAlchemy 모델들의 공통 기능을 제공합니다.
"""

from datetime import datetime
from typing import Any, Dict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func

# SQLAlchemy 기본 클래스 생성
Base = declarative_base()

class TimestampMixin:
    """타임스탬프 믹스인 클래스"""
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class BaseModel(Base, TimestampMixin):
    """기본 모델 클래스"""
    
    __abstract__ = True
    
    # 공통 필드
    id = Column(String(36), primary_key=True, index=True)  # UUID 문자열
    metadata_json = Column(Text, nullable=True)  # JSON 메타데이터
    
    def to_dict(self) -> Dict[str, Any]:
        """모델을 딕셔너리로 변환합니다"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat() if value else None
            else:
                result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """딕셔너리로부터 모델을 업데이트합니다"""
        for key, value in data.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """모델의 문자열 표현을 반환합니다"""
        return f"<{self.__class__.__name__}(id={self.id})>"
