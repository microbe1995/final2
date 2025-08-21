from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.common.db import Base

class Company(Base):
    """기업(회사) 엔티티 - 회원가입 시 사용"""
    __tablename__ = "companies"

    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # 로그인 정보
    company_id = Column(String(100), unique=True, index=True, nullable=False, comment="기업 ID (로그인용)")
    hashed_password = Column(String(255), nullable=False, comment="해시된 비밀번호")

    # 기업 정보
    Installation = Column(String(200), nullable=False, comment="사업장명")
    Installation_en = Column(String(200), nullable=True, comment="사업장 영문명")
    economic_activity = Column(String(200), nullable=True, comment="업종명")
    economic_activity_en = Column(String(200), nullable=True, comment="업종명 영문명")
    representative = Column(String(100), nullable=True, comment="대표자명")
    representative_en = Column(String(100), nullable=True, comment="영문대표자명")
    email = Column(String(100), nullable=True, comment="이메일")
    telephone = Column(String(50), nullable=True, comment="전화번호")

    # 주소 정보
    street = Column(String(200), nullable=True, comment="도로명")
    street_en = Column(String(200), nullable=True, comment="도로명 영문")
    number = Column(String(50), nullable=True, comment="건물 번호")
    number_en = Column(String(50), nullable=True, comment="건물 번호 영문")
    postcode = Column(String(20), nullable=True, comment="우편번호")
    city = Column(String(100), nullable=True, comment="도시명")
    city_en = Column(String(100), nullable=True, comment="도시명 영문")
    country = Column(String(100), nullable=True, comment="국가명")
    country_en = Column(String(100), nullable=True, comment="국가명 영문")
    unlocode = Column(String(10), nullable=True, comment="UNLOCODE")

    # 위치 정보
    sourcelatitude = Column(Float, nullable=True, comment="위도")
    sourcelongitude = Column(Float, nullable=True, comment="경도")

    # 시스템 필드
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # 관계 설정
    users = relationship("User", back_populates="company")

    # 인덱스 설정
    __table_args__ = (
        Index('idx_company_id', 'company_id'),
        Index('idx_company_email', 'email'),
        Index('idx_company_installation', 'Installation'),
        Index('idx_company_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Company(id={self.id}, company_id='{self.company_id}', Installation='{self.Installation}')>"

    def to_dict(self):
        """기업 정보를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "company_id": self.company_id,
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
            "sourcelatitude": self.sourcelatitude,
            "sourcelongitude": self.sourcelongitude,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
