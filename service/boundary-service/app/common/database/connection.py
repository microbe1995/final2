# ============================================================================
# 🔌 Database Connection - 데이터베이스 연결 관리
# ============================================================================

"""
데이터베이스 연결을 관리하는 모듈

PostgreSQL 데이터베이스와의 연결을 설정하고 관리합니다.
"""

import asyncio
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import NullPool
from loguru import logger

from .config import db_config

class DatabaseConnection:
    """데이터베이스 연결 관리 클래스"""
    
    def __init__(self):
        """DatabaseConnection 초기화"""
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """데이터베이스 연결을 초기화합니다"""
        try:
            if self._is_initialized:
                logger.info("✅ 데이터베이스 연결이 이미 초기화되어 있습니다")
                return
            
            logger.info("🚀 데이터베이스 연결 초기화 중...")
            
            # 비동기 엔진 생성
            self._engine = create_async_engine(
                db_config.async_connection_string,
                echo=db_config.echo,
                poolclass=NullPool,  # 개발용으로 NullPool 사용
                connect_args={
                    "command_timeout": db_config.command_timeout,
                    "server_settings": {
                        "application_name": "cal_boundary_service"
                    }
                }
            )
            
            # 세션 팩토리 생성
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False
            )
            
            # 연결 테스트
            await self._test_connection()
            
            self._is_initialized = True
            logger.info("✅ 데이터베이스 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 초기화 실패: {str(e)}")
            raise
    
    async def _test_connection(self) -> None:
        """데이터베이스 연결을 테스트합니다"""
        try:
            async with self._engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ 데이터베이스 연결 테스트 성공")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 테스트 실패: {str(e)}")
            raise
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """데이터베이스 세션을 반환합니다"""
        if not self._is_initialized:
            await self.initialize()
        
        if not self._session_factory:
            raise RuntimeError("데이터베이스 세션 팩토리가 초기화되지 않았습니다")
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"❌ 데이터베이스 세션 오류: {str(e)}")
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_session_context(self):
        """컨텍스트 매니저로 데이터베이스 세션을 제공합니다"""
        if not self._is_initialized:
            await self.initialize()
        
        if not self._session_factory:
            raise RuntimeError("데이터베이스 세션 팩토리가 초기화되지 않았습니다")
        
        session = self._session_factory()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ 데이터베이스 세션 오류: {str(e)}")
            raise
        finally:
            await session.close()
    
    async def close(self) -> None:
        """데이터베이스 연결을 종료합니다"""
        try:
            if self._engine:
                await self._engine.dispose()
                logger.info("✅ 데이터베이스 연결 종료 완료")
            
            self._is_initialized = False
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 종료 실패: {str(e)}")
            raise
    
    @property
    def engine(self) -> Optional[AsyncEngine]:
        """데이터베이스 엔진을 반환합니다"""
        return self._engine
    
    @property
    def is_initialized(self) -> bool:
        """초기화 상태를 반환합니다"""
        return self._is_initialized
    
    async def health_check(self) -> bool:
        """데이터베이스 연결 상태를 확인합니다"""
        try:
            if not self._is_initialized:
                return False
            
            async with self._engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 헬스체크 실패: {str(e)}")
            return False

# 전역 데이터베이스 연결 인스턴스
db_connection = DatabaseConnection()

# 애플리케이션 시작 시 초기화
async def initialize_database():
    """데이터베이스를 초기화합니다"""
    await db_connection.initialize()

# 애플리케이션 종료 시 정리
async def close_database():
    """데이터베이스 연결을 종료합니다"""
    await db_connection.close()

# 의존성 주입용 함수
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 의존성 주입용 데이터베이스 세션"""
    async for session in db_connection.get_session():
        yield session
