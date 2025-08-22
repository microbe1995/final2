# ============================================================================
# 🔗 Edge Service - ReactFlow 엣지 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from app.domain.edge.edge_repository import EdgeRepository
from app.domain.edge.edge_schema import (
    EdgeCreateRequest,
    EdgeUpdateRequest,
    EdgeResponse,
    EdgeListResponse,
    EdgeStatsResponse,
    EdgeSearchRequest,
    EdgeBatchUpdateRequest,
    ConnectionRequest,
    ConnectionResponse,
    EdgeChangesRequest,
    EdgeChangesResponse
)

class EdgeService:
    """엣지 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, repository: Optional[EdgeRepository] = None):
        """EdgeService 초기화"""
        self.edge_repository = repository or EdgeRepository(use_database=True)
    
    # ============================================================================
    # 🔗 엣지 기본 CRUD 메서드
    # ============================================================================
    
    async def create_edge(self, request: EdgeCreateRequest) -> EdgeResponse:
        """엣지 생성"""
        try:
            logger.info(f"🔗 엣지 생성 요청: {request.source} -> {request.target}")
            
            # ID 생성 (제공되지 않은 경우)
            edge_id = request.id or f"edge_{uuid.uuid4().hex[:8]}"
            
            # 엣지 데이터 준비
            edge_data = {
                "id": edge_id,
                "flow_id": request.flow_id,
                "source": request.source,
                "target": request.target,
                "type": request.type,
                "data": request.data.dict() if request.data else {},
                "style": request.style.dict() if request.style else {},
                "animated": request.animated,
                "hidden": request.hidden,
                "deletable": request.deletable
            }
            
            # 비즈니스 규칙 검증
            await self._validate_edge_creation(edge_data)
            
            # 엣지 생성
            created_edge = await self.edge_repository.create_edge(edge_data)
            
            logger.info(f"✅ 엣지 생성 성공: {edge_id}")
            return self._convert_to_edge_response(created_edge)
            
        except Exception as e:
            logger.error(f"❌ 엣지 생성 실패: {str(e)}")
            raise ValueError(f"엣지 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_edge_by_id(self, edge_id: str) -> Optional[EdgeResponse]:
        """엣지 ID로 조회"""
        try:
            logger.info(f"🔍 엣지 조회: {edge_id}")
            
            edge = await self.edge_repository.get_edge_by_id(edge_id)
            if not edge:
                logger.warning(f"⚠️ 엣지를 찾을 수 없음: {edge_id}")
                return None
            
            logger.info(f"✅ 엣지 조회 성공: {edge_id}")
            return self._convert_to_edge_response(edge)
            
        except Exception as e:
            logger.error(f"❌ 엣지 조회 실패: {str(e)}")
            return None
    
    async def get_edges_by_flow_id(self, flow_id: str) -> EdgeListResponse:
        """플로우 ID로 엣지 목록 조회"""
        try:
            logger.info(f"📋 플로우별 엣지 목록 조회: {flow_id}")
            
            edges = await self.edge_repository.get_edges_by_flow_id(flow_id)
            
            # EdgeResponse 형식으로 변환
            edge_responses = [self._convert_to_edge_response(edge) for edge in edges]
            
            logger.info(f"✅ 플로우별 엣지 목록 조회 성공: {len(edges)}개")
            return EdgeListResponse(
                edges=edge_responses,
                total=len(edges)
            )
            
        except Exception as e:
            logger.error(f"❌ 플로우별 엣지 목록 조회 실패: {str(e)}")
            raise ValueError(f"플로우별 엣지 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def update_edge(self, edge_id: str, request: EdgeUpdateRequest) -> Optional[EdgeResponse]:
        """엣지 수정"""
        try:
            logger.info(f"✏️ 엣지 수정: {edge_id}")
            
            # 기존 엣지 확인
            existing_edge = await self.edge_repository.get_edge_by_id(edge_id)
            if not existing_edge:
                logger.warning(f"⚠️ 수정할 엣지를 찾을 수 없음: {edge_id}")
                return None
            
            # 수정 데이터 준비
            update_data = {}
            
            if request.source is not None:
                update_data["source"] = request.source
            
            if request.target is not None:
                update_data["target"] = request.target
            
            if request.type is not None:
                update_data["type"] = request.type
            
            if request.data is not None:
                update_data["data"] = request.data.dict()
            
            if request.style is not None:
                update_data["style"] = request.style.dict()
            
            if request.animated is not None:
                update_data["animated"] = request.animated
            
            if request.hidden is not None:
                update_data["hidden"] = request.hidden
            
            if request.deletable is not None:
                update_data["deletable"] = request.deletable
            
            if request.selected is not None:
                update_data["selected"] = request.selected
            
            # 엣지 수정
            updated_edge = await self.edge_repository.update_edge(edge_id, update_data)
            
            if updated_edge:
                logger.info(f"✅ 엣지 수정 성공: {edge_id}")
                return self._convert_to_edge_response(updated_edge)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ 엣지 수정 실패: {str(e)}")
            raise ValueError(f"엣지 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_edge(self, edge_id: str) -> bool:
        """엣지 삭제"""
        try:
            logger.info(f"🗑️ 엣지 삭제: {edge_id}")
            
            # 엣지 존재 확인
            existing_edge = await self.edge_repository.get_edge_by_id(edge_id)
            if not existing_edge:
                logger.warning(f"⚠️ 삭제할 엣지를 찾을 수 없음: {edge_id}")
                return False
            
            # 엣지 삭제
            deleted = await self.edge_repository.delete_edge(edge_id)
            
            if deleted:
                logger.info(f"✅ 엣지 삭제 성공: {edge_id}")
            else:
                logger.error(f"❌ 엣지 삭제 실패: {edge_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"❌ 엣지 삭제 실패: {str(e)}")
            raise ValueError(f"엣지 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔗 ReactFlow 연결 처리 (onConnect 핸들러 지원)
    # ============================================================================
    
    async def create_connection(self, flow_id: str, request: ConnectionRequest) -> ConnectionResponse:
        """ReactFlow 연결 생성 (onConnect 핸들러용)"""
        try:
            logger.info(f"🔗 ReactFlow 연결 생성: {request.source} -> {request.target}")
            
            # 연결 요청을 엣지 생성 요청으로 변환
            edge_request = EdgeCreateRequest(
                flow_id=flow_id,
                source=request.source,
                target=request.target,
                type="default",  # 기본 엣지 타입
                data={"label": "연결", "processType": "standard"},
                animated=False,
                deletable=True
            )
            
            # 엣지 생성
            edge_response = await self.create_edge(edge_request)
            
            logger.info(f"✅ ReactFlow 연결 생성 성공: {edge_response.id}")
            return ConnectionResponse(
                edge=edge_response,
                message="연결이 성공적으로 생성되었습니다"
            )
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 연결 생성 실패: {str(e)}")
            raise ValueError(f"연결 생성 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔄 엣지 변경사항 처리 (onEdgesChange 핸들러 지원)
    # ============================================================================
    
    async def process_edge_changes(self, flow_id: str, request: EdgeChangesRequest) -> EdgeChangesResponse:
        """ReactFlow 엣지 변경사항 처리"""
        try:
            logger.info(f"🔄 엣지 변경사항 처리: {len(request.changes)}개")
            
            processed_changes = 0
            updated_edges = []
            
            for change in request.changes:
                try:
                    change_type = change.type
                    edge_id = change.id
                    
                    if change_type == "remove":
                        # 엣지 삭제
                        await self.delete_edge(edge_id)
                        processed_changes += 1
                        
                    elif change_type == "select":
                        # 엣지 선택 상태 변경
                        if change.item:
                            update_request = EdgeUpdateRequest(selected=change.item.get("selected", False))
                            updated_edge = await self.update_edge(edge_id, update_request)
                            if updated_edge:
                                updated_edges.append(updated_edge)
                        processed_changes += 1
                        
                    elif change_type == "add":
                        # 새 엣지 추가
                        if change.item:
                            edge_request = EdgeCreateRequest(
                                flow_id=flow_id,
                                **change.item
                            )
                            new_edge = await self.create_edge(edge_request)
                            updated_edges.append(new_edge)
                        processed_changes += 1
                        
                    else:
                        logger.warning(f"⚠️ 지원하지 않는 변경 타입: {change_type}")
                        
                except Exception as change_error:
                    logger.error(f"❌ 개별 변경사항 처리 실패: {str(change_error)}")
                    continue
            
            logger.info(f"✅ 엣지 변경사항 처리 완료: {processed_changes}개")
            return EdgeChangesResponse(
                processed_changes=processed_changes,
                updated_edges=updated_edges,
                message=f"{processed_changes}개의 엣지 변경사항이 성공적으로 처리되었습니다"
            )
            
        except Exception as e:
            logger.error(f"❌ 엣지 변경사항 처리 실패: {str(e)}")
            raise ValueError(f"엣지 변경사항 처리 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 📊 엣지 일괄 처리 및 통계
    # ============================================================================
    
    async def batch_update_edges(self, request: EdgeBatchUpdateRequest) -> EdgeListResponse:
        """엣지 일괄 수정"""
        try:
            logger.info(f"📊 엣지 일괄 수정: {len(request.edges)}개")
            
            updated_edges = await self.edge_repository.batch_update_edges(request.edges)
            
            # EdgeResponse 형식으로 변환
            edge_responses = [self._convert_to_edge_response(edge) for edge in updated_edges]
            
            logger.info(f"✅ 엣지 일괄 수정 완료: {len(updated_edges)}개")
            return EdgeListResponse(
                edges=edge_responses,
                total=len(updated_edges)
            )
            
        except Exception as e:
            logger.error(f"❌ 엣지 일괄 수정 실패: {str(e)}")
            raise ValueError(f"엣지 일괄 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def search_edges(self, request: EdgeSearchRequest) -> EdgeListResponse:
        """엣지 검색"""
        try:
            logger.info(f"🔍 엣지 검색: {request}")
            
            all_edges = await self.edge_repository.get_all_edges()
            filtered_edges = []
            
            for edge in all_edges:
                # 플로우 ID 검색
                if request.flow_id and edge.get('flow_id') != request.flow_id:
                    continue
                
                # 시작 노드 검색
                if request.source and edge.get('source') != request.source:
                    continue
                
                # 끝 노드 검색
                if request.target and edge.get('target') != request.target:
                    continue
                
                # 타입 검색
                if request.type and edge.get('type') != request.type:
                    continue
                
                # 애니메이션 여부 검색
                if request.animated is not None and edge.get('animated') != request.animated:
                    continue
                
                # 숨김 여부 검색
                if request.hidden is not None and edge.get('hidden') != request.hidden:
                    continue
                
                filtered_edges.append(edge)
            
            # EdgeResponse 형식으로 변환
            edge_responses = [self._convert_to_edge_response(edge) for edge in filtered_edges]
            
            logger.info(f"✅ 엣지 검색 완료: {len(filtered_edges)}개")
            return EdgeListResponse(
                edges=edge_responses,
                total=len(filtered_edges)
            )
            
        except Exception as e:
            logger.error(f"❌ 엣지 검색 실패: {str(e)}")
            raise ValueError(f"엣지 검색 중 오류가 발생했습니다: {str(e)}")
    
    async def get_edge_stats(self) -> EdgeStatsResponse:
        """엣지 통계 조회"""
        try:
            logger.info(f"📊 엣지 통계 조회")
            
            all_edges = await self.edge_repository.get_all_edges()
            
            # 타입별 통계
            edges_by_type = {}
            animated_count = 0
            hidden_count = 0
            
            for edge in all_edges:
                edge_type = edge.get('type', 'default')
                edges_by_type[edge_type] = edges_by_type.get(edge_type, 0) + 1
                
                if edge.get('animated'):
                    animated_count += 1
                
                if edge.get('hidden'):
                    hidden_count += 1
            
            # 플로우별 평균 엣지 수 계산 (임시로 1로 설정)
            # TODO: 실제로는 FlowRepository에서 플로우 수를 조회해야 함
            total_flows = 1
            average_edges_per_flow = len(all_edges) / total_flows if total_flows > 0 else 0
            
            logger.info(f"✅ 엣지 통계 조회 완료: 총 {len(all_edges)}개")
            
            return EdgeStatsResponse(
                total_edges=len(all_edges),
                edges_by_type=edges_by_type,
                animated_edges=animated_count,
                hidden_edges=hidden_count,
                average_edges_per_flow=round(average_edges_per_flow, 2)
            )
            
        except Exception as e:
            logger.error(f"❌ 엣지 통계 조회 실패: {str(e)}")
            raise ValueError(f"엣지 통계 조회 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    async def _validate_edge_creation(self, edge_data: Dict[str, Any]) -> None:
        """엣지 생성 검증"""
        # 중복 ID 확인
        existing_edge = await self.edge_repository.get_edge_by_id(edge_data.get('id'))
        if existing_edge:
            raise ValueError(f"이미 존재하는 엣지 ID입니다: {edge_data.get('id')}")
        
        # 필수 필드 확인
        if not edge_data.get('source'):
            raise ValueError("시작 노드 ID는 필수입니다")
        
        if not edge_data.get('target'):
            raise ValueError("끝 노드 ID는 필수입니다")
        
        # 자기 자신으로의 연결 방지
        if edge_data.get('source') == edge_data.get('target'):
            raise ValueError("노드는 자기 자신과 연결될 수 없습니다")
    
    def _convert_to_edge_response(self, edge: Dict[str, Any]) -> EdgeResponse:
        """엣지를 EdgeResponse로 변환"""
        return EdgeResponse(
            id=edge['id'],
            flow_id=edge['flow_id'],
            source=edge['source'],
            target=edge['target'],
            type=edge['type'],
            data=edge.get('data'),
            style=edge.get('style'),
            animated=edge.get('animated', False),
            hidden=edge.get('hidden', False),
            deletable=edge.get('deletable', True),
            selected=edge.get('selected', False),
            created_at=edge.get('created_at', ''),
            updated_at=edge.get('updated_at', '')
        )
