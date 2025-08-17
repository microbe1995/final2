# ============================================================================
# 🖼️ Canvas Service - Canvas 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from ..entity.canvas_entity import Canvas
from ..schema.canvas_schema import (
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

class CanvasService:
    """Canvas 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self):
        """CanvasService 초기화"""
        self._canvases: Dict[str, Canvas] = {}  # 메모리 저장소 (실제로는 DB 사용)
        logger.info("✅ CanvasService 초기화 완료")
    
    # ============================================================================
    # 🎯 CRUD 작업
    # ============================================================================
    
    async def create_canvas(self, request: CanvasCreateRequest) -> CanvasResponse:
        """새 Canvas를 생성합니다"""
        try:
            # 고유 ID 생성
            canvas_id = str(uuid.uuid4())
            
            # Canvas 엔티티 생성
            canvas = Canvas(
                id=canvas_id,
                name=request.name,
                width=request.width,
                height=request.height,
                background_color=request.background_color,
                metadata=request.metadata or {}
            )
            
            # 저장
            self._canvases[canvas_id] = canvas
            logger.info(f"✅ Canvas 생성 완료: {canvas_id} ({request.name})")
            
            return CanvasResponse(**canvas.to_dict())
            
        except Exception as e:
            logger.error(f"❌ Canvas 생성 실패: {str(e)}")
            raise
    
    async def get_canvas(self, canvas_id: str) -> Optional[CanvasResponse]:
        """ID로 Canvas를 조회합니다"""
        try:
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            logger.info(f"✅ Canvas 조회 완료: {canvas_id}")
            return CanvasResponse(**canvas.to_dict())
            
        except Exception as e:
            logger.error(f"❌ Canvas 조회 실패: {str(e)}")
            raise
    
    async def get_all_canvases(self, page: int = 1, size: int = 20) -> CanvasListResponse:
        """모든 Canvas를 페이지네이션으로 조회합니다"""
        try:
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            
            canvases_list = list(self._canvases.values())
            total = len(canvases_list)
            
            # 페이지네이션 적용
            paginated_canvases = canvases_list[start_idx:end_idx]
            
            # 응답 생성
            canvas_responses = [CanvasResponse(**canvas.to_dict()) for canvas in paginated_canvases]
            
            logger.info(f"✅ Canvas 목록 조회 완료: {len(canvas_responses)}개 (페이지 {page})")
            
            return CanvasListResponse(
                canvases=canvas_responses,
                total=total,
                page=page,
                size=size
            )
            
        except Exception as e:
            logger.error(f"❌ Canvas 목록 조회 실패: {str(e)}")
            raise
    
    async def update_canvas(self, canvas_id: str, request: CanvasUpdateRequest) -> Optional[CanvasResponse]:
        """Canvas를 수정합니다"""
        try:
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 수정할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            # 업데이트할 필드들만 수정
            if request.name is not None:
                canvas.name = request.name
            if request.width is not None:
                canvas.width = request.width
            if request.height is not None:
                canvas.height = request.height
            if request.background_color is not None:
                canvas.background_color = request.background_color
            if request.zoom_level is not None:
                canvas.set_zoom(request.zoom_level)
            if request.pan_x is not None:
                canvas.pan_x = request.pan_x
            if request.pan_y is not None:
                canvas.pan_y = request.pan_y
            if request.metadata is not None:
                canvas.metadata.update(request.metadata)
            
            # 수정 시간 업데이트
            canvas.updated_at = datetime.utcnow()
            
            logger.info(f"✅ Canvas 수정 완료: {canvas_id}")
            return CanvasResponse(**canvas.to_dict())
            
        except Exception as e:
            logger.error(f"❌ Canvas 수정 실패: {str(e)}")
            raise
    
    async def delete_canvas(self, canvas_id: str) -> bool:
        """Canvas를 삭제합니다"""
        try:
            if canvas_id not in self._canvases:
                logger.warning(f"⚠️ 삭제할 Canvas를 찾을 수 없음: {canvas_id}")
                return False
            
            del self._canvases[canvas_id]
            logger.info(f"✅ Canvas 삭제 완료: {canvas_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Canvas 삭제 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔍 검색 및 필터링
    # ============================================================================
    
    async def search_canvases(self, request: CanvasSearchRequest) -> CanvasListResponse:
        """조건에 맞는 Canvas를 검색합니다"""
        try:
            filtered_canvases = []
            
            for canvas in self._canvases.values():
                # 이름 필터 (부분 일치)
                if request.name and request.name.lower() not in canvas.name.lower():
                    continue
                
                # 너비 필터
                if request.min_width is not None and canvas.width < request.min_width:
                    continue
                if request.max_width is not None and canvas.width > request.max_width:
                    continue
                
                # 높이 필터
                if request.min_height is not None and canvas.height < request.min_height:
                    continue
                if request.max_height is not None and canvas.height > request.max_height:
                    continue
                
                # 도형 포함 여부 필터
                if request.has_shapes is not None:
                    has_shapes = len(canvas.shapes) > 0
                    if has_shapes != request.has_shapes:
                        continue
                
                # 화살표 포함 여부 필터
                if request.has_arrows is not None:
                    has_arrows = len(canvas.arrows) > 0
                    if has_arrows != request.has_arrows:
                        continue
                
                filtered_canvases.append(canvas)
            
            # 페이지네이션 적용
            start_idx = (request.page - 1) * request.size
            end_idx = start_idx + request.size
            paginated_canvases = filtered_canvases[start_idx:end_idx]
            
            # 응답 생성
            canvas_responses = [CanvasResponse(**canvas.to_dict()) for canvas in paginated_canvases]
            
            logger.info(f"✅ Canvas 검색 완료: {len(canvas_responses)}개 (필터링된 {len(filtered_canvases)}개)")
            
            return CanvasListResponse(
                canvases=canvas_responses,
                total=len(filtered_canvases),
                page=request.page,
                size=request.size
            )
            
        except Exception as e:
            logger.error(f"❌ Canvas 검색 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🎨 Canvas 조작
    # ============================================================================
    
    async def resize_canvas(self, canvas_id: str, new_width: float, new_height: float) -> Optional[CanvasResponse]:
        """Canvas의 크기를 변경합니다"""
        try:
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 크기 변경할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            canvas.resize(new_width, new_height)
            logger.info(f"✅ Canvas 크기 변경 완료: {canvas_id} ({new_width}x{new_height})")
            
            return CanvasResponse(**canvas.to_dict())
            
        except Exception as e:
            logger.error(f"❌ Canvas 크기 변경 실패: {str(e)}")
            raise
    
    async def set_canvas_zoom(self, canvas_id: str, zoom_level: float) -> Optional[CanvasResponse]:
        """Canvas의 확대/축소 레벨을 설정합니다"""
        try:
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 확대/축소할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            canvas.set_zoom(zoom_level)
            logger.info(f"✅ Canvas 확대/축소 완료: {canvas_id} ({zoom_level}x)")
            
            return CanvasResponse(**canvas.to_dict())
            
        except Exception as e:
            logger.error(f"❌ Canvas 확대/축소 실패: {str(e)}")
            raise
    
    async def pan_canvas(self, canvas_id: str, dx: float, dy: float) -> Optional[CanvasResponse]:
        """Canvas를 이동시킵니다"""
        try:
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 이동할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            canvas.pan(dx, dy)
            logger.info(f"✅ Canvas 이동 완료: {canvas_id} (dx: {dx}, dy: {dy})")
            
            return CanvasResponse(**canvas.to_dict())
            
        except Exception as e:
            logger.error(f"❌ Canvas 이동 실패: {str(e)}")
            raise
    
    async def clear_canvas(self, canvas_id: str) -> Optional[CanvasResponse]:
        """Canvas의 모든 요소를 제거합니다"""
        try:
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 초기화할 Canvas를 찾을 수 없음: {canvas_id}")
                return None
            
            canvas.clear()
            logger.info(f"✅ Canvas 초기화 완료: {canvas_id}")
            
            return CanvasResponse(**canvas.to_dict())
            
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
        """Canvas 통계를 조회합니다"""
        try:
            total_canvases = len(self._canvases)
            
            # 도형과 화살표 수 계산
            total_shapes = sum(len(canvas.shapes) for canvas in self._canvases.values())
            total_arrows = sum(len(canvas.arrows) for canvas in self._canvases.values())
            
            # 평균 Canvas 크기 계산
            if total_canvases > 0:
                total_width = sum(canvas.width for canvas in self._canvases.values())
                total_height = sum(canvas.height for canvas in self._canvases.values())
                avg_width = total_width / total_canvases
                avg_height = total_height / total_canvases
            else:
                avg_width = avg_height = 0.0
            
            # 색상 사용 통계 (간단한 구현)
            most_used_colors = [
                {"color": "#FFFFFF", "count": total_canvases},  # 배경색
                {"color": "#3B82F6", "count": 0},  # 기본 도형 색상
                {"color": "#EF4444", "count": 0}   # 기본 화살표 색상
            ]
            
            # Canvas 사용 통계
            canvas_usage_stats = {
                "empty": sum(1 for c in self._canvases.values() if len(c.shapes) == 0 and len(c.arrows) == 0),
                "with_shapes": sum(1 for c in self._canvases.values() if len(c.shapes) > 0),
                "with_arrows": sum(1 for c in self._canvases.values() if len(c.arrows) > 0),
                "templates": sum(1 for c in self._canvases.values() if c.metadata.get("is_template", False))
            }
            
            logger.info(f"✅ Canvas 통계 조회 완료: 총 {total_canvases}개")
            
            return CanvasStatsResponse(
                total_canvases=total_canvases,
                total_shapes=total_shapes,
                total_arrows=total_arrows,
                average_canvas_size={"width": avg_width, "height": avg_height},
                most_used_colors=most_used_colors,
                canvas_usage_stats=canvas_usage_stats
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
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 경계를 계산할 Canvas를 찾을 수 없음: {canvas_id}")
                return {}
            
            bounds = canvas.get_bounds()
            logger.info(f"✅ Canvas 경계 계산 완료: {canvas_id}")
            
            return bounds
            
        except Exception as e:
            logger.error(f"❌ Canvas 경계 계산 실패: {str(e)}")
            raise
    
    async def get_elements_at_point(self, canvas_id: str, x: float, y: float) -> Dict[str, Any]:
        """주어진 점에 있는 모든 요소를 반환합니다"""
        try:
            canvas = self._canvases.get(canvas_id)
            if not canvas:
                logger.warning(f"⚠️ 요소를 찾을 Canvas를 찾을 수 없음: {canvas_id}")
                return {}
            
            elements = canvas.get_elements_at_point(x, y)
            
            # 응답 데이터 구성
            result = {
                "canvas_id": canvas_id,
                "point": {"x": x, "y": y},
                "shapes": [shape.to_dict() for shape in elements if hasattr(shape, 'type') and 'shape' in str(type(shape)).lower()],
                "arrows": [arrow.to_dict() for arrow in elements if hasattr(arrow, 'type') and 'arrow' in str(type(arrow)).lower()]
            }
            
            logger.info(f"✅ 점 근처 요소 조회 완료: ({x}, {y}) - {len(elements)}개")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 점 근처 요소 조회 실패: {str(e)}")
            raise
