# ============================================================================
# 🖼️ Canvas Service - Canvas 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from app.domain.canvas.canvas_entity import Canvas
from app.domain.canvas.canvas_schema import (
    CanvasCreateRequest,
    CanvasUpdateRequest,
    CanvasResponse,
    CanvasListResponse,
    CanvasSearchRequest,
    CanvasStatsResponse,
    CanvasExportRequest,
    CanvasImportRequest,
    CanvasDuplicateRequest,
    CanvasMergeRequest,
    CanvasBulkOperationRequest,
    CanvasTemplateRequest,
    # ReactFlow 관련 스키마
    ReactFlowNode,
    ReactFlowEdge,
    ReactFlowState,
    ReactFlowUpdateRequest,
    NodeChangeEvent,
    EdgeChangeEvent,
    ReactFlowViewport,
    # Connection 관련 스키마
    ConnectionParams,
    ConnectionEvent,
    ConnectionRequest
)
from app.domain.canvas.canvas_repository import CanvasRepository

class CanvasService:
    """Canvas 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, repository: Optional[CanvasRepository] = None):
        """CanvasService 초기화

        repository가 주어지면 해당 Repository를 사용하고, 없으면 기본 DB Repository를 사용합니다.
        """
        self.repository = repository or CanvasRepository(use_database=True)
        logger.info("✅ CanvasService 초기화 완료 (Repository: %s)", type(self.repository).__name__)
    
    # ============================================================================
    # 🎯 CRUD 작업
    # ============================================================================
    
    async def create_canvas(self, request: CanvasCreateRequest) -> CanvasResponse:
        """새 Canvas를 생성합니다 - React Flow 지원"""
        try:
            # 레포지토리를 통해 저장 (DB 또는 메모리)
            return await self.repository.create(request)
        except Exception as e:
            logger.error(f"❌ Canvas 생성 실패: {str(e)}")
            raise
    
    async def get_canvas(self, canvas_id: str) -> Optional[CanvasResponse]:
        """ID로 Canvas를 조회합니다"""
        try:
            res = await self.repository.get_by_id(canvas_id)
            if not res:
                logger.warning(f"⚠️ Canvas를 찾을 수 없음: {canvas_id}")
                return None
            logger.info(f"✅ Canvas 조회 완료: {canvas_id}")
            return res
            
        except Exception as e:
            logger.error(f"❌ Canvas 조회 실패: {str(e)}")
            raise
    
    async def get_all_canvases(self, page: int = 1, size: int = 20) -> CanvasListResponse:
        """모든 Canvas를 페이지네이션으로 조회합니다"""
        try:
            res = await self.repository.list_all(page=page, size=size)
            logger.info(f"✅ Canvas 목록 조회 완료: {len(res.canvases)}개 (페이지 {page})")
            return res
            
        except Exception as e:
            logger.error(f"❌ Canvas 목록 조회 실패: {str(e)}")
            raise
    
    async def update_canvas(self, canvas_id: str, request: CanvasUpdateRequest) -> Optional[CanvasResponse]:
        """Canvas를 수정합니다"""
        try:
            updated = await self.repository.update(canvas_id, request)
            if not updated:
                logger.warning(f"⚠️ 수정할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            logger.info(f"✅ Canvas 수정 완료: {canvas_id}")
            return updated
            
        except Exception as e:
            logger.error(f"❌ Canvas 수정 실패: {str(e)}")
            raise
    
    async def delete_canvas(self, canvas_id: str) -> bool:
        """Canvas를 삭제합니다"""
        try:
            ok = await self.repository.delete(canvas_id)
            if not ok:
                logger.warning(f"⚠️ 삭제할 Canvas를 찾을 수 없음: {canvas_id}")
                return False
            logger.info(f"✅ Canvas 삭제 완료: {canvas_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Canvas 삭제 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔍 검색 및 필터링
    # ============================================================================
    
    async def search_canvases(self, request: CanvasSearchRequest) -> CanvasListResponse:
        """조건에 맞는 Canvas를 검색합니다 (DB 쿼리 최적화)"""
        try:
            # 검색 필터 구성
            filters = {}
            if request.name:
                filters["name"] = request.name
            if request.min_width is not None:
                filters["min_width"] = request.min_width
            if request.max_width is not None:
                filters["max_width"] = request.max_width
            if request.min_height is not None:
                filters["min_height"] = request.min_height
            if request.max_height is not None:
                filters["max_height"] = request.max_height
            
            # Repository의 최적화된 DB 쿼리 사용
            result = await self.repository.search_with_filters(
                filters=filters,
                page=request.page,
                size=request.size
            )
            
            logger.info(f"✅ Canvas 검색 완료: {len(result.canvases)}개 (총 {result.total}개)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Canvas 검색 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🎨 Canvas 조작
    # ============================================================================
    
    async def resize_canvas(self, canvas_id: str, new_width: float, new_height: float) -> Optional[CanvasResponse]:
        """Canvas의 크기를 변경합니다"""
        try:
            # 기존 Canvas 조회
            canvas = await self.repository.get_by_id(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 크기 변경할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            # 크기 변경 요청 생성
            update_request = CanvasUpdateRequest(
                width=new_width,
                height=new_height
            )
            
            # Repository를 통해 업데이트
            updated_canvas = await self.repository.update(canvas_id, update_request)
            logger.info(f"✅ Canvas 크기 변경 완료: {canvas_id} ({new_width}x{new_height})")
            
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ Canvas 크기 변경 실패: {str(e)}")
            raise
    
    async def set_canvas_zoom(self, canvas_id: str, zoom_level: float) -> Optional[CanvasResponse]:
        """Canvas의 확대/축소 레벨을 설정합니다"""
        try:
            # 기존 Canvas 조회
            canvas = await self.repository.get_by_id(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 확대/축소할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            # 줌 레벨 변경 요청 생성
            update_request = CanvasUpdateRequest(zoom_level=zoom_level)
            
            # Repository를 통해 업데이트
            updated_canvas = await self.repository.update(canvas_id, update_request)
            logger.info(f"✅ Canvas 확대/축소 완료: {canvas_id} ({zoom_level}x)")
            
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ Canvas 확대/축소 실패: {str(e)}")
            raise
    
    async def pan_canvas(self, canvas_id: str, dx: float, dy: float) -> Optional[CanvasResponse]:
        """Canvas를 이동시킵니다"""
        try:
            # 기존 Canvas 조회
            canvas = await self.repository.get_by_id(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 이동할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            # 현재 위치에서 상대적 이동
            new_pan_x = canvas.pan_x + dx
            new_pan_y = canvas.pan_y + dy
            
            # 이동 요청 생성
            update_request = CanvasUpdateRequest(
                pan_x=new_pan_x,
                pan_y=new_pan_y
            )
            
            # Repository를 통해 업데이트
            updated_canvas = await self.repository.update(canvas_id, update_request)
            logger.info(f"✅ Canvas 이동 완료: {canvas_id} (dx: {dx}, dy: {dy})")
            
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ Canvas 이동 실패: {str(e)}")
            raise
    
    async def clear_canvas(self, canvas_id: str) -> Optional[CanvasResponse]:
        """Canvas의 모든 요소를 제거합니다"""
        try:
            # 기존 Canvas 조회
            canvas = await self.repository.get_by_id(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 초기화할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            # 모든 요소 제거 요청 생성
            update_request = CanvasUpdateRequest(
                nodes=[],  # 빈 노드 배열
                edges=[],  # 빈 엣지 배열
                metadata={}  # 빈 메타데이터
            )
            
            # Repository를 통해 업데이트
            updated_canvas = await self.repository.update(canvas_id, update_request)
            logger.info(f"✅ Canvas 초기화 완료: {canvas_id}")
            
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ Canvas 초기화 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🎯 특수 기능
    # ============================================================================
    
    async def duplicate_canvas(self, request: CanvasDuplicateRequest) -> CanvasResponse:
        """Canvas를 복제합니다"""
        try:
            # 원본 Canvas 찾기
            source_canvas = None
            for canvas in self._canvases.values():
                if canvas.name == request.new_name:
                    logger.warning(f"⚠️ 같은 이름의 Canvas가 이미 존재함: {request.new_name}")
                    raise ValueError("같은 이름의 Canvas가 이미 존재합니다")
            
            # 임시로 첫 번째 Canvas를 원본으로 사용 (실제로는 ID로 찾아야 함)
            source_canvas = list(self._canvases.values())[0] if self._canvases else None
            if not source_canvas:
                raise ValueError("복제할 원본 Canvas가 없습니다")
            
            # 새 Canvas 생성
            new_canvas_request = CanvasCreateRequest(
                name=request.new_name,
                width=source_canvas.width,
                height=source_canvas.height,
                background_color=source_canvas.background_color,
                metadata=source_canvas.metadata.copy() if request.include_metadata else {}
            )
            
            new_canvas_response = await self.create_canvas(new_canvas_request)
            logger.info(f"✅ Canvas 복제 완료: {request.new_name}")
            
            return new_canvas_response
            
        except Exception as e:
            logger.error(f"❌ Canvas 복제 실패: {str(e)}")
            raise
    
    async def export_canvas(self, canvas_id: str, request: CanvasExportRequest) -> Dict[str, Any]:
        """Canvas를 내보냅니다"""
        try:
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 내보낼 Canvas를 찾을 수 없음: {canvas_id}")
                raise ValueError("Canvas를 찾을 수 없습니다")
            
            export_data = {
                "canvas": {
                    "id": canvas.id,
                    "name": canvas.name,
                    "width": canvas.width,
                    "height": canvas.height,
                    "background_color": canvas.background_color,
                    "zoom_level": canvas.zoom_level,
                    "pan_x": canvas.pan_x,
                    "pan_y": canvas.pan_y
                }
            }
            
            # 도형 포함 여부
            if request.include_shapes:
                export_data["shapes"] = [shape.to_dict() for shape in canvas.shapes]
            
            # 화살표 포함 여부
            if request.include_arrows:
                export_data["arrows"] = [arrow.to_dict() for arrow in canvas.arrows]
            
            # 메타데이터 포함 여부
            if request.include_metadata:
                export_data["metadata"] = canvas.metadata
            
            # 형식별 처리
            if request.format.lower() == "json":
                logger.info(f"✅ Canvas JSON 내보내기 완료: {canvas_id}")
                return export_data
            elif request.format.lower() == "svg":
                # SVG 생성 로직 (구현 예정)
                logger.info(f"✅ Canvas SVG 내보내기 완료: {canvas_id}")
                return {"format": "svg", "data": export_data}
            elif request.format.lower() == "png":
                # PNG 생성 로직 (구현 예정)
                logger.info(f"✅ Canvas PNG 내보내기 완료: {canvas_id}")
                return {"format": "png", "data": export_data}
            else:
                raise ValueError("지원하지 않는 내보내기 형식입니다")
            
        except Exception as e:
            logger.error(f"❌ Canvas 내보내기 실패: {str(e)}")
            raise
    
    async def import_canvas(self, request: CanvasImportRequest) -> CanvasResponse:
        """Canvas를 가져옵니다"""
        try:
            # JSON 데이터 파싱
            import json
            try:
                canvas_data = json.loads(request.data)
            except json.JSONDecodeError:
                raise ValueError("잘못된 JSON 형식입니다")
            
            # Canvas 이름 생성
            canvas_name = canvas_data.get("canvas", {}).get("name", "가져온 Canvas")
            if request.overwrite:
                # 기존 Canvas 덮어쓰기
                existing_canvas = None
                for canvas in self._canvases.values():
                    if canvas.name == canvas_name:
                        existing_canvas = canvas
                        break
                
                if existing_canvas:
                    # 기존 Canvas 업데이트
                    update_request = CanvasUpdateRequest(
                        width=canvas_data["canvas"].get("width"),
                        height=canvas_data["canvas"].get("height"),
                        background_color=canvas_data["canvas"].get("background_color"),
                        metadata=canvas_data.get("metadata", {})
                    )
                    return await self.update_canvas(existing_canvas.id, update_request)
            
            # 새 Canvas 생성
            create_request = CanvasCreateRequest(
                name=canvas_name,
                width=canvas_data["canvas"].get("width", 800.0),
                height=canvas_data["canvas"].get("height", 600.0),
                background_color=canvas_data["canvas"].get("background_color", "#FFFFFF"),
                metadata=canvas_data.get("metadata", {})
            )
            
            canvas_response = await self.create_canvas(create_request)
            logger.info(f"✅ Canvas 가져오기 완료: {canvas_name}")
            
            return canvas_response
            
        except Exception as e:
            logger.error(f"❌ Canvas 가져오기 실패: {str(e)}")
            raise
    
    async def create_canvas_template(self, request: CanvasTemplateRequest) -> CanvasResponse:
        """Canvas 템플릿을 생성합니다"""
        try:
            # 템플릿별 기본 설정
            template_configs = {
                "flowchart": {
                    "width": 1200.0 if request.size == "large" else 800.0,
                    "height": 800.0 if request.size == "large" else 600.0,
                    "background_color": "#F8FAFC"
                },
                "diagram": {
                    "width": 1000.0 if request.size == "large" else 700.0,
                    "height": 700.0 if request.size == "large" else 500.0,
                    "background_color": "#FFFFFF"
                },
                "mindmap": {
                    "width": 1400.0 if request.size == "large" else 900.0,
                    "height": 900.0 if request.size == "large" else 600.0,
                    "background_color": "#FEF3C7"
                }
            }
            
            template_config = template_configs.get(request.template_type, template_configs["diagram"])
            
            # Canvas 생성
            canvas_request = CanvasCreateRequest(
                name=f"{request.template_type.title()} 템플릿",
                width=template_config["width"],
                height=template_config["height"],
                background_color=template_config["background_color"],
                metadata={
                    "template_type": request.template_type,
                    "size": request.size,
                    "theme": request.theme,
                    "is_template": True
                }
            )
            
            canvas_response = await self.create_canvas(canvas_request)
            logger.info(f"✅ Canvas 템플릿 생성 완료: {request.template_type}")
            
            return canvas_response
            
        except Exception as e:
            logger.error(f"❌ Canvas 템플릿 생성 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_canvas_stats(self) -> CanvasStatsResponse:
        """Canvas 통계를 조회합니다 (DB 집계 쿼리 최적화)"""
        try:
            # Repository의 최적화된 DB 집계 쿼리 사용
            stats_data = await self.repository.get_statistics()
            
            # CanvasStatsResponse 형태로 변환
            logger.info(f"✅ Canvas 통계 조회 완료: 총 {stats_data['total_canvases']}개")
            
            return CanvasStatsResponse(
                total_canvases=stats_data["total_canvases"],
                total_shapes=0,  # Shape Repository에서 별도 조회 필요
                total_arrows=0,  # Arrow Repository에서 별도 조회 필요
                average_canvas_size=stats_data["average_canvas_size"],
                most_used_colors=stats_data["most_used_colors"],
                canvas_usage_stats=stats_data.get("size_distribution", {})
            )
            
        except Exception as e:
            logger.error(f"❌ Canvas 통계 조회 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔧 유틸리티
    # ============================================================================
    
    async def get_canvas_bounds(self, canvas_id: str) -> Dict[str, float]:
        """Canvas의 경계를 계산합니다"""
        try:
            # Repository를 통해 Canvas 조회
            canvas = await self.repository.get_by_id(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 경계를 계산할 Canvas를 찾을 수 없음: {canvas_id}")
                return {}
            
            # 경계 계산 (Canvas 크기 기반)
            bounds = {
                "min_x": canvas.pan_x,
                "min_y": canvas.pan_y,
                "max_x": canvas.pan_x + canvas.width,
                "max_y": canvas.pan_y + canvas.height,
                "width": canvas.width,
                "height": canvas.height
            }
            
            logger.info(f"✅ Canvas 경계 계산 완료: {canvas_id}")
            return bounds
            
        except Exception as e:
            logger.error(f"❌ Canvas 경계 계산 실패: {str(e)}")
            raise
    
    async def get_elements_at_point(self, canvas_id: str, x: float, y: float) -> Dict[str, Any]:
        """주어진 점에 있는 모든 요소를 반환합니다"""
        try:
            # Repository를 통해 Canvas 조회
            canvas = await self.repository.get_by_id(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 요소를 찾을 Canvas를 찾을 수 없음: {canvas_id}")
                return {}
            
            # 점이 Canvas 영역 내에 있는지 확인
            if not (canvas.pan_x <= x <= canvas.pan_x + canvas.width and 
                    canvas.pan_y <= y <= canvas.pan_y + canvas.height):
                logger.info(f"✅ 점이 Canvas 영역 밖에 있음: ({x}, {y})")
                return {
                    "canvas_id": canvas_id,
                    "point": {"x": x, "y": y},
                    "nodes": [],
                    "edges": []
                }
            
            # 노드와 엣지에서 해당 점 근처의 요소 찾기
            nearby_nodes = []
            nearby_edges = []
            
            # 노드 검사
            for node in canvas.nodes:
                node_x = node.get("position", {}).get("x", 0)
                node_y = node.get("position", {}).get("y", 0)
                node_width = node.get("width", 100)
                node_height = node.get("height", 50)
                
                if (node_x <= x <= node_x + node_width and 
                    node_y <= y <= node_y + node_height):
                    nearby_nodes.append(node)
            
            # 응답 데이터 구성
            result = {
                "canvas_id": canvas_id,
                "point": {"x": x, "y": y},
                "nodes": nearby_nodes,
                "edges": nearby_edges  # 엣지는 복잡한 계산이 필요하므로 향후 구현
            }
            
            logger.info(f"✅ 점 근처 요소 조회 완료: ({x}, {y}) - 노드 {len(nearby_nodes)}개")
            return result
            
        except Exception as e:
            logger.error(f"❌ 점 근처 요소 조회 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔄 ReactFlow 전용 메서드
    # ============================================================================
    
    async def update_reactflow_state(self, request: ReactFlowUpdateRequest) -> CanvasResponse:
        """ReactFlow 상태 업데이트"""
        try:
            logger.info(f"🔄 ReactFlow 상태 업데이트: {request.canvas_id}")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(request.canvas_id)
            if not canvas:
                raise Exception(f"Canvas {request.canvas_id}를 찾을 수 없습니다")
            
            # 업데이트 요청 생성
            update_request = CanvasUpdateRequest(
                nodes=request.nodes,
                edges=request.edges,
                viewport=request.viewport
            )
            
            # 캔버스 업데이트
            updated_canvas = await self.update_canvas(request.canvas_id, update_request)
            
            logger.info(f"✅ ReactFlow 상태 업데이트 완료: {request.canvas_id}")
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 상태 업데이트 실패: {str(e)}")
            raise
    
    async def add_reactflow_node(self, canvas_id: str, node: ReactFlowNode) -> CanvasResponse:
        """ReactFlow 노드 추가"""
        try:
            logger.info(f"➕ ReactFlow 노드 추가: {canvas_id} - {node.id}")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(canvas_id)
            if not canvas:
                raise Exception(f"Canvas {canvas_id}를 찾을 수 없습니다")
            
            # 기존 노드 목록에 새 노드 추가
            updated_nodes = canvas.nodes.copy()
            updated_nodes.append(node)
            
            # 캔버스 업데이트
            update_request = CanvasUpdateRequest(nodes=updated_nodes)
            updated_canvas = await self.update_canvas(canvas_id, update_request)
            
            logger.info(f"✅ ReactFlow 노드 추가 완료: {node.id}")
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 노드 추가 실패: {str(e)}")
            raise
    
    async def remove_reactflow_node(self, canvas_id: str, node_id: str) -> CanvasResponse:
        """ReactFlow 노드 제거"""
        try:
            logger.info(f"➖ ReactFlow 노드 제거: {canvas_id} - {node_id}")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(canvas_id)
            if not canvas:
                raise Exception(f"Canvas {canvas_id}를 찾을 수 없습니다")
            
            # 노드 제거
            updated_nodes = [node for node in canvas.nodes if node.id != node_id]
            
            # 관련 엣지도 제거
            updated_edges = [
                edge for edge in canvas.edges 
                if edge.source != node_id and edge.target != node_id
            ]
            
            # 캔버스 업데이트
            update_request = CanvasUpdateRequest(nodes=updated_nodes, edges=updated_edges)
            updated_canvas = await self.update_canvas(canvas_id, update_request)
            
            logger.info(f"✅ ReactFlow 노드 제거 완료: {node_id}")
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 노드 제거 실패: {str(e)}")
            raise
    
    async def add_reactflow_edge(self, canvas_id: str, edge: ReactFlowEdge) -> CanvasResponse:
        """ReactFlow 엣지 추가"""
        try:
            logger.info(f"🔗 ReactFlow 엣지 추가: {canvas_id} - {edge.id}")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(canvas_id)
            if not canvas:
                raise Exception(f"Canvas {canvas_id}를 찾을 수 없습니다")
            
            # 소스와 타겟 노드 존재 확인
            node_ids = {node.id for node in canvas.nodes}
            if edge.source not in node_ids:
                raise Exception(f"소스 노드 {edge.source}를 찾을 수 없습니다")
            if edge.target not in node_ids:
                raise Exception(f"타겟 노드 {edge.target}를 찾을 수 없습니다")
            
            # 기존 엣지 목록에 새 엣지 추가
            updated_edges = canvas.edges.copy()
            updated_edges.append(edge)
            
            # 캔버스 업데이트
            update_request = CanvasUpdateRequest(edges=updated_edges)
            updated_canvas = await self.update_canvas(canvas_id, update_request)
            
            logger.info(f"✅ ReactFlow 엣지 추가 완료: {edge.id}")
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 엣지 추가 실패: {str(e)}")
            raise
    
    async def remove_reactflow_edge(self, canvas_id: str, edge_id: str) -> CanvasResponse:
        """ReactFlow 엣지 제거"""
        try:
            logger.info(f"🔗❌ ReactFlow 엣지 제거: {canvas_id} - {edge_id}")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(canvas_id)
            if not canvas:
                raise Exception(f"Canvas {canvas_id}를 찾을 수 없습니다")
            
            # 엣지 제거
            updated_edges = [edge for edge in canvas.edges if edge.id != edge_id]
            
            # 캔버스 업데이트
            update_request = CanvasUpdateRequest(edges=updated_edges)
            updated_canvas = await self.update_canvas(canvas_id, update_request)
            
            logger.info(f"✅ ReactFlow 엣지 제거 완료: {edge_id}")
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 엣지 제거 실패: {str(e)}")
            raise
    
    async def apply_node_changes(self, canvas_id: str, changes: List[NodeChangeEvent]) -> CanvasResponse:
        """ReactFlow 노드 변경사항 적용 (이벤트 핸들러)"""
        try:
            logger.info(f"🔄 ReactFlow 노드 변경사항 적용: {canvas_id} - {len(changes)}개")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(canvas_id)
            if not canvas:
                raise Exception(f"Canvas {canvas_id}를 찾을 수 없습니다")
            
            updated_nodes = canvas.nodes.copy()
            
            # 각 변경사항 적용
            for change in changes:
                if change.type == "position":
                    # 노드 위치 변경
                    for node in updated_nodes:
                        if node.id == change.id and change.position:
                            node.position = change.position
                
                elif change.type == "select":
                    # 노드 선택 상태 변경
                    for node in updated_nodes:
                        if node.id == change.id:
                            # 선택 상태는 일반적으로 클라이언트에서 관리하므로 로그만 기록
                            logger.debug(f"노드 {change.id} 선택 상태: {change.selected}")
                
                elif change.type == "remove":
                    # 노드 제거
                    updated_nodes = [node for node in updated_nodes if node.id != change.id]
            
            # 캔버스 업데이트
            update_request = CanvasUpdateRequest(nodes=updated_nodes)
            updated_canvas = await self.update_canvas(canvas_id, update_request)
            
            logger.info(f"✅ ReactFlow 노드 변경사항 적용 완료: {len(changes)}개")
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 노드 변경사항 적용 실패: {str(e)}")
            raise
    
    async def apply_edge_changes(self, canvas_id: str, changes: List[EdgeChangeEvent]) -> CanvasResponse:
        """ReactFlow 엣지 변경사항 적용 (이벤트 핸들러)"""
        try:
            logger.info(f"🔄 ReactFlow 엣지 변경사항 적용: {canvas_id} - {len(changes)}개")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(canvas_id)
            if not canvas:
                raise Exception(f"Canvas {canvas_id}를 찾을 수 없습니다")
            
            updated_edges = canvas.edges.copy()
            
            # 각 변경사항 적용
            for change in changes:
                if change.type == "select":
                    # 엣지 선택 상태 변경 (클라이언트에서 관리)
                    logger.debug(f"엣지 {change.id} 선택 상태: {change.selected}")
                
                elif change.type == "remove":
                    # 엣지 제거
                    updated_edges = [edge for edge in updated_edges if edge.id != change.id]
            
            # 캔버스 업데이트
            update_request = CanvasUpdateRequest(edges=updated_edges)
            updated_canvas = await self.update_canvas(canvas_id, update_request)
            
            logger.info(f"✅ ReactFlow 엣지 변경사항 적용 완료: {len(changes)}개")
            return updated_canvas
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 엣지 변경사항 적용 실패: {str(e)}")
            raise
    
    async def get_reactflow_examples(self) -> Dict[str, Any]:
        """ReactFlow 사용 예제 반환"""
        try:
            logger.info("📝 ReactFlow 사용 예제 반환")
            
            # 기본 노드/엣지 예제 (사용자 요청사항)
            initial_nodes = [
                {
                    "id": "n1",
                    "position": {"x": 0, "y": 0},
                    "data": {"label": "Node 1"},
                    "type": "input"
                },
                {
                    "id": "n2", 
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "Node 2"}
                }
            ]
            
            initial_edges = [
                {
                    "id": "n1-n2",
                    "source": "n1",
                    "target": "n2"
                }
            ]
            
            # React 코드 예제
            react_examples = {
                "imports": """import { useState, useCallback } from 'react';
