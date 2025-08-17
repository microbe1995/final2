# ============================================================================
# 🎨 Shape Service - 도형 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from ..entity.shape_entity import Shape, ShapeType
from ..schema.shape_schema import (
    ShapeCreateRequest,
    ShapeUpdateRequest,
    ShapeResponse,
    ShapeListResponse,
    ShapeSearchRequest,
    ShapeStatsResponse
)

class ShapeService:
    """도형 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self):
        """ShapeService 초기화"""
        self._shapes: Dict[str, Shape] = {}  # 메모리 저장소 (실제로는 DB 사용)
        logger.info("✅ ShapeService 초기화 완료")
    
    # ============================================================================
    # 🎯 CRUD 작업
    # ============================================================================
    
    async def create_shape(self, request: ShapeCreateRequest) -> ShapeResponse:
        """새 도형을 생성합니다"""
        try:
            # 고유 ID 생성
            shape_id = str(uuid.uuid4())
            
            # Shape 엔티티 생성
            shape = Shape(
                id=shape_id,
                type=ShapeType(request.type.value),
                x=request.x,
                y=request.y,
                width=request.width,
                height=request.height,
                color=request.color,
                stroke_width=request.stroke_width,
                fill_color=request.fill_color,
                rotation=request.rotation,
                opacity=request.opacity,
                canvas_id=request.canvas_id,
                metadata=request.metadata or {}
            )
            
            # 저장
            self._shapes[shape_id] = shape
            logger.info(f"✅ 도형 생성 완료: {shape_id} ({request.type.value})")
            
            return ShapeResponse(**shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 생성 실패: {str(e)}")
            raise
    
    async def get_shape(self, shape_id: str) -> Optional[ShapeResponse]:
        """ID로 도형을 조회합니다"""
        try:
            shape = self._shapes.get(shape_id)
            if not shape:
                logger.warning(f"⚠️ 도형을 찾을 수 없음: {shape_id}")
                return None
            
            logger.info(f"✅ 도형 조회 완료: {shape_id}")
            return ShapeResponse(**shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 조회 실패: {str(e)}")
            raise
    
    async def get_all_shapes(self, page: int = 1, size: int = 20) -> ShapeListResponse:
        """모든 도형을 페이지네이션으로 조회합니다"""
        try:
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            
            shapes_list = list(self._shapes.values())
            total = len(shapes_list)
            
            # 페이지네이션 적용
            paginated_shapes = shapes_list[start_idx:end_idx]
            
            # 응답 생성
            shape_responses = [ShapeResponse(**shape.to_dict()) for shape in paginated_shapes]
            
            logger.info(f"✅ 도형 목록 조회 완료: {len(shape_responses)}개 (페이지 {page})")
            
            return ShapeListResponse(
                shapes=shape_responses,
                total=total,
                page=page,
                size=size
            )
            
        except Exception as e:
            logger.error(f"❌ 도형 목록 조회 실패: {str(e)}")
            raise
    
    async def update_shape(self, shape_id: str, request: ShapeUpdateRequest) -> Optional[ShapeResponse]:
        """도형을 수정합니다"""
        try:
            shape = self._shapes.get(shape_id)
            if not shape:
                logger.warning(f"⚠️ 수정할 도형을 찾을 수 없음: {shape_id}")
                return None
            
            # 업데이트할 필드들만 수정
            if request.x is not None:
                shape.x = request.x
            if request.y is not None:
                shape.y = request.y
            if request.width is not None:
                shape.width = request.width
            if request.height is not None:
                shape.height = request.height
            if request.color is not None:
                shape.color = request.color
            if request.stroke_width is not None:
                shape.stroke_width = request.stroke_width
            if request.fill_color is not None:
                shape.fill_color = request.fill_color
            if request.rotation is not None:
                shape.rotation = request.rotation
            if request.opacity is not None:
                shape.opacity = request.opacity
            if request.metadata is not None:
                shape.metadata.update(request.metadata)
            
            # 수정 시간 업데이트
            shape.updated_at = datetime.utcnow()
            
            logger.info(f"✅ 도형 수정 완료: {shape_id}")
            return ShapeResponse(**shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 수정 실패: {str(e)}")
            raise
    
    async def delete_shape(self, shape_id: str) -> bool:
        """도형을 삭제합니다"""
        try:
            if shape_id not in self._shapes:
                logger.warning(f"⚠️ 삭제할 도형을 찾을 수 없음: {shape_id}")
                return False
            
            del self._shapes[shape_id]
            logger.info(f"✅ 도형 삭제 완료: {shape_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 도형 삭제 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔍 검색 및 필터링
    # ============================================================================
    
    async def search_shapes(self, request: ShapeSearchRequest) -> ShapeListResponse:
        """조건에 맞는 도형을 검색합니다"""
        try:
            filtered_shapes = []
            
            for shape in self._shapes.values():
                # 타입 필터
                if request.type and shape.type != ShapeType(request.type.value):
                    continue
                
                # Canvas ID 필터
                if request.canvas_id and shape.canvas_id != request.canvas_id:
                    continue
                
                # 좌표 범위 필터
                if request.min_x is not None and shape.x < request.min_x:
                    continue
                if request.max_x is not None and shape.x > request.max_x:
                    continue
                if request.min_y is not None and shape.y < request.min_y:
                    continue
                if request.max_y is not None and shape.y > request.max_y:
                    continue
                
                # 색상 필터
                if request.color and shape.color != request.color:
                    continue
                
                filtered_shapes.append(shape)
            
            # 페이지네이션 적용
            start_idx = (request.page - 1) * request.size
            end_idx = start_idx + request.size
            paginated_shapes = filtered_shapes[start_idx:end_idx]
            
            # 응답 생성
            shape_responses = [ShapeResponse(**shape.to_dict()) for shape in paginated_shapes]
            
            logger.info(f"✅ 도형 검색 완료: {len(shape_responses)}개 (필터링된 {len(filtered_shapes)}개)")
            
            return ShapeListResponse(
                shapes=shape_responses,
                total=len(filtered_shapes),
                page=request.page,
                size=request.size
            )
            
        except Exception as e:
            logger.error(f"❌ 도형 검색 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🎨 도형 조작
    # ============================================================================
    
    async def move_shape(self, shape_id: str, dx: float, dy: float) -> Optional[ShapeResponse]:
        """도형을 이동시킵니다"""
        try:
            shape = self._shapes.get(shape_id)
            if not shape:
                logger.warning(f"⚠️ 이동할 도형을 찾을 수 없음: {shape_id}")
                return None
            
            shape.move(dx, dy)
            logger.info(f"✅ 도형 이동 완료: {shape_id} (dx: {dx}, dy: {dy})")
            
            return ShapeResponse(**shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 이동 실패: {str(e)}")
            raise
    
    async def resize_shape(self, shape_id: str, new_width: float, new_height: float) -> Optional[ShapeResponse]:
        """도형의 크기를 변경합니다"""
        try:
            shape = self._shapes.get(shape_id)
            if not shape:
                logger.warning(f"⚠️ 크기 변경할 도형을 찾을 수 없음: {shape_id}")
                return None
            
            shape.resize(new_width, new_height)
            logger.info(f"✅ 도형 크기 변경 완료: {shape_id} ({new_width}x{new_height})")
            
            return ShapeResponse(**shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 크기 변경 실패: {str(e)}")
            raise
    
    async def rotate_shape(self, shape_id: str, angle: float) -> Optional[ShapeResponse]:
        """도형을 회전시킵니다"""
        try:
            shape = self._shapes.get(shape_id)
            if not shape:
                logger.warning(f"⚠️ 회전할 도형을 찾을 수 없음: {shape_id}")
                return None
            
            shape.rotate(angle)
            logger.info(f"✅ 도형 회전 완료: {shape_id} ({angle}도)")
            
            return ShapeResponse(**shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 회전 실패: {str(e)}")
            raise
    
    async def change_shape_color(self, shape_id: str, new_color: str) -> Optional[ShapeResponse]:
        """도형의 색상을 변경합니다"""
        try:
            shape = self._shapes.get(shape_id)
            if not shape:
                logger.warning(f"⚠️ 색상 변경할 도형을 찾을 수 없음: {shape_id}")
                return None
            
            shape.change_color(new_color)
            logger.info(f"✅ 도형 색상 변경 완료: {shape_id} ({new_color})")
            
            return ShapeResponse(**shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 색상 변경 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_shape_stats(self) -> ShapeStatsResponse:
        """도형 통계를 조회합니다"""
        try:
            total_shapes = len(self._shapes)
            
            # 타입별 도형 수
            shapes_by_type = {}
            for shape in self._shapes.values():
                type_name = shape.type.value
                shapes_by_type[type_name] = shapes_by_type.get(type_name, 0) + 1
            
            # 색상별 도형 수
            shapes_by_color = {}
            for shape in self._shapes.values():
                color = shape.color
                shapes_by_color[color] = shapes_by_color.get(color, 0) + 1
            
            # 평균 크기 계산
            if total_shapes > 0:
                total_width = sum(shape.width for shape in self._shapes.values())
                total_height = sum(shape.height for shape in self._shapes.values())
                avg_width = total_width / total_shapes
                avg_height = total_height / total_shapes
            else:
                avg_width = avg_height = 0.0
            
            # Canvas 수 (고유한 canvas_id 개수)
            canvas_ids = set(shape.canvas_id for shape in self._shapes.values() if shape.canvas_id)
            canvas_count = len(canvas_ids)
            
            logger.info(f"✅ 도형 통계 조회 완료: 총 {total_shapes}개")
            
            return ShapeStatsResponse(
                total_shapes=total_shapes,
                shapes_by_type=shapes_by_type,
                shapes_by_color=shapes_by_color,
                average_size={"width": avg_width, "height": avg_height},
                canvas_count=canvas_count
            )
            
        except Exception as e:
            logger.error(f"❌ 도형 통계 조회 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔧 유틸리티
    # ============================================================================
    
    async def get_shapes_by_canvas(self, canvas_id: str) -> List[ShapeResponse]:
        """특정 Canvas에 속한 도형들을 조회합니다"""
        try:
            canvas_shapes = [
                shape for shape in self._shapes.values()
                if shape.canvas_id == canvas_id
            ]
            
            shape_responses = [ShapeResponse(**shape.to_dict()) for shape in canvas_shapes]
            logger.info(f"✅ Canvas 도형 조회 완료: {canvas_id} ({len(shape_responses)}개)")
            
            return shape_responses
            
        except Exception as e:
            logger.error(f"❌ Canvas 도형 조회 실패: {str(e)}")
            raise
    
    async def clear_canvas_shapes(self, canvas_id: str) -> int:
        """특정 Canvas의 모든 도형을 제거합니다"""
        try:
            shapes_to_remove = [
                shape_id for shape_id, shape in self._shapes.items()
                if shape.canvas_id == canvas_id
            ]
            
            for shape_id in shapes_to_remove:
                del self._shapes[shape_id]
            
            logger.info(f"✅ Canvas 도형 제거 완료: {canvas_id} ({len(shapes_to_remove)}개)")
            return len(shapes_to_remove)
            
        except Exception as e:
            logger.error(f"❌ Canvas 도형 제거 실패: {str(e)}")
            raise
