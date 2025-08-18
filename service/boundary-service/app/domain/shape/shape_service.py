# ============================================================================
# 🎨 Shape Service - 도형 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from loguru import logger

from ..shape.shape_entity import Shape, ShapeType
from ..shape.shape_repository import ShapeRepository
from ..shape.shape_schema import (
    ShapeCreateRequest,
    ShapeUpdateRequest,
    ShapeResponse,
    ShapeListResponse,
    ShapeSearchRequest,
    ShapeStatsResponse
)

class ShapeService:
    """
    도형 관련 비즈니스 로직을 처리하는 서비스 클래스
    
    주요 기능:
    - 도형 생성/조회/수정/삭제
    - 도형 검색 및 필터링
    - 도형 통계 및 분석
    - 도형 변환 및 조작
    """
    
    def __init__(self, shape_repository: ShapeRepository):
        """
        ShapeService 초기화
        
        Args:
            shape_repository: 도형 데이터 저장소
        """
        self.shape_repository = shape_repository
        logger.info("✅ ShapeService 초기화 완료")
    
    # ============================================================================
    # 🎯 CRUD 작업
    # ============================================================================
    
    async def create_shape(self, request: ShapeCreateRequest) -> ShapeResponse:
        """새 도형을 생성합니다"""
        try:
            logger.info(f"🎨 도형 생성 시작: {request.type.value}")
            
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
                label=request.label,
                label_position=request.label_position,
                rotation=request.rotation,
                visible=request.visible,
                locked=request.locked,
                canvas_id=request.canvas_id,
                metadata=request.metadata or {}
            )
            
            # Repository를 통해 저장
            created_shape = await self.shape_repository.create_shape(shape)
            
            logger.info(f"✅ 도형 생성 완료: {shape_id} ({request.type.value})")
            return ShapeResponse(**created_shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 생성 실패: {str(e)}")
            raise ValueError(f"도형 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_shape(self, shape_id: str) -> Optional[ShapeResponse]:
        """ID로 도형을 조회합니다"""
        try:
            logger.info(f"🔍 도형 조회 시작: {shape_id}")
            
            shape = await self.shape_repository.get_shape_by_id(shape_id)
            if not shape:
                logger.warning(f"⚠️ 도형을 찾을 수 없음: {shape_id}")
                return None
            
            logger.info(f"✅ 도형 조회 완료: {shape_id}")
            return ShapeResponse(**shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 조회 실패: {shape_id} - {str(e)}")
            return None
    
    async def get_all_shapes(self, page: int = 1, size: int = 20) -> ShapeListResponse:
        """모든 도형을 페이지네이션으로 조회합니다"""
        try:
            logger.info(f"📋 도형 목록 조회: 페이지 {page}, 크기 {size}")
            
            # Repository에서 전체 도형 조회
            all_shapes = await self.shape_repository.get_all_shapes()
            
            # 페이지네이션 적용
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            paginated_shapes = all_shapes[start_idx:end_idx]
            
            # 응답 생성
            shape_responses = [ShapeResponse(**shape.to_dict()) for shape in paginated_shapes]
            
            logger.info(f"✅ 도형 목록 조회 완료: {len(shape_responses)}개")
            
            return ShapeListResponse(
                shapes=shape_responses,
                total=len(all_shapes),
                page=page,
                size=size
            )
            
        except Exception as e:
            logger.error(f"❌ 도형 목록 조회 실패: {str(e)}")
            raise ValueError(f"도형 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def update_shape(self, shape_id: str, request: ShapeUpdateRequest) -> Optional[ShapeResponse]:
        """도형을 수정합니다"""
        try:
            logger.info(f"✏️ 도형 수정 시작: {shape_id}")
            
            # 기존 도형 조회
            shape = await self.shape_repository.get_shape_by_id(shape_id)
            if not shape:
                logger.warning(f"⚠️ 수정할 도형을 찾을 수 없음: {shape_id}")
                return None
            
            # 업데이트할 필드들만 수정
            if request.type is not None:
                shape.type = ShapeType(request.type.value)
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
            if request.label is not None:
                shape.label = request.label
            if request.label_position is not None:
                shape.label_position = request.label_position
            if request.rotation is not None:
                shape.rotation = request.rotation
            if request.visible is not None:
                shape.visible = request.visible
            if request.locked is not None:
                shape.locked = request.locked
            if request.metadata is not None:
                shape.metadata.update(request.metadata)
            
            # 수정 시간 업데이트
            shape.updated_at = datetime.utcnow()
            
            # Repository를 통해 업데이트
            updated_shape = await self.shape_repository.update_shape(shape)
            
            logger.info(f"✅ 도형 수정 완료: {shape_id}")
            return ShapeResponse(**updated_shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 수정 실패: {shape_id} - {str(e)}")
            raise ValueError(f"도형 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_shape(self, shape_id: str) -> bool:
        """도형을 삭제합니다"""
        try:
            logger.info(f"🗑️ 도형 삭제 시작: {shape_id}")
            
            # Repository를 통해 삭제
            success = await self.shape_repository.delete_shape(shape_id)
            
            if success:
                logger.info(f"✅ 도형 삭제 완료: {shape_id}")
            else:
                logger.warning(f"⚠️ 삭제할 도형을 찾을 수 없음: {shape_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 도형 삭제 실패: {shape_id} - {str(e)}")
            raise ValueError(f"도형 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔍 검색 및 필터링
    # ============================================================================
    
    async def search_shapes(self, request: ShapeSearchRequest) -> ShapeListResponse:
        """조건에 맞는 도형을 검색합니다"""
        try:
            logger.info(f"🔍 도형 검색 시작")
            
            # 모든 도형 조회 (실제로는 DB에서 필터링 쿼리 사용)
            all_shapes = await self.shape_repository.get_all_shapes()
            
            # 필터링 로직
            filtered_shapes = []
            for shape in all_shapes:
                # Canvas ID 필터
                if request.canvas_id and shape.canvas_id != request.canvas_id:
                    continue
                
                # 타입 필터
                if request.type and shape.type.value != request.type.value:
                    continue
                
                # 색상 필터
                if request.color and shape.color != request.color:
                    continue
                
                # 표시 상태 필터
                if request.visible is not None and shape.visible != request.visible:
                    continue
                
                # 잠금 상태 필터
                if request.locked is not None and shape.locked != request.locked:
                    continue
                
                filtered_shapes.append(shape)
            
            # 페이지네이션 적용
            start_idx = (request.page - 1) * request.size
            end_idx = start_idx + request.size
            paginated_shapes = filtered_shapes[start_idx:end_idx]
            
            # 응답 생성
            shape_responses = [ShapeResponse(**shape.to_dict()) for shape in paginated_shapes]
            
            logger.info(f"✅ 도형 검색 완료: {len(shape_responses)}개")
            
            return ShapeListResponse(
                shapes=shape_responses,
                total=len(filtered_shapes),
                page=request.page,
                size=request.size
            )
            
        except Exception as e:
            logger.error(f"❌ 도형 검색 실패: {str(e)}")
            raise ValueError(f"도형 검색 중 오류가 발생했습니다: {str(e)}")
    
    async def get_shapes_by_canvas(self, canvas_id: str) -> List[ShapeResponse]:
        """Canvas ID로 도형 목록을 조회합니다"""
        try:
            logger.info(f"📋 Canvas 도형 조회: {canvas_id}")
            
            shapes = await self.shape_repository.get_shapes_by_canvas(canvas_id)
            shape_responses = [ShapeResponse(**shape.to_dict()) for shape in shapes]
            
            logger.info(f"✅ Canvas 도형 조회 완료: {len(shape_responses)}개")
            return shape_responses
            
        except Exception as e:
            logger.error(f"❌ Canvas 도형 조회 실패: {canvas_id} - {str(e)}")
            return []
    
    async def get_shapes_by_type(self, shape_type: ShapeType) -> List[ShapeResponse]:
        """도형 타입별로 조회합니다"""
        try:
            logger.info(f"📋 도형 타입별 조회: {shape_type.value}")
            
            shapes = await self.shape_repository.get_shapes_by_type(shape_type)
            shape_responses = [ShapeResponse(**shape.to_dict()) for shape in shapes]
            
            logger.info(f"✅ 도형 타입별 조회 완료: {len(shape_responses)}개")
            return shape_responses
            
        except Exception as e:
            logger.error(f"❌ 도형 타입별 조회 실패: {shape_type.value} - {str(e)}")
            return []
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_shape_stats(self) -> ShapeStatsResponse:
        """도형 통계를 조회합니다"""
        try:
            logger.info("📊 도형 통계 조회 시작")
            
            all_shapes = await self.shape_repository.get_all_shapes()
            
            # 기본 통계
            total_shapes = len(all_shapes)
            
            # 타입별 분포
            type_distribution = {}
            for shape in all_shapes:
                type_name = shape.type.value
                type_distribution[type_name] = type_distribution.get(type_name, 0) + 1
            
            # 색상별 분포 (상위 5개)
            color_distribution = {}
            for shape in all_shapes:
                color = shape.color
                color_distribution[color] = color_distribution.get(color, 0) + 1
            
            most_used_colors = sorted(
                [{"color": k, "count": v} for k, v in color_distribution.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:5]
            
            # 표시/잠금 상태 통계
            visible_shapes = sum(1 for shape in all_shapes if shape.visible)
            locked_shapes = sum(1 for shape in all_shapes if shape.locked)
            
            # 평균 크기 계산
            if total_shapes > 0:
                total_area = sum(shape.width * shape.height for shape in all_shapes)
                average_area = total_area / total_shapes
            else:
                average_area = 0.0
            
            logger.info(f"✅ 도형 통계 조회 완료: 총 {total_shapes}개")
            
            return ShapeStatsResponse(
                total_shapes=total_shapes,
                type_distribution=type_distribution,
                most_used_colors=most_used_colors,
                visible_shapes=visible_shapes,
                locked_shapes=locked_shapes,
                average_area=average_area,
                shapes_with_labels=sum(1 for shape in all_shapes if shape.label)
            )
            
        except Exception as e:
            logger.error(f"❌ 도형 통계 조회 실패: {str(e)}")
            raise ValueError(f"도형 통계 조회 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    async def move_shape(self, shape_id: str, x: float, y: float) -> Optional[ShapeResponse]:
        """도형을 이동합니다"""
        try:
            logger.info(f"📍 도형 이동: {shape_id} -> ({x}, {y})")
            
            shape = await self.shape_repository.get_shape_by_id(shape_id)
            if not shape:
                return None
            
            # 위치 업데이트
            shape.x = x
            shape.y = y
            shape.updated_at = datetime.utcnow()
            
            # Repository를 통해 업데이트
            updated_shape = await self.shape_repository.update_shape(shape)
            
            logger.info(f"✅ 도형 이동 완료: {shape_id}")
            return ShapeResponse(**updated_shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 이동 실패: {shape_id} - {str(e)}")
            return None
    
    async def resize_shape(self, shape_id: str, width: float, height: float) -> Optional[ShapeResponse]:
        """도형 크기를 조정합니다"""
        try:
            logger.info(f"📏 도형 크기 조정: {shape_id} -> {width}x{height}")
            
            shape = await self.shape_repository.get_shape_by_id(shape_id)
            if not shape:
                return None
            
            # 크기 업데이트
            shape.width = width
            shape.height = height
            shape.updated_at = datetime.utcnow()
            
            # Repository를 통해 업데이트
            updated_shape = await self.shape_repository.update_shape(shape)
            
            logger.info(f"✅ 도형 크기 조정 완료: {shape_id}")
            return ShapeResponse(**updated_shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 크기 조정 실패: {shape_id} - {str(e)}")
            return None
    
    async def rotate_shape(self, shape_id: str, rotation: float) -> Optional[ShapeResponse]:
        """도형을 회전합니다"""
        try:
            logger.info(f"🔄 도형 회전: {shape_id} -> {rotation}도")
            
            shape = await self.shape_repository.get_shape_by_id(shape_id)
            if not shape:
                return None
            
            # 회전 업데이트 (0-360도 범위로 정규화)
            shape.rotation = rotation % 360
            shape.updated_at = datetime.utcnow()
            
            # Repository를 통해 업데이트
            updated_shape = await self.shape_repository.update_shape(shape)
            
            logger.info(f"✅ 도형 회전 완료: {shape_id}")
            return ShapeResponse(**updated_shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 회전 실패: {shape_id} - {str(e)}")
            return None
    
    async def duplicate_shape(self, shape_id: str, offset_x: float = 20.0, offset_y: float = 20.0) -> Optional[ShapeResponse]:
        """도형을 복제합니다"""
        try:
            logger.info(f"📋 도형 복제: {shape_id}")
            
            original_shape = await self.shape_repository.get_shape_by_id(shape_id)
            if not original_shape:
                return None
            
            # 새로운 ID와 위치로 복제
            new_id = str(uuid.uuid4())
            duplicated_shape = Shape(
                id=new_id,
                type=original_shape.type,
                x=original_shape.x + offset_x,
                y=original_shape.y + offset_y,
                width=original_shape.width,
                height=original_shape.height,
                color=original_shape.color,
                stroke_width=original_shape.stroke_width,
                fill_color=original_shape.fill_color,
                label=f"{original_shape.label} (복제)" if original_shape.label else None,
                label_position=original_shape.label_position,
                rotation=original_shape.rotation,
                visible=original_shape.visible,
                locked=False,  # 복제된 도형은 잠금 해제
                canvas_id=original_shape.canvas_id,
                metadata=original_shape.metadata.copy()
            )
            
            # Repository를 통해 저장
            created_shape = await self.shape_repository.create_shape(duplicated_shape)
            
            logger.info(f"✅ 도형 복제 완료: {shape_id} -> {new_id}")
            return ShapeResponse(**created_shape.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 복제 실패: {shape_id} - {str(e)}")
            return None