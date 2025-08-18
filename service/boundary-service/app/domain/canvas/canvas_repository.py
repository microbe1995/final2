# ============================================================================
# 🗄️ Canvas Repository - DB 접근 레이어
# ============================================================================

import json
from typing import Optional, List
from datetime import datetime
from loguru import logger

from sqlalchemy import String, Float, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select, update, delete

from app.common.database.models import Base
from app.common.database.connection import db_connection
from app.domain.canvas.canvas_entity import Canvas
from app.domain.canvas.canvas_schema import CanvasCreateRequest, CanvasUpdateRequest, CanvasResponse, CanvasListResponse


class CanvasDB(Base):
    __tablename__ = "canvases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    width: Mapped[float] = mapped_column(Float, nullable=False, default=1200.0)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=800.0)
    background_color: Mapped[str] = mapped_column(String(16), nullable=False, default="#FFFFFF")

    zoom_level: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    pan_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pan_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    nodes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    edges_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class CanvasRepository:
    """Canvas 데이터의 DB 접근을 담당합니다."""

    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory: dict[str, Canvas] = {}
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} Canvas 저장소 사용")

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------
    def _to_response(self, canvas: Canvas) -> CanvasResponse:
        return CanvasResponse(**canvas.to_dict())

    # ---------------------------------------------------------------------
    # Create
    # ---------------------------------------------------------------------
    async def create(self, request: CanvasCreateRequest) -> CanvasResponse:
        if not self.use_database or db_connection.engine is None:
            from uuid import uuid4
            canvas = Canvas(
                id=str(uuid4()),
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

        async with db_connection.get_session_context() as session:
            from uuid import uuid4
            now = datetime.utcnow()
            canvas_id = str(uuid4())
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

        async with db_connection.get_session_context() as session:
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

        async with db_connection.get_session_context() as session:
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

        async with db_connection.get_session_context() as session:
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

        async with db_connection.get_session_context() as session:
            result = await session.execute(delete(CanvasDB).where(CanvasDB.id == canvas_id))
            await session.commit()
            return result.rowcount > 0


