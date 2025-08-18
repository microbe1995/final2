# ============================================================================
# ➡️ Arrow Repository - DB 접근 레이어 (독립적 DB 연결 포함)
# ============================================================================

import json
import os
from typing import Optional, List, AsyncGenerator
from datetime import datetime
from contextlib import asynccontextmanager
from loguru import logger

from sqlalchemy import String, Float, Boolean, Text, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import NullPool

from app.domain.arrow.arrow_entity import Arrow, ArrowType, Base
from app.domain.arrow.arrow_schema import (
    ArrowCreateRequest,
    ArrowUpdateRequest,
    ArrowResponse,
    ArrowListResponse
)

# Arrow 도메인 전용 DB 연결 클래스
class ArrowDatabaseConnection:
    """Arrow 도메인 전용 데이터베이스 연결 관리"""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """Arrow 도메인 DB 연결 초기화"""
        if self._is_initialized:
            return
            
        try:
            logger.info("➡️ Arrow 도메인 DB 연결 초기화 중...")
            
            # DB URL 가져오기
            db_url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_INTERNAL_URL")
            if not db_url:
                raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다")
            
            # PostgreSQL → asyncpg 변환
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            # 엔진 생성
            self._engine = create_async_engine(
                db_url,
                echo=False,
                poolclass=NullPool,
                connect_args={
                    "command_timeout": 30,
                    "server_settings": {
                        "application_name": "arrow_domain_service"
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
            
            # 연결 테스트 및 테이블 생성
            await self._test_connection()
            await self._create_tables()
            
            self._is_initialized = True
            logger.info("✅ Arrow 도메인 DB 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Arrow 도메인 DB 연결 초기화 실패: {str(e)}")
            raise
    
    async def _test_connection(self) -> None:
        """연결 테스트"""
        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Arrow 도메인 DB 연결 테스트 성공")
    
    async def _create_tables(self) -> None:
        """Arrow 테이블 생성"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Arrow 테이블 생성/확인 완료")
    
    @asynccontextmanager
    async def get_session(self):
        """세션 제공"""
        if not self._is_initialized:
            await self.initialize()
        
        session = self._session_factory()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Arrow DB 세션 오류: {str(e)}")
            raise
        finally:
            await session.close()
    
    async def close(self) -> None:
        """연결 종료"""
        if self._engine:
            await self._engine.dispose()
            logger.info("✅ Arrow 도메인 DB 연결 종료")
        self._is_initialized = False

# Arrow 도메인 전용 DB 연결 인스턴스
arrow_db = ArrowDatabaseConnection()


class ArrowRepository:
    """Arrow 데이터의 DB 접근을 담당합니다."""

    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory: dict[str, Arrow] = {}
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} Arrow 저장소 사용")

    def _to_response(self, arrow: Arrow) -> ArrowResponse:
        """Arrow Entity를 Response로 변환"""
        return ArrowResponse(**arrow.to_dict())

    async def create(self, request: ArrowCreateRequest) -> ArrowResponse:
        """새 Arrow를 생성합니다"""
        if not self.use_database:
            from uuid import uuid4
            arrow = Arrow(
                id=str(uuid4()),
                type=request.type,
                start_x=request.start_x,
                start_y=request.start_y,
                end_x=request.end_x,
                end_y=request.end_y,
                color=request.color or "#000000",
                width=request.width or 2.0,
                opacity=request.opacity or 1.0,
                canvas_id=request.canvas_id,
                name=request.name or "Arrow",
                description=request.description,
            )
            arrow.metadata = request.metadata or {}
            self._memory[arrow.id] = arrow
            return self._to_response(arrow)

        async with arrow_db.get_session() as session:
            from uuid import uuid4
            now = datetime.utcnow()
            arrow_id = str(uuid4())
            
            arrow = Arrow(
                id=arrow_id,
                type=request.type,
                start_x=request.start_x,
                start_y=request.start_y,
                end_x=request.end_x,
                end_y=request.end_y,
                color=request.color or "#000000",
                width=request.width or 2.0,
                opacity=request.opacity or 1.0,
                canvas_id=request.canvas_id,
                name=request.name or "Arrow",
                description=request.description,
                created_at=now,
                updated_at=now,
            )
            arrow.metadata = request.metadata or {}
            
            session.add(arrow)
            await session.commit()
            return self._to_response(arrow)

    async def get_by_id(self, arrow_id: str) -> Optional[ArrowResponse]:
        """ID로 Arrow를 조회합니다"""
        if not self.use_database:
            arrow = self._memory.get(arrow_id)
            return self._to_response(arrow) if arrow else None

        async with arrow_db.get_session() as session:
            result = await session.execute(select(Arrow).where(Arrow.id == arrow_id))
            arrow = result.scalar_one_or_none()
            return self._to_response(arrow) if arrow else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> ArrowListResponse:
        """모든 Arrow를 조회합니다"""
        if not self.use_database:
            arrows = list(self._memory.values())[skip:skip + limit]
            return ArrowListResponse(
                arrows=[self._to_response(arrow) for arrow in arrows],
                total=len(self._memory),
                skip=skip,
                limit=limit
            )

        async with arrow_db.get_session() as session:
            # 총 개수 조회
            count_result = await session.execute(select(Arrow).count())
            total = count_result.scalar()
            
            # 데이터 조회
            result = await session.execute(
                select(Arrow).offset(skip).limit(limit)
            )
            arrows = result.scalars().all()
            
            return ArrowListResponse(
                arrows=[self._to_response(arrow) for arrow in arrows],
                total=total,
                skip=skip,
                limit=limit
            )

    async def update(self, arrow_id: str, request: ArrowUpdateRequest) -> Optional[ArrowResponse]:
        """Arrow를 업데이트합니다"""
        if not self.use_database:
            arrow = self._memory.get(arrow_id)
            if not arrow:
                return None
            
            # 업데이트 로직
            for key, value in request.dict(exclude_unset=True).items():
                if hasattr(arrow, key):
                    setattr(arrow, key, value)
            arrow.updated_at = datetime.utcnow()
            
            return self._to_response(arrow)

        async with arrow_db.get_session() as session:
            result = await session.execute(select(Arrow).where(Arrow.id == arrow_id))
            arrow = result.scalar_one_or_none()
            
            if not arrow:
                return None
            
            # 업데이트
            update_data = request.dict(exclude_unset=True)
            update_data['updated_at'] = datetime.utcnow()
            
            for key, value in update_data.items():
                if hasattr(arrow, key):
                    setattr(arrow, key, value)
            
            await session.commit()
            return self._to_response(arrow)

    async def delete(self, arrow_id: str) -> bool:
        """Arrow를 삭제합니다"""
        if not self.use_database:
            return self._memory.pop(arrow_id, None) is not None

        async with arrow_db.get_session() as session:
            result = await session.execute(delete(Arrow).where(Arrow.id == arrow_id))
            await session.commit()
            return result.rowcount > 0

    async def get_by_canvas_id(self, canvas_id: str) -> List[ArrowResponse]:
        """Canvas ID로 Arrow들을 조회합니다"""
        if not self.use_database:
            arrows = [arrow for arrow in self._memory.values() if arrow.canvas_id == canvas_id]
            return [self._to_response(arrow) for arrow in arrows]

        async with arrow_db.get_session() as session:
            result = await session.execute(
                select(Arrow).where(Arrow.canvas_id == canvas_id)
            )
            arrows = result.scalars().all()
            return [self._to_response(arrow) for arrow in arrows]