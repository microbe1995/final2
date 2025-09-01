# ============================================================================
# 🗄️ 공통 데이터베이스 Base 클래스
# ============================================================================

"""
모든 도메인에서 공통으로 사용할 SQLAlchemy Base 클래스

SQLAlchemy 2.0 호환성을 위해 DeclarativeBase를 사용합니다.
각 도메인별로 개별 Base를 생성하는 대신 공통 Base를 사용하여
메타데이터 충돌을 방지합니다.
"""

import os
import logging
from typing import Any, Optional
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON, create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, Session, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """SQLAlchemy 2.0 호환 Base 클래스"""
    pass

# ============================================================================
# 🗄️ 데이터베이스 연결 관리
# ============================================================================

def get_database_url() -> Optional[str]:
    """데이터베이스 URL 가져오기"""
    return os.getenv("DATABASE_URL")

def clean_database_url(url: str) -> str:
    """데이터베이스 URL에서 잘못된 파라미터 제거 및 Railway PostgreSQL 최적화"""
    import re
    
    # Railway PostgreSQL에서 발생할 수 있는 잘못된 파라미터들
    invalid_params = [
        'db_type', 'db_type=postgresql', 'db_type=postgres',
        'db_type=mysql', 'db_type=sqlite'
    ]
    
    # URL에서 잘못된 파라미터 제거
    for param in invalid_params:
        if param in url:
            url = url.replace(param, '')
            logger.warning(f"잘못된 데이터베이스 파라미터 제거: {param}")
    
    # 연속된 & 제거
    url = re.sub(r'&&+', '&', url)
    url = re.sub(r'&+$', '', url)
    
    # URL 시작이 ?로 시작하면 &로 변경
    if '?' in url and url.split('?')[1].startswith('&'):
        url = url.replace('?&', '?')
    
    return url

def create_database_engine(database_url: Optional[str] = None):
    """동기 데이터베이스 엔진 생성 (Railway PostgreSQL 최적화)"""
    try:
        if not database_url:
            database_url = get_database_url()
        
        if not database_url:
            logger.warning("DATABASE_URL이 설정되지 않음. SQLite 폴백 사용")
            return create_engine(
                "sqlite:///./cbam_fallback.db",
                pool_pre_ping=True,
                echo=False
            )
        
        # DATABASE_URL 정리
        clean_url = clean_database_url(database_url)
        
        # Railway PostgreSQL 최적화 설정 (collation 문제 해결)
        engine_params = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 20,
            'echo': False,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'cbam-service',
                # PostgreSQL collation 문제 해결을 위한 설정
                'options': '-c timezone=utc -c client_encoding=utf8'
            }
        }
        
        # SSL 모드 설정
        if 'postgresql' in clean_url.lower():
            if '?' in clean_url:
                clean_url += "&sslmode=require"
            else:
                clean_url += "?sslmode=require"
        
        logger.info(f"데이터베이스 연결 시도: {clean_url.split('@')[1] if '@' in clean_url else clean_url}")
        
        engine = create_engine(clean_url, **engine_params)
        
        # 연결 테스트 및 collation 문제 해결
        with engine.connect() as conn:
            # collation 버전 확인 및 업데이트
            try:
                result = conn.execute(text("SELECT current_setting('server_version_num')"))
                version = result.scalar()
                logger.info(f"PostgreSQL 버전: {version}")
                
                # collation 문제 해결을 위한 설정
                conn.execute(text("SET client_encoding = 'UTF8'"))
                conn.execute(text("SET timezone = 'UTC'"))
                
                # 기본 연결 테스트
                conn.execute(text("SELECT 1"))
                logger.info("✅ 데이터베이스 연결 성공")
                
            except Exception as e:
                logger.warning(f"데이터베이스 초기 설정 중 경고: {str(e)}")
                # 경고만 로그하고 계속 진행
        
        return engine
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 엔진 생성 실패: {str(e)}")
        # SQLite 폴백
        logger.info("SQLite 폴백 데이터베이스 사용")
        return create_engine(
            "sqlite:///./cbam_fallback.db",
            pool_pre_ping=True,
            echo=False
        )

def get_database_session() -> Session:
    """데이터베이스 세션 생성 (FastAPI 의존성 주입용)"""
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_db_session() -> Session:
    """데이터베이스 세션 생성 (기존 호환성 유지)"""
    return get_database_session()

def get_db() -> Session:
    """FastAPI 의존성 주입용 동기 데이터베이스 세션 생성"""
    return get_database_session()

def create_async_database_engine(database_url: Optional[str] = None):
    """비동기 데이터베이스 엔진 생성 (Railway PostgreSQL 최적화)"""
    try:
        if not database_url:
            database_url = get_database_url()
        
        if not database_url:
            logger.warning("DATABASE_URL이 설정되지 않음. SQLite 폴백 사용")
            return create_async_engine(
                "sqlite+aiosqlite:///./cbam_fallback.db",
                pool_pre_ping=True,
                echo=False
            )
        
        # DATABASE_URL 정리
        clean_url = clean_database_url(database_url)
        
        # PostgreSQL URL을 비동기 URL로 변환
        if 'postgresql://' in clean_url:
            async_url = clean_url.replace('postgresql://', 'postgresql+asyncpg://')
        elif 'postgres://' in clean_url:
            async_url = clean_url.replace('postgres://', 'postgresql+asyncpg://')
        else:
            async_url = clean_url
        
        # Railway PostgreSQL 최적화 설정
        engine_params = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 20,
            'echo': False,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'cbam-service',
                'options': '-c timezone=utc -c client_encoding=utf8'
            }
        }
        
        # SSL 모드 설정
        if 'postgresql' in async_url.lower():
            if '?' in async_url:
                async_url += "&sslmode=require"
            else:
                async_url += "?sslmode=require"
        
        logger.info(f"비동기 데이터베이스 연결 시도: {async_url.split('@')[1] if '@' in async_url else async_url}")
        
        engine = create_async_engine(async_url, **engine_params)
        
        return engine
        
    except Exception as e:
        logger.error(f"❌ 비동기 데이터베이스 엔진 생성 실패: {str(e)}")
        # SQLite 폴백
        logger.info("비동기 SQLite 폴백 데이터베이스 사용")
        return create_async_engine(
            "sqlite+aiosqlite:///./cbam_fallback.db",
            pool_pre_ping=True,
            echo=False
        )

def get_async_db() -> AsyncSession:
    """FastAPI 의존성 주입용 비동기 데이터베이스 세션 생성"""
    engine = create_async_database_engine()
    AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return AsyncSessionLocal()

# ============================================================================
# 🗄️ 데이터베이스 기본 엔티티
# ============================================================================

class DatabaseBase(Base):
    """데이터베이스 기본 엔티티"""
    
    __abstract__ = True
    
    id: Mapped[str] = mapped_column(Text(36), primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# 공통 Base 인스턴스 (모든 도메인에서 사용)
# Base = DatabaseBase

# 공통 필드를 가진 Base 클래스 (필요 시 사용)
class TimestampMixin:
    """생성/수정 시간 공통 필드"""
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class IdentityMixin:
    """ID 공통 필드"""
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)

# ============================================================================
# 📦 Export 설정
# ============================================================================

__all__ = [
    "Base",
    "get_database_session",
    "get_db_session",
    "get_db",
    "get_async_db",
    "create_database_engine",
    "create_async_database_engine",
    "DatabaseBase",
    "TimestampMixin",
    "IdentityMixin"
]
