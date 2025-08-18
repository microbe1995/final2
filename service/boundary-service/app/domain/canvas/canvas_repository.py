# ============================================================================
# 🗄️ Canvas Repository - DB 접근 레이어 (독립적 DB 연결 포함)
# ============================================================================

import json
import os
import uuid
import re
from typing import Optional, List, AsyncGenerator
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from loguru import logger

from sqlalchemy import String, Float, Boolean, Text, DateTime, text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import NullPool

from app.domain.canvas.canvas_entity import Canvas, Base
from app.domain.canvas.canvas_schema import CanvasCreateRequest, CanvasUpdateRequest, CanvasResponse, CanvasListResponse

# Canvas 도메인 전용 DB 연결 클래스
class CanvasDatabaseConnection:
    """Canvas 도메인 전용 데이터베이스 연결 관리"""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self._is_initialized = False
    
    async def initialize(self) -> None:
        """Canvas 도메인 DB 연결 초기화"""
        if self._is_initialized:
            return
            
        try:
            logger.info("🎨 Canvas 도메인 DB 연결 초기화 중...")
            
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
                        "application_name": "canvas_domain_service"
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
            logger.info("✅ Canvas 도메인 DB 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Canvas 도메인 DB 연결 초기화 실패: {str(e)}")
            raise
    
    async def _test_connection(self) -> None:
        """연결 테스트"""
        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Canvas 도메인 DB 연결 테스트 성공")
    
    async def _create_tables(self) -> None:
        """Canvas 테이블 생성"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Canvas 테이블 생성/확인 완료")
    
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
            logger.error(f"❌ Canvas DB 세션 오류: {str(e)}")
            raise
        finally:
            await session.close()
    
    async def close(self) -> None:
        """연결 종료"""
        if self._engine:
            await self._engine.dispose()
            logger.info("✅ Canvas 도메인 DB 연결 종료")
        self._is_initialized = False

# Canvas 도메인 전용 DB 연결 인스턴스
canvas_db = CanvasDatabaseConnection()


class CanvasRepository:
    """Canvas 데이터의 DB 접근을 담당합니다."""

    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory: dict[str, Canvas] = {}
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} Canvas 저장소 사용")
    
    # ============================================================================
    # 🔧 유틸리티 메서드들 (구 utility/helpers.py에서 이동)
    # ============================================================================
    
    def _generate_uuid(self) -> str:
        """Canvas ID 생성"""
        return str(uuid.uuid4())
    
    def _format_timestamp(self, timestamp: Optional[datetime] = None, 
                         format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """타임스탬프 포맷팅"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        return timestamp.strftime(format_str)
    
    def _sanitize_filename(self, filename: str) -> str:
        """파일명 정리 (Canvas 내보내기용)"""
        # 특수문자 제거
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # 연속 공백 제거
        filename = re.sub(r'\s+', ' ', filename)
        # 앞뒤 공백 제거
        filename = filename.strip()
        # 기본 이름 설정
        if not filename:
            filename = f"canvas_{self._format_timestamp(format_str='%Y%m%d_%H%M%S')}"
        return filename

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _to_response(self, canvas: Canvas) -> CanvasResponse:
        return CanvasResponse(**canvas.to_dict())

    # ---------------------------------------------------------------------
    # Create
    # ---------------------------------------------------------------------
    async def create(self, request: CanvasCreateRequest) -> CanvasResponse:
        if not self.use_database:
            canvas = Canvas(
                id=self._generate_uuid(),
                name=request.name,
                width=request.width or 1200.0,
                height=request.height or 800.0,
                background_color=request.background_color or "#FFFFFF",
                nodes=request.nodes or [],
                edges=request.edges or [],
                metadata=request.metadata or {},
            )
            self._memory[canvas.id] = canvas
            return self._to_response(canvas)

        async with canvas_db.get_session() as session:
            now = datetime.utcnow()
            canvas_id = self._generate_uuid()  # 새로운 유틸리티 메서드 사용
            db_obj = CanvasDB(
                id=canvas_id,
                name=request.name,
                description=request.description,
                width=request.width or 1200.0,
                height=request.height or 800.0,
                background_color=request.background_color or "#FFFFFF",
                zoom_level=1.0,
                pan_x=0.0,
                pan_y=0.0,
                nodes_json=json.dumps(request.nodes or []),
                edges_json=json.dumps(request.edges or []),
                metadata_json=json.dumps(request.metadata or {}),
                created_at=now,
                updated_at=now,
            )
            session.add(db_obj)
            await session.commit()
            return await self.get_by_id(canvas_id)  # type: ignore

    # ---------------------------------------------------------------------
    # Read
    # ---------------------------------------------------------------------
    async def get_by_id(self, canvas_id: str) -> Optional[CanvasResponse]:
        if not self.use_database or db_connection.engine is None:
            c = self._memory.get(canvas_id)
            return self._to_response(c) if c else None

        async with canvas_db.get_session() as session:
            result = await session.execute(select(CanvasDB).where(CanvasDB.id == canvas_id))
            row = result.scalar_one_or_none()
            if not row:
                return None
            canvas = Canvas(
                id=row.id,
                name=row.name,
                width=row.width,
                height=row.height,
                background_color=row.background_color,
                nodes=json.loads(row.nodes_json or "[]"),
                edges=json.loads(row.edges_json or "[]"),
                zoom_level=row.zoom_level,
                pan_x=row.pan_x,
                pan_y=row.pan_y,
                created_at=row.created_at,
                updated_at=row.updated_at,
                metadata=json.loads(row.metadata_json or "{}"),
            )
            return self._to_response(canvas)

    async def list_all(self, page: int = 1, size: int = 20) -> CanvasListResponse:
        if not self.use_database or db_connection.engine is None:
            items = list(self._memory.values())
            total = len(items)
            start = (page - 1) * size
            end = start + size
            return CanvasListResponse(
                canvases=[self._to_response(c) for c in items[start:end]],
                total=total,
                page=page,
                size=size,
            )

        async with canvas_db.get_session() as session:
            result = await session.execute(select(CanvasDB))
            rows = result.scalars().all()
            total = len(rows)
            start = (page - 1) * size
            end = start + size
            canvases = []
            for row in rows[start:end]:
                canvases.append(CanvasResponse(
                    id=row.id,
                    name=row.name,
                    description=row.description,
                    nodes=json.loads(row.nodes_json or "[]"),
                    edges=json.loads(row.edges_json or "[]"),
                    width=row.width,
                    height=row.height,
                    background_color=row.background_color,
                    zoom_level=row.zoom_level,
                    pan_x=row.pan_x,
                    pan_y=row.pan_y,
                    created_at=row.created_at.isoformat(),
                    updated_at=row.updated_at.isoformat(),
                    metadata=json.loads(row.metadata_json or "{}"),
                ))
            return CanvasListResponse(canvases=canvases, total=total, page=page, size=size)

    # ---------------------------------------------------------------------
    # Update
    # ---------------------------------------------------------------------
    async def update(self, canvas_id: str, request: CanvasUpdateRequest) -> Optional[CanvasResponse]:
        if not self.use_database or db_connection.engine is None:
            c = self._memory.get(canvas_id)
            if not c:
                return None
            if request.name is not None:
                c.name = request.name
            if request.width is not None:
                c.width = request.width
            if request.height is not None:
                c.height = request.height
            if request.background_color is not None:
                c.background_color = request.background_color
            if request.nodes is not None:
                c.nodes = request.nodes
            if request.edges is not None:
                c.edges = request.edges
            if request.zoom_level is not None:
                c.zoom_level = request.zoom_level
            if request.pan_x is not None:
                c.pan_x = request.pan_x
            if request.pan_y is not None:
                c.pan_y = request.pan_y
            if request.metadata is not None:
                c.metadata.update(request.metadata)
            c.updated_at = datetime.utcnow()
            return self._to_response(c)

        async with canvas_db.get_session() as session:
            values = {
                "updated_at": datetime.utcnow(),
            }
            if request.name is not None:
                values["name"] = request.name
            if request.width is not None:
                values["width"] = request.width
            if request.height is not None:
                values["height"] = request.height
            if request.background_color is not None:
                values["background_color"] = request.background_color
            if request.nodes is not None:
                values["nodes_json"] = json.dumps(request.nodes)
            if request.edges is not None:
                values["edges_json"] = json.dumps(request.edges)
            if request.zoom_level is not None:
                values["zoom_level"] = request.zoom_level
            if request.pan_x is not None:
                values["pan_x"] = request.pan_x
            if request.pan_y is not None:
                values["pan_y"] = request.pan_y
            if request.metadata is not None:
                values["metadata_json"] = json.dumps(request.metadata)

            await session.execute(update(CanvasDB).where(CanvasDB.id == canvas_id).values(**values))
            await session.commit()
            return await self.get_by_id(canvas_id)

    # ---------------------------------------------------------------------
    # Delete
    # ---------------------------------------------------------------------
    async def delete(self, canvas_id: str) -> bool:
        if not self.use_database or db_connection.engine is None:
            return self._memory.pop(canvas_id, None) is not None

        async with canvas_db.get_session() as session:
            result = await session.execute(delete(CanvasDB).where(CanvasDB.id == canvas_id))
            await session.commit()
            return result.rowcount > 0
    
    # ============================================================================
    # 🔍 DB 기반 검색 및 통계 (성능 최적화)
    # ============================================================================
    
    async def search_with_filters(self, filters: Dict[str, Any], page: int = 1, size: int = 20) -> CanvasListResponse:
        """DB 쿼리 기반 Canvas 검색 (성능 최적화)"""
        if not self.use_database:
            # 메모리 모드에서는 기존 로직 사용
            return await self._search_in_memory(filters, page, size)
        
        async with canvas_db.get_session() as session:
            # 동적 쿼리 구성
            query = select(CanvasDB)
            
            # 필터 조건 추가
            if filters.get("name"):
                query = query.where(CanvasDB.name.ilike(f"%{filters['name']}%"))
            
            if filters.get("min_width"):
                query = query.where(CanvasDB.width >= filters["min_width"])
            
            if filters.get("max_width"):
                query = query.where(CanvasDB.width <= filters["max_width"])
            
            if filters.get("min_height"):
                query = query.where(CanvasDB.height >= filters["min_height"])
            
            if filters.get("max_height"):
                query = query.where(CanvasDB.height <= filters["max_height"])
            
            if filters.get("background_color"):
                query = query.where(CanvasDB.background_color == filters["background_color"])
            
            # 전체 개수 조회
            count_query = select(func.count(CanvasDB.id)).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0
            
            # 페이지네이션 적용
            offset = (page - 1) * size
            query = query.offset(offset).limit(size).order_by(CanvasDB.created_at.desc())
            
            result = await session.execute(query)
            canvases = result.scalars().all()
            
            canvas_responses = [self._to_response(Canvas(
                id=c.id, name=c.name, width=c.width, height=c.height,
                background_color=c.background_color, zoom_level=c.zoom_level,
                pan_x=c.pan_x, pan_y=c.pan_y,
                nodes=json.loads(c.nodes_json) if c.nodes_json else [],
                edges=json.loads(c.edges_json) if c.edges_json else [],
                metadata=json.loads(c.metadata_json) if c.metadata_json else {},
                created_at=c.created_at, updated_at=c.updated_at
            )) for c in canvases]
            
            return CanvasListResponse(
                canvases=canvas_responses,
                total=total,
                page=page,
                size=size
            )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """DB 집계 함수 기반 Canvas 통계 (성능 최적화)"""
        if not self.use_database:
            return await self._get_memory_statistics()
        
        async with canvas_db.get_session() as session:
            # 기본 통계 쿼리
            stats_query = select(
                func.count(CanvasDB.id).label('total_canvases'),
                func.avg(CanvasDB.width).label('avg_width'),
                func.avg(CanvasDB.height).label('avg_height'),
                func.min(CanvasDB.created_at).label('oldest_canvas'),
                func.max(CanvasDB.created_at).label('newest_canvas')
            )
            
            stats_result = await session.execute(stats_query)
            stats = stats_result.first()
            
            # 배경색 분포 쿼리
            color_query = select(
                CanvasDB.background_color,
                func.count(CanvasDB.id).label('count')
            ).group_by(CanvasDB.background_color).order_by(func.count(CanvasDB.id).desc()).limit(5)
            
            color_result = await session.execute(color_query)
            color_distribution = [
                {"color": row.background_color, "count": row.count}
                for row in color_result
            ]
            
            # 크기별 분포 쿼리
            size_query = select(
                func.case(
                    (CanvasDB.width * CanvasDB.height < 500000, 'small'),
                    (CanvasDB.width * CanvasDB.height < 1000000, 'medium'),
                    else_='large'
                ).label('size_category'),
                func.count(CanvasDB.id).label('count')
            ).group_by('size_category')
            
            size_result = await session.execute(size_query)
            size_distribution = {row.size_category: row.count for row in size_result}
            
            return {
                "total_canvases": stats.total_canvases or 0,
                "average_canvas_size": {
                    "width": float(stats.avg_width or 0),
                    "height": float(stats.avg_height or 0)
                },
                "most_used_colors": color_distribution,
                "size_distribution": size_distribution,
                "date_range": {
                    "oldest": stats.oldest_canvas.isoformat() if stats.oldest_canvas else None,
                    "newest": stats.newest_canvas.isoformat() if stats.newest_canvas else None
                }
            }
    
    async def _search_in_memory(self, filters: Dict[str, Any], page: int, size: int) -> CanvasListResponse:
        """메모리 모드 검색 (폴백)"""
        filtered_canvases = []
        for canvas in self._memory.values():
            if filters.get("name") and filters["name"].lower() not in canvas.name.lower():
                continue
            if filters.get("min_width") and canvas.width < filters["min_width"]:
                continue
            if filters.get("max_width") and canvas.width > filters["max_width"]:
                continue
            if filters.get("min_height") and canvas.height < filters["min_height"]:
                continue
            if filters.get("max_height") and canvas.height > filters["max_height"]:
                continue
            filtered_canvases.append(canvas)
        
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated = filtered_canvases[start_idx:end_idx]
        
        return CanvasListResponse(
            canvases=[self._to_response(c) for c in paginated],
            total=len(filtered_canvases),
            page=page,
            size=size
        )
    
    async def _get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 모드 통계 (폴백)"""
        if not self._memory:
            return {"total_canvases": 0, "average_canvas_size": {"width": 0, "height": 0}}
        
        total = len(self._memory)
        total_width = sum(c.width for c in self._memory.values())
        total_height = sum(c.height for c in self._memory.values())
        
        return {
            "total_canvases": total,
            "average_canvas_size": {
                "width": total_width / total,
                "height": total_height / total
            }
        }


