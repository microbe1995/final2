"""
데이터베이스 연결 설정
PostgreSQL 연결 및 세션 관리
"""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .db_models import Base

# 로거 설정
logger = logging.getLogger(__name__)

class Database:
    """데이터베이스 연결 관리 클래스"""
    
    def __init__(self):
        """데이터베이스 초기화"""
        self.database_url = os.getenv("DATABASE_URL")
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        
        if not self.database_url:
            logger.warning("⚠️ DATABASE_URL 환경변수가 설정되지 않았습니다. 메모리 저장소를 사용합니다.")
            return
            
        self._setup_database()
    
    def _setup_database(self):
        """데이터베이스 연결 설정"""
        try:
            # Railway PostgreSQL URL을 asyncpg 형식으로 변환
            if self.database_url.startswith("postgresql://"):
                async_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            else:
                async_url = self.database_url
            
            # 동기 엔진 (테이블 생성용)
            self.engine = create_engine(
                self.database_url,
                poolclass=NullPool,  # Railway에서 권장
                echo=False
            )
            
            # 비동기 엔진 (실제 사용)
            self.async_engine = create_async_engine(
                async_url,
                poolclass=NullPool,  # Railway에서 권장
                echo=False
            )
            
            # 세션 팩토리 생성
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.AsyncSessionLocal = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.async_engine
            )
            
            logger.info("✅ 데이터베이스 연결 설정 완료")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 설정 실패: {str(e)}")
            self.database_url = None
    
    def create_tables(self):
        """테이블 생성 (없는 경우)"""
        if not self.engine:
            logger.warning("⚠️ 데이터베이스 연결이 설정되지 않았습니다.")
            return False
            
        try:
            # 테이블 존재 여부 확인
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 FROM users LIMIT 1"))
                logger.info("✅ users 테이블이 이미 존재합니다.")
                return True
        except Exception:
            try:
                # 테이블 생성
                Base.metadata.create_all(bind=self.engine)
                logger.info("✅ users 테이블 생성 완료")
                return True
            except Exception as e:
                logger.error(f"❌ 테이블 생성 실패: {str(e)}")
                return False
    
    def get_session(self):
        """동기 세션 반환"""
        if not self.SessionLocal:
            return None
        return self.SessionLocal()
    
    async def get_async_session(self) -> AsyncSession:
        """비동기 세션 반환"""
        if not self.AsyncSessionLocal:
            return None
        async with self.AsyncSessionLocal() as session:
            return session
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()
        if self.async_engine:
            self.async_engine.dispose()
        logger.info("🔌 데이터베이스 연결 종료")

# 전역 데이터베이스 인스턴스
database = Database()
