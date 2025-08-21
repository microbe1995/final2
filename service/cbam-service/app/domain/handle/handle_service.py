# ============================================================================
# 🔘 Handle Service - ReactFlow 핸들 비즈니스 로직
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.domain.handle.handle_repository import HandleRepository
from app.domain.handle.handle_schema import (
    HandleCreateRequest,
    HandleUpdateRequest,
    HandleResponse,
    HandleListResponse,
    HandleStatsResponse,
    ReactFlowHandleResponse
)

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🔘 핸들 서비스 클래스
# ============================================================================

class HandleService:
    """핸들 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, repository: Optional[HandleRepository] = None):
        """HandleService 초기화"""
        self.handle_repository = repository or HandleRepository(use_database=True)
    
    # ============================================================================
    # 🔘 핸들 기본 CRUD 메서드
    # ============================================================================
    
    async def create_handle(self, request: HandleCreateRequest) -> HandleResponse:
        """핸들 생성"""
        try:
            # ID 자동 생성
            handle_id = request.id or f"handle-{uuid.uuid4().hex[:8]}"
            
            handle_data = {
                "id": handle_id,
                "node_id": request.node_id,
                "flow_id": request.flow_id,
                "type": request.type.value,
                "position": request.position.value,
                "style": request.style,
                "data": request.data,
                "is_connectable": request.is_connectable,
                "is_valid_connection": request.is_valid_connection
            }
            
            result = await self.handle_repository.create_handle(handle_data)
            
            logger.info(f"✅ 핸들 생성 성공: {handle_id}")
            return HandleResponse(**result)
            
        except Exception as e:
            logger.error(f"❌ 핸들 생성 실패: {str(e)}")
            raise
    
    async def get_handle_by_id(self, handle_id: str) -> Optional[HandleResponse]:
        """핸들 ID로 조회"""
        try:
            result = await self.handle_repository.get_handle_by_id(handle_id)
            
            if result:
                return HandleResponse(**result)
            return None
            
        except Exception as e:
            logger.error(f"❌ 핸들 조회 실패: {str(e)}")
            return None
    
    async def get_handles_by_node_id(self, node_id: str) -> List[HandleResponse]:
        """노드 ID로 핸들들 조회"""
        try:
            results = await self.handle_repository.get_handles_by_node_id(node_id)
            
            return [HandleResponse(**result) for result in results]
            
        except Exception as e:
            logger.error(f"❌ 노드별 핸들 조회 실패: {str(e)}")
            return []
    
    async def get_handles_by_flow_id(self, flow_id: str) -> List[HandleResponse]:
        """플로우 ID로 핸들들 조회"""
        try:
            results = await self.handle_repository.get_handles_by_flow_id(flow_id)
            
            return [HandleResponse(**result) for result in results]
            
        except Exception as e:
            logger.error(f"❌ 플로우별 핸들 조회 실패: {str(e)}")
            return []
    
    async def update_handle(self, handle_id: str, request: HandleUpdateRequest) -> Optional[HandleResponse]:
        """핸들 수정"""
        try:
            # 업데이트할 필드만 추출
            update_data = {}
            
            if request.type is not None:
                update_data['type'] = request.type.value
            
            if request.position is not None:
                update_data['position'] = request.position.value
            
            if request.style is not None:
                update_data['style'] = request.style
            
            if request.data is not None:
                update_data['data'] = request.data
            
            if request.is_connectable is not None:
                update_data['is_connectable'] = request.is_connectable
            
            if request.is_valid_connection is not None:
                update_data['is_valid_connection'] = request.is_valid_connection
            
            if not update_data:
                logger.warning(f"⚠️ 업데이트할 필드가 없음: {handle_id}")
                return None
            
            result = await self.handle_repository.update_handle(handle_id, update_data)
            
            if result:
                logger.info(f"✅ 핸들 수정 성공: {handle_id}")
                return HandleResponse(**result)
            return None
            
        except Exception as e:
            logger.error(f"❌ 핸들 수정 실패: {str(e)}")
            raise
    
    async def delete_handle(self, handle_id: str) -> bool:
        """핸들 삭제"""
        try:
            result = await self.handle_repository.delete_handle(handle_id)
            
            if result:
                logger.info(f"✅ 핸들 삭제 성공: {handle_id}")
            else:
                logger.warning(f"⚠️ 핸들 삭제 실패: {handle_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 핸들 삭제 실패: {str(e)}")
            return False
    
    async def get_all_handles(self) -> List[HandleResponse]:
        """모든 핸들 조회"""
        try:
            results = await self.handle_repository.get_all_handles()
            
            return [HandleResponse(**result) for result in results]
            
        except Exception as e:
            logger.error(f"❌ 전체 핸들 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🔗 핸들 연결 관련 메서드
    # ============================================================================
    
    async def validate_connection(self, source_handle_id: str, target_handle_id: str) -> bool:
        """핸들 연결 유효성 검증"""
        try:
            source_handle = await self.get_handle_by_id(source_handle_id)
            target_handle = await self.get_handle_by_id(target_handle_id)
            
            if not source_handle or not target_handle:
                logger.warning(f"⚠️ 연결할 핸들을 찾을 수 없음: {source_handle_id} -> {target_handle_id}")
                return False
            
            # 소스 핸들은 source 타입이어야 함
            if source_handle.type != 'source':
                logger.warning(f"⚠️ 소스 핸들이 source 타입이 아님: {source_handle_id}")
                return False
            
            # 타겟 핸들은 target 타입이어야 함
            if target_handle.type != 'target':
                logger.warning(f"⚠️ 타겟 핸들이 target 타입이 아님: {target_handle_id}")
                return False
            
            # 연결 가능한 핸들인지 확인
            if not source_handle.is_connectable or not target_handle.is_connectable:
                logger.warning(f"⚠️ 연결 불가능한 핸들: {source_handle_id} -> {target_handle_id}")
                return False
            
            # 유효한 연결인지 확인
            if not source_handle.is_valid_connection or not target_handle.is_valid_connection:
                logger.warning(f"⚠️ 유효하지 않은 연결: {source_handle_id} -> {target_handle_id}")
                return False
            
            logger.info(f"✅ 핸들 연결 유효성 검증 성공: {source_handle_id} -> {target_handle_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 핸들 연결 유효성 검증 실패: {str(e)}")
            return False
    
    async def get_connectable_handles(self, flow_id: str, exclude_node_id: Optional[str] = None) -> List[ReactFlowHandleResponse]:
        """연결 가능한 핸들들 조회"""
        try:
            all_handles = await self.get_handles_by_flow_id(flow_id)
            
            # 연결 가능한 핸들만 필터링
            connectable_handles = [
                handle for handle in all_handles
                if handle.is_connectable and handle.is_valid_connection
            ]
            
            # 특정 노드 제외
            if exclude_node_id:
                connectable_handles = [
                    handle for handle in connectable_handles
                    if handle.node_id != exclude_node_id
                ]
            
            # ReactFlow 호환 형식으로 변환
            reactflow_handles = [
                ReactFlowHandleResponse(
                    id=handle.id,
                    type=handle.type,
                    position=handle.position,
                    style=handle.style,
                    data=handle.data,
                    is_connectable=handle.is_connectable,
                    is_valid_connection=handle.is_valid_connection
                )
                for handle in connectable_handles
            ]
            
            logger.info(f"✅ 연결 가능한 핸들 조회 성공: {len(reactflow_handles)}개")
            return reactflow_handles
            
        except Exception as e:
            logger.error(f"❌ 연결 가능한 핸들 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 📊 핸들 통계 메서드
    # ============================================================================
    
    async def get_handle_stats(self) -> HandleStatsResponse:
        """핸들 통계 조회"""
        try:
            all_handles = await self.get_all_handles()
            
            stats = {
                "total_handles": len(all_handles),
                "source_handles": len([h for h in all_handles if h.type == 'source']),
                "target_handles": len([h for h in all_handles if h.type == 'target']),
                "left_handles": len([h for h in all_handles if h.position == 'left']),
                "right_handles": len([h for h in all_handles if h.position == 'right']),
                "top_handles": len([h for h in all_handles if h.position == 'top']),
                "bottom_handles": len([h for h in all_handles if h.position == 'bottom']),
                "connectable_handles": len([h for h in all_handles if h.is_connectable]),
                "valid_connection_handles": len([h for h in all_handles if h.is_valid_connection])
            }
            
            logger.info(f"✅ 핸들 통계 조회 성공: {stats['total_handles']}개")
            return HandleStatsResponse(**stats)
            
        except Exception as e:
            logger.error(f"❌ 핸들 통계 조회 실패: {str(e)}")
            return HandleStatsResponse(
                total_handles=0,
                source_handles=0,
                target_handles=0,
                left_handles=0,
                right_handles=0,
                top_handles=0,
                bottom_handles=0,
                connectable_handles=0,
                valid_connection_handles=0
            )
    
    # ============================================================================
    # 🎯 ReactFlow 전용 메서드
    # ============================================================================
    
    async def create_reactflow_handles_for_node(
        self, 
        node_id: str, 
        flow_id: str, 
        handle_configs: List[Dict[str, Any]]
    ) -> List[ReactFlowHandleResponse]:
        """노드에 ReactFlow 핸들들 자동 생성"""
        try:
            created_handles = []
            
            for config in handle_configs:
                handle_request = HandleCreateRequest(
                    node_id=node_id,
                    flow_id=flow_id,
                    type=config.get('type', 'default'),
                    position=config.get('position', 'left'),
                    style=config.get('style'),
                    data=config.get('data'),
                    is_connectable=config.get('is_connectable', True),
                    is_valid_connection=config.get('is_valid_connection', True)
                )
                
                created_handle = await self.create_handle(handle_request)
                created_handles.append(created_handle)
            
            logger.info(f"✅ ReactFlow 핸들 자동 생성 성공: {node_id}에 {len(created_handles)}개")
            return created_handles
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 핸들 자동 생성 실패: {str(e)}")
            return []
    
    async def get_reactflow_handles_for_node(self, node_id: str) -> List[ReactFlowHandleResponse]:
        """노드의 ReactFlow 핸들들 조회"""
        try:
            handles = await self.get_handles_by_node_id(node_id)
            
            reactflow_handles = [
                ReactFlowHandleResponse(
                    id=handle.id,
                    type=handle.type,
                    position=handle.position,
                    style=handle.style,
                    data=handle.data,
                    is_connectable=handle.is_connectable,
                    is_valid_connection=handle.is_valid_connection
                )
                for handle in handles
            ]
            
            logger.info(f"✅ ReactFlow 핸들 조회 성공: {node_id}에 {len(reactflow_handles)}개")
            return reactflow_handles
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 핸들 조회 실패: {str(e)}")
            return []
