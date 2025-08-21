from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.common.db import Base

class Country(Base):
    """국가 코드 테이블 (엑셀 데이터 기반)"""
    __tablename__ = "countries"
    
    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # 국가 정보
    code = Column(String(10), unique=True, index=True, nullable=False, comment="국가 코드")
    country_name = Column(String(100), nullable=False, comment="영문 국가명")
    korean_name = Column(String(100), nullable=False, comment="한국어 국가명")
    unlocode = Column(String(10), nullable=True, comment="UNLOCODE")
    
    # 시스템 필드
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_country_code', 'code'),
        Index('idx_country_name', 'country_name'),
        Index('idx_country_korean_name', 'korean_name'),
        Index('idx_country_unlocode', 'unlocode'),
        Index('idx_country_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Country(id={self.id}, code='{self.code}', country_name='{self.country_name}', korean_name='{self.korean_name}', unlocode='{self.unlocode}')>"
    
    def to_dict(self):
        """국가 정보를 딕셔너리로 변환"""
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
