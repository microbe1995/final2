from sqlalchemy import Column, Integer, String, DateTime, Index, Text, Boolean, Float
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.common.db import Base

class Admin(Base):
    """Admin(기업) 모델 (이미지 데이터 구조 기반) - 스트림 구조 지원"""
    __tablename__ = "admins"
    
    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # 계정 정보
    admin_id = Column(String(100), unique=True, index=True, nullable=False, comment="Admin 로그인 ID")
    hashed_password = Column(String(255), nullable=False, comment="해시된 비밀번호")
    
    # 사용자 직접 입력 필드
    Installation = Column(String(255), nullable=False, comment="사업장명")
    Installation_en = Column(String(255), nullable=True, comment="사업장영문명")
    economic_activity = Column(String(200), nullable=True, comment="업종명")
    economic_activity_en = Column(String(200), nullable=True, comment="업종영문명")
    representative = Column(String(100), nullable=True, comment="대표자명")
    representative_en = Column(String(100), nullable=True, comment="영문대표자명")
    email = Column(String(255), nullable=True, comment="이메일")
    telephone = Column(String(20), nullable=True, comment="전화번호")
    
    # 주소 검색 모달을 통해 자동 입력되는 필드
    street = Column(String(255), nullable=True, comment="도로명")
    street_en = Column(String(255), nullable=True, comment="도로영문명")
    number = Column(String(50), nullable=True, comment="건물번호")
    number_en = Column(String(50), nullable=True, comment="건물번호영문명")
    postcode = Column(String(20), nullable=True, comment="우편번호")
    city = Column(String(100), nullable=True, comment="도시명")
    city_en = Column(String(100), nullable=True, comment="도시영문명")
    country = Column(String(100), nullable=True, comment="국가명")
    country_en = Column(String(100), nullable=True, comment="국가영문명")
    unlocode = Column(String(20), nullable=True, comment="UNLOCODE")
    sourcelatitude = Column(Float, nullable=True, comment="사업장위도")
    sourcelongitude = Column(Float, nullable=True, comment="사업장경도")
    
    # 스트림 구조 필드
    stream_id = Column(String(100), nullable=True, index=True, comment="스트림 식별자")
    stream_version = Column(Integer, default=1, nullable=False, comment="스트림 버전")
    stream_metadata = Column(Text, nullable=True, comment="스트림 메타데이터 (JSON)")
    is_stream_active = Column(Boolean, default=True, nullable=False, comment="스트림 활성 상태")
    
    # 시스템 필드
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_admin_uuid', 'uuid'),
        Index('idx_admin_id', 'admin_id'),
        Index('idx_admin_installation', 'Installation'),
        Index('idx_admin_postcode', 'postcode'),
        Index('idx_admin_city', 'city'),
        Index('idx_admin_country', 'country'),
        Index('idx_admin_stream_id', 'stream_id'),
        Index('idx_admin_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Admin(id={self.id}, uuid='{self.uuid}', Installation='{self.Installation}', admin_id='{self.admin_id}')>"
    
    def to_dict(self):
        """Admin 정보를 딕셔너리로 변환"""
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
            "sourcelatitude": self.sourcelatitude,
            "sourcelongitude": self.sourcelongitude,
            "stream_id": self.stream_id,
            "stream_version": self.stream_version,
            "stream_metadata": self.stream_metadata,
            "is_stream_active": self.is_stream_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self):
        """공개용 Admin 정보 (민감한 정보 제외)"""
        return {
            "id": self.id,
            "uuid": self.uuid,
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
            "stream_id": self.stream_id,
            "stream_version": self.stream_version,
            "is_stream_active": self.is_stream_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_user_count(self) -> int:
        """소속 사용자 수 반환"""
        return len(self.users) if self.users else 0
    
    def get_active_users(self):
        """활성 사용자 목록 반환"""
        return [user for user in self.users if user.is_active]
    
    def get_users_by_role(self, role: str):
        """특정 역할의 사용자 목록 반환"""
        return [user for user in self.users if user.role == role and user.is_active]
    
    def can_manage_user(self, user_id: int) -> bool:
        """특정 사용자 관리 권한 확인"""
        user = next((u for u in self.users if u.id == user_id), None)
        if not user:
            return False
        
        # Admin은 모든 사용자 관리 가능
        return True
    
    def update_stream_version(self):
        """스트림 버전 업데이트"""
        self.stream_version += 1
        self.updated_at = func.now()
    
    def set_stream_metadata(self, metadata: dict):
        """스트림 메타데이터 설정"""
        import json
        self.stream_metadata = json.dumps(metadata, ensure_ascii=False)
        self.update_stream_version()
