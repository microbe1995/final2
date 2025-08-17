# ============================================================================
# ➡️ Arrow Schema - 화살표 API 스키마
# ============================================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

class ArrowTypeEnum(str, Enum):
    """화살표 타입 열거형"""
    STRAIGHT = "straight"      # 직선 화살표
    CURVED = "curved"          # 곡선 화살표
    BIDIRECTIONAL = "bidirectional"  # 양방향 화살표
    DASHED = "dashed"          # 점선 화살표

# ============================================================================
# 📝 요청 스키마
# ============================================================================

class ArrowCreateRequest(BaseModel):
    """화살표 생성 요청 스키마"""
    type: ArrowTypeEnum = Field(..., description="화살표 타입")
    start_x: float = Field(..., ge=0, description="시작점 X 좌표")
    start_y: float = Field(..., ge=0, description="시작점 Y 좌표")
    end_x: float = Field(..., ge=0, description="끝점 X 좌표")
    end_y: float = Field(..., ge=0, description="끝점 Y 좌표")
    color: str = Field(default="#EF4444", description="화살표 색상")
    stroke_width: int = Field(default=3, ge=1, le=20, description="선 두께")
    arrow_size: float = Field(default=10.0, gt=0, le=50, description="화살표 크기")
    is_dashed: bool = Field(default=False, description="점선 여부")
    dash_pattern: Optional[List[float]] = Field(default=None, description="점선 패턴")
    control_points: Optional[List[Tuple[float, float]]] = Field(default=None, description="제어점 (곡선용)")
    canvas_id: Optional[str] = Field(default=None, description="Canvas ID")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="추가 메타데이터")

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """색상 형식 검증"""
        if not v.startswith('#') or len(v) not in [4, 7, 9]:
            raise ValueError('색상은 #RGB, #RRGGBB, #RRGGBBAA 형식이어야 합니다')
        return v

    @field_validator('dash_pattern')
    @classmethod
    def validate_dash_pattern(cls, v):
        """점선 패턴 검증"""
        if v is not None:
            if not all(isinstance(x, (int, float)) and x > 0 for x in v):
                raise ValueError('점선 패턴은 양수 값들로 구성되어야 합니다')
        return v

    @field_validator('control_points')
    @classmethod
    def validate_control_points(cls, v):
        """제어점 검증"""
        if v is not None:
            if not all(len(point) == 2 and all(isinstance(x, (int, float)) for x in point) for point in v):
                raise ValueError('제어점은 (x, y) 튜플로 구성되어야 합니다')
        return v

class ArrowUpdateRequest(BaseModel):
    """화살표 수정 요청 스키마"""
    start_x: Optional[float] = Field(default=None, ge=0, description="시작점 X 좌표")
    start_y: Optional[float] = Field(default=None, ge=0, description="시작점 Y 좌표")
    end_x: Optional[float] = Field(default=None, ge=0, description="끝점 X 좌표")
    end_y: Optional[float] = Field(default=None, ge=0, description="끝점 Y 좌표")
    color: Optional[str] = Field(default=None, description="화살표 색상")
    stroke_width: Optional[int] = Field(default=None, ge=1, le=20, description="선 두께")
    arrow_size: Optional[float] = Field(default=None, gt=0, le=50, description="화살표 크기")
    is_dashed: Optional[bool] = Field(default=None, description="점선 여부")
    dash_pattern: Optional[List[float]] = Field(default=None, description="점선 패턴")
    control_points: Optional[List[Tuple[float, float]]] = Field(default=None, description="제어점 (곡선용)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="추가 메타데이터")

    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """색상 형식 검증"""
        if v is None:
            return v
        if not v.startswith('#') or len(v) not in [4, 7, 9]:
            raise ValueError('색상은 #RGB, #RRGGBB, #RRGGBBAA 형식이어야 합니다')
        return v

# ============================================================================
# 📤 응답 스키마
# ============================================================================

class ArrowResponse(BaseModel):
    """화살표 응답 스키마"""
    id: str = Field(..., description="화살표 ID")
    type: ArrowTypeEnum = Field(..., description="화살표 타입")
    start_x: float = Field(..., description="시작점 X 좌표")
    start_y: float = Field(..., description="시작점 Y 좌표")
    end_x: float = Field(..., description="끝점 X 좌표")
    end_y: float = Field(..., description="끝점 Y 좌표")
    color: str = Field(..., description="화살표 색상")
    stroke_width: int = Field(..., description="선 두께")
    arrow_size: float = Field(..., description="화살표 크기")
    is_dashed: bool = Field(..., description="점선 여부")
    dash_pattern: List[float] = Field(..., description="점선 패턴")
    control_points: List[Tuple[float, float]] = Field(..., description="제어점")
    canvas_id: Optional[str] = Field(default=None, description="Canvas ID")
    created_at: str = Field(..., description="생성 시간")
    updated_at: str = Field(..., description="수정 시간")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")

class ArrowListResponse(BaseModel):
    """화살표 목록 응답 스키마"""
    arrows: list[ArrowResponse] = Field(..., description="화살표 목록")
    total: int = Field(..., description="전체 화살표 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")

# ============================================================================
# 🔍 검색 스키마
# ============================================================================

class ArrowSearchRequest(BaseModel):
    """화살표 검색 요청 스키마"""
    type: Optional[ArrowTypeEnum] = Field(default=None, description="화살표 타입")
    canvas_id: Optional[str] = Field(default=None, description="Canvas ID")
    min_length: Optional[float] = Field(default=None, description="최소 길이")
    max_length: Optional[float] = Field(default=None, description="최대 길이")
    color: Optional[str] = Field(default=None, description="색상")
    is_dashed: Optional[bool] = Field(default=None, description="점선 여부")
    page: int = Field(default=1, ge=1, description="페이지 번호")
    size: int = Field(default=20, ge=1, le=100, description="페이지 크기")

# ============================================================================
# 📊 통계 스키마
# ============================================================================

class ArrowStatsResponse(BaseModel):
    """화살표 통계 응답 스키마"""
    total_arrows: int = Field(..., description="전체 화살표 수")
    arrows_by_type: Dict[str, int] = Field(..., description="타입별 화살표 수")
    arrows_by_color: Dict[str, int] = Field(..., description="색상별 화살표 수")
    average_length: float = Field(..., description="평균 길이")
    dashed_count: int = Field(..., description="점선 화살표 수")
    canvas_count: int = Field(..., description="사용 중인 Canvas 수")

# ============================================================================
# 🎯 특수 기능 스키마
# ============================================================================

class ArrowConnectionRequest(BaseModel):
    """화살표 연결 요청 스키마"""
    from_shape_id: str = Field(..., description="시작 도형 ID")
    to_shape_id: str = Field(..., description="끝 도형 ID")
    arrow_type: ArrowTypeEnum = Field(default=ArrowTypeEnum.STRAIGHT, description="화살표 타입")
    color: str = Field(default="#EF4444", description="화살표 색상")
    stroke_width: int = Field(default=3, description="선 두께")
    canvas_id: str = Field(..., description="Canvas ID")

class ArrowBatchCreateRequest(BaseModel):
    """화살표 일괄 생성 요청 스키마"""
    arrows: list[ArrowCreateRequest] = Field(..., description="화살표 목록")
    canvas_id: str = Field(..., description="Canvas ID")
