"""
화살표 저장소 - 화살표 정보의 데이터 접근 로직
boundary 서비스에서 화살표 정보를 저장하고 조회

주요 기능:
- 화살표 생성/조회/수정/삭제
- 화살표 검색 및 필터링
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
from sqlalchemy import String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select, update, delete, text

from app.common.database.models import Base
from app.common.database.connection import db_connection
from app.domain.arrow.arrow_entity import Arrow, ArrowType
from app.domain.arrow.arrow_schema import (
    ArrowCreateRequest,
    ArrowUpdateRequest,
    ArrowResponse,
    ArrowListResponse
)

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🗄️ Arrow DB 모델
# ============================================================================

class ArrowDB(Base):
    """화살표 데이터베이스 모델"""
    __tablename__ = "arrows"
    
    # 기본 필드
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    canvas_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 좌표 정보
    start_x: Mapped[float] = mapped_column(Float, nullable=False)
    start_y: Mapped[float] = mapped_column(Float, nullable=False)
    end_x: Mapped[float] = mapped_column(Float, nullable=False)
    end_y: Mapped[float] = mapped_column(Float, nullable=False)
    
    # 스타일 정보
    color: Mapped[str] = mapped_column(String(16), nullable=False, default="#000000")
    stroke_width: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    arrow_size: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    
    # 연결 정보
    source_shape_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    target_shape_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # 라벨 정보
    label: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    label_position: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    
    # 메타데이터
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 시간 필드
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

# ============================================================================
# 📚 화살표 저장소 클래스
# ============================================================================

class ArrowRepository:
    """
    화살표 데이터 저장소
    
    주요 기능:
    - 화살표 생성/조회/수정/삭제
    - 화살표 검색 및 필터링
    - PostgreSQL 및 메모리 저장소 지원
    """
    
    def __init__(self, use_database: bool = True):
        """
        화살표 저장소 초기화
        
        Args:
            use_database: PostgreSQL 사용 여부 (기본값: True)
        """
        self.use_database = use_database
        
        # 메모리 저장소는 항상 초기화 (fallback용)
        self._arrows: dict = {}
        
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} 화살표 데이터베이스 저장소 사용")
    
    # ============================================================================
    # 📝 화살표 CRUD 메서드
    # ============================================================================
    
    async def create_arrow(self, arrow: Arrow) -> Arrow:
        """
        화살표 생성
        
        Args:
            arrow: 생성할 화살표 정보
            
        Returns:
            Arrow: 생성된 화살표 정보
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._create_arrow_db(arrow)
            else:
                return await self._create_arrow_memory(arrow)
        except Exception as e:
            logger.error(f"❌ 화살표 생성 실패: {str(e)}")
            raise
    
    async def get_arrow_by_id(self, arrow_id: str) -> Optional[Arrow]:
        """
        화살표 ID로 화살표 조회
        
        Args:
            arrow_id: 조회할 화살표 ID
            
        Returns:
            Optional[Arrow]: 화살표 정보 또는 None
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_arrow_by_id_db(arrow_id)
            else:
                return self._arrows.get(arrow_id)
        except Exception as e:
            logger.error(f"❌ 화살표 ID 조회 실패: {arrow_id} - {str(e)}")
            return None
    
    async def update_arrow(self, arrow: Arrow) -> Arrow:
        """
        화살표 정보 업데이트
        
        Args:
            arrow: 업데이트할 화살표 정보
            
        Returns:
            Arrow: 업데이트된 화살표 정보
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._update_arrow_db(arrow)
            else:
                return await self._update_arrow_memory(arrow)
        except Exception as e:
            logger.error(f"❌ 화살표 업데이트 실패: {arrow.id} - {str(e)}")
            raise
    
    async def delete_arrow(self, arrow_id: str) -> bool:
        """
        화살표 삭제
        
        Args:
            arrow_id: 삭제할 화살표 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._delete_arrow_db(arrow_id)
            else:
                return await self._delete_arrow_memory(arrow_id)
        except Exception as e:
            logger.error(f"❌ 화살표 삭제 실패: {arrow_id} - {str(e)}")
            return False
    
    async def get_all_arrows(self) -> List[Arrow]:
        """
        모든 화살표 조회
        
        Returns:
            List[Arrow]: 화살표 목록
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_all_arrows_db()
            else:
                return list(self._arrows.values())
        except Exception as e:
            logger.error(f"❌ 모든 화살표 조회 실패: {str(e)}")
            return []
    
    async def get_arrows_by_canvas(self, canvas_id: str) -> List[Arrow]:
        """
        Canvas ID로 화살표 목록 조회
        
        Args:
            canvas_id: Canvas ID
            
        Returns:
            List[Arrow]: 화살표 목록
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_arrows_by_canvas_db(canvas_id)
            else:
                return [arrow for arrow in self._arrows.values() if arrow.canvas_id == canvas_id]
        except Exception as e:
            logger.error(f"❌ Canvas 화살표 조회 실패: {canvas_id} - {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드
    # ============================================================================
    
    async def _create_arrow_db(self, arrow: Arrow) -> Arrow:
        """PostgreSQL에 화살표 생성"""
        try:
            async with db_connection.get_session_context() as session:
                arrow_db = ArrowDB(
                    id=arrow.id,
                    canvas_id=arrow.canvas_id,
                    type=arrow.type.value,
                    start_x=arrow.start_x,
                    start_y=arrow.start_y,
                    end_x=arrow.end_x,
                    end_y=arrow.end_y,
                    color=arrow.color,
                    stroke_width=arrow.stroke_width,
                    arrow_size=arrow.arrow_size,
                    source_shape_id=arrow.source_shape_id,
                    target_shape_id=arrow.target_shape_id,
                    label=arrow.label,
                    label_position=arrow.label_position,
                    metadata_json=json.dumps(arrow.metadata),
                    created_at=arrow.created_at,
                    updated_at=arrow.updated_at
                )
                
                session.add(arrow_db)
                await session.commit()
                
                logger.info(f"✅ PostgreSQL 화살표 생성 성공: {arrow.id}")
                return arrow
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 화살표 생성 실패: {str(e)}")
            raise
    
    async def _get_arrow_by_id_db(self, arrow_id: str) -> Optional[Arrow]:
        """PostgreSQL에서 화살표 ID로 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(ArrowDB).where(ArrowDB.id == arrow_id)
                )
                arrow_data = result.scalar_one_or_none()
                
                if arrow_data:
                    return Arrow(
                        id=arrow_data.id,
                        canvas_id=arrow_data.canvas_id,
                        type=ArrowType(arrow_data.type),
                        start_x=arrow_data.start_x,
                        start_y=arrow_data.start_y,
                        end_x=arrow_data.end_x,
                        end_y=arrow_data.end_y,
                        color=arrow_data.color,
                        stroke_width=arrow_data.stroke_width,
                        arrow_size=arrow_data.arrow_size,
                        source_shape_id=arrow_data.source_shape_id,
                        target_shape_id=arrow_data.target_shape_id,
                        label=arrow_data.label,
                        label_position=arrow_data.label_position,
                        metadata=json.loads(arrow_data.metadata_json or "{}"),
                        created_at=arrow_data.created_at,
                        updated_at=arrow_data.updated_at
                    )
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 화살표 ID 조회 실패: {str(e)}")
            return None
    
    async def _update_arrow_db(self, arrow: Arrow) -> Arrow:
        """PostgreSQL에서 화살표 정보 업데이트"""
        try:
            async with db_connection.get_session_context() as session:
                await session.execute(
                    update(ArrowDB).where(ArrowDB.id == arrow.id).values(
                        canvas_id=arrow.canvas_id,
                        type=arrow.type.value,
                        start_x=arrow.start_x,
                        start_y=arrow.start_y,
                        end_x=arrow.end_x,
                        end_y=arrow.end_y,
                        color=arrow.color,
                        stroke_width=arrow.stroke_width,
                        arrow_size=arrow.arrow_size,
                        source_shape_id=arrow.source_shape_id,
                        target_shape_id=arrow.target_shape_id,
                        label=arrow.label,
                        label_position=arrow.label_position,
                        metadata_json=json.dumps(arrow.metadata),
                        updated_at=arrow.updated_at
                    )
                )
                await session.commit()
                
                logger.info(f"✅ PostgreSQL 화살표 업데이트 성공: {arrow.id}")
                return arrow
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 화살표 업데이트 실패: {str(e)}")
            raise
    
    async def _delete_arrow_db(self, arrow_id: str) -> bool:
        """PostgreSQL에서 화살표 삭제"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    delete(ArrowDB).where(ArrowDB.id == arrow_id)
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 화살표 삭제 성공: {arrow_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 화살표 삭제 실패: 화살표를 찾을 수 없음 {arrow_id}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 화살표 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_arrows_db(self) -> List[Arrow]:
        """PostgreSQL에서 모든 화살표 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(select(ArrowDB))
                arrows_data = result.scalars().all()
                
                arrows = []
                for arrow_data in arrows_data:
                    arrow = Arrow(
                        id=arrow_data.id,
                        canvas_id=arrow_data.canvas_id,
                        type=ArrowType(arrow_data.type),
                        start_x=arrow_data.start_x,
                        start_y=arrow_data.start_y,
                        end_x=arrow_data.end_x,
                        end_y=arrow_data.end_y,
                        color=arrow_data.color,
                        stroke_width=arrow_data.stroke_width,
                        arrow_size=arrow_data.arrow_size,
                        source_shape_id=arrow_data.source_shape_id,
                        target_shape_id=arrow_data.target_shape_id,
                        label=arrow_data.label,
                        label_position=arrow_data.label_position,
                        metadata=json.loads(arrow_data.metadata_json or "{}"),
                        created_at=arrow_data.created_at,
                        updated_at=arrow_data.updated_at
                    )
                    arrows.append(arrow)
                
                return arrows
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 모든 화살표 조회 실패: {str(e)}")
            return []
    
    async def _get_arrows_by_canvas_db(self, canvas_id: str) -> List[Arrow]:
        """PostgreSQL에서 Canvas별 화살표 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(ArrowDB).where(ArrowDB.canvas_id == canvas_id)
                )
                arrows_data = result.scalars().all()
                
                arrows = []
                for arrow_data in arrows_data:
                    arrow = Arrow(
                        id=arrow_data.id,
                        canvas_id=arrow_data.canvas_id,
                        type=ArrowType(arrow_data.type),
                        start_x=arrow_data.start_x,
                        start_y=arrow_data.start_y,
                        end_x=arrow_data.end_x,
                        end_y=arrow_data.end_y,
                        color=arrow_data.color,
                        stroke_width=arrow_data.stroke_width,
                        arrow_size=arrow_data.arrow_size,
                        source_shape_id=arrow_data.source_shape_id,
                        target_shape_id=arrow_data.target_shape_id,
                        label=arrow_data.label,
                        label_position=arrow_data.label_position,
                        metadata=json.loads(arrow_data.metadata_json or "{}"),
                        created_at=arrow_data.created_at,
                        updated_at=arrow_data.updated_at
                    )
                    arrows.append(arrow)
                
                return arrows
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL Canvas 화살표 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_arrow_memory(self, arrow: Arrow) -> Arrow:
        """메모리에 화살표 생성"""
        self._arrows[arrow.id] = arrow
        
        logger.info(f"✅ 메모리 화살표 생성: {arrow.id}")
        return arrow
    
    async def _update_arrow_memory(self, arrow: Arrow) -> Arrow:
        """메모리에서 화살표 정보 업데이트"""
        if arrow.id in self._arrows:
            self._arrows[arrow.id] = arrow
            
            logger.info(f"✅ 메모리 화살표 업데이트 성공: {arrow.id}")
            return arrow
        else:
            raise ValueError(f"화살표를 찾을 수 없습니다: {arrow.id}")
    
    async def _delete_arrow_memory(self, arrow_id: str) -> bool:
        """메모리에서 화살표 삭제"""
        if arrow_id in self._arrows:
            del self._arrows[arrow_id]
            
            logger.info(f"✅ 메모리 화살표 삭제 성공: {arrow_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 화살표 삭제 실패: 화살표를 찾을 수 없음 {arrow_id}")
            return False
