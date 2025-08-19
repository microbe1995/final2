# ============================================================================
# 🖱️ Viewport Schema - ReactFlow 뷰포트 API 스키마
# ============================================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime

# ============================================================================
# 📱 뷰포트 기본 스키마
# ============================================================================

class ViewportState(BaseModel):
    """뷰포트 상태"""
    x: float = Field(default=0.0, description="뷰포트 X 좌표")
    y: float = Field(default=0.0, description="뷰포트 Y 좌표")
    zoom: float = Field(default=1.0, ge=0.1, le=5.0, description="뷰포트 줌 레벨")

class ViewportSettings(BaseModel):
    """뷰포트 설정"""
    min_zoom: float = Field(default=0.1, ge=0.01, le=1.0, description="최소 줌 레벨")
    max_zoom: float = Field(default=5.0, ge=1.0, le=10.0, description="최대 줌 레벨")
    pan_enabled: bool = Field(default=True, description="팬 활성화 여부")
    zoom_enabled: bool = Field(default=True, description="줌 활성화 여부")
    fit_view_on_init: bool = Field(default=True, description="초기화 시 뷰 맞춤")
    snap_to_grid: bool = Field(default=False, description="그리드에 스냅")
    grid_size: int = Field(default=20, ge=5, le=100, description="그리드 크기")

# ============================================================================
# 📝 뷰포트 요청 스키마
# ============================================================================

class ViewportCreateRequest(BaseModel):
    """뷰포트 생성 요청"""
    flow_id: str = Field(..., description="플로우 ID")
    viewport: ViewportState = Field(default_factory=ViewportState, description="초기 뷰포트 상태")
    settings: Optional[ViewportSettings] = Field(default_factory=ViewportSettings, description="뷰포트 설정")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="뷰포트 메타데이터")

class ViewportUpdateRequest(BaseModel):
    """뷰포트 수정 요청"""
    viewport: Optional[ViewportState] = Field(default=None, description="뷰포트 상태")
    settings: Optional[ViewportSettings] = Field(default=None, description="뷰포트 설정")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="뷰포트 메타데이터")

class ViewportStateUpdateRequest(BaseModel):
    """뷰포트 상태 업데이트 요청"""
    viewport: ViewportState = Field(..., description="새로운 뷰포트 상태")

class ViewportSettingsUpdateRequest(BaseModel):
    """뷰포트 설정 업데이트 요청"""
    settings: ViewportSettings = Field(..., description="새로운 뷰포트 설정")

# ============================================================================
# 📤 뷰포트 응답 스키마
# ============================================================================

class ViewportResponse(BaseModel):
    """뷰포트 응답"""
    id: str = Field(..., description="뷰포트 ID")
    flow_id: str = Field(..., description="플로우 ID")
    viewport: ViewportState = Field(..., description="뷰포트 상태")
    settings: ViewportSettings = Field(..., description="뷰포트 설정")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="뷰포트 메타데이터")
    created_at: str = Field(..., description="생성 시간")
    updated_at: str = Field(..., description="수정 시간")
    
    class Config:
        from_attributes = True

class ViewportListResponse(BaseModel):
    """뷰포트 목록 응답"""
    viewports: List[ViewportResponse] = Field(..., description="뷰포트 목록")
    total: int = Field(..., description="전체 뷰포트 수")

class ViewportStateResponse(BaseModel):
    """뷰포트 상태 응답"""
    viewport: ViewportState = Field(..., description="뷰포트 상태")
    settings: ViewportSettings = Field(..., description="뷰포트 설정")

# ============================================================================
# 🔍 뷰포트 검색 스키마
# ============================================================================

class ViewportSearchRequest(BaseModel):
    """뷰포트 검색 요청"""
    flow_id: Optional[str] = Field(default=None, description="플로우 ID")
    zoom_range: Optional[tuple[float, float]] = Field(default=None, description="줌 레벨 범위")
    
    @field_validator('zoom_range')
    @classmethod
    def validate_zoom_range(cls, v):
        if v is not None:
            min_zoom, max_zoom = v
            if min_zoom >= max_zoom:
                raise ValueError("최소 줌은 최대 줌보다 작아야 합니다")
            if min_zoom < 0.01 or max_zoom > 10.0:
                raise ValueError("줌 범위는 0.01 ~ 10.0 사이여야 합니다")
        return v

# ============================================================================
# 📊 뷰포트 통계 스키마
# ============================================================================

class ViewportStatsResponse(BaseModel):
    """뷰포트 통계 응답"""
    total_viewports: int = Field(..., description="전체 뷰포트 수")
    average_zoom: float = Field(..., description="평균 줌 레벨")
    most_used_zoom: float = Field(..., description="가장 많이 사용된 줌 레벨")
    pan_usage_count: int = Field(..., description="팬 사용 횟수")
    zoom_usage_count: int = Field(..., description="줌 사용 횟수")

# ============================================================================
# 🎯 뷰포트 모드 스키마
# ============================================================================

class ViewportMode(BaseModel):
    """뷰포트 모드"""
    mode: str = Field(..., description="뷰포트 모드 (default, design, map, presentation)")
    description: str = Field(..., description="모드 설명")
    settings: ViewportSettings = Field(..., description="모드별 설정")

class ViewportModeResponse(BaseModel):
    """뷰포트 모드 응답"""
    current_mode: str = Field(..., description="현재 모드")
    available_modes: List[ViewportMode] = Field(..., description="사용 가능한 모드 목록")
    mode_settings: ViewportSettings = Field(..., description="현재 모드 설정")
