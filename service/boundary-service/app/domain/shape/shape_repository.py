"""
도형 저장소 - 도형 정보의 데이터 접근 로직
boundary 서비스에서 도형 정보를 저장하고 조회

주요 기능:
- 도형 생성/조회/수정/삭제
- 도형 검색 및 필터링
- PostgreSQL 및 메모리 저장소 지원
- 자동 UUID 생성 및 타임스탬프 관리
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

import json
import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select, update, delete, text

from ...common.database.models import Base
from ...common.database.connection import db_connection
from ..shape.shape_entity import Shape, ShapeType
from ..shape.shape_schema import (
    ShapeCreateRequest,
    ShapeUpdateRequest,
    ShapeResponse,
    ShapeListResponse
)

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🗄️ Shape DB 모델
# ============================================================================

class ShapeDB(Base):
    """도형 데이터베이스 모델"""
    __tablename__ = "shapes"
    
    # 기본 필드
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    canvas_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 위치 및 크기
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    
    # 스타일 정보
    color: Mapped[str] = mapped_column(String(16), nullable=False, default="#3B82F6")
    stroke_width: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    fill_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    
    # 라벨 정보
    label: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    label_position: Mapped[str] = mapped_column(String(20), nullable=False, default="center")
    
    # 회전 정보
    rotation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # 표시 상태
    visible: Mapped[bool] = mapped_column(String(5), nullable=False, default="true")
    locked: Mapped[bool] = mapped_column(String(5), nullable=False, default="false")
    
    # 메타데이터
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 시간 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

# ============================================================================
# 📚 도형 저장소 클래스
# ============================================================================

class ShapeRepository:
    """
    도형 데이터 저장소
    
    주요 기능:
    - 도형 생성/조회/수정/삭제
    - 도형 검색 및 필터링
    - PostgreSQL 및 메모리 저장소 지원
    """
    
    def __init__(self, use_database: bool = True):
        """
        도형 저장소 초기화
        
        Args:
            use_database: PostgreSQL 사용 여부 (기본값: True)
        """
        self.use_database = use_database
        
        # 메모리 저장소는 항상 초기화 (fallback용)
        self._shapes: dict = {}
        
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} 도형 데이터베이스 저장소 사용")
    
    # ============================================================================
    # 📝 도형 CRUD 메서드
    # ============================================================================
    
    async def create_shape(self, shape: Shape) -> Shape:
        """
        도형 생성
        
        Args:
            shape: 생성할 도형 정보
            
        Returns:
            Shape: 생성된 도형 정보
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._create_shape_db(shape)
            else:
                return await self._create_shape_memory(shape)
        except Exception as e:
            logger.error(f"❌ 도형 생성 실패: {str(e)}")
            raise
    
    async def get_shape_by_id(self, shape_id: str) -> Optional[Shape]:
        """
        도형 ID로 도형 조회
        
        Args:
            shape_id: 조회할 도형 ID
            
        Returns:
            Optional[Shape]: 도형 정보 또는 None
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_shape_by_id_db(shape_id)
            else:
                return self._shapes.get(shape_id)
        except Exception as e:
            logger.error(f"❌ 도형 ID 조회 실패: {shape_id} - {str(e)}")
            return None
    
    async def update_shape(self, shape: Shape) -> Shape:
        """
        도형 정보 업데이트
        
        Args:
            shape: 업데이트할 도형 정보
            
        Returns:
            Shape: 업데이트된 도형 정보
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._update_shape_db(shape)
            else:
                return await self._update_shape_memory(shape)
        except Exception as e:
            logger.error(f"❌ 도형 업데이트 실패: {shape.id} - {str(e)}")
            raise
    
    async def delete_shape(self, shape_id: str) -> bool:
        """
        도형 삭제
        
        Args:
            shape_id: 삭제할 도형 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._delete_shape_db(shape_id)
            else:
                return await self._delete_shape_memory(shape_id)
        except Exception as e:
            logger.error(f"❌ 도형 삭제 실패: {shape_id} - {str(e)}")
            return False
    
    async def get_all_shapes(self) -> List[Shape]:
        """
        모든 도형 조회
        
        Returns:
            List[Shape]: 도형 목록
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_all_shapes_db()
            else:
                return list(self._shapes.values())
        except Exception as e:
            logger.error(f"❌ 모든 도형 조회 실패: {str(e)}")
            return []
    
    async def get_shapes_by_canvas(self, canvas_id: str) -> List[Shape]:
        """
        Canvas ID로 도형 목록 조회
        
        Args:
            canvas_id: Canvas ID
            
        Returns:
            List[Shape]: 도형 목록
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_shapes_by_canvas_db(canvas_id)
            else:
                return [shape for shape in self._shapes.values() if shape.canvas_id == canvas_id]
        except Exception as e:
            logger.error(f"❌ Canvas 도형 조회 실패: {canvas_id} - {str(e)}")
            return []
    
    async def get_shapes_by_type(self, shape_type: ShapeType) -> List[Shape]:
        """
        도형 타입별 조회
        
        Args:
            shape_type: 도형 타입
            
        Returns:
            List[Shape]: 도형 목록
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_shapes_by_type_db(shape_type)
            else:
                return [shape for shape in self._shapes.values() if shape.type == shape_type]
        except Exception as e:
            logger.error(f"❌ 도형 타입별 조회 실패: {shape_type} - {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드
    # ============================================================================
    
    async def _create_shape_db(self, shape: Shape) -> Shape:
        """PostgreSQL에 도형 생성"""
        try:
            async with db_connection.get_session_context() as session:
                shape_db = ShapeDB(
                    id=shape.id,
                    canvas_id=shape.canvas_id,
                    type=shape.type.value,
                    x=shape.x,
                    y=shape.y,
                    width=shape.width,
                    height=shape.height,
                    color=shape.color,
                    stroke_width=shape.stroke_width,
                    fill_color=shape.fill_color,
                    label=shape.label,
                    label_position=shape.label_position,
                    rotation=shape.rotation,
                    visible=str(shape.visible).lower(),
                    locked=str(shape.locked).lower(),
                    metadata_json=json.dumps(shape.metadata),
                    created_at=shape.created_at,
                    updated_at=shape.updated_at
                )
                
                session.add(shape_db)
                await session.commit()
                
                logger.info(f"✅ PostgreSQL 도형 생성 성공: {shape.id}")
                return shape
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 도형 생성 실패: {str(e)}")
            raise
    
    async def _get_shape_by_id_db(self, shape_id: str) -> Optional[Shape]:
        """PostgreSQL에서 도형 ID로 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(ShapeDB).where(ShapeDB.id == shape_id)
                )
                shape_data = result.scalar_one_or_none()
                
                if shape_data:
                    return Shape(
                        id=shape_data.id,
                        type=ShapeType(shape_data.type),
                        x=shape_data.x,
                        y=shape_data.y,
                        width=shape_data.width,
                        height=shape_data.height,
                        color=shape_data.color,
                        stroke_width=shape_data.stroke_width,
                        fill_color=shape_data.fill_color,
                        label=shape_data.label,
                        label_position=shape_data.label_position,
                        rotation=shape_data.rotation,
                        visible=shape_data.visible == "true",
                        locked=shape_data.locked == "true",
                        canvas_id=shape_data.canvas_id,
                        metadata=json.loads(shape_data.metadata_json or "{}"),
                        created_at=shape_data.created_at,
                        updated_at=shape_data.updated_at
                    )
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 도형 ID 조회 실패: {str(e)}")
            return None
    
    async def _update_shape_db(self, shape: Shape) -> Shape:
        """PostgreSQL에서 도형 정보 업데이트"""
        try:
            async with db_connection.get_session_context() as session:
                await session.execute(
                    update(ShapeDB).where(ShapeDB.id == shape.id).values(
                        canvas_id=shape.canvas_id,
                        type=shape.type.value,
                        x=shape.x,
                        y=shape.y,
                        width=shape.width,
                        height=shape.height,
                        color=shape.color,
                        stroke_width=shape.stroke_width,
                        fill_color=shape.fill_color,
                        label=shape.label,
                        label_position=shape.label_position,
                        rotation=shape.rotation,
                        visible=str(shape.visible).lower(),
                        locked=str(shape.locked).lower(),
                        metadata_json=json.dumps(shape.metadata),
                        updated_at=shape.updated_at
                    )
                )
                await session.commit()
                
                logger.info(f"✅ PostgreSQL 도형 업데이트 성공: {shape.id}")
                return shape
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 도형 업데이트 실패: {str(e)}")
            raise
    
    async def _delete_shape_db(self, shape_id: str) -> bool:
        """PostgreSQL에서 도형 삭제"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    delete(ShapeDB).where(ShapeDB.id == shape_id)
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 도형 삭제 성공: {shape_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 도형 삭제 실패: 도형을 찾을 수 없음 {shape_id}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 도형 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_shapes_db(self) -> List[Shape]:
        """PostgreSQL에서 모든 도형 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(select(ShapeDB))
                shapes_data = result.scalars().all()
                
                shapes = []
                for shape_data in shapes_data:
                    shape = Shape(
                        id=shape_data.id,
                        type=ShapeType(shape_data.type),
                        x=shape_data.x,
                        y=shape_data.y,
                        width=shape_data.width,
                        height=shape_data.height,
                        color=shape_data.color,
                        stroke_width=shape_data.stroke_width,
                        fill_color=shape_data.fill_color,
                        label=shape_data.label,
                        label_position=shape_data.label_position,
                        rotation=shape_data.rotation,
                        visible=shape_data.visible == "true",
                        locked=shape_data.locked == "true",
                        canvas_id=shape_data.canvas_id,
                        metadata=json.loads(shape_data.metadata_json or "{}"),
                        created_at=shape_data.created_at,
                        updated_at=shape_data.updated_at
                    )
                    shapes.append(shape)
                
                return shapes
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 모든 도형 조회 실패: {str(e)}")
            return []
    
    async def _get_shapes_by_canvas_db(self, canvas_id: str) -> List[Shape]:
        """PostgreSQL에서 Canvas별 도형 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(ShapeDB).where(ShapeDB.canvas_id == canvas_id)
                )
                shapes_data = result.scalars().all()
                
                shapes = []
                for shape_data in shapes_data:
                    shape = Shape(
                        id=shape_data.id,
                        type=ShapeType(shape_data.type),
                        x=shape_data.x,
                        y=shape_data.y,
                        width=shape_data.width,
                        height=shape_data.height,
                        color=shape_data.color,
                        stroke_width=shape_data.stroke_width,
                        fill_color=shape_data.fill_color,
                        label=shape_data.label,
                        label_position=shape_data.label_position,
                        rotation=shape_data.rotation,
                        visible=shape_data.visible == "true",
                        locked=shape_data.locked == "true",
                        canvas_id=shape_data.canvas_id,
                        metadata=json.loads(shape_data.metadata_json or "{}"),
                        created_at=shape_data.created_at,
                        updated_at=shape_data.updated_at
                    )
                    shapes.append(shape)
                
                return shapes
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL Canvas 도형 조회 실패: {str(e)}")
            return []
    
    async def _get_shapes_by_type_db(self, shape_type: ShapeType) -> List[Shape]:
        """PostgreSQL에서 타입별 도형 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(ShapeDB).where(ShapeDB.type == shape_type.value)
                )
                shapes_data = result.scalars().all()
                
                shapes = []
                for shape_data in shapes_data:
                    shape = Shape(
                        id=shape_data.id,
                        type=ShapeType(shape_data.type),
                        x=shape_data.x,
                        y=shape_data.y,
                        width=shape_data.width,
                        height=shape_data.height,
                        color=shape_data.color,
                        stroke_width=shape_data.stroke_width,
                        fill_color=shape_data.fill_color,
                        label=shape_data.label,
                        label_position=shape_data.label_position,
                        rotation=shape_data.rotation,
                        visible=shape_data.visible == "true",
                        locked=shape_data.locked == "true",
                        canvas_id=shape_data.canvas_id,
                        metadata=json.loads(shape_data.metadata_json or "{}"),
                        created_at=shape_data.created_at,
                        updated_at=shape_data.updated_at
                    )
                    shapes.append(shape)
                
                return shapes
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 타입별 도형 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_shape_memory(self, shape: Shape) -> Shape:
        """메모리에 도형 생성"""
        self._shapes[shape.id] = shape
        
        logger.info(f"✅ 메모리 도형 생성: {shape.id}")
        return shape
    
    async def _update_shape_memory(self, shape: Shape) -> Shape:
        """메모리에서 도형 정보 업데이트"""
        if shape.id in self._shapes:
            self._shapes[shape.id] = shape
            
            logger.info(f"✅ 메모리 도형 업데이트 성공: {shape.id}")
            return shape
        else:
            raise ValueError(f"도형을 찾을 수 없습니다: {shape.id}")
    
    async def _delete_shape_memory(self, shape_id: str) -> bool:
        """메모리에서 도형 삭제"""
        if shape_id in self._shapes:
            del self._shapes[shape_id]
            
            logger.info(f"✅ 메모리 도형 삭제 성공: {shape_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 도형 삭제 실패: 도형을 찾을 수 없음 {shape_id}")
            return False
