# ============================================================================
# 🖱️ Viewport Service - ReactFlow 뷰포트 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from app.domain.Viewport.Viewport_repository import ViewportRepository
from app.domain.Viewport.Viewport_schema import (
    ViewportCreateRequest,
    ViewportUpdateRequest,
    ViewportStateUpdateRequest,
    ViewportSettingsUpdateRequest,
    ViewportResponse,
    ViewportListResponse,
    ViewportStateResponse,
    ViewportSearchRequest,
    ViewportStatsResponse,
    ViewportModeResponse,
    ViewportMode
)

class ViewportService:
    """뷰포트 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, repository: Optional[ViewportRepository] = None):
        """ViewportService 초기화"""
        self.viewport_repository = repository or ViewportRepository(use_database=True)
    
    # ============================================================================
    # 🖱️ 뷰포트 기본 CRUD 메서드
    # ============================================================================
    
    async def create_viewport(self, request: ViewportCreateRequest) -> ViewportResponse:
        """뷰포트 생성"""
        try:
            logger.info(f"🖱️ 뷰포트 생성 요청: {request.flow_id}")
            
            # ID 생성
            viewport_id = f"viewport_{uuid.uuid4().hex[:8]}"
            
            # 뷰포트 데이터 준비
            viewport_data = {
                "id": viewport_id,
                "flow_id": request.flow_id,
                "viewport": {
                    "x": request.viewport.x,
                    "y": request.viewport.y,
                    "zoom": request.viewport.zoom
                },
                "settings": request.settings.dict() if request.settings else {},
                "metadata": request.metadata or {}
            }
            
            # 비즈니스 규칙 검증
            await self._validate_viewport_creation(viewport_data)
            
            # 뷰포트 생성
            created_viewport = await self.viewport_repository.create_viewport(viewport_data)
            
            logger.info(f"✅ 뷰포트 생성 성공: {viewport_id}")
            return self._convert_to_viewport_response(created_viewport)
            
        except Exception as e:
            logger.error(f"❌ 뷰포트 생성 실패: {str(e)}")
            raise ValueError(f"뷰포트 생성 중 오류가 발생했습니다: {str(e)}")
    
    async def get_viewport_by_id(self, viewport_id: str) -> Optional[ViewportResponse]:
        """뷰포트 ID로 조회"""
        try:
            logger.info(f"🔍 뷰포트 조회: {viewport_id}")
            
            viewport = await self.viewport_repository.get_viewport_by_id(viewport_id)
            if not viewport:
                logger.warning(f"⚠️ 뷰포트를 찾을 수 없음: {viewport_id}")
                return None
            
            logger.info(f"✅ 뷰포트 조회 성공: {viewport_id}")
            return self._convert_to_viewport_response(viewport)
            
        except Exception as e:
            logger.error(f"❌ 뷰포트 조회 실패: {str(e)}")
            return None
    
    async def get_viewport_by_flow_id(self, flow_id: str) -> Optional[ViewportResponse]:
        """플로우 ID로 뷰포트 조회"""
        try:
            logger.info(f"🔍 플로우 뷰포트 조회: {flow_id}")
            
            viewport = await self.viewport_repository.get_viewport_by_flow_id(flow_id)
            if not viewport:
                logger.warning(f"⚠️ 플로우 뷰포트를 찾을 수 없음: {flow_id}")
                return None
            
            logger.info(f"✅ 플로우 뷰포트 조회 성공: {flow_id}")
            return self._convert_to_viewport_response(viewport)
            
        except Exception as e:
            logger.error(f"❌ 플로우 뷰포트 조회 실패: {str(e)}")
            return None
    
    async def get_all_viewports(self) -> ViewportListResponse:
        """모든 뷰포트 목록 조회"""
        try:
            logger.info(f"📋 뷰포트 목록 조회")
            
            viewports = await self.viewport_repository.get_all_viewports()
            
            # ViewportResponse 형식으로 변환
            viewport_responses = [self._convert_to_viewport_response(viewport) for viewport in viewports]
            
            logger.info(f"✅ 뷰포트 목록 조회 성공: {len(viewports)}개")
            return ViewportListResponse(
                viewports=viewport_responses,
                total=len(viewports)
            )
            
        except Exception as e:
            logger.error(f"❌ 뷰포트 목록 조회 실패: {str(e)}")
            return ViewportListResponse(viewports=[], total=0)
    
    async def update_viewport(self, viewport_id: str, request: ViewportUpdateRequest) -> Optional[ViewportResponse]:
        """뷰포트 수정"""
        try:
            logger.info(f"✏️ 뷰포트 수정: {viewport_id}")
            
            # 기존 뷰포트 확인
            existing_viewport = await self.viewport_repository.get_viewport_by_id(viewport_id)
            if not existing_viewport:
                logger.warning(f"⚠️ 수정할 뷰포트를 찾을 수 없음: {viewport_id}")
                return None
            
            # 업데이트 데이터 준비
            update_data = {}
            
            if request.viewport is not None:
                update_data["viewport"] = {
                    "x": request.viewport.x,
                    "y": request.viewport.y,
                    "zoom": request.viewport.zoom
                }
            
            if request.settings is not None:
                update_data["settings"] = request.settings.dict()
            
            if request.metadata is not None:
                update_data["metadata"] = request.metadata
            
            # 뷰포트 수정
            updated_viewport = await self.viewport_repository.update_viewport(viewport_id, update_data)
            
            if updated_viewport:
                logger.info(f"✅ 뷰포트 수정 성공: {viewport_id}")
                return self._convert_to_viewport_response(updated_viewport)
            else:
                logger.error(f"❌ 뷰포트 수정 실패: {viewport_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 뷰포트 수정 실패: {str(e)}")
            return None
    
    async def delete_viewport(self, viewport_id: str) -> bool:
        """뷰포트 삭제"""
        try:
            logger.info(f"🗑️ 뷰포트 삭제: {viewport_id}")
            
            # 뷰포트 삭제
            success = await self.viewport_repository.delete_viewport(viewport_id)
            
            if success:
                logger.info(f"✅ 뷰포트 삭제 성공: {viewport_id}")
            else:
                logger.warning(f"⚠️ 뷰포트 삭제 실패: {viewport_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 뷰포트 삭제 실패: {str(e)}")
            return False
    
    # ============================================================================
    # 🖱️ 뷰포트 상태 및 설정 관리
    # ============================================================================
    
    async def update_viewport_state(self, flow_id: str, request: ViewportStateUpdateRequest) -> Optional[ViewportStateResponse]:
        """뷰포트 상태 업데이트"""
        try:
            logger.info(f"🔄 뷰포트 상태 업데이트: {flow_id}")
            
            # 뷰포트 상태 업데이트
            updated_viewport = await self.viewport_repository.update_viewport_state(
                flow_id, 
                request.viewport.dict()
            )
            
            if updated_viewport:
                logger.info(f"✅ 뷰포트 상태 업데이트 성공: {flow_id}")
                return ViewportStateResponse(
                    viewport=request.viewport,
                    settings=updated_viewport.get("settings", {})
                )
            else:
                logger.warning(f"⚠️ 뷰포트 상태 업데이트 실패: {flow_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 뷰포트 상태 업데이트 실패: {str(e)}")
            return None
    
    async def update_viewport_settings(self, flow_id: str, request: ViewportSettingsUpdateRequest) -> Optional[ViewportResponse]:
        """뷰포트 설정 업데이트"""
        try:
            logger.info(f"⚙️ 뷰포트 설정 업데이트: {flow_id}")
            
            # 뷰포트 설정 업데이트
            updated_viewport = await self.viewport_repository.update_viewport_settings(
                flow_id, 
                request.settings.dict()
            )
            
            if updated_viewport:
                logger.info(f"✅ 뷰포트 설정 업데이트 성공: {flow_id}")
                return self._convert_to_viewport_response(updated_viewport)
            else:
                logger.warning(f"⚠️ 뷰포트 설정 업데이트 실패: {flow_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 뷰포트 설정 업데이트 실패: {str(e)}")
            return None
    
    # ============================================================================
    # 🔍 뷰포트 검색 및 통계
    # ============================================================================
    
    async def search_viewports(self, request: ViewportSearchRequest) -> ViewportListResponse:
        """뷰포트 검색"""
        try:
            logger.info(f"🔍 뷰포트 검색: {request}")
            
            # 모든 뷰포트 조회 (실제로는 검색 조건 적용)
            all_viewports = await self.viewport_repository.get_all_viewports()
            
            # 검색 조건 적용
            filtered_viewports = []
            for viewport in all_viewports:
                # 플로우 ID 필터
                if request.flow_id and viewport.get("flow_id") != request.flow_id:
                    continue
                
                # 줌 레벨 범위 필터
                if request.zoom_range:
                    min_zoom, max_zoom = request.zoom_range
                    viewport_zoom = viewport.get("viewport", {}).get("zoom", 1.0)
                    if not (min_zoom <= viewport_zoom <= max_zoom):
                        continue
                
                filtered_viewports.append(viewport)
            
            # ViewportResponse 형식으로 변환
            viewport_responses = [self._convert_to_viewport_response(viewport) for viewport in filtered_viewports]
            
            logger.info(f"✅ 뷰포트 검색 성공: {len(filtered_viewports)}개")
            return ViewportListResponse(
                viewports=viewport_responses,
                total=len(filtered_viewports)
            )
            
        except Exception as e:
            logger.error(f"❌ 뷰포트 검색 실패: {str(e)}")
            return ViewportListResponse(viewports=[], total=0)
    
    async def get_viewport_stats(self) -> ViewportStatsResponse:
        """뷰포트 통계 조회"""
        try:
            logger.info(f"📊 뷰포트 통계 조회")
            
            stats = await self.viewport_repository.get_viewport_stats()
            
            logger.info(f"✅ 뷰포트 통계 조회 성공")
            return ViewportStatsResponse(**stats)
            
        except Exception as e:
            logger.error(f"❌ 뷰포트 통계 조회 실패: {str(e)}")
            return ViewportStatsResponse(
                total_viewports=0,
                average_zoom=1.0,
                most_used_zoom=1.0,
                pan_usage_count=0,
                zoom_usage_count=0
            )
    
    # ============================================================================
    # 🎯 뷰포트 모드 관리
    # ============================================================================
    
    async def get_viewport_modes(self, flow_id: str) -> ViewportModeResponse:
        """뷰포트 모드 조회"""
        try:
            logger.info(f"🎯 뷰포트 모드 조회: {flow_id}")
            
            # 현재 뷰포트 조회
            current_viewport = await self.viewport_repository.get_viewport_by_flow_id(flow_id)
            
            # 사용 가능한 모드 정의
            available_modes = [
                ViewportMode(
                    mode="default",
                    description="기본 뷰포트 모드",
                    settings=current_viewport.get("settings", {}) if current_viewport else {}
                ),
                ViewportMode(
                    mode="design",
                    description="디자인 도구 모드",
                    settings={
                        "minZoom": 0.1,
                        "maxZoom": 3.0,
                        "panEnabled": True,
                        "zoomEnabled": True,
                        "fitViewOnInit": False,
                        "snapToGrid": True,
                        "gridSize": 10
                    }
                ),
                ViewportMode(
                    mode="map",
                    description="지도 네비게이션 모드",
                    settings={
                        "minZoom": 0.5,
                        "maxZoom": 5.0,
                        "panEnabled": True,
                        "zoomEnabled": True,
                        "fitViewOnInit": True,
                        "snapToGrid": False,
                        "gridSize": 20
                    }
                ),
                ViewportMode(
                    mode="presentation",
                    description="프레젠테이션 모드",
                    settings={
                        "minZoom": 0.8,
                        "maxZoom": 2.0,
                        "panEnabled": False,
                        "zoomEnabled": True,
                        "fitViewOnInit": True,
                        "snapToGrid": False,
                        "gridSize": 20
                    }
                )
            ]
            
            # 현재 모드 결정
            current_mode = "default"
            if current_viewport:
                current_mode = current_viewport.get("metadata", {}).get("mode", "default")
            
            # 현재 모드 설정
            mode_settings = {}
            for mode in available_modes:
                if mode.mode == current_mode:
                    mode_settings = mode.settings
                    break
            
            logger.info(f"✅ 뷰포트 모드 조회 성공: {flow_id}")
            return ViewportModeResponse(
                current_mode=current_mode,
                available_modes=available_modes,
                mode_settings=mode_settings
            )
            
        except Exception as e:
            logger.error(f"❌ 뷰포트 모드 조회 실패: {str(e)}")
            # 기본 모드 반환
            return ViewportModeResponse(
                current_mode="default",
                available_modes=[],
                mode_settings={}
            )
    
    async def set_viewport_mode(self, flow_id: str, mode: str) -> Optional[ViewportResponse]:
        """뷰포트 모드 설정"""
        try:
            logger.info(f"🎯 뷰포트 모드 설정: {flow_id} -> {mode}")
            
            # 모드별 설정 가져오기
            mode_settings = await self._get_mode_settings(mode)
            
            # 뷰포트 메타데이터 업데이트
            update_data = {
                "metadata": {"mode": mode},
                "settings": mode_settings
            }
            
            # 뷰포트 업데이트
            updated_viewport = await self.viewport_repository.update_viewport_settings(flow_id, mode_settings)
            
            if updated_viewport:
                logger.info(f"✅ 뷰포트 모드 설정 성공: {flow_id} -> {mode}")
                return self._convert_to_viewport_response(updated_viewport)
            else:
                logger.warning(f"⚠️ 뷰포트 모드 설정 실패: {flow_id} -> {mode}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 뷰포트 모드 설정 실패: {str(e)}")
            return None
    
    # ============================================================================
    # 🔧 내부 헬퍼 메서드
    # ============================================================================
    
    async def _validate_viewport_creation(self, viewport_data: Dict[str, Any]) -> None:
        """뷰포트 생성 검증"""
        # 줌 레벨 검증
        zoom = viewport_data.get("viewport", {}).get("zoom", 1.0)
        if not (0.1 <= zoom <= 5.0):
            raise ValueError("줌 레벨은 0.1 ~ 5.0 사이여야 합니다")
        
        # 설정 검증
        settings = viewport_data.get("settings", {})
        min_zoom = settings.get("minZoom", 0.1)
        max_zoom = settings.get("maxZoom", 5.0)
        
        if min_zoom >= max_zoom:
            raise ValueError("최소 줌은 최대 줌보다 작아야 합니다")
        
        if not (0.01 <= min_zoom <= 1.0):
            raise ValueError("최소 줌은 0.01 ~ 1.0 사이여야 합니다")
        
        if not (1.0 <= max_zoom <= 10.0):
            raise ValueError("최대 줌은 1.0 ~ 10.0 사이여야 합니다")
    
    def _convert_to_viewport_response(self, viewport_data: Dict[str, Any]) -> ViewportResponse:
        """뷰포트 데이터를 응답 형식으로 변환"""
        from app.domain.Viewport.Viewport_schema import ViewportState, ViewportSettings
        
        return ViewportResponse(
            id=viewport_data["id"],
            flow_id=viewport_data["flow_id"],
            viewport=ViewportState(**viewport_data["viewport"]),
            settings=ViewportSettings(**viewport_data.get("settings", {})),
            metadata=viewport_data.get("metadata", {}),
            created_at=viewport_data["created_at"].isoformat() if viewport_data.get("created_at") else None,
            updated_at=viewport_data["updated_at"].isoformat() if viewport_data.get("updated_at") else None
        )
    
    async def _get_mode_settings(self, mode: str) -> Dict[str, Any]:
        """모드별 설정 반환"""
        mode_settings_map = {
            "default": {
                "minZoom": 0.1,
                "maxZoom": 5.0,
                "panEnabled": True,
                "zoomEnabled": True,
                "fitViewOnInit": True,
                "snapToGrid": False,
                "gridSize": 20
            },
            "design": {
                "minZoom": 0.1,
                "maxZoom": 3.0,
                "panEnabled": True,
                "zoomEnabled": True,
                "fitViewOnInit": False,
                "snapToGrid": True,
                "gridSize": 10
            },
            "map": {
                "minZoom": 0.5,
                "maxZoom": 5.0,
                "panEnabled": True,
                "zoomEnabled": True,
                "fitViewOnInit": True,
                "snapToGrid": False,
                "gridSize": 20
            },
            "presentation": {
                "minZoom": 0.8,
                "maxZoom": 2.0,
                "panEnabled": False,
                "zoomEnabled": True,
                "fitViewOnInit": True,
                "snapToGrid": False,
                "gridSize": 20
            }
        }
        
        return mode_settings_map.get(mode, mode_settings_map["default"])
