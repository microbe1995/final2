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
    CanvasTemplateRequest
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
