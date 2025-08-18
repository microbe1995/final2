# ============================================================================
# 🎨 Shape Repository - DB 접근 레이어 (독립적 DB 연결 포함)
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

from app.domain.shape.shape_entity import Shape, ShapeType
from app.common.database_base import Base
from app.domain.shape.shape_schema import (
    ShapeCreateRequest,
    ShapeUpdateRequest,
    ShapeResponse,
    ShapeListResponse
)

# Shape 도메인 전용 DB 연결 클래스
class ShapeDatabaseConnection:
    """Shape 도메인 전용 데이터베이스 연결 관리"""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """Shape 도메인 DB 연결 초기화"""
        if self._is_initialized:
            return
            
        try:
            logger.info("🔷 Shape 도메인 DB 연결 초기화 중...")
            
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
                        "application_name": "shape_domain_service"
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
            logger.info("✅ Shape 도메인 DB 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Shape 도메인 DB 연결 초기화 실패: {str(e)}")
            raise
    
    async def _test_connection(self) -> None:
        """연결 테스트"""
        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Shape 도메인 DB 연결 테스트 성공")
    
    async def _create_tables(self) -> None:
        """Shape 테이블 생성"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Shape 테이블 생성/확인 완료")
    
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
            logger.error(f"❌ Shape DB 세션 오류: {str(e)}")
            raise
        finally:
            await session.close()
    
    async def close(self) -> None:
        """연결 종료"""
        if self._engine:
            await self._engine.dispose()
            logger.info("✅ Shape 도메인 DB 연결 종료")
        self._is_initialized = False

# Shape 도메인 전용 DB 연결 인스턴스
shape_db = ShapeDatabaseConnection()


class ShapeRepository:
    """Shape 데이터의 DB 접근을 담당합니다."""

    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory: dict[str, Shape] = {}
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} Shape 저장소 사용")

    def _to_response(self, shape: Shape) -> ShapeResponse:
        """Shape Entity를 Response로 변환"""
        return ShapeResponse(**shape.to_dict())

    async def create(self, request: ShapeCreateRequest) -> ShapeResponse:
        """새 Shape를 생성합니다"""
        if not self.use_database:
            from uuid import uuid4
            shape = Shape(
                id=str(uuid4()),
                type=request.type,
                x=request.x,
                y=request.y,
                width=request.width,
                height=request.height,
                fill_color=request.fill_color or "#FFFFFF",
                stroke_color=request.stroke_color or "#000000",
                stroke_width=request.stroke_width or 1.0,
                opacity=request.opacity or 1.0,
                canvas_id=request.canvas_id,
                name=request.name or "Shape",
                description=request.description,
            )
            shape.metadata = request.metadata or {}
            self._memory[shape.id] = shape
            return self._to_response(shape)

        async with shape_db.get_session() as session:
            from uuid import uuid4
            now = datetime.utcnow()
            shape_id = str(uuid4())
            
            shape = Shape(
                id=shape_id,
                type=request.type,
                x=request.x,
                y=request.y,
                width=request.width,
                height=request.height,
                fill_color=request.fill_color or "#FFFFFF",
                stroke_color=request.stroke_color or "#000000",
                stroke_width=request.stroke_width or 1.0,
                opacity=request.opacity or 1.0,
                rotation=request.rotation or 0.0,
                scale_x=request.scale_x or 1.0,
                scale_y=request.scale_y or 1.0,
                canvas_id=request.canvas_id,
                name=request.name or "Shape",
                description=request.description,
                created_at=now,
                updated_at=now,
            )
            shape.metadata = request.metadata or {}
            
            session.add(shape)
            await session.commit()
            return self._to_response(shape)

    async def get_by_id(self, shape_id: str) -> Optional[ShapeResponse]:
        """ID로 Shape를 조회합니다"""
        if not self.use_database:
            shape = self._memory.get(shape_id)
            return self._to_response(shape) if shape else None

        async with shape_db.get_session() as session:
            result = await session.execute(select(Shape).where(Shape.id == shape_id))
            shape = result.scalar_one_or_none()
            return self._to_response(shape) if shape else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> ShapeListResponse:
        """모든 Shape를 조회합니다"""
        if not self.use_database:
            shapes = list(self._memory.values())[skip:skip + limit]
            return ShapeListResponse(
                shapes=[self._to_response(shape) for shape in shapes],
                total=len(self._memory),
                skip=skip,
                limit=limit
            )

        async with shape_db.get_session() as session:
            # 총 개수 조회
            count_result = await session.execute(select(Shape).count())
            total = count_result.scalar()
            
            # 데이터 조회
            result = await session.execute(
                select(Shape).offset(skip).limit(limit)
            )
            shapes = result.scalars().all()
            
            return ShapeListResponse(
                shapes=[self._to_response(shape) for shape in shapes],
                total=total,
                skip=skip,
                limit=limit
            )

    async def update(self, shape_id: str, request: ShapeUpdateRequest) -> Optional[ShapeResponse]:
        """Shape를 업데이트합니다"""
        if not self.use_database:
            shape = self._memory.get(shape_id)
            if not shape:
                return None
            
            # 업데이트 로직
            for key, value in request.dict(exclude_unset=True).items():
                if hasattr(shape, key):
                    setattr(shape, key, value)
            shape.updated_at = datetime.utcnow()
            
            return self._to_response(shape)

        async with shape_db.get_session() as session:
            result = await session.execute(select(Shape).where(Shape.id == shape_id))
            shape = result.scalar_one_or_none()
            
            if not shape:
                return None
            
            # 업데이트
            update_data = request.dict(exclude_unset=True)
            update_data['updated_at'] = datetime.utcnow()
            
            for key, value in update_data.items():
                if hasattr(shape, key):
                    setattr(shape, key, value)
            
            await session.commit()
            return self._to_response(shape)

    async def delete(self, shape_id: str) -> bool:
        """Shape를 삭제합니다"""
        if not self.use_database:
            return self._memory.pop(shape_id, None) is not None

        async with shape_db.get_session() as session:
            result = await session.execute(delete(Shape).where(Shape.id == shape_id))
            await session.commit()
            return result.rowcount > 0

    async def get_by_canvas_id(self, canvas_id: str) -> List[ShapeResponse]:
        """Canvas ID로 Shape들을 조회합니다"""
        if not self.use_database:
            shapes = [shape for shape in self._memory.values() if shape.canvas_id == canvas_id]
            return [self._to_response(shape) for shape in shapes]

        async with shape_db.get_session() as session:
            result = await session.execute(
                select(Shape).where(Shape.canvas_id == canvas_id)
            )
            shapes = result.scalars().all()
            return [self._to_response(shape) for shape in shapes]