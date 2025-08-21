# ============================================================================
# 🖱️ Viewport Repository - ReactFlow 뷰포트 데이터 접근
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import StaticPool

from app.common.database_base import Base
from app.domain.Viewport.Viewport_entity import ReactFlowViewport

# ============================================================================
# 🗄️ 뷰포트 데이터베이스 연결
# ============================================================================

class ViewportDatabaseConnection:
    """뷰포트 데이터베이스 연결 관리"""
    
    def __init__(self):
        self._is_initialized = False
        self.SessionLocal = None
        self.engine = None
    
    async def initialize(self):
        """데이터베이스 초기화"""
        if self._is_initialized:
            return
        
        try:
            # PostgreSQL 연결 설정
            from app.common.database import get_database_url
            database_url = await get_database_url()
            
            if database_url:
                from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
                
                self.engine = create_async_engine(database_url, echo=False)
                self.SessionLocal = async_sessionmaker(
                    self.engine, 
                    class_=AsyncSession, 
                    expire_on_commit=False
                )
                self._is_initialized = True
                logging.info("✅ 뷰포트 데이터베이스 연결 성공")
            else:
                # 메모리 데이터베이스로 폴백
                self.engine = create_engine(
                    "sqlite:///:memory:",
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool
                )
                self.SessionLocal = lambda: self.engine.connect()
                self._is_initialized = True
                logging.info("⚠️ 뷰포트 메모리 데이터베이스 사용")
                
        except Exception as e:
            logging.error(f"❌ 뷰포트 데이터베이스 초기화 실패: {str(e)}")
            # 메모리 데이터베이스로 폴백
            self.engine = create_engine(
                "sqlite:///:memory:",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
            self.SessionLocal = lambda: self.engine.connect()
            self._is_initialized = True
            logging.info("⚠️ 뷰포트 메모리 데이터베이스 폴백")
    
    async def get_session_context(self):
        """세션 컨텍스트 매니저"""
        if not self._is_initialized:
            await self.initialize()
        
        session = self.SessionLocal()
        try:
            yield session
        finally:
            await session.close()

# ============================================================================
# 🗄️ 뷰포트 저장소
# ============================================================================

class ViewportRepository:
    """뷰포트 데이터 접근 클래스"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory_viewports: Dict[str, Dict[str, Any]] = {}
        self._db_connection = ViewportDatabaseConnection() if use_database else None
    
    # ============================================================================
    # 🖱️ 뷰포트 기본 CRUD 메서드
    # ============================================================================
    
    async def create_viewport(self, viewport_data: Dict[str, Any]) -> Dict[str, Any]:
        """뷰포트 생성"""
        if self.use_database and self._db_connection:
            return await self._create_viewport_db(viewport_data)
        else:
            return await self._create_viewport_memory(viewport_data)
    
    async def get_viewport_by_id(self, viewport_id: str) -> Optional[Dict[str, Any]]:
        """뷰포트 ID로 조회"""
        if self.use_database and self._db_connection:
            return await self._get_viewport_by_id_db(viewport_id)
        else:
            return await self._get_viewport_by_id_memory(viewport_id)
    
    async def get_viewport_by_flow_id(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """플로우 ID로 뷰포트 조회"""
        if self.use_database and self._db_connection:
            return await self._get_viewport_by_flow_id_db(flow_id)
        else:
            return await self._get_viewport_by_flow_id_memory(flow_id)
    
    async def update_viewport(self, viewport_id: str, viewport_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """뷰포트 수정"""
        if self.use_database and self._db_connection:
            return await self._update_viewport_db(viewport_id, viewport_data)
        else:
            return await self._update_viewport_memory(viewport_id, viewport_data)
    
    async def delete_viewport(self, viewport_id: str) -> bool:
        """뷰포트 삭제"""
        if self.use_database and self._db_connection:
            return await self._delete_viewport_db(viewport_id)
        else:
            return await self._delete_viewport_memory(viewport_id)
    
    async def get_all_viewports(self) -> List[Dict[str, Any]]:
        """모든 뷰포트 조회"""
        if self.use_database and self._db_connection:
            return await self._get_all_viewports_db()
        else:
            return await self._get_all_viewports_memory()
    
    # ============================================================================
    # 🖱️ 뷰포트 특수 쿼리 메서드
    # ============================================================================
    
    async def update_viewport_state(self, flow_id: str, viewport_state: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """뷰포트 상태 업데이트"""
        viewport = await self.get_viewport_by_flow_id(flow_id)
        if not viewport:
            return None
        
        update_data = {
            "viewport": viewport_state,
            "updated_at": datetime.utcnow()
        }
        
        return await self.update_viewport(viewport["id"], update_data)
    
    async def update_viewport_settings(self, flow_id: str, settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """뷰포트 설정 업데이트"""
        viewport = await self.get_viewport_by_flow_id(flow_id)
        if not viewport:
            return None
        
        update_data = {
            "settings": settings,
            "updated_at": datetime.utcnow()
        }
        
        return await self.update_viewport(viewport["id"], update_data)
    
    async def get_viewport_stats(self) -> Dict[str, Any]:
        """뷰포트 통계 조회"""
        viewports = await self.get_all_viewports()
        
        if not viewports:
            return {
                "total_viewports": 0,
                "average_zoom": 1.0,
                "most_used_zoom": 1.0,
                "pan_usage_count": 0,
                "zoom_usage_count": 0
            }
        
        total_viewports = len(viewports)
        zoom_levels = [v.get("viewport", {}).get("zoom", 1.0) for v in viewports]
        average_zoom = sum(zoom_levels) / len(zoom_levels)
        
        # 가장 많이 사용된 줌 레벨 (간단한 구현)
        most_used_zoom = max(set(zoom_levels), key=zoom_levels.count)
        
        return {
            "total_viewports": total_viewports,
            "average_zoom": round(average_zoom, 2),
            "most_used_zoom": most_used_zoom,
            "pan_usage_count": total_viewports,  # 실제로는 사용 로그에서 계산
            "zoom_usage_count": total_viewports   # 실제로는 사용 로그에서 계산
        }
    
    # ============================================================================
    # 🗄️ 데이터베이스 메서드들
    # ============================================================================
    
    async def _create_viewport_db(self, viewport_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 뷰포트 생성"""
        try:
            async with self._db_connection.get_session_context() as session:
                viewport = ReactFlowViewport(
                    id=viewport_data.get("id"),
                    flow_id=viewport_data.get("flow_id"),
                    x=viewport_data.get("viewport", {}).get("x", 0.0),
                    y=viewport_data.get("viewport", {}).get("y", 0.0),
                    zoom=viewport_data.get("viewport", {}).get("zoom", 1.0),
                    min_zoom=viewport_data.get("settings", {}).get("minZoom", 0.1),
                    max_zoom=viewport_data.get("settings", {}).get("maxZoom", 5.0),
                    pan_enabled=str(viewport_data.get("settings", {}).get("panEnabled", True)).lower(),
                    zoom_enabled=str(viewport_data.get("settings", {}).get("zoomEnabled", True)).lower(),
                    settings_json=viewport_data.get("settings"),
                    metadata_json=viewport_data.get("metadata")
                )
                
                session.add(viewport)
                await session.commit()
                await session.refresh(viewport)
                
                return viewport.to_dict()
                
        except Exception as e:
            logging.error(f"❌ 뷰포트 데이터베이스 생성 실패: {str(e)}")
            raise
    
    async def _get_viewport_by_id_db(self, viewport_id: str) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 뷰포트 ID로 조회"""
        try:
            async with self._db_connection.get_session_context() as session:
                result = await session.execute(
                    select(ReactFlowViewport).where(ReactFlowViewport.id == viewport_id)
                )
                viewport = result.scalar_one_or_none()
                
                return viewport.to_dict() if viewport else None
                
        except Exception as e:
            logging.error(f"❌ 뷰포트 데이터베이스 조회 실패: {str(e)}")
            return None
    
    async def _get_viewport_by_flow_id_db(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 플로우 ID로 뷰포트 조회"""
        try:
            async with self._db_connection.get_session_context() as session:
                result = await session.execute(
                    select(ReactFlowViewport).where(ReactFlowViewport.flow_id == flow_id)
                )
                viewport = result.scalar_one_or_none()
                
                return viewport.to_dict() if viewport else None
                
        except Exception as e:
            logging.error(f"❌ 뷰포트 데이터베이스 조회 실패: {str(e)}")
            return None
    
    async def _update_viewport_db(self, viewport_id: str, viewport_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 뷰포트 수정"""
        try:
            async with self._db_connection.get_session_context() as session:
                update_fields = {}
                
                if "viewport" in viewport_data:
                    viewport = viewport_data["viewport"]
                    update_fields["x"] = viewport.get("x")
                    update_fields["y"] = viewport.get("y")
                    update_fields["zoom"] = viewport.get("zoom")
                
                if "settings" in viewport_data:
                    update_fields["settings_json"] = viewport_data["settings"]
                
                if "metadata" in viewport_data:
                    update_fields["metadata_json"] = viewport_data["metadata"]
                
                update_fields["updated_at"] = datetime.utcnow()
                
                await session.execute(
                    update(ReactFlowViewport)
                    .where(ReactFlowViewport.id == viewport_id)
                    .values(**update_fields)
                )
                await session.commit()
                
                return await self._get_viewport_by_id_db(viewport_id)
                
        except Exception as e:
            logging.error(f"❌ 뷰포트 데이터베이스 수정 실패: {str(e)}")
            return None
    
    async def _delete_viewport_db(self, viewport_id: str) -> bool:
        """데이터베이스에서 뷰포트 삭제"""
        try:
            async with self._db_connection.get_session_context() as session:
                await session.execute(
                    delete(ReactFlowViewport).where(ReactFlowViewport.id == viewport_id)
                )
                await session.commit()
                return True
                
        except Exception as e:
            logging.error(f"❌ 뷰포트 데이터베이스 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_viewports_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 모든 뷰포트 조회"""
        try:
            async with self._db_connection.get_session_context() as session:
                result = await session.execute(select(ReactFlowViewport))
                viewports = result.scalars().all()
                
                return [viewport.to_dict() for viewport in viewports]
                
        except Exception as e:
            logging.error(f"❌ 뷰포트 데이터베이스 목록 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 메서드들
    # ============================================================================
    
    async def _create_viewport_memory(self, viewport_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 뷰포트 생성"""
        viewport_id = viewport_data.get("id") or f"viewport_{len(self._memory_viewports) + 1}"
        
        viewport = {
            "id": viewport_id,
            "flow_id": viewport_data.get("flow_id"),
            "viewport": viewport_data.get("viewport", {"x": 0.0, "y": 0.0, "zoom": 1.0}),
            "settings": viewport_data.get("settings", {}),
            "metadata": viewport_data.get("metadata", {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self._memory_viewports[viewport_id] = viewport
        return viewport
    
    async def _get_viewport_by_id_memory(self, viewport_id: str) -> Optional[Dict[str, Any]]:
        """메모리에서 뷰포트 ID로 조회"""
        return self._memory_viewports.get(viewport_id)
    
    async def _get_viewport_by_flow_id_memory(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """메모리에서 플로우 ID로 뷰포트 조회"""
        for viewport in self._memory_viewports.values():
            if viewport.get("flow_id") == flow_id:
                return viewport
        return None
    
    async def _update_viewport_memory(self, viewport_id: str, viewport_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """메모리에서 뷰포트 수정"""
        if viewport_id not in self._memory_viewports:
            return None
        
        viewport = self._memory_viewports[viewport_id]
        
        if "viewport" in viewport_data:
            viewport["viewport"].update(viewport_data["viewport"])
        
        if "settings" in viewport_data:
            viewport["settings"].update(viewport_data["settings"])
        
        if "metadata" in viewport_data:
            viewport["metadata"].update(viewport_data["metadata"])
        
        viewport["updated_at"] = datetime.utcnow()
        
        return viewport
    
    async def _delete_viewport_memory(self, viewport_id: str) -> bool:
        """메모리에서 뷰포트 삭제"""
        if viewport_id in self._memory_viewports:
            del self._memory_viewports[viewport_id]
            return True
        return False
    
    async def _get_all_viewports_memory(self) -> List[Dict[str, Any]]:
        """메모리에서 모든 뷰포트 조회"""
        return list(self._memory_viewports.values())
