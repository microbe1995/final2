"""
데이터베이스 모델 - SQLAlchemy 기반
PostgreSQL 연결을 위한 테이블 스키마 정의

주요 기능:
- 사용자 테이블 스키마 정의
- 자동 UUID 생성
- 타임스탬프 자동 관리
- 인덱스 및 제약조건 설정
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

# ============================================================================
# 🗄️ SQLAlchemy Base 클래스
# ============================================================================

Base = declarative_base()

# ============================================================================
# 👥 사용자 데이터베이스 모델
# ============================================================================

class UserDB(Base):
    """
    사용자 데이터베이스 모델
    
    주요 속성:
    - id: 사용자 고유 ID (UUID, 자동 생성)
    - username: 사용자명 (한글, 영문, 숫자, 언더스코어 허용)
    - email: 이메일 주소 (고유, 인덱스)
    - full_name: 전체 이름
    - password_hash: 해시된 비밀번호
    - is_active: 계정 활성화 상태
    - created_at: 계정 생성 시간 (자동 설정)
    - updated_at: 계정 수정 시간 (자동 업데이트)
    - last_login: 마지막 로그인 시간
    """
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    password_hash = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserDB(id='{self.id}', username='{self.username}', email='{self.email}')>"
    
    def to_dict(self):
        """사용자 정보를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
