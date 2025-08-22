# ============================================================================
# 🔗 Edge Repository - ReactFlow 엣지 데이터 접근
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text
from sqlalchemy.engine import create_engine
from sqlalchemy.pool import StaticPool

from app.common.database_base import Base
from app.domain.edge.edge_entity import Edge

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🗄️ 데이터베이스 연결 관리
# ============================================================================

class EdgeDatabaseConnection:
    """엣지 도메인 전용 데이터베이스 연결"""
    
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
                    "sqlite+aiosqlite:///./edges.db",
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
            logger.info("✅ Edge 도메인 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Edge 도메인 데이터베이스 초기화 실패: {str(e)}")
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
            logger.info("✅ Edge 도메인 데이터베이스 연결 종료")

# 전역 데이터베이스 연결 인스턴스
edge_db = EdgeDatabaseConnection()

# ============================================================================
# 📚 엣지 저장소 클래스
# ============================================================================

class EdgeRepository:
    """엣지 데이터 접근 클래스"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory_edges: Dict[str, Dict[str, Any]] = {}
        
        if self.use_database:
            logger.info("✅ PostgreSQL 엣지 저장소 사용")
        else:
            logger.info("✅ 메모리 엣지 저장소 사용")
    
    # ============================================================================
    # 🔗 엣지 CRUD 메서드
    # ============================================================================
    
    async def create_edge(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """엣지 생성"""
        try:
            if self.use_database:
                return await self._create_edge_db(edge_data)
            else:
                return await self._create_edge_memory(edge_data)
        except Exception as e:
            logger.error(f"❌ 엣지 생성 실패: {str(e)}")
            raise
    
    async def get_edge_by_id(self, edge_id: str) -> Optional[Dict[str, Any]]:
        """엣지 ID로 조회"""
        try:
            if self.use_database:
                return await self._get_edge_by_id_db(edge_id)
            else:
                return self._memory_edges.get(edge_id)
        except Exception as e:
            logger.error(f"❌ 엣지 조회 실패: {str(e)}")
            return None
    
    async def get_edges_by_flow_id(self, flow_id: str) -> List[Dict[str, Any]]:
        """플로우 ID로 엣지 목록 조회"""
        try:
            if self.use_database:
                return await self._get_edges_by_flow_id_db(flow_id)
            else:
                return [edge for edge in self._memory_edges.values() if edge.get('flow_id') == flow_id]
        except Exception as e:
            logger.error(f"❌ 플로우별 엣지 조회 실패: {str(e)}")
            return []
    
    async def update_edge(self, edge_id: str, edge_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 수정"""
        try:
            if self.use_database:
                return await self._update_edge_db(edge_id, edge_data)
            else:
                return await self._update_edge_memory(edge_id, edge_data)
        except Exception as e:
            logger.error(f"❌ 엣지 수정 실패: {str(e)}")
            raise
    
    async def delete_edge(self, edge_id: str) -> bool:
        """엣지 삭제"""
        try:
            if self.use_database:
                return await self._delete_edge_db(edge_id)
            else:
                return await self._delete_edge_memory(edge_id)
        except Exception as e:
            logger.error(f"❌ 엣지 삭제 실패: {str(e)}")
            return False
    
    async def get_all_edges(self) -> List[Dict[str, Any]]:
        """모든 엣지 조회"""
        try:
            if self.use_database:
                return await self._get_all_edges_db()
            else:
                return list(self._memory_edges.values())
        except Exception as e:
            logger.error(f"❌ 전체 엣지 조회 실패: {str(e)}")
            return []
    
    async def batch_update_edges(self, edges_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """엣지 일괄 수정"""
        try:
            updated_edges = []
            for edge_data in edges_data:
                edge_id = edge_data.get('id')
                if edge_id:
                    updated_edge = await self.update_edge(edge_id, edge_data)
                    if updated_edge:
                        updated_edges.append(updated_edge)
            return updated_edges
        except Exception as e:
            logger.error(f"❌ 엣지 일괄 수정 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드
    # ============================================================================
    
    async def _create_edge_db(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 엣지 생성"""
        try:
            async with edge_db.get_session_context() as session:
                edge_entity = Edge.from_reactflow_data(
                    flow_id=edge_data.get('flow_id'),
                    edge_data=edge_data
                )
                
                session.add(edge_entity)
                await session.commit()
                await session.refresh(edge_entity)
                
                logger.info(f"✅ PostgreSQL 엣지 생성 성공: {edge_entity.id}")
                return edge_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 엣지 생성 실패: {str(e)}")
            raise
    
    async def _get_edge_by_id_db(self, edge_id: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 엣지 ID로 조회"""
        try:
            async with edge_db.get_session_context() as session:
                result = await session.execute(
                    select(Edge).where(Edge.id == edge_id)
                )
                edge_entity = result.scalar_one_or_none()
                
                if edge_entity:
                    return edge_entity.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 엣지 조회 실패: {str(e)}")
            return None
    
    async def _get_edges_by_flow_id_db(self, flow_id: str) -> List[Dict[str, Any]]:
        """PostgreSQL에서 플로우별 엣지 조회"""
        try:
            async with edge_db.get_session_context() as session:
                result = await session.execute(
                    select(Edge).where(Edge.flow_id == flow_id)
                )
                edge_entities = result.scalars().all()
                
                return [edge.to_dict() for edge in edge_entities]
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 플로우별 엣지 조회 실패: {str(e)}")
            return []
    
    async def _update_edge_db(self, edge_id: str, edge_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 엣지 수정"""
        try:
            async with edge_db.get_session_context() as session:
                # 업데이트할 필드만 추출
                update_fields = {}
                
                if 'source' in edge_data:
                    update_fields['source'] = edge_data['source']
                
                if 'target' in edge_data:
                    update_fields['target'] = edge_data['target']
                
                if 'type' in edge_data:
                    update_fields['type'] = edge_data['type']
                
                if 'data' in edge_data:
                    import json
                    update_fields['data_json'] = json.dumps(edge_data['data']) if edge_data['data'] else None
                
                if 'style' in edge_data:
                    import json
                    update_fields['style_json'] = json.dumps(edge_data['style']) if edge_data['style'] else None
                
                if 'animated' in edge_data:
                    update_fields['animated'] = edge_data['animated']
                
                if 'hidden' in edge_data:
                    update_fields['hidden'] = edge_data['hidden']
                
                if 'deletable' in edge_data:
                    update_fields['deletable'] = edge_data['deletable']
                
                if 'selected' in edge_data:
                    update_fields['selected'] = edge_data['selected']
                
                if update_fields:
                    update_fields['updated_at'] = datetime.utcnow()
                    
                    await session.execute(
                        update(Edge).where(Edge.id == edge_id).values(**update_fields)
                    )
                    await session.commit()
                
                # 업데이트된 데이터 조회
                result = await session.execute(
                    select(Edge).where(Edge.id == edge_id)
                )
                updated_edge = result.scalar_one_or_none()
                
                if updated_edge:
                    logger.info(f"✅ PostgreSQL 엣지 수정 성공: {edge_id}")
                    return updated_edge.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 엣지 수정 실패: {str(e)}")
            raise
    
    async def _delete_edge_db(self, edge_id: str) -> bool:
        """PostgreSQL에서 엣지 삭제"""
        try:
            async with edge_db.get_session_context() as session:
                result = await session.execute(
                    delete(Edge).where(Edge.id == edge_id)
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 엣지 삭제 성공: {edge_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 엣지 삭제 실패: 엣지를 찾을 수 없음 {edge_id}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 엣지 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_edges_db(self) -> List[Dict[str, Any]]:
        """PostgreSQL에서 모든 엣지 조회"""
        try:
            async with edge_db.get_session_context() as session:
                result = await session.execute(select(Edge))
                edge_entities = result.scalars().all()
                
                return [edge.to_dict() for edge in edge_entities]
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 전체 엣지 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_edge_memory(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 엣지 생성"""
        edge_id = edge_data.get('id')
        self._memory_edges[edge_id] = {
            **edge_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ 메모리 엣지 생성: {edge_id}")
        return self._memory_edges[edge_id]
    
    async def _update_edge_memory(self, edge_id: str, edge_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """메모리에서 엣지 수정"""
        if edge_id in self._memory_edges:
            self._memory_edges[edge_id].update(edge_data)
            self._memory_edges[edge_id]['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ 메모리 엣지 수정 성공: {edge_id}")
            return self._memory_edges[edge_id]
        else:
            return None
    
    async def _delete_edge_memory(self, edge_id: str) -> bool:
        """메모리에서 엣지 삭제"""
        if edge_id in self._memory_edges:
            del self._memory_edges[edge_id]
            
            logger.info(f"✅ 메모리 엣지 삭제 성공: {edge_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 엣지 삭제 실패: 엣지를 찾을 수 없음 {edge_id}")
            return False
