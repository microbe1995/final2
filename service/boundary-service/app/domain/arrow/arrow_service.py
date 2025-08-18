# ============================================================================
# ➡️ Arrow Service - 화살표 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from loguru import logger

from ..entity.arrow_entity import Arrow, ArrowType
from ..schema.arrow_schema import (
    ArrowCreateRequest,
    ArrowUpdateRequest,
    ArrowResponse,
    ArrowListResponse,
    ArrowSearchRequest,
    ArrowStatsResponse,
    ArrowConnectionRequest,
    ArrowBatchCreateRequest
)

class ArrowService:
    """화살표 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self):
        """ArrowService 초기화"""
        self._arrows: Dict[str, Arrow] = {}  # 메모리 저장소 (실제로는 DB 사용)
        logger.info("✅ ArrowService 초기화 완료")
    
    # ============================================================================
    # 🎯 CRUD 작업
    # ============================================================================
    
    async def create_arrow(self, request: ArrowCreateRequest) -> ArrowResponse:
        """새 화살표를 생성합니다"""
        try:
            # 고유 ID 생성
            arrow_id = str(uuid.uuid4())
            
            # Arrow 엔티티 생성
            arrow = Arrow(
                id=arrow_id,
                type=ArrowType(request.type.value),
                start_x=request.start_x,
                start_y=request.start_y,
                end_x=request.end_x,
                end_y=request.end_y,
                color=request.color,
                stroke_width=request.stroke_width,
                arrow_size=request.arrow_size,
                is_dashed=request.is_dashed,
                dash_pattern=request.dash_pattern,
                control_points=request.control_points or [],
                canvas_id=request.canvas_id,
                metadata=request.metadata or {}
            )
            
            # 저장
            self._arrows[arrow_id] = arrow
            logger.info(f"✅ 화살표 생성 완료: {arrow_id} ({request.type.value})")
            
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 생성 실패: {str(e)}")
            raise
    
    async def get_arrow(self, arrow_id: str) -> Optional[ArrowResponse]:
        """ID로 화살표를 조회합니다"""
        try:
            arrow = self._arrows.get(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            logger.info(f"✅ 화살표 조회 완료: {arrow_id}")
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 조회 실패: {str(e)}")
            raise
    
    async def get_all_arrows(self, page: int = 1, size: int = 20) -> ArrowListResponse:
        """모든 화살표를 페이지네이션으로 조회합니다"""
        try:
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            
            arrows_list = list(self._arrows.values())
            total = len(arrows_list)
            
            # 페이지네이션 적용
            paginated_arrows = arrows_list[start_idx:end_idx]
            
            # 응답 생성
            arrow_responses = [ArrowResponse(**arrow.to_dict()) for arrow in paginated_arrows]
            
            logger.info(f"✅ 화살표 목록 조회 완료: {len(arrow_responses)}개 (페이지 {page})")
            
            return ArrowListResponse(
                arrows=arrow_responses,
                total=total,
                page=page,
                size=size
            )
            
        except Exception as e:
            logger.error(f"❌ 화살표 목록 조회 실패: {str(e)}")
            raise
    
    async def update_arrow(self, arrow_id: str, request: ArrowUpdateRequest) -> Optional[ArrowResponse]:
        """화살표를 수정합니다"""
        try:
            arrow = self._arrows.get(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 수정할 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            # 업데이트할 필드들만 수정
            if request.start_x is not None:
                arrow.start_x = request.start_x
            if request.start_y is not None:
                arrow.start_y = request.start_y
            if request.end_x is not None:
                arrow.end_x = request.end_x
            if request.end_y is not None:
                arrow.end_y = request.end_y
            if request.color is not None:
                arrow.color = request.color
            if request.stroke_width is not None:
                arrow.stroke_width = request.stroke_width
            if request.arrow_size is not None:
                arrow.arrow_size = request.arrow_size
            if request.is_dashed is not None:
                arrow.is_dashed = request.is_dashed
            if request.dash_pattern is not None:
                arrow.dash_pattern = request.dash_pattern
            if request.control_points is not None:
                arrow.control_points = request.control_points
            if request.metadata is not None:
                arrow.metadata.update(request.metadata)
            
            # 수정 시간 업데이트
            arrow.updated_at = datetime.utcnow()
            
            logger.info(f"✅ 화살표 수정 완료: {arrow_id}")
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 수정 실패: {str(e)}")
            raise
    
    async def delete_arrow(self, arrow_id: str) -> bool:
        """화살표를 삭제합니다"""
        try:
            if arrow_id not in self._arrows:
                logger.warning(f"⚠️ 삭제할 화살표를 찾을 수 없음: {arrow_id}")
                return False
            
            del self._arrows[arrow_id]
            logger.info(f"✅ 화살표 삭제 완료: {arrow_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 화살표 삭제 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔍 검색 및 필터링
    # ============================================================================
    
    async def search_arrows(self, request: ArrowSearchRequest) -> ArrowListResponse:
        """조건에 맞는 화살표를 검색합니다"""
        try:
            filtered_arrows = []
            
            for arrow in self._arrows.values():
                # 타입 필터
                if request.type and arrow.type != ArrowType(request.type.value):
                    continue
                
                # Canvas ID 필터
                if request.canvas_id and arrow.canvas_id != request.canvas_id:
                    continue
                
                # 길이 필터
                if request.min_length is not None:
                    arrow_length = arrow.get_length()
                    if arrow_length < request.min_length:
                        continue
                if request.max_length is not None:
                    arrow_length = arrow.get_length()
                    if arrow_length > request.max_length:
                        continue
                
                # 색상 필터
                if request.color and arrow.color != request.color:
                    continue
                
                # 점선 여부 필터
                if request.is_dashed is not None and arrow.is_dashed != request.is_dashed:
                    continue
                
                filtered_arrows.append(arrow)
            
            # 페이지네이션 적용
            start_idx = (request.page - 1) * request.size
            end_idx = start_idx + request.size
            paginated_arrows = filtered_arrows[start_idx:end_idx]
            
            # 응답 생성
            arrow_responses = [ArrowResponse(**arrow.to_dict()) for arrow in paginated_arrows]
            
            logger.info(f"✅ 화살표 검색 완료: {len(arrow_responses)}개 (필터링된 {len(filtered_arrows)}개)")
            
            return ArrowListResponse(
                arrows=arrow_responses,
                total=len(filtered_arrows),
                page=request.page,
                size=request.size
            )
            
        except Exception as e:
            logger.error(f"❌ 화살표 검색 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🎨 화살표 조작
    # ============================================================================
    
    async def move_arrow(self, arrow_id: str, dx: float, dy: float) -> Optional[ArrowResponse]:
        """화살표를 이동시킵니다"""
        try:
            arrow = self._arrows.get(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 이동할 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            arrow.move(dx, dy)
            logger.info(f"✅ 화살표 이동 완료: {arrow_id} (dx: {dx}, dy: {dy})")
            
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 이동 실패: {str(e)}")
            raise
    
    async def resize_arrow(self, arrow_id: str, new_start_x: float, new_start_y: float,
                          new_end_x: float, new_end_y: float) -> Optional[ArrowResponse]:
        """화살표의 크기와 위치를 변경합니다"""
        try:
            arrow = self._arrows.get(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 크기 변경할 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            arrow.resize(new_start_x, new_start_y, new_end_x, new_end_y)
            logger.info(f"✅ 화살표 크기 변경 완료: {arrow_id}")
            
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 크기 변경 실패: {str(e)}")
            raise
    
    async def change_arrow_color(self, arrow_id: str, new_color: str) -> Optional[ArrowResponse]:
        """화살표의 색상을 변경합니다"""
        try:
            arrow = self._arrows.get(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 색상 변경할 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            arrow.change_color(new_color)
            logger.info(f"✅ 화살표 색상 변경 완료: {arrow_id} ({new_color})")
            
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 색상 변경 실패: {str(e)}")
            raise
    
    async def set_arrow_dash_pattern(self, arrow_id: str, pattern: List[float]) -> Optional[ArrowResponse]:
        """화살표의 점선 패턴을 설정합니다"""
        try:
            arrow = self._arrows.get(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 점선 패턴을 설정할 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            arrow.set_dash_pattern(pattern)
            logger.info(f"✅ 화살표 점선 패턴 설정 완료: {arrow_id} ({pattern})")
            
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 점선 패턴 설정 실패: {str(e)}")
            raise
    
    async def add_control_point(self, arrow_id: str, x: float, y: float) -> Optional[ArrowResponse]:
        """곡선 화살표에 제어점을 추가합니다"""
        try:
            arrow = self._arrows.get(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 제어점을 추가할 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            if arrow.type != ArrowType.CURVED:
                logger.warning(f"⚠️ 곡선 화살표가 아님: {arrow_id} (타입: {arrow.type.value})")
                return None
            
            arrow.add_control_point(x, y)
            logger.info(f"✅ 제어점 추가 완료: {arrow_id} ({x}, {y})")
            
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 제어점 추가 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🎯 특수 기능
    # ============================================================================
    
    async def connect_shapes(self, request: ArrowConnectionRequest) -> ArrowResponse:
        """두 도형을 화살표로 연결합니다"""
        try:
            # 시작점과 끝점 계산 (도형의 중심점 사용)
            # 실제로는 ShapeService에서 도형 정보를 가져와야 함
            start_x, start_y = 0, 0  # from_shape의 중심점
            end_x, end_y = 100, 100  # to_shape의 중심점
            
            # 화살표 생성
            arrow_request = ArrowCreateRequest(
                type=request.arrow_type,
                start_x=start_x,
                start_y=start_y,
                end_x=end_x,
                end_y=end_y,
                color=request.color,
                stroke_width=request.stroke_width,
                canvas_id=request.canvas_id
            )
            
            arrow_response = await self.create_arrow(arrow_request)
            logger.info(f"✅ 도형 연결 완료: {request.from_shape_id} → {request.to_shape_id}")
            
            return arrow_response
            
        except Exception as e:
            logger.error(f"❌ 도형 연결 실패: {str(e)}")
            raise
    
    async def create_batch_arrows(self, request: ArrowBatchCreateRequest) -> List[ArrowResponse]:
        """여러 화살표를 일괄 생성합니다"""
        try:
            created_arrows = []
            
            for arrow_request in request.arrows:
                arrow_request.canvas_id = request.canvas_id
                arrow_response = await self.create_arrow(arrow_request)
                created_arrows.append(arrow_response)
            
            logger.info(f"✅ 화살표 일괄 생성 완료: {len(created_arrows)}개")
            return created_arrows
            
        except Exception as e:
            logger.error(f"❌ 화살표 일괄 생성 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_arrow_stats(self) -> ArrowStatsResponse:
        """화살표 통계를 조회합니다"""
        try:
            total_arrows = len(self._arrows)
            
            # 타입별 화살표 수
            arrows_by_type = {}
            for arrow in self._arrows.values():
                type_name = arrow.type.value
                arrows_by_type[type_name] = arrows_by_type.get(type_name, 0) + 1
            
            # 색상별 화살표 수
            arrows_by_color = {}
            for arrow in self._arrows.values():
                color = arrow.color
                arrows_by_color[color] = arrows_by_color.get(color, 0) + 1
            
            # 평균 길이 계산
            if total_arrows > 0:
                total_length = sum(arrow.get_length() for arrow in self._arrows.values())
                average_length = total_length / total_arrows
            else:
                average_length = 0.0
            
            # 점선 화살표 수
            dashed_count = sum(1 for arrow in self._arrows.values() if arrow.is_dashed)
            
            # Canvas 수 (고유한 canvas_id 개수)
            canvas_ids = set(arrow.canvas_id for arrow in self._arrows.values() if arrow.canvas_id)
            canvas_count = len(canvas_ids)
            
            logger.info(f"✅ 화살표 통계 조회 완료: 총 {total_arrows}개")
            
            return ArrowStatsResponse(
                total_arrows=total_arrows,
                arrows_by_type=arrows_by_type,
                arrows_by_color=arrows_by_color,
                average_length=average_length,
                dashed_count=dashed_count,
                canvas_count=canvas_count
            )
            
        except Exception as e:
            logger.error(f"❌ 화살표 통계 조회 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔧 유틸리티
    # ============================================================================
    
    async def get_arrows_by_canvas(self, canvas_id: str) -> List[ArrowResponse]:
        """특정 Canvas에 속한 화살표들을 조회합니다"""
        try:
            canvas_arrows = [
                arrow for arrow in self._arrows.values()
                if arrow.canvas_id == canvas_id
            ]
            
            arrow_responses = [ArrowResponse(**arrow.to_dict()) for arrow in canvas_arrows]
            logger.info(f"✅ Canvas 화살표 조회 완료: {canvas_id} ({len(arrow_responses)}개)")
            
            return arrow_responses
            
        except Exception as e:
            logger.error(f"❌ Canvas 화살표 조회 실패: {str(e)}")
            raise
    
    async def clear_canvas_arrows(self, canvas_id: str) -> int:
        """특정 Canvas의 모든 화살표를 제거합니다"""
        try:
            arrows_to_remove = [
                arrow_id for arrow_id, arrow in self._arrows.items()
                if arrow.canvas_id == canvas_id
            ]
            
            for arrow_id in arrows_to_remove:
                del self._arrows[arrow_id]
            
            logger.info(f"✅ Canvas 화살표 제거 완료: {canvas_id} ({len(arrows_to_remove)}개)")
            return len(arrows_to_remove)
            
        except Exception as e:
            logger.error(f"❌ Canvas 화살표 제거 실패: {str(e)}")
            raise
    
    async def get_arrows_at_point(self, x: float, y: float, threshold: float = 5.0) -> List[ArrowResponse]:
        """주어진 점 근처의 화살표들을 찾습니다"""
        try:
            nearby_arrows = []
            
            for arrow in self._arrows.values():
                # 점과 선분 사이의 최단 거리 계산
                if self._point_near_line(x, y, arrow, threshold):
                    nearby_arrows.append(arrow)
            
            arrow_responses = [ArrowResponse(**arrow.to_dict()) for arrow in nearby_arrows]
            logger.info(f"✅ 점 근처 화살표 조회 완료: ({x}, {y}) - {len(arrow_responses)}개")
            
            return arrow_responses
            
        except Exception as e:
            logger.error(f"❌ 점 근처 화살표 조회 실패: {str(e)}")
            raise
    
    def _point_near_line(self, x: float, y: float, arrow: Arrow, threshold: float) -> bool:
        """점이 선 근처에 있는지 확인합니다"""
        import math
        
        # 선분과 점 사이의 최단 거리 계산
        A = x - arrow.start_x
        B = y - arrow.start_y
        C = arrow.end_x - arrow.start_x
        D = arrow.end_y - arrow.start_y
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            # 시작점과 끝점이 같은 경우
            return math.sqrt(A * A + B * B) <= threshold
        
        param = dot / len_sq
        
        if param < 0:
            xx, yy = arrow.start_x, arrow.start_y
        elif param > 1:
            xx, yy = arrow.end_x, arrow.end_y
        else:
            xx = arrow.start_x + param * C
            yy = arrow.start_y + param * D
        
        dx = x - xx
        dy = y - yy
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance <= threshold
