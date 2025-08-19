# ============================================================================
# 🔘 Handle Repository - ReactFlow 핸들 데이터 접근
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import StaticPool

from app.common.database_base import Base
from app.domain.handle.handle_entity import ReactFlowHandle

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🗄️ 데이터베이스 연결 관리
# ============================================================================

class HandleDatabaseConnection:
    """핸들 도메인 전용 데이터베이스 연결"""
    
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
                    "sqlite+aiosqlite:///./handles.db",
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
            logger.info("✅ Handle 도메인 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Handle 도메인 데이터베이스 초기화 실패: {str(e)}")
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
            logger.info("✅ Handle 도메인 데이터베이스 연결 종료")

# 전역 데이터베이스 연결 인스턴스
handle_db = HandleDatabaseConnection()

# ============================================================================
# 📚 핸들 저장소 클래스
# ============================================================================

class HandleRepository:
    """핸들 데이터 접근 클래스"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory_handles: Dict[str, Dict[str, Any]] = {}
        
        if self.use_database:
            logger.info("✅ PostgreSQL 핸들 저장소 사용")
        else:
            logger.info("✅ 메모리 핸들 저장소 사용")
    
    # ============================================================================
    # 🔘 핸들 CRUD 메서드
    # ============================================================================
    
    async def create_handle(self, handle_data: Dict[str, Any]) -> Dict[str, Any]:
        """핸들 생성"""
        try:
            if self.use_database:
                return await self._create_handle_db(handle_data)
            else:
                return await self._create_handle_memory(handle_data)
        except Exception as e:
            logger.error(f"❌ 핸들 생성 실패: {str(e)}")
            raise
    
    async def get_handle_by_id(self, handle_id: str) -> Optional[Dict[str, Any]]:
        """핸들 ID로 조회"""
        try:
            if self.use_database:
                return await self._get_handle_by_id_db(handle_id)
            else:
                return self._memory_handles.get(handle_id)
        except Exception as e:
            logger.error(f"❌ 핸들 조회 실패: {str(e)}")
            return None
    
    async def get_handles_by_node_id(self, node_id: str) -> List[Dict[str, Any]]:
        """노드 ID로 핸들들 조회"""
        try:
            if self.use_database:
                return await self._get_handles_by_node_id_db(node_id)
            else:
                return [h for h in self._memory_handles.values() if h['node_id'] == node_id]
        except Exception as e:
            logger.error(f"❌ 노드별 핸들 조회 실패: {str(e)}")
            return []
    
    async def get_handles_by_flow_id(self, flow_id: str) -> List[Dict[str, Any]]:
        """플로우 ID로 핸들들 조회"""
        try:
            if self.use_database:
                return await self._get_handles_by_flow_id_db(flow_id)
            else:
                return [h for h in self._memory_handles.values() if h['flow_id'] == flow_id]
        except Exception as e:
            logger.error(f"❌ 플로우별 핸들 조회 실패: {str(e)}")
            return []
    
    async def update_handle(self, handle_id: str, handle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """핸들 수정"""
        try:
            if self.use_database:
                return await self._update_handle_db(handle_id, handle_data)
            else:
                return await self._update_handle_memory(handle_id, handle_data)
        except Exception as e:
            logger.error(f"❌ 핸들 수정 실패: {str(e)}")
            raise
    
    async def delete_handle(self, handle_id: str) -> bool:
        """핸들 삭제"""
        try:
            if self.use_database:
                return await self._delete_handle_db(handle_id)
            else:
                return await self._delete_handle_memory(handle_id)
        except Exception as e:
            logger.error(f"❌ 핸들 삭제 실패: {str(e)}")
            return False
    
    async def get_all_handles(self) -> List[Dict[str, Any]]:
        """모든 핸들 조회"""
        try:
            if self.use_database:
                return await self._get_all_handles_db()
            else:
                return list(self._memory_handles.values())
        except Exception as e:
            logger.error(f"❌ 전체 핸들 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드
    # ============================================================================
    
    async def _create_handle_db(self, handle_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 핸들 생성"""
        try:
            async with handle_db.get_session_context() as session:
                handle_entity = ReactFlowHandle(
                    id=handle_data.get('id'),
                    node_id=handle_data.get('node_id'),
                    flow_id=handle_data.get('flow_id'),
                    type=handle_data.get('type', 'default'),
                    position=handle_data.get('position', 'left'),
                    style=str(handle_data.get('style', {})) if handle_data.get('style') else None,
                    data=str(handle_data.get('data', {})) if handle_data.get('data') else None,
                    is_connectable=handle_data.get('is_connectable', True),
                    is_valid_connection=handle_data.get('is_valid_connection', True)
                )
                
                session.add(handle_entity)
                await session.commit()
                await session.refresh(handle_entity)
                
                logger.info(f"✅ PostgreSQL 핸들 생성 성공: {handle_entity.id}")
                return handle_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 핸들 생성 실패: {str(e)}")
            raise
    
    async def _get_handle_by_id_db(self, handle_id: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 핸들 ID로 조회"""
        try:
            async with handle_db.get_session_context() as session:
                result = await session.execute(
                    select(ReactFlowHandle).where(ReactFlowHandle.id == handle_id)
                )
                handle_entity = result.scalar_one_or_none()
                
                if handle_entity:
                    return handle_entity.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 핸들 조회 실패: {str(e)}")
            return None
    
    async def _get_handles_by_node_id_db(self, node_id: str) -> List[Dict[str, Any]]:
        """PostgreSQL에서 노드 ID로 핸들들 조회"""
        try:
            async with handle_db.get_session_context() as session:
                result = await session.execute(
                    select(ReactFlowHandle).where(ReactFlowHandle.node_id == node_id)
                )
                handle_entities = result.scalars().all()
                
                return [handle.to_dict() for handle in handle_entities]
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 노드별 핸들 조회 실패: {str(e)}")
            return []
    
    async def _get_handles_by_flow_id_db(self, flow_id: str) -> List[Dict[str, Any]]:
        """PostgreSQL에서 플로우 ID로 핸들들 조회"""
        try:
            async with handle_db.get_session_context() as session:
                result = await session.execute(
                    select(ReactFlowHandle).where(ReactFlowHandle.flow_id == flow_id)
                )
                handle_entities = result.scalars().all()
                
                return [handle.to_dict() for handle in handle_entities]
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 플로우별 핸들 조회 실패: {str(e)}")
            return []
    
    async def _update_handle_db(self, handle_id: str, handle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 핸들 수정"""
        try:
            async with handle_db.get_session_context() as session:
                # 업데이트할 필드만 추출
                update_fields = {}
                
                if 'type' in handle_data:
                    update_fields['type'] = handle_data['type']
                
                if 'position' in handle_data:
                    update_fields['position'] = handle_data['position']
                
                if 'style' in handle_data:
                    update_fields['style'] = str(handle_data['style']) if handle_data['style'] else None
                
                if 'data' in handle_data:
                    update_fields['data'] = str(handle_data['data']) if handle_data['data'] else None
                
                if 'is_connectable' in handle_data:
                    update_fields['is_connectable'] = handle_data['is_connectable']
                
                if 'is_valid_connection' in handle_data:
                    update_fields['is_valid_connection'] = handle_data['is_valid_connection']
                
                if update_fields:
                    update_fields['updated_at'] = datetime.utcnow()
                    
                    await session.execute(
                        update(ReactFlowHandle).where(ReactFlowHandle.id == handle_id).values(**update_fields)
                    )
                    await session.commit()
                
                # 업데이트된 데이터 조회
                result = await session.execute(
                    select(ReactFlowHandle).where(ReactFlowHandle.id == handle_id)
                )
                updated_handle = result.scalar_one_or_none()
                
                if updated_handle:
                    logger.info(f"✅ PostgreSQL 핸들 수정 성공: {handle_id}")
                    return updated_handle.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 핸들 수정 실패: {str(e)}")
            raise
    
    async def _delete_handle_db(self, handle_id: str) -> bool:
        """PostgreSQL에서 핸들 삭제"""
        try:
            async with handle_db.get_session_context() as session:
                result = await session.execute(
                    delete(ReactFlowHandle).where(ReactFlowHandle.id == handle_id)
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 핸들 삭제 성공: {handle_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 핸들 삭제 실패: 핸들을 찾을 수 없음 {handle_id}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 핸들 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_handles_db(self) -> List[Dict[str, Any]]:
        """PostgreSQL에서 모든 핸들 조회"""
        try:
            async with handle_db.get_session_context() as session:
                result = await session.execute(select(ReactFlowHandle))
                handle_entities = result.scalars().all()
                
                return [handle.to_dict() for handle in handle_entities]
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 전체 핸들 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_handle_memory(self, handle_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 핸들 생성"""
        handle_id = handle_data.get('id')
        self._memory_handles[handle_id] = {
            **handle_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ 메모리 핸들 생성: {handle_id}")
        return self._memory_handles[handle_id]
    
    async def _update_handle_memory(self, handle_id: str, handle_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """메모리에서 핸들 수정"""
        if handle_id in self._memory_handles:
            self._memory_handles[handle_id].update(handle_data)
            self._memory_handles[handle_id]['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ 메모리 핸들 수정 성공: {handle_id}")
            return self._memory_handles[handle_id]
        else:
            return None
    
    async def _delete_handle_memory(self, handle_id: str) -> bool:
        """메모리에서 핸들 삭제"""
        if handle_id in self._memory_handles:
            del self._memory_handles[handle_id]
            
            logger.info(f"✅ 메모리 핸들 삭제 성공: {handle_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 핸들 삭제 실패: 핸들을 찾을 수 없음 {handle_id}")
            return False
