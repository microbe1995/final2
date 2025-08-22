# ============================================================================
# 🌊 Flow Service - ReactFlow 플로우 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from app.domain.flow.flow_repository import FlowRepository
from app.domain.flow.flow_schema import (
    FlowCreateRequest,
    FlowUpdateRequest,
    FlowResponse,
    FlowListResponse,
    FlowStateResponse,
    FlowSearchRequest,
    FlowStatsResponse
)

class FlowService:
    """플로우 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, repository: Optional[FlowRepository] = None):
        """FlowService 초기화"""
        self.flow_repository = repository or FlowRepository(use_database=True)
    
    # ============================================================================
    # 🌊 플로우 기본 CRUD 메서드
    # ============================================================================
    
    async def create_flow(self, request: FlowCreateRequest) -> FlowResponse:
        """플로우 생성"""
        try:
            logger.info(f"🌊 플로우 생성 요청: {request.name}")
            
            # ID 생성 (제공되지 않은 경우)
            flow_id = request.id or f"flow_{uuid.uuid4().hex[:8]}"
            
            # 플로우 데이터 준비
            flow_data = {
                "id": flow_id,
                "name": request.name,
                "description": request.description,
                # "viewport": {  # Viewport 도메인으로 분리됨
                #     "x": request.viewport.x,
                #     "y": request.viewport.y,
                #     "zoom": request.viewport.zoom
                # },
                "settings": request.settings or {},
                "flow_metadata": request.metadata or {}
            }
            
            # 비즈니스 규칙 검증
            await self._validate_flow_creation(flow_data)
            
            # 플로우 생성
            created_flow = await self.flow_repository.create_flow(flow_data)
            
            logger.info(f"✅ 플로우 생성 성공: {flow_id}")
            return self._convert_to_flow_response(created_flow)
            
        except Exception as e:
            logger.error(f"❌ 플로우 생성 실패: {str(e)}")
            raise ValueError(f"플로우 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_flow_by_id(self, flow_id: str) -> Optional[FlowResponse]:
        """플로우 ID로 조회"""
        try:
            logger.info(f"🔍 플로우 조회: {flow_id}")
            
            flow = await self.flow_repository.get_flow_by_id(flow_id)
            if not flow:
                logger.warning(f"⚠️ 플로우를 찾을 수 없음: {flow_id}")
                return None
            
            logger.info(f"✅ 플로우 조회 성공: {flow_id}")
            return self._convert_to_flow_response(flow)
            
        except Exception as e:
            logger.error(f"❌ 플로우 조회 실패: {str(e)}")
            return None
    
    async def get_all_flows(self) -> FlowListResponse:
        """모든 플로우 목록 조회"""
        try:
            logger.info(f"📋 플로우 목록 조회")
            
            flows = await self.flow_repository.get_all_flows()
            
            # FlowResponse 형식으로 변환
            flow_responses = [self._convert_to_flow_response(flow) for flow in flows]
            
            logger.info(f"✅ 플로우 목록 조회 성공: {len(flows)}개")
            return FlowListResponse(
                flows=flow_responses,
                total=len(flows)
            )
            
        except Exception as e:
            logger.error(f"❌ 플로우 목록 조회 실패: {str(e)}")
            raise ValueError(f"플로우 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def update_flow(self, flow_id: str, request: FlowUpdateRequest) -> Optional[FlowResponse]:
        """플로우 수정"""
        try:
            logger.info(f"✏️ 플로우 수정: {flow_id}")
            
            # 기존 플로우 확인
            existing_flow = await self.flow_repository.get_flow_by_id(flow_id)
            if not existing_flow:
                logger.warning(f"⚠️ 수정할 플로우를 찾을 수 없음: {flow_id}")
                return None
            
            # 수정 데이터 준비
            update_data = {}
            
            if request.name is not None:
                update_data["name"] = request.name
            
            if request.description is not None:
                update_data["description"] = request.description
            
                    # if request.viewport is not None:  # Viewport 도메인으로 분리됨
        #     update_data["viewport"] = {
        #         "x": request.viewport.x,
        #         "y": request.viewport.y,
        #         "zoom": request.viewport.zoom
        #     }
            
            if request.settings is not None:
                update_data["settings"] = request.settings
            
            if request.metadata is not None:
                update_data["flow_metadata"] = request.metadata
            
            # 플로우 수정
            updated_flow = await self.flow_repository.update_flow(flow_id, update_data)
            
            if updated_flow:
                logger.info(f"✅ 플로우 수정 성공: {flow_id}")
                return self._convert_to_flow_response(updated_flow)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ 플로우 수정 실패: {str(e)}")
            raise ValueError(f"플로우 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_flow(self, flow_id: str) -> bool:
        """플로우 삭제"""
        try:
            logger.info(f"🗑️ 플로우 삭제: {flow_id}")
            
            # 플로우 존재 확인
            existing_flow = await self.flow_repository.get_flow_by_id(flow_id)
            if not existing_flow:
                logger.warning(f"⚠️ 삭제할 플로우를 찾을 수 없음: {flow_id}")
                return False
            
            # 플로우 삭제
            deleted = await self.flow_repository.delete_flow(flow_id)
            
            if deleted:
                logger.info(f"✅ 플로우 삭제 성공: {flow_id}")
            else:
                logger.error(f"❌ 플로우 삭제 실패: {flow_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"❌ 플로우 삭제 실패: {str(e)}")
            raise ValueError(f"플로우 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 📱 뷰포트 관리 메서드 (Viewport 도메인으로 분리됨)
    # ============================================================================
    
    # ============================================================================
    # 🎯 ReactFlow 전체 상태 관리
    # ============================================================================
    
    async def get_flow_state(self, flow_id: str) -> Optional[FlowStateResponse]:
        """ReactFlow 전체 상태 조회 (플로우 + 노드 + 엣지)"""
        try:
            logger.info(f"🎯 ReactFlow 상태 조회: {flow_id}")
            
            # 플로우 정보 조회
            flow = await self.flow_repository.get_flow_by_id(flow_id)
            if not flow:
                logger.warning(f"⚠️ 플로우를 찾을 수 없음: {flow_id}")
                return None
            
            # TODO: 실제로는 NodeRepository에서 노드들을 조회해야 함
            # from app.domain.node.node_repository import NodeRepository
            # node_repo = NodeRepository()
            # nodes = await node_repo.get_nodes_by_flow_id(flow_id)
            
            # 임시로 빈 목록 반환
            nodes = []
            edges = []
            
            response = FlowStateResponse(
                flow=self._convert_to_flow_response(flow),
                nodes=nodes,
                edges=edges
            )
            
            logger.info(f"✅ ReactFlow 상태 조회 성공: {flow_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 상태 조회 실패: {str(e)}")
            return None
    
    # ============================================================================
    # 📊 검색 및 통계 메서드
    # ============================================================================
    
    async def search_flows(self, request: FlowSearchRequest) -> FlowListResponse:
        """플로우 검색"""
        try:
            logger.info(f"🔍 플로우 검색: {request}")
            
            all_flows = await self.flow_repository.get_all_flows()
            filtered_flows = []
            
            for flow in all_flows:
                # 이름 검색
                if request.name:
                    if request.name.lower() not in flow.get('name', '').lower():
                        continue
                
                filtered_flows.append(flow)
            
            # FlowResponse 형식으로 변환
            flow_responses = [self._convert_to_flow_response(flow) for flow in filtered_flows]
            
            logger.info(f"✅ 플로우 검색 완료: {len(filtered_flows)}개")
            return FlowListResponse(
                flows=flow_responses,
                total=len(filtered_flows)
            )
            
        except Exception as e:
            logger.error(f"❌ 플로우 검색 실패: {str(e)}")
            raise ValueError(f"플로우 검색 중 오류가 발생했습니다: {str(e)}")
    
    async def get_flow_stats(self) -> FlowStatsResponse:
        """플로우 통계 조회"""
        try:
            logger.info(f"📊 플로우 통계 조회")
            
            all_flows = await self.flow_repository.get_all_flows()
            
            # TODO: 실제로는 NodeRepository와 EdgeRepository에서 조회
            total_nodes = 0
            total_edges = 0
            
            # 평균 계산
            total_flows = len(all_flows)
            average_nodes_per_flow = total_nodes / total_flows if total_flows > 0 else 0
            average_edges_per_flow = total_edges / total_flows if total_flows > 0 else 0
            
            logger.info(f"✅ 플로우 통계 조회 완료: 총 {total_flows}개")
            
            return FlowStatsResponse(
                total_flows=total_flows,
                total_nodes=total_nodes,
                total_edges=total_edges,
                average_nodes_per_flow=round(average_nodes_per_flow, 2),
                average_edges_per_flow=round(average_edges_per_flow, 2)
            )
            
        except Exception as e:
            logger.error(f"❌ 플로우 통계 조회 실패: {str(e)}")
            raise ValueError(f"플로우 통계 조회 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    async def _validate_flow_creation(self, flow_data: Dict[str, Any]) -> None:
        """플로우 생성 검증"""
        # 중복 ID 확인
        existing_flow = await self.flow_repository.get_flow_by_id(flow_data.get('id'))
        if existing_flow:
            raise ValueError(f"이미 존재하는 플로우 ID입니다: {flow_data.get('id')}")
        
        # 필수 필드 확인
        if not flow_data.get('name'):
            raise ValueError("플로우 이름은 필수입니다")
    
    def _convert_to_flow_response(self, flow: Dict[str, Any]) -> FlowResponse:
        """플로우를 FlowResponse로 변환"""
        from app.domain.flow.flow_schema import FlowViewport
        
        # viewport 파싱
        viewport = flow.get('viewport', {})
        if isinstance(viewport, str):
            import json
            try:
                viewport = json.loads(viewport)
            except:
                viewport = {"x": 0, "y": 0, "zoom": 1.0}
        
        # settings 파싱
        settings = flow.get('settings', {})
        if isinstance(settings, str):
            import json
            try:
                settings = json.loads(settings)
            except:
                settings = {}
        
        # metadata 파싱
        metadata = flow.get('metadata', {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata)
            except:
                metadata = {}
        
        return FlowResponse(
            id=flow['id'],
            name=flow['name'],
            description=flow.get('description'),
            viewport=FlowViewport(
                x=viewport.get('x', 0),
                y=viewport.get('y', 0),
                zoom=viewport.get('zoom', 1.0)
            ),
            settings=settings,
            metadata=metadata,
            created_at=flow.get('created_at', ''),
            updated_at=flow.get('updated_at', '')
        )
