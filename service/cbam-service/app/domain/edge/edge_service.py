# ============================================================================
# 🔗 Edge Service - 엣지 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from .edge_repository import EdgeRepository
from .edge_schema import (
    EdgeCreateRequest, EdgeResponse, EdgeUpdateRequest
)

logger = logging.getLogger(__name__)

class EdgeService:
    """엣지 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.edge_repository = EdgeRepository()
        logger.info("✅ Edge 서비스 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.edge_repository.initialize()
            logger.info("✅ Edge 서비스 데이터베이스 연결 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Edge 서비스 데이터베이스 초기화 실패 (서비스는 계속 실행): {e}")
            logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    async def create_edge(self, request: EdgeCreateRequest) -> EdgeResponse:
        """엣지 생성"""
        try:
            edge_data = {
                "source_id": request.source_id,
                "target_id": request.target_id,
                "edge_kind": request.edge_kind
            }
            
            saved_edge = await self.edge_repository.create_edge(edge_data)
            if saved_edge:
                return EdgeResponse(**saved_edge)
            else:
                raise Exception("엣지 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error creating edge: {e}")
            raise e
    
    async def get_edges(self) -> List[EdgeResponse]:
        """모든 엣지 조회"""
        try:
            edges = await self.edge_repository.get_edges()
            return [EdgeResponse(**edge) for edge in edges]
        except Exception as e:
            logger.error(f"Error getting edges: {e}")
            raise e
    
    async def get_edge(self, edge_id: int) -> Optional[EdgeResponse]:
        """특정 엣지 조회"""
        try:
            edge = await self.edge_repository.get_edge(edge_id)
            if edge:
                return EdgeResponse(**edge)
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting edge {edge_id}: {e}")
            raise e
    
    async def update_edge(self, edge_id: int, request: EdgeUpdateRequest) -> Optional[EdgeResponse]:
        """엣지 업데이트"""
        try:
            update_data = {}
            if request.source_id is not None:
                update_data["source_id"] = request.source_id
            if request.target_id is not None:
                update_data["target_id"] = request.target_id
            if request.edge_kind is not None:
                update_data["edge_kind"] = request.edge_kind
            
            if not update_data:
                raise Exception("업데이트할 데이터가 없습니다.")
            
            updated_edge = await self.edge_repository.update_edge(edge_id, update_data)
            if updated_edge:
                return EdgeResponse(**updated_edge)
            else:
                return None
        except Exception as e:
            logger.error(f"Error updating edge {edge_id}: {e}")
            raise e
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제"""
        try:
            success = await self.edge_repository.delete_edge(edge_id)
            if success:
                logger.info(f"✅ 엣지 {edge_id} 삭제 성공")
            else:
                logger.warning(f"⚠️ 엣지 {edge_id}를 찾을 수 없음")
            return success
        except Exception as e:
            logger.error(f"Error deleting edge {edge_id}: {e}")
            raise e
    
    async def get_edges_by_type(self, edge_kind: str) -> List[EdgeResponse]:
        """타입별 엣지 조회"""
        try:
            edges = await self.edge_repository.get_edges_by_type(edge_kind)
            return [EdgeResponse(**edge) for edge in edges]
        except Exception as e:
            logger.error(f"Error getting edges by type {edge_kind}: {e}")
            raise e
    
    async def get_edges_by_node(self, node_id: int) -> List[EdgeResponse]:
        """노드와 연결된 엣지 조회"""
        try:
            edges = await self.edge_repository.get_edges_by_node(node_id)
            return [EdgeResponse(**edge) for edge in edges]
        except Exception as e:
            logger.error(f"Error getting edges by node {node_id}: {e}")
            raise e