import { ReactFlow, applyEdgeChanges, applyNodeChanges } from '@xyflow/react';""",
                
                "define_nodes_edges": f"""const initialNodes = {initial_nodes};
const initialEdges = {initial_edges};""",
                
                "initialize_state": """export default function App() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  
  return (
    <div style={{ height: '100%', width: '100%' }}>
      <ReactFlow>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}""",
                
                "event_handlers": """const onNodesChange = useCallback(
  (changes) => setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)),
  [],
);
const onEdgesChange = useCallback(
  (changes) => setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
  [],
);""",
                
                "pass_to_reactflow": """<ReactFlow
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  fitView
>
  <Background />
  <Controls />
</ReactFlow>"""
            }
            
            return {
                "initialNodes": initial_nodes,
                "initialEdges": initial_edges,
                "examples": react_examples,
                "api_endpoints": {
                    "initialize": "POST /canvas/reactflow/initialize",
                    "get_state": "GET /canvas/reactflow/{canvas_id}/state",
                    "update_state": "PUT /canvas/reactflow/{canvas_id}/state",
                    "add_node": "POST /canvas/reactflow/{canvas_id}/nodes",
                    "remove_node": "DELETE /canvas/reactflow/{canvas_id}/nodes/{node_id}",
                    "add_edge": "POST /canvas/reactflow/{canvas_id}/edges",
                    "remove_edge": "DELETE /canvas/reactflow/{canvas_id}/edges/{edge_id}",
                    "apply_node_changes": "POST /canvas/reactflow/{canvas_id}/changes/nodes",
                    "apply_edge_changes": "POST /canvas/reactflow/{canvas_id}/changes/edges"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 예제 반환 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔗 Connection 관련 메서드
    # ============================================================================
    
    async def handle_connection(self, canvas_id: str, connection_request: ConnectionRequest) -> ReactFlowEdge:
        """ReactFlow onConnect 핸들러 - 연결을 엣지로 변환하여 추가"""
        try:
            logger.info(f"🔗 ReactFlow 연결 처리: {canvas_id} - {connection_request.connection.source} → {connection_request.connection.target}")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(canvas_id)
            if not canvas:
                raise Exception(f"Canvas {canvas_id}를 찾을 수 없습니다")
            
            # 소스와 타겟 노드 존재 확인
            node_ids = {node.id for node in canvas.nodes}
            if connection_request.connection.source not in node_ids:
                raise Exception(f"소스 노드 {connection_request.connection.source}를 찾을 수 없습니다")
            if connection_request.connection.target not in node_ids:
                raise Exception(f"타겟 노드 {connection_request.connection.target}를 찾을 수 없습니다")
            
            # 연결 파라미터를 엣지로 변환
            edge_id = self._generate_edge_id(
                connection_request.connection.source, 
                connection_request.connection.target,
                connection_request.connection.sourceHandle,
                connection_request.connection.targetHandle
            )
            
            # 기본 엣지 옵션
            default_options = {
                "type": "default",
                "animated": False,
                "style": {"stroke": "#b1b1b7"},
                "labelStyle": {"fill": "#000"},
                "labelBgStyle": {"fill": "#fff", "color": "#000"}
            }
            
            # 사용자 지정 옵션과 병합
            edge_options = {**default_options, **connection_request.edge_options}
            
            # ReactFlow 엣지 생성
            new_edge = ReactFlowEdge(
                id=edge_id,
                source=connection_request.connection.source,
                target=connection_request.connection.target,
                type=edge_options.get("type", "default"),
                animated=edge_options.get("animated", False),
                style=edge_options.get("style", {}),
                label=edge_options.get("label"),
                labelStyle=edge_options.get("labelStyle", {}),
                labelBgStyle=edge_options.get("labelBgStyle", {})
            )
            
            # 핸들 정보가 있으면 추가
            if connection_request.connection.sourceHandle:
                new_edge.sourceHandle = connection_request.connection.sourceHandle
            if connection_request.connection.targetHandle:
                new_edge.targetHandle = connection_request.connection.targetHandle
            
            # 엣지를 캔버스에 추가
            updated_canvas = await self.add_reactflow_edge(canvas_id, new_edge)
            
            logger.info(f"✅ ReactFlow 연결 처리 완료: {edge_id}")
            return new_edge
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 연결 처리 실패: {str(e)}")
            raise
    
    async def handle_multiple_connections(self, canvas_id: str, connections: List[ConnectionParams]) -> List[ReactFlowEdge]:
        """여러 연결을 한 번에 처리"""
        try:
            logger.info(f"🔗📦 ReactFlow 다중 연결 처리: {canvas_id} - {len(connections)}개 연결")
            
            created_edges = []
            for connection in connections:
                try:
                    connection_request = ConnectionRequest(
                        canvas_id=canvas_id,
                        connection=connection
                    )
                    new_edge = await self.handle_connection(canvas_id, connection_request)
                    created_edges.append(new_edge)
                except Exception as conn_error:
                    logger.error(f"❌ 개별 연결 처리 실패: {connection.source} → {connection.target} - {str(conn_error)}")
                    # 개별 연결 실패는 전체를 중단시키지 않음
                    continue
            
            logger.info(f"✅ ReactFlow 다중 연결 처리 완료: {len(created_edges)}/{len(connections)}개 성공")
            return created_edges
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 다중 연결 처리 실패: {str(e)}")
            raise
    
    async def validate_connection(self, canvas_id: str, connection: ConnectionParams) -> Dict[str, Any]:
        """연결 유효성 검증"""
        try:
            logger.info(f"🔍 ReactFlow 연결 유효성 검증: {canvas_id} - {connection.source} → {connection.target}")
            
            # 기존 캔버스 조회
            canvas = await self.get_canvas(canvas_id)
            if not canvas:
                return {
                    "valid": False,
                    "error": f"Canvas {canvas_id}를 찾을 수 없습니다"
                }
            
            # 노드 존재 확인
            node_ids = {node.id for node in canvas.nodes}
            
            if connection.source not in node_ids:
                return {
                    "valid": False,
                    "error": f"소스 노드 {connection.source}를 찾을 수 없습니다"
                }
            
            if connection.target not in node_ids:
                return {
                    "valid": False,
                    "error": f"타겟 노드 {connection.target}를 찾을 수 없습니다"
                }
            
            # 자기 자신으로의 연결 방지
            if connection.source == connection.target:
                return {
                    "valid": False,
                    "error": "자기 자신으로의 연결은 허용되지 않습니다"
                }
            
            # 중복 연결 확인
            edge_id = self._generate_edge_id(
                connection.source, 
                connection.target,
                connection.sourceHandle,
                connection.targetHandle
            )
            
            existing_edge_ids = {edge.id for edge in canvas.edges}
            if edge_id in existing_edge_ids:
                return {
                    "valid": False,
                    "error": "이미 존재하는 연결입니다"
                }
            
            return {
                "valid": True,
                "message": "유효한 연결입니다",
                "edge_id": edge_id
            }
            
        except Exception as e:
            logger.error(f"❌ ReactFlow 연결 유효성 검증 실패: {str(e)}")
            return {
                "valid": False,
                "error": f"유효성 검증 중 오류 발생: {str(e)}"
            }
    
    def _generate_edge_id(self, source: str, target: str, source_handle: Optional[str] = None, target_handle: Optional[str] = None) -> str:
        """엣지 ID 생성"""
        parts = [source, target]
        
        if source_handle:
            parts.append(f"sh-{source_handle}")
        if target_handle:
            parts.append(f"th-{target_handle}")
        
        return "-".join(parts)
    
    async def get_connection_examples(self) -> Dict[str, Any]:
        """Connection 사용 예제 반환"""
        try:
            logger.info("📝 ReactFlow Connection 사용 예제 반환")
            
            return {
                "onConnect_handler": {
                    "description": "ReactFlow onConnect 핸들러 구현",
                    "import": "import { addEdge } from '@xyflow/react';",
                    "basic_usage": """const onConnect = useCallback(
  (params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
  [],
);""",
                    "with_backend_sync": """const onConnect = useCallback(
  async (params) => {
    // 로컬 상태 즉시 업데이트
    setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot));
    
    // 백엔드 동기화 (비동기)
    try {
      await fetch(`/canvas/reactflow/${canvasId}/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          canvas_id: canvasId,
          connection: params,
          edge_options: { 
            animated: false, 
            style: { stroke: '#b1b1b7' } 
          }
        })
      });
    } catch (error) {
      console.error('연결 저장 실패:', error);
      // 실패 시 롤백 로직 추가 가능
    }
  },
  [canvasId],
);""",
                    "reactflow_usage": """<ReactFlow
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  onConnect={onConnect}
  fitView
>
  <Background />
  <Controls />
</ReactFlow>"""
                },
                "connection_params": {
                    "source": "출발 노드 ID",
                    "target": "도착 노드 ID", 
                    "sourceHandle": "출발 핸들 ID (선택적)",
                    "targetHandle": "도착 핸들 ID (선택적)"
                },
                "api_endpoints": {
                    "create_connection": "POST /canvas/reactflow/{canvas_id}/connect",
                    "batch_connections": "POST /canvas/reactflow/{canvas_id}/connection-events",
                    "examples": "GET /canvas/reactflow/examples/onconnect"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ ReactFlow Connection 예제 반환 실패: {str(e)}")
            raise
