from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any
import uuid

Base = declarative_base()

# ============================================================================
# 🌍 국가 엔티티
# ============================================================================

class Country(Base):
    """국가 엔티티"""
    
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(Text, unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # 국가 정보
    code = Column(Text, unique=True, index=True, nullable=False, comment="국가 코드")
    country_name = Column(Text, nullable=False, comment="영문 국가명")
    korean_name = Column(Text, nullable=False, comment="한국어 국가명")
    unlocode = Column(Text, nullable=True, comment="UNLOCODE")
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "code": self.code,
            "country_name": self.country_name,
            "korean_name": self.korean_name,
            "unlocode": self.unlocode,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
