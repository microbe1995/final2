from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any
import uuid

Base = declarative_base()

# ============================================================================
# 👨‍💼 관리자 엔티티
# ============================================================================

class Admin(Base):
    """관리자 엔티티"""
    
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(Text, unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # 관리자 계정 정보
    admin_id = Column(Text, unique=True, index=True, nullable=False, comment="Admin 로그인 ID")
    hashed_password = Column(Text, nullable=False, comment="해시된 비밀번호")
    
    # 사업장 정보
    Installation = Column(Text, nullable=False, comment="사업장명")
    Installation_en = Column(Text, nullable=True, comment="사업장영문명")
    economic_activity = Column(Text, nullable=True, comment="업종명")
    economic_activity_en = Column(Text, nullable=True, comment="업종영문명")
    representative = Column(Text, nullable=True, comment="대표자명")
    representative_en = Column(Text, nullable=True, comment="영문대표자명")
    email = Column(Text, nullable=True, comment="이메일")
    telephone = Column(Text, nullable=True, comment="전화번호")
    
    # 주소 정보
    street = Column(Text, nullable=True, comment="도로명")
    street_en = Column(Text, nullable=True, comment="도로영문명")
    number = Column(Text, nullable=True, comment="건물번호")
    number_en = Column(Text, nullable=True, comment="건물번호영문명")
    postcode = Column(Text, nullable=True, comment="우편번호")
    city = Column(Text, nullable=True, comment="도시명")
    city_en = Column(Text, nullable=True, comment="도시영문명")
    country = Column(Text, nullable=True, comment="국가명")
    country_en = Column(Text, nullable=True, comment="국가영문명")
    unlocode = Column(Text, nullable=True, comment="UNLOCODE")
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 스트림 관련
    stream_id = Column(Text, nullable=True, index=True, comment="스트림 식별자")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "admin_id": self.admin_id,
            "Installation": self.Installation,
            "Installation_en": self.Installation_en,
            "economic_activity": self.economic_activity,
            "economic_activity_en": self.economic_activity_en,
            "representative": self.representative,
            "representative_en": self.representative_en,
            "email": self.email,
            "telephone": self.telephone,
            "street": self.street,
            "street_en": self.street_en,
            "number": self.number,
            "number_en": self.number_en,
            "postcode": self.postcode,
            "city": self.city,
            "city_en": self.city_en,
            "country": self.country,
            "country_en": self.country_en,
            "unlocode": self.unlocode,
            "stream_id": self.stream_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
