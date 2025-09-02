"""
Dummy 데이터 엔티티
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

from sqlalchemy import Column, Integer, Text, DateTime, Date, Numeric, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, date
from typing import Dict, Any

from app.common.database_base import Base

# ============================================================================
# 🎭 Dummy Entity - Dummy 데이터베이스 모델
# ============================================================================

class DummyData(Base):
    """Dummy 데이터 엔티티"""
    
    __tablename__ = "dummy"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    로트번호 = Column(Text, nullable=False, index=True)
    생산품명 = Column(Text, nullable=False, index=True)
    생산수량 = Column(Numeric(10, 2), nullable=False)
    투입일 = Column(Date, nullable=True)
    종료일 = Column(Date, nullable=True)
    공정 = Column(Text, nullable=False, index=True)
    투입물명 = Column(Text, nullable=False, index=True)
    수량 = Column(Numeric(10, 2), nullable=False)
    단위 = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<DummyData(id={self.id}, 로트번호='{self.로트번호}', 생산품명='{self.생산품명}', 공정='{self.공정}')>"
