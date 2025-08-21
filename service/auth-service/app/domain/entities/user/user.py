from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

# 순환 import 방지를 위해 여기서 Base 생성
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class User(Base):
    """사용자 엔티티 - 기업 소속 사용자"""
    __tablename__ = "users"

    # 기본 필드
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # 로그인 정보
    username = Column(String(100), unique=True, index=True, nullable=False, comment="사용자명 (로그인용)")
    hashed_password = Column(String(255), nullable=False, comment="해시된 비밀번호")

    # 사용자 정보
    full_name = Column(String(100), nullable=False, comment="전체 이름")

    # 기업 연결
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, comment="소속 기업 ID")
    company = relationship("Company", back_populates="users")

    # 권한 정보
    role = Column(String(50), nullable=False, default="user", comment="사용자 역할")
    permissions = Column(Text, nullable=False, default="{}", comment="권한 정보 (JSON)")

    # 권한 플래그
    is_company_admin = Column(Boolean, nullable=False, default=False, comment="기업 관리자 여부")
    can_manage_users = Column(Boolean, nullable=False, default=False, comment="사용자 관리 권한")
    can_view_reports = Column(Boolean, nullable=False, default=True, comment="보고서 조회 권한")
    can_edit_data = Column(Boolean, nullable=False, default=True, comment="데이터 편집 권한")
    can_export_data = Column(Boolean, nullable=False, default=True, comment="데이터 내보내기 권한")

    # 상태 정보
    is_active = Column(Boolean, nullable=False, default=True, comment="활성 상태")

    # 시스템 필드
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # 인덱스 설정
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_company_id', 'company_id'),
        Index('idx_user_role', 'role'),
        Index('idx_user_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', full_name='{self.full_name}')>"

    def to_dict(self):
        """사용자 정보를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "username": self.username,
            "full_name": self.full_name,
            "company_id": self.company_id,
            "role": self.role,
            "permissions": json.loads(self.permissions) if self.permissions else {},
            "is_company_admin": self.is_company_admin,
            "can_manage_users": self.can_manage_users,
            "can_view_reports": self.can_view_reports,
            "can_edit_data": self.can_edit_data,
            "can_export_data": self.can_export_data,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def to_dict_with_company_info(self):
        """기업 정보를 포함한 사용자 정보를 딕셔너리로 변환"""
        user_info = self.to_dict()
        if self.company:
            user_info["company_info"] = {
                "company_id": self.company.company_id,
                "Installation": self.company.Installation,
                "Installation_en": self.company.Installation_en,
                "email": self.company.email,
                "telephone": self.company.telephone
            }
        return user_info
