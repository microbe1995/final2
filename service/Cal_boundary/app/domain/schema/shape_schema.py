# ============================================================================
# 🎨 Shape Schema - 도형 API 스키마
# ============================================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from enum import Enum

class ShapeTypeEnum(str, Enum):
    """도형 타입 열거형"""
    RECTANGLE = "rectangle"    # 사각형
    CIRCLE = "circle"          # 원
    TRIANGLE = "triangle"      # 삼각형
    ELLIPSE = "ellipse"        # 타원
    POLYGON = "polygon"        # 다각형

# ============================================================================
# 📝 요청 스키마
# ============================================================================

class ShapeCreateRequest(BaseModel):
    """도형 생성 요청 스키마"""
    type: ShapeTypeEnum = Field(..., description="도형 타입")
    x: float = Field(..., ge=0, description="X 좌표")
    y: float = Field(..., ge=0, description="Y 좌표")
    width: float = Field(..., gt=0, description="너비")
    height: float = Field(..., gt=0, description="높이")
    color: str = Field(default="#3B82F6", description="테두리 색상")
    stroke_width: int = Field(default=2, ge=1, le=20, description="테두리 두께")
    fill_color: Optional[str] = Field(default=None, description="채우기 색상")
    rotation: float = Field(default=0.0, ge=0, le=360, description="회전 각도")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="투명도")
    canvas_id: Optional[str] = Field(default=None, description="Canvas ID")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="추가 메타데이터")

    @field_validator('color', 'fill_color')
    @classmethod
    def validate_color(cls, v):
        """색상 형식 검증"""
        if v is None:
            return v
        if not v.startswith('#') or len(v) not in [4, 7, 9]:
            raise ValueError('색상은 #RGB, #RRGGBB, #RRGGBBAA 형식이어야 합니다')
        return v

class ShapeUpdateRequest(BaseModel):
    """도형 수정 요청 스키마"""
    x: Optional[float] = Field(default=None, ge=0, description="X 좌표")
    y: Optional[float] = Field(default=None, ge=0, description="Y 좌표")
    width: Optional[float] = Field(default=None, gt=0, description="너비")
    height: Optional[float] = Field(default=None, gt=0, description="높이")
    color: Optional[str] = Field(default=None, description="테두리 색상")
    stroke_width: Optional[int] = Field(default=None, ge=1, le=20, description="테두리 두께")
    fill_color: Optional[str] = Field(default=None, description="채우기 색상")
    rotation: Optional[float] = Field(default=None, ge=0, le=360, description="회전 각도")
    opacity: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="투명도")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="추가 메타데이터")

    @field_validator('color', 'fill_color')
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

class ShapeResponse(BaseModel):
    """도형 응답 스키마"""
    id: str = Field(..., description="도형 ID")
    type: ShapeTypeEnum = Field(..., description="도형 타입")
    x: float = Field(..., description="X 좌표")
    y: float = Field(..., description="Y 좌표")
    width: float = Field(..., description="너비")
    height: float = Field(..., description="높이")
    color: str = Field(..., description="테두리 색상")
    stroke_width: int = Field(..., description="테두리 두께")
    fill_color: Optional[str] = Field(default=None, description="채우기 색상")
    rotation: float = Field(..., description="회전 각도")
    opacity: float = Field(..., description="투명도")
    canvas_id: Optional[str] = Field(default=None, description="Canvas ID")
    created_at: str = Field(..., description="생성 시간")
    updated_at: str = Field(..., description="수정 시간")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")

class ShapeListResponse(BaseModel):
    """도형 목록 응답 스키마"""
    shapes: list[ShapeResponse] = Field(..., description="도형 목록")
    total: int = Field(..., description="전체 도형 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")

# ============================================================================
# 🔍 검색 스키마
# ============================================================================

class ShapeSearchRequest(BaseModel):
    """도형 검색 요청 스키마"""
    type: Optional[ShapeTypeEnum] = Field(default=None, description="도형 타입")
    canvas_id: Optional[str] = Field(default=None, description="Canvas ID")
    min_x: Optional[float] = Field(default=None, description="최소 X 좌표")
    max_x: Optional[float] = Field(default=None, description="최대 X 좌표")
    min_y: Optional[float] = Field(default=None, description="최소 Y 좌표")
    max_y: Optional[float] = Field(default=None, description="최대 Y 좌표")
    color: Optional[str] = Field(default=None, description="색상")
    page: int = Field(default=1, ge=1, description="페이지 번호")
    size: int = Field(default=20, ge=1, le=100, description="페이지 크기")

# ============================================================================
# 📊 통계 스키마
# ============================================================================

class ShapeStatsResponse(BaseModel):
    """도형 통계 응답 스키마"""
    total_shapes: int = Field(..., description="전체 도형 수")
    shapes_by_type: Dict[str, int] = Field(..., description="타입별 도형 수")
    shapes_by_color: Dict[str, int] = Field(..., description="색상별 도형 수")
    average_size: Dict[str, float] = Field(..., description="평균 크기 (너비, 높이)")
    canvas_count: int = Field(..., description="사용 중인 Canvas 수")
