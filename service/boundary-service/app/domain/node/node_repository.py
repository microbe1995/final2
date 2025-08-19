# ============================================================================
# 🔵 Node Repository - ReactFlow 노드 데이터 접근
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import StaticPool

from app.common.database_base import Base
from app.domain.node.node_entity import ReactFlowNode

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🗄️ 데이터베이스 연결 관리
# ============================================================================

class NodeDatabaseConnection:
    """노드 도메인 전용 데이터베이스 연결"""
    
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
                    "sqlite+aiosqlite:///./nodes.db",
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
            logger.info("✅ Node 도메인 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Node 도메인 데이터베이스 초기화 실패: {str(e)}")
            raise
    
    async def get_session_context(self):
        """세션 컨텍스트 매니저"""
        if not self._is_initialized:
            await self.initialize()
        
        async with self.SessionLocal() as session:
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
            logger.info("✅ Node 도메인 데이터베이스 연결 종료")

# 전역 데이터베이스 연결 인스턴스
node_db = NodeDatabaseConnection()

# ============================================================================
# 📚 노드 저장소 클래스
# ============================================================================

class NodeRepository:
    """노드 데이터 접근 클래스"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory_nodes: Dict[str, Dict[str, Any]] = {}
        
        if self.use_database:
            logger.info("✅ PostgreSQL 노드 저장소 사용")
        else:
            logger.info("✅ 메모리 노드 저장소 사용")
    
    # ============================================================================
    # 🔵 노드 CRUD 메서드
    # ============================================================================
    
    async def create_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """노드 생성"""
        try:
            if self.use_database:
                return await self._create_node_db(node_data)
            else:
                return await self._create_node_memory(node_data)
        except Exception as e:
            logger.error(f"❌ 노드 생성 실패: {str(e)}")
            raise
    
    async def get_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        """노드 ID로 조회"""
        try:
            if self.use_database:
                return await self._get_node_by_id_db(node_id)
            else:
                return self._memory_nodes.get(node_id)
        except Exception as e:
            logger.error(f"❌ 노드 조회 실패: {str(e)}")
            return None
    
    async def get_nodes_by_flow_id(self, flow_id: str) -> List[Dict[str, Any]]:
        """플로우 ID로 노드 목록 조회"""
        try:
            if self.use_database:
                return await self._get_nodes_by_flow_id_db(flow_id)
            else:
                return [node for node in self._memory_nodes.values() 
                       if node.get('flow_id') == flow_id]
        except Exception as e:
            logger.error(f"❌ 플로우별 노드 조회 실패: {str(e)}")
            return []
    
    async def update_node(self, node_id: str, node_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """노드 수정"""
        try:
            if self.use_database:
                return await self._update_node_db(node_id, node_data)
            else:
                return await self._update_node_memory(node_id, node_data)
        except Exception as e:
            logger.error(f"❌ 노드 수정 실패: {str(e)}")
            raise
    
    async def delete_node(self, node_id: str) -> bool:
        """노드 삭제"""
        try:
            if self.use_database:
                return await self._delete_node_db(node_id)
            else:
                return await self._delete_node_memory(node_id)
        except Exception as e:
            logger.error(f"❌ 노드 삭제 실패: {str(e)}")
            return False
    
    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        """모든 노드 조회"""
        try:
            if self.use_database:
                return await self._get_all_nodes_db()
            else:
                return list(self._memory_nodes.values())
        except Exception as e:
            logger.error(f"❌ 전체 노드 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드
    # ============================================================================
    
    async def _create_node_db(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 노드 생성"""
        try:
            async with node_db.get_session_context() as session:
                node_entity = ReactFlowNode(
                    id=node_data.get('id'),
                    flow_id=node_data.get('flow_id'),
                    node_type=node_data.get('type', 'default'),
                    position_x=node_data.get('position', {}).get('x', 0),
                    position_y=node_data.get('position', {}).get('y', 0),
                    data_json=str(node_data.get('data', {})),
                    width=node_data.get('width'),
                    height=node_data.get('height'),
                    draggable=node_data.get('draggable', True),
                    selectable=node_data.get('selectable', True),
                    deletable=node_data.get('deletable', True),
                    style_json=str(node_data.get('style', {})) if node_data.get('style') else None
                )
                
                session.add(node_entity)
                await session.commit()
                await session.refresh(node_entity)
                
                logger.info(f"✅ PostgreSQL 노드 생성 성공: {node_entity.id}")
                return node_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 노드 생성 실패: {str(e)}")
            raise
    
    async def _get_node_by_id_db(self, node_id: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 노드 ID로 조회"""
        try:
            async with node_db.get_session_context() as session:
                result = await session.execute(
                    select(ReactFlowNode).where(ReactFlowNode.id == node_id)
                )
                node_entity = result.scalar_one_or_none()
                
                if node_entity:
                    return node_entity.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 노드 조회 실패: {str(e)}")
            return None
    
    async def _get_nodes_by_flow_id_db(self, flow_id: str) -> List[Dict[str, Any]]:
        """PostgreSQL에서 플로우 ID로 노드 목록 조회"""
        try:
            async with node_db.get_session_context() as session:
                result = await session.execute(
                    select(ReactFlowNode).where(ReactFlowNode.flow_id == flow_id)
                )
                node_entities = result.scalars().all()
                
                return [node.to_dict() for node in node_entities]
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 플로우별 노드 조회 실패: {str(e)}")
            return []
    
    async def _update_node_db(self, node_id: str, node_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 노드 수정"""
        try:
            async with node_db.get_session_context() as session:
                # 업데이트할 필드만 추출
                update_fields = {}
                
                if 'position' in node_data:
                    update_fields['position_x'] = node_data['position'].get('x')
                    update_fields['position_y'] = node_data['position'].get('y')
                
                if 'data' in node_data:
                    update_fields['data_json'] = str(node_data['data'])
                
                if 'width' in node_data:
                    update_fields['width'] = node_data['width']
                
                if 'height' in node_data:
                    update_fields['height'] = node_data['height']
                
                if 'draggable' in node_data:
                    update_fields['draggable'] = node_data['draggable']
                
                if 'selectable' in node_data:
                    update_fields['selectable'] = node_data['selectable']
                
                if 'deletable' in node_data:
                    update_fields['deletable'] = node_data['deletable']
                
                if 'style' in node_data:
                    update_fields['style_json'] = str(node_data['style']) if node_data['style'] else None
                
                if update_fields:
                    update_fields['updated_at'] = datetime.utcnow()
                    
                    await session.execute(
                        update(ReactFlowNode).where(ReactFlowNode.id == node_id).values(**update_fields)
                    )
                    await session.commit()
                
                # 업데이트된 데이터 조회
                result = await session.execute(
                    select(ReactFlowNode).where(ReactFlowNode.id == node_id)
                )
                updated_node = result.scalar_one_or_none()
                
                if updated_node:
                    logger.info(f"✅ PostgreSQL 노드 수정 성공: {node_id}")
                    return updated_node.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 노드 수정 실패: {str(e)}")
            raise
    
    async def _delete_node_db(self, node_id: str) -> bool:
        """PostgreSQL에서 노드 삭제"""
        try:
            async with node_db.get_session_context() as session:
                result = await session.execute(
                    delete(ReactFlowNode).where(ReactFlowNode.id == node_id)
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 노드 삭제 성공: {node_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 노드 삭제 실패: 노드를 찾을 수 없음 {node_id}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 노드 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_nodes_db(self) -> List[Dict[str, Any]]:
        """PostgreSQL에서 모든 노드 조회"""
        try:
            async with node_db.get_session_context() as session:
                result = await session.execute(select(ReactFlowNode))
                node_entities = result.scalars().all()
                
                return [node.to_dict() for node in node_entities]
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 전체 노드 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_node_memory(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 노드 생성"""
        node_id = node_data.get('id')
        self._memory_nodes[node_id] = {
            **node_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ 메모리 노드 생성: {node_id}")
        return self._memory_nodes[node_id]
    
    async def _update_node_memory(self, node_id: str, node_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """메모리에서 노드 수정"""
        if node_id in self._memory_nodes:
            self._memory_nodes[node_id].update(node_data)
            self._memory_nodes[node_id]['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ 메모리 노드 수정 성공: {node_id}")
            return self._memory_nodes[node_id]
        else:
            return None
    
    async def _delete_node_memory(self, node_id: str) -> bool:
        """메모리에서 노드 삭제"""
        if node_id in self._memory_nodes:
            del self._memory_nodes[node_id]
            
            logger.info(f"✅ 메모리 노드 삭제 성공: {node_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 노드 삭제 실패: 노드를 찾을 수 없음 {node_id}")
            return False
