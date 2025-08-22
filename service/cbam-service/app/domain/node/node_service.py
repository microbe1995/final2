# ============================================================================
# 🔵 Node Service - ReactFlow 노드 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from app.domain.node.node_repository import NodeRepository
from app.domain.node.node_schema import (
    NodeCreateRequest,
    NodeUpdateRequest,
    NodeResponse,
    NodeListResponse,
    NodeSearchRequest,
    NodeStatsResponse,
    NodeBatchUpdateRequest,
    NodeChangesRequest,
    NodeChangesResponse
)

class NodeService:
    """노드 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, repository: Optional[NodeRepository] = None):
        """NodeService 초기화"""
        self.node_repository = repository or NodeRepository(use_database=True)
    
    # ============================================================================
    # 🔵 노드 기본 CRUD 메서드
    # ============================================================================
    
    async def create_node(self, request: NodeCreateRequest) -> NodeResponse:
        """노드 생성"""
        try:
            logger.info(f"🔵 노드 생성 요청: {request.data.label}")
            
            # ID 생성 (제공되지 않은 경우)
            node_id = request.id or f"node_{uuid.uuid4().hex[:8]}"
            
            # 노드 데이터 준비
            node_data = {
                "id": node_id,
                "flow_id": request.flow_id,
                "type": request.type,
                "position": {
                    "x": request.position.x,
                    "y": request.position.y
                },
                "data": {
                    "label": request.data.label,
                    "description": request.data.description,
                    "color": request.data.color,
                    "icon": request.data.icon,
                    "metadata": request.data.metadata or {}
                },
                "width": request.width,
                "height": request.height,
                "draggable": request.draggable,
                "selectable": request.selectable,
                "deletable": request.deletable,
                "style": request.style or {}
            }
            
            # 비즈니스 규칙 검증
            await self._validate_node_creation(node_data)
            
            # 노드 생성
            created_node = await self.node_repository.create_node(node_data)
            
            logger.info(f"✅ 노드 생성 성공: {node_id}")
            return self._convert_to_node_response(created_node)
            
        except Exception as e:
            logger.error(f"❌ 노드 생성 실패: {str(e)}")
            raise ValueError(f"노드 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_node_by_id(self, node_id: str) -> Optional[NodeResponse]:
        """노드 ID로 조회"""
        try:
            logger.info(f"🔍 노드 조회: {node_id}")
            
            node = await self.node_repository.get_node_by_id(node_id)
            if not node:
                logger.warning(f"⚠️ 노드를 찾을 수 없음: {node_id}")
                return None
            
            logger.info(f"✅ 노드 조회 성공: {node_id}")
            return self._convert_to_node_response(node)
            
        except Exception as e:
            logger.error(f"❌ 노드 조회 실패: {str(e)}")
            return None
    
    async def get_nodes_by_flow_id(self, flow_id: str) -> NodeListResponse:
        """플로우 ID로 노드 목록 조회"""
        try:
            logger.info(f"📋 플로우별 노드 조회: {flow_id}")
            
            nodes = await self.node_repository.get_nodes_by_flow_id(flow_id)
            
            # ReactFlow 형식으로 변환
            reactflow_nodes = [self._convert_to_node_response(node) for node in nodes]
            
            logger.info(f"✅ 플로우별 노드 조회 성공: {len(nodes)}개")
            return NodeListResponse(
                nodes=reactflow_nodes,
                total=len(nodes),
                flow_id=flow_id
            )
            
        except Exception as e:
            logger.error(f"❌ 플로우별 노드 조회 실패: {str(e)}")
            raise ValueError(f"노드 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def update_node(self, node_id: str, request: NodeUpdateRequest) -> Optional[NodeResponse]:
        """노드 수정"""
        try:
            logger.info(f"✏️ 노드 수정: {node_id}")
            
            # 기존 노드 확인
            existing_node = await self.node_repository.get_node_by_id(node_id)
            if not existing_node:
                logger.warning(f"⚠️ 수정할 노드를 찾을 수 없음: {node_id}")
                return None
            
            # 수정 데이터 준비
            update_data = {}
            
            if request.position:
                update_data["position"] = {
                    "x": request.position.x,
                    "y": request.position.y
                }
            
            if request.data:
                update_data["data"] = {
                    "label": request.data.label,
                    "description": request.data.description,
                    "color": request.data.color,
                    "icon": request.data.icon,
                    "metadata": request.data.metadata or {}
                }
            
            if request.width is not None:
                update_data["width"] = request.width
            
            if request.height is not None:
                update_data["height"] = request.height
            
            if request.draggable is not None:
                update_data["draggable"] = request.draggable
            
            if request.selectable is not None:
                update_data["selectable"] = request.selectable
            
            if request.deletable is not None:
                update_data["deletable"] = request.deletable
            
            if request.style is not None:
                update_data["style"] = request.style
            
            # 노드 수정
            updated_node = await self.node_repository.update_node(node_id, update_data)
            
            if updated_node:
                logger.info(f"✅ 노드 수정 성공: {node_id}")
                return self._convert_to_node_response(updated_node)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ 노드 수정 실패: {str(e)}")
            raise ValueError(f"노드 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_node(self, node_id: str) -> bool:
        """노드 삭제"""
        try:
            logger.info(f"🗑️ 노드 삭제: {node_id}")
            
            # 노드 존재 확인
            existing_node = await self.node_repository.get_node_by_id(node_id)
            if not existing_node:
                logger.warning(f"⚠️ 삭제할 노드를 찾을 수 없음: {node_id}")
                return False
            
            # 노드 삭제
            deleted = await self.node_repository.delete_node(node_id)
            
            if deleted:
                logger.info(f"✅ 노드 삭제 성공: {node_id}")
            else:
                logger.error(f"❌ 노드 삭제 실패: {node_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"❌ 노드 삭제 실패: {str(e)}")
            raise ValueError(f"노드 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔄 일괄 처리 메서드
    # ============================================================================
    
    async def batch_update_nodes(self, request: NodeBatchUpdateRequest) -> List[NodeResponse]:
        """노드 일괄 수정 (ReactFlow onNodesChange 이벤트 처리)"""
        try:
            logger.info(f"🔄 노드 일괄 수정: {len(request.nodes)}개")
            
            updated_nodes = []
            
            for node_change in request.nodes:
                node_id = node_change.get('id')
                if not node_id:
                    continue
                
                # 위치 변경 처리
                if 'position' in node_change:
                    update_data = {"position": node_change['position']}
                    updated_node = await self.node_repository.update_node(node_id, update_data)
                    
                    if updated_node:
                        updated_nodes.append(self._convert_to_node_response(updated_node))
            
            logger.info(f"✅ 노드 일괄 수정 완료: {len(updated_nodes)}개")
            return updated_nodes
            
        except Exception as e:
            logger.error(f"❌ 노드 일괄 수정 실패: {str(e)}")
            raise ValueError(f"노드 일괄 수정 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 📊 검색 및 통계 메서드
    # ============================================================================
    
    async def search_nodes(self, request: NodeSearchRequest) -> NodeListResponse:
        """노드 검색"""
        try:
            logger.info(f"🔍 노드 검색: {request}")
            
            all_nodes = await self.node_repository.get_all_nodes()
            filtered_nodes = []
            
            for node in all_nodes:
                # 플로우 ID 필터
                if request.flow_id and node.get('flow_id') != request.flow_id:
                    continue
                
                # 노드 타입 필터
                if request.node_type and node.get('type') != request.node_type:
                    continue
                
                # 레이블 검색
                if request.label:
                    node_data = node.get('data', {})
                    if isinstance(node_data, str):
                        import json
                        try:
                            node_data = json.loads(node_data)
                        except:
                            node_data = {}
                    
                    label = node_data.get('label', '')
                    if request.label.lower() not in label.lower():
                        continue
                
                filtered_nodes.append(node)
            
            # ReactFlow 형식으로 변환
            reactflow_nodes = [self._convert_to_node_response(node) for node in filtered_nodes]
            
            logger.info(f"✅ 노드 검색 완료: {len(filtered_nodes)}개")
            return NodeListResponse(
                nodes=reactflow_nodes,
                total=len(filtered_nodes),
                flow_id=request.flow_id or "all"
            )
            
        except Exception as e:
            logger.error(f"❌ 노드 검색 실패: {str(e)}")
            raise ValueError(f"노드 검색 중 오류가 발생했습니다: {str(e)}")
    
    async def get_node_stats(self) -> NodeStatsResponse:
        """노드 통계 조회"""
        try:
            logger.info(f"📊 노드 통계 조회")
            
            all_nodes = await self.node_repository.get_all_nodes()
            
            # 타입별 집계
            nodes_by_type = {}
            flows_with_nodes = set()
            
            for node in all_nodes:
                node_type = node.get('type', 'default')
                nodes_by_type[node_type] = nodes_by_type.get(node_type, 0) + 1
                
                flow_id = node.get('flow_id')
                if flow_id:
                    flows_with_nodes.add(flow_id)
            
            # 평균 계산
            total_nodes = len(all_nodes)
            total_flows = len(flows_with_nodes)
            average_nodes_per_flow = total_nodes / total_flows if total_flows > 0 else 0
            
            logger.info(f"✅ 노드 통계 조회 완료: 총 {total_nodes}개")
            
            return NodeStatsResponse(
                total_nodes=total_nodes,
                nodes_by_type=nodes_by_type,
                flows_with_nodes=total_flows,
                average_nodes_per_flow=round(average_nodes_per_flow, 2)
            )
            
        except Exception as e:
            logger.error(f"❌ 노드 통계 조회 실패: {str(e)}")
            raise ValueError(f"노드 통계 조회 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    async def _validate_node_creation(self, node_data: Dict[str, Any]) -> None:
        """노드 생성 검증"""
        # 중복 ID 확인
        existing_node = await self.node_repository.get_node_by_id(node_data.get('id'))
        if existing_node:
            raise ValueError(f"이미 존재하는 노드 ID입니다: {node_data.get('id')}")
        
        # 필수 필드 확인
        if not node_data.get('flow_id'):
            raise ValueError("플로우 ID는 필수입니다")
        
        if not node_data.get('data', {}).get('label'):
            raise ValueError("노드 레이블은 필수입니다")
    
    def _convert_to_node_response(self, node: Dict[str, Any]) -> NodeResponse:
        """노드를 NodeResponse로 변환"""
        return NodeResponse(
            id=node['id'],
            flow_id=node['flow_id'],
            node_type=node.get('type', 'default'),
            position_x=float(node.get('position_x', 0)),
            position_y=float(node.get('position_y', 0)),
            width=float(node['width']) if node.get('width') else None,
            height=float(node['height']) if node.get('height') else None,
            data=node.get('data'),
            style=node.get('style'),
            hidden=node.get('hidden', False),
            selected=node.get('selected', False),
            deletable=node.get('deletable', True),
            created_at=node.get('created_at'),
            updated_at=node.get('updated_at')
        )
