# ============================================================================
# ➡️ Arrow Service - 화살표 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from loguru import logger

from app.domain.arrow.arrow_entity import Arrow, ArrowType
from app.domain.arrow.arrow_repository import ArrowRepository
from app.domain.arrow.arrow_schema import (
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
    """
    화살표 관련 비즈니스 로직을 처리하는 서비스 클래스
    
    주요 기능:
    - 화살표 생성/조회/수정/삭제
    - 화살표 검색 및 필터링  
    - 화살표 연결 관리
    - 통계 및 분석
    """
    
    def __init__(self, arrow_repository: ArrowRepository):
        """
        ArrowService 초기화
        
        Args:
            arrow_repository: 화살표 데이터 저장소
        """
        self.arrow_repository = arrow_repository
        logger.info("✅ ArrowService 초기화 완료")
    
    # ============================================================================
    # 🎯 CRUD 작업
    # ============================================================================
    
    async def create_arrow(self, request: ArrowCreateRequest) -> ArrowResponse:
        """새 화살표를 생성합니다"""
        try:
            logger.info(f"➡️ 화살표 생성 시작: {request.type.value}")
            
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
                source_shape_id=request.source_shape_id,
                target_shape_id=request.target_shape_id,
                label=request.label,
                label_position=request.label_position,
                canvas_id=request.canvas_id,
                metadata=request.metadata or {}
            )
            
            # Repository를 통해 저장
            created_arrow = await self.arrow_repository.create_arrow(arrow)
            
            logger.info(f"✅ 화살표 생성 완료: {arrow_id} ({request.type.value})")
            return ArrowResponse(**created_arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 생성 실패: {str(e)}")
            raise ValueError(f"화살표 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_arrow(self, arrow_id: str) -> Optional[ArrowResponse]:
        """ID로 화살표를 조회합니다"""
        try:
            logger.info(f"🔍 화살표 조회 시작: {arrow_id}")
            
            arrow = await self.arrow_repository.get_arrow_by_id(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            logger.info(f"✅ 화살표 조회 완료: {arrow_id}")
            return ArrowResponse(**arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 조회 실패: {arrow_id} - {str(e)}")
            return None
    
    async def get_all_arrows(self, page: int = 1, size: int = 20) -> ArrowListResponse:
        """모든 화살표를 페이지네이션으로 조회합니다"""
        try:
            logger.info(f"📋 화살표 목록 조회: 페이지 {page}, 크기 {size}")
            
            # Repository에서 전체 화살표 조회
            all_arrows = await self.arrow_repository.get_all_arrows()
            
            # 페이지네이션 적용
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            paginated_arrows = all_arrows[start_idx:end_idx]
            
            # 응답 생성
            arrow_responses = [ArrowResponse(**arrow.to_dict()) for arrow in paginated_arrows]
            
            logger.info(f"✅ 화살표 목록 조회 완료: {len(arrow_responses)}개")
            
            return ArrowListResponse(
                arrows=arrow_responses,
                total=len(all_arrows),
                page=page,
                size=size
            )
            
        except Exception as e:
            logger.error(f"❌ 화살표 목록 조회 실패: {str(e)}")
            raise ValueError(f"화살표 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def update_arrow(self, arrow_id: str, request: ArrowUpdateRequest) -> Optional[ArrowResponse]:
        """화살표를 수정합니다"""
        try:
            logger.info(f"✏️ 화살표 수정 시작: {arrow_id}")
            
            # 기존 화살표 조회
            arrow = await self.arrow_repository.get_arrow_by_id(arrow_id)
            if not arrow:
                logger.warning(f"⚠️ 수정할 화살표를 찾을 수 없음: {arrow_id}")
                return None
            
            # 업데이트할 필드들만 수정
            if request.type is not None:
                arrow.type = ArrowType(request.type.value)
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
            if request.source_shape_id is not None:
                arrow.source_shape_id = request.source_shape_id
            if request.target_shape_id is not None:
                arrow.target_shape_id = request.target_shape_id
            if request.label is not None:
                arrow.label = request.label
            if request.label_position is not None:
                arrow.label_position = request.label_position
            if request.metadata is not None:
                arrow.metadata.update(request.metadata)
            
            # 수정 시간 업데이트
            arrow.updated_at = datetime.utcnow()
            
            # Repository를 통해 업데이트
            updated_arrow = await self.arrow_repository.update_arrow(arrow)
            
            logger.info(f"✅ 화살표 수정 완료: {arrow_id}")
            return ArrowResponse(**updated_arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 화살표 수정 실패: {arrow_id} - {str(e)}")
            raise ValueError(f"화살표 수정 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_arrow(self, arrow_id: str) -> bool:
        """화살표를 삭제합니다"""
        try:
            logger.info(f"🗑️ 화살표 삭제 시작: {arrow_id}")
            
            # Repository를 통해 삭제
            success = await self.arrow_repository.delete_arrow(arrow_id)
            
            if success:
                logger.info(f"✅ 화살표 삭제 완료: {arrow_id}")
            else:
                logger.warning(f"⚠️ 삭제할 화살표를 찾을 수 없음: {arrow_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 화살표 삭제 실패: {arrow_id} - {str(e)}")
            raise ValueError(f"화살표 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔍 검색 및 필터링
    # ============================================================================
    
    async def search_arrows(self, request: ArrowSearchRequest) -> ArrowListResponse:
        """조건에 맞는 화살표를 검색합니다"""
        try:
            logger.info(f"🔍 화살표 검색 시작")
            
            # 모든 화살표 조회 (실제로는 DB에서 필터링 쿼리 사용)
            all_arrows = await self.arrow_repository.get_all_arrows()
            
            # 필터링 로직
            filtered_arrows = []
            for arrow in all_arrows:
                # Canvas ID 필터
                if request.canvas_id and arrow.canvas_id != request.canvas_id:
                    continue
                
                # 타입 필터
                if request.type and arrow.type.value != request.type.value:
                    continue
                
                # 색상 필터
                if request.color and arrow.color != request.color:
                    continue
                
                # 연결된 도형 필터
                if request.connected_shape_id:
                    if (arrow.source_shape_id != request.connected_shape_id and 
                        arrow.target_shape_id != request.connected_shape_id):
                        continue
                
                filtered_arrows.append(arrow)
            
            # 페이지네이션 적용
            start_idx = (request.page - 1) * request.size
            end_idx = start_idx + request.size
            paginated_arrows = filtered_arrows[start_idx:end_idx]
            
            # 응답 생성
            arrow_responses = [ArrowResponse(**arrow.to_dict()) for arrow in paginated_arrows]
            
            logger.info(f"✅ 화살표 검색 완료: {len(arrow_responses)}개")
            
            return ArrowListResponse(
                arrows=arrow_responses,
                total=len(filtered_arrows),
                page=request.page,
                size=request.size
            )
            
        except Exception as e:
            logger.error(f"❌ 화살표 검색 실패: {str(e)}")
            raise ValueError(f"화살표 검색 중 오류가 발생했습니다: {str(e)}")
    
    async def get_arrows_by_canvas(self, canvas_id: str) -> List[ArrowResponse]:
        """Canvas ID로 화살표 목록을 조회합니다"""
        try:
            logger.info(f"📋 Canvas 화살표 조회: {canvas_id}")
            
            arrows = await self.arrow_repository.get_arrows_by_canvas(canvas_id)
            arrow_responses = [ArrowResponse(**arrow.to_dict()) for arrow in arrows]
            
            logger.info(f"✅ Canvas 화살표 조회 완료: {len(arrow_responses)}개")
            return arrow_responses
            
        except Exception as e:
            logger.error(f"❌ Canvas 화살표 조회 실패: {canvas_id} - {str(e)}")
            return []
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_arrow_stats(self) -> ArrowStatsResponse:
        """화살표 통계를 조회합니다"""
        try:
            logger.info("📊 화살표 통계 조회 시작")
            
            all_arrows = await self.arrow_repository.get_all_arrows()
            
            # 기본 통계
            total_arrows = len(all_arrows)
            
            # 타입별 분포
            type_distribution = {}
            for arrow in all_arrows:
                type_name = arrow.type.value
                type_distribution[type_name] = type_distribution.get(type_name, 0) + 1
            
            # 색상별 분포 (상위 5개)
            color_distribution = {}
            for arrow in all_arrows:
                color = arrow.color
                color_distribution[color] = color_distribution.get(color, 0) + 1
            
            most_used_colors = sorted(
                [{"color": k, "count": v} for k, v in color_distribution.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:5]
            
            # 연결 통계
            connected_arrows = sum(1 for arrow in all_arrows 
                                 if arrow.source_shape_id or arrow.target_shape_id)
            
            # 평균 길이 계산
            if total_arrows > 0:
                total_length = sum(
                    ((arrow.end_x - arrow.start_x) ** 2 + (arrow.end_y - arrow.start_y) ** 2) ** 0.5
                    for arrow in all_arrows
                )
                average_length = total_length / total_arrows
            else:
                average_length = 0.0
            
            logger.info(f"✅ 화살표 통계 조회 완료: 총 {total_arrows}개")
            
            return ArrowStatsResponse(
                total_arrows=total_arrows,
                type_distribution=type_distribution,
                most_used_colors=most_used_colors,
                connected_arrows=connected_arrows,
                average_length=average_length,
                arrows_with_labels=sum(1 for arrow in all_arrows if arrow.label)
            )
            
        except Exception as e:
            logger.error(f"❌ 화살표 통계 조회 실패: {str(e)}")
            raise ValueError(f"화살표 통계 조회 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    async def get_arrow_connections(self, shape_id: str) -> List[ArrowResponse]:
        """특정 도형에 연결된 모든 화살표를 조회합니다"""
        try:
            logger.info(f"🔗 도형 연결 화살표 조회: {shape_id}")
            
            all_arrows = await self.arrow_repository.get_all_arrows()
            
            connected_arrows = [
                arrow for arrow in all_arrows
                if arrow.source_shape_id == shape_id or arrow.target_shape_id == shape_id
            ]
            
            arrow_responses = [ArrowResponse(**arrow.to_dict()) for arrow in connected_arrows]
            
            logger.info(f"✅ 도형 연결 화살표 조회 완료: {len(arrow_responses)}개")
            return arrow_responses
            
        except Exception as e:
            logger.error(f"❌ 도형 연결 화살표 조회 실패: {shape_id} - {str(e)}")
            return []
    
    async def create_connection(self, request: ArrowConnectionRequest) -> ArrowResponse:
        """두 도형을 화살표로 연결합니다"""
        try:
            logger.info(f"🔗 도형 연결 생성: {request.source_shape_id} -> {request.target_shape_id}")
            
            # 연결 화살표 생성
            arrow_id = str(uuid.uuid4())
            
            arrow = Arrow(
                id=arrow_id,
                type=ArrowType(request.arrow_type.value),
                start_x=request.start_x,
                start_y=request.start_y,
                end_x=request.end_x,
                end_y=request.end_y,
                color=request.color or "#000000",
                stroke_width=request.stroke_width or 2.0,
                arrow_size=request.arrow_size or 10.0,
                source_shape_id=request.source_shape_id,
                target_shape_id=request.target_shape_id,
                label=request.label,
                canvas_id=request.canvas_id,
                metadata={}
            )
            
            # Repository를 통해 저장
            created_arrow = await self.arrow_repository.create_arrow(arrow)
            
            logger.info(f"✅ 도형 연결 생성 완료: {arrow_id}")
            return ArrowResponse(**created_arrow.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 도형 연결 생성 실패: {str(e)}")
            raise ValueError(f"도형 연결 생성 중 오류가 발생했습니다: {str(e)}")