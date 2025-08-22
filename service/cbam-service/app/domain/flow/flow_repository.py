# ============================================================================
# 🌊 Flow Repository - ReactFlow 플로우 데이터 접근
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import StaticPool

from app.common.database_base import Base
from app.domain.flow.flow_entity import Flow

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🗄️ 데이터베이스 연결 관리
# ============================================================================

class FlowDatabaseConnection:
    """플로우 도메인 전용 데이터베이스 연결"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._is_initialized = False
    
    async def initialize(self, database_url: str = None):
        """데이터베이스 초기화"""
        if self._is_initialized:
            return
        
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
            
            if database_url:
                # PostgreSQL 연결
                self.engine = create_async_engine(
                    database_url,
                    echo=False,
                    pool_pre_ping=True
                )
            else:
                # SQLite 메모리 데이터베이스 (테스트용)
                self.engine = create_async_engine(
                    "sqlite+aiosqlite:///./flows.db",
                    echo=False,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False}
                )
            
            self.SessionLocal = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 테이블 생성
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self._is_initialized = True
            logger.info("✅ Flow 도메인 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Flow 도메인 데이터베이스 초기화 실패: {str(e)}")
            raise
    
    async def get_session_context(self):
        """세션 컨텍스트 매니저"""
        if not self._is_initialized:
            await self.initialize()
        
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def close(self):
        """연결 종료"""
        if self.engine:
            await self.engine.dispose()
            logger.info("✅ Flow 도메인 데이터베이스 연결 종료")

# 전역 데이터베이스 연결 인스턴스
flow_db = FlowDatabaseConnection()

# ============================================================================
# 📚 플로우 저장소 클래스
# ============================================================================

class FlowRepository:
    """플로우 데이터 접근 클래스"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory_flows: Dict[str, Dict[str, Any]] = {}
        
        if self.use_database:
            logger.info("✅ PostgreSQL 플로우 저장소 사용")
        else:
            logger.info("✅ 메모리 플로우 저장소 사용")
    
    # ============================================================================
    # 🌊 플로우 CRUD 메서드
    # ============================================================================
    
    async def create_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """플로우 생성"""
        try:
            if self.use_database:
                return await self._create_flow_db(flow_data)
            else:
                return await self._create_flow_memory(flow_data)
        except Exception as e:
            logger.error(f"❌ 플로우 생성 실패: {str(e)}")
            raise
    
    async def get_flow_by_id(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """플로우 ID로 조회"""
        try:
            if self.use_database:
                return await self._get_flow_by_id_db(flow_id)
            else:
                return self._memory_flows.get(flow_id)
        except Exception as e:
            logger.error(f"❌ 플로우 조회 실패: {str(e)}")
            return None
    
    async def update_flow(self, flow_id: str, flow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """플로우 수정"""
        try:
            if self.use_database:
                return await self._update_flow_db(flow_id, flow_data)
            else:
                return await self._update_flow_memory(flow_id, flow_data)
        except Exception as e:
            logger.error(f"❌ 플로우 수정 실패: {str(e)}")
            raise
    
    async def delete_flow(self, flow_id: str) -> bool:
        """플로우 삭제"""
        try:
            if self.use_database:
                return await self._delete_flow_db(flow_id)
            else:
                return await self._delete_flow_memory(flow_id)
        except Exception as e:
            logger.error(f"❌ 플로우 삭제 실패: {str(e)}")
            return False
    
    async def get_all_flows(self) -> List[Dict[str, Any]]:
        """모든 플로우 조회"""
        try:
            if self.use_database:
                return await self._get_all_flows_db()
            else:
                return list(self._memory_flows.values())
        except Exception as e:
            logger.error(f"❌ 전체 플로우 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드
    # ============================================================================
    
    async def _create_flow_db(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 플로우 생성"""
        try:
            async with flow_db.get_session_context() as session:
                flow_entity = Flow(
                    id=flow_data.get('id'),
                    name=flow_data.get('name'),
                    description=flow_data.get('description'),
                                # viewport_x=flow_data.get('viewport', {}).get('x', 0),  # Viewport 도메인으로 분리됨
            # viewport_y=flow_data.get('viewport', {}).get('y', 0),  # Viewport 도메인으로 분리됨
            # viewport_zoom=flow_data.get('viewport', {}).get('zoom', 1.0),  # Viewport 도메인으로 분리됨
                    settings_json=str(flow_data.get('settings', {})) if flow_data.get('settings') else None,
                    metadata_json=str(flow_data.get('flow_metadata', {})) if flow_data.get('flow_metadata') else None
                )
                
                session.add(flow_entity)
                await session.commit()
                await session.refresh(flow_entity)
                
                logger.info(f"✅ PostgreSQL 플로우 생성 성공: {flow_entity.id}")
                return flow_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 플로우 생성 실패: {str(e)}")
            raise
    
    async def _get_flow_by_id_db(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 플로우 ID로 조회"""
        try:
            async with flow_db.get_session_context() as session:
                result = await session.execute(
                    select(Flow).where(Flow.id == flow_id)
                )
                flow_entity = result.scalar_one_or_none()
                
                if flow_entity:
                    return flow_entity.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 플로우 조회 실패: {str(e)}")
            return None
    
    async def _update_flow_db(self, flow_id: str, flow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 플로우 수정"""
        try:
            async with flow_db.get_session_context() as session:
                # 업데이트할 필드만 추출
                update_fields = {}
                
                if 'name' in flow_data:
                    update_fields['name'] = flow_data['name']
                
                if 'description' in flow_data:
                    update_fields['description'] = flow_data['description']
                
                        # if 'viewport' in flow_data:  # Viewport 도메인으로 분리됨
        #     viewport = flow_data['viewport']
        #     update_fields['viewport_x'] = viewport.get('x')
        #     update_fields['viewport_y'] = viewport.get('y')
        #     update_fields['viewport_zoom'] = viewport.get('zoom')
                
                if 'settings' in flow_data:
                    update_fields['settings_json'] = str(flow_data['settings']) if flow_data['settings'] else None
                
                if 'flow_metadata' in flow_data:
                    update_fields['metadata_json'] = str(flow_data['flow_metadata']) if flow_data['flow_metadata'] else None
                
                if update_fields:
                    update_fields['updated_at'] = datetime.utcnow()
                    
                    await session.execute(
                        update(Flow).where(Flow.id == flow_id).values(**update_fields)
                    )
                    await session.commit()
                
                # 업데이트된 데이터 조회
                result = await session.execute(
                    select(Flow).where(Flow.id == flow_id)
                )
                updated_flow = result.scalar_one_or_none()
                
                if updated_flow:
                    logger.info(f"✅ PostgreSQL 플로우 수정 성공: {flow_id}")
                    return updated_flow.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 플로우 수정 실패: {str(e)}")
            raise
    
    async def _delete_flow_db(self, flow_id: str) -> bool:
        """PostgreSQL에서 플로우 삭제"""
        try:
            async with flow_db.get_session_context() as session:
                result = await session.execute(
                    delete(Flow).where(Flow.id == flow_id)
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 플로우 삭제 성공: {flow_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 플로우 삭제 실패: 플로우를 찾을 수 없음 {flow_id}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 플로우 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_flows_db(self) -> List[Dict[str, Any]]:
        """PostgreSQL에서 모든 플로우 조회"""
        try:
            async with flow_db.get_session_context() as session:
                result = await session.execute(select(Flow))
                flow_entities = result.scalars().all()
                
                return [flow.to_dict() for flow in flow_entities]
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 전체 플로우 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_flow_memory(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 플로우 생성"""
        flow_id = flow_data.get('id')
        self._memory_flows[flow_id] = {
            **flow_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ 메모리 플로우 생성: {flow_id}")
        return self._memory_flows[flow_id]
    
    async def _update_flow_memory(self, flow_id: str, flow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """메모리에서 플로우 수정"""
        if flow_id in self._memory_flows:
            self._memory_flows[flow_id].update(flow_data)
            self._memory_flows[flow_id]['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ 메모리 플로우 수정 성공: {flow_id}")
            return self._memory_flows[flow_id]
        else:
            return None
    
    async def _delete_flow_memory(self, flow_id: str) -> bool:
        """메모리에서 플로우 삭제"""
        if flow_id in self._memory_flows:
            del self._memory_flows[flow_id]
            
            logger.info(f"✅ 메모리 플로우 삭제 성공: {flow_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 플로우 삭제 실패: 플로우를 찾을 수 없음 {flow_id}")
            return False
