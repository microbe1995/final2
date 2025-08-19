# ============================================================================
# 🖼️ Canvas Schema - Canvas API 스키마 (ReactFlow 통합)
# ============================================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List, Union
from app.domain.shape.shape_schema import ShapeResponse
from app.domain.arrow.arrow_schema import ArrowResponse

# ============================================================================
# 🔄 ReactFlow 전용 스키마
# ============================================================================

class ReactFlowPosition(BaseModel):
    """ReactFlow 노드 위치"""
    x: float = Field(..., description="X 좌표")
    y: float = Field(..., description="Y 좌표")

class ReactFlowNodeData(BaseModel):
    """ReactFlow 노드 데이터"""
    label: str = Field(..., description="노드 레이블")
    # 추가 데이터 필드들
    color: Optional[str] = Field(default=None, description="노드 색상")
    description: Optional[str] = Field(default=None, description="노드 설명")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 메타데이터")

class ReactFlowNode(BaseModel):
    """ReactFlow 노드"""
    id: str = Field(..., description="노드 ID")
    position: ReactFlowPosition = Field(..., description="노드 위치")
    data: ReactFlowNodeData = Field(..., description="노드 데이터")
    type: Optional[str] = Field(default="default", description="노드 타입")
    draggable: Optional[bool] = Field(default=True, description="드래그 가능 여부")
    selectable: Optional[bool] = Field(default=True, description="선택 가능 여부")
    deletable: Optional[bool] = Field(default=True, description="삭제 가능 여부")
    style: Optional[Dict[str, Any]] = Field(default_factory=dict, description="노드 스타일")

class ReactFlowEdge(BaseModel):
    """ReactFlow 엣지"""
    id: str = Field(..., description="엣지 ID")
    source: str = Field(..., description="출발 노드 ID")
    target: str = Field(..., description="도착 노드 ID")
    type: Optional[str] = Field(default="default", description="엣지 타입")
    animated: Optional[bool] = Field(default=False, description="애니메이션 여부")
    style: Optional[Dict[str, Any]] = Field(default_factory=dict, description="엣지 스타일")
    label: Optional[str] = Field(default=None, description="엣지 레이블")
    labelStyle: Optional[Dict[str, Any]] = Field(default_factory=dict, description="레이블 스타일")
    labelBgStyle: Optional[Dict[str, Any]] = Field(default_factory=dict, description="레이블 배경 스타일")

class ReactFlowViewport(BaseModel):
    """ReactFlow 뷰포트 상태"""
    x: float = Field(default=0, description="X축 팬")
    y: float = Field(default=0, description="Y축 팬")
    zoom: float = Field(default=1, description="줌 레벨")

class ReactFlowState(BaseModel):
    """ReactFlow 상태 관리"""
    nodes: List[ReactFlowNode] = Field(default_factory=list, description="노드 목록")
    edges: List[ReactFlowEdge] = Field(default_factory=list, description="엣지 목록")
    viewport: ReactFlowViewport = Field(default_factory=ReactFlowViewport, description="뷰포트 상태")

# ============================================================================
# 🔄 ReactFlow 이벤트 스키마
# ============================================================================

class NodeChangeEvent(BaseModel):
    """노드 변경 이벤트"""
    type: str = Field(..., description="변경 타입 (add, remove, select, position)")
    id: str = Field(..., description="노드 ID")
    position: Optional[ReactFlowPosition] = Field(default=None, description="새 위치")
    selected: Optional[bool] = Field(default=None, description="선택 상태")

class EdgeChangeEvent(BaseModel):
    """엣지 변경 이벤트"""
    type: str = Field(..., description="변경 타입 (add, remove, select)")
    id: str = Field(..., description="엣지 ID")
    selected: Optional[bool] = Field(default=None, description="선택 상태")

class ReactFlowUpdateRequest(BaseModel):
    """ReactFlow 상태 업데이트 요청"""
    canvas_id: str = Field(..., description="캔버스 ID")
    nodes: Optional[List[ReactFlowNode]] = Field(default=None, description="업데이트할 노드")
    edges: Optional[List[ReactFlowEdge]] = Field(default=None, description="업데이트할 엣지")
    viewport: Optional[ReactFlowViewport] = Field(default=None, description="뷰포트 상태")

# ============================================================================
# 🔗 Connection 관련 스키마
# ============================================================================

class ConnectionParams(BaseModel):
    """ReactFlow 연결 파라미터"""
    source: str = Field(..., description="출발 노드 ID")
    target: str = Field(..., description="도착 노드 ID")
    sourceHandle: Optional[str] = Field(default=None, description="출발 핸들 ID")
    targetHandle: Optional[str] = Field(default=None, description="도착 핸들 ID")

class ConnectionEvent(BaseModel):
    """ReactFlow 연결 이벤트"""
    type: str = Field(default="connection", description="이벤트 타입")
    params: ConnectionParams = Field(..., description="연결 파라미터")
    timestamp: Optional[str] = Field(default=None, description="이벤트 발생 시간")

class ConnectionRequest(BaseModel):
    """ReactFlow 연결 생성 요청"""
    canvas_id: str = Field(..., description="캔버스 ID")
    connection: ConnectionParams = Field(..., description="연결 정보")
    edge_options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="엣지 옵션 (스타일, 타입 등)")

# ============================================================================
# 📝 요청 스키마
# ============================================================================

class CanvasCreateRequest(BaseModel):
    """Canvas 생성 요청 스키마 - ReactFlow 통합"""
    name: str = Field(..., min_length=1, max_length=100, description="Canvas 이름")
    description: Optional[str] = Field(default=None, description="Canvas 설명")
    # ReactFlow 데이터 구조 (새로운 스키마 사용)
    nodes: Optional[List[ReactFlowNode]] = Field(default_factory=list, description="ReactFlow 노드 목록")
    edges: Optional[List[ReactFlowEdge]] = Field(default_factory=list, description="ReactFlow 엣지 목록")
    viewport: Optional[ReactFlowViewport] = Field(default_factory=ReactFlowViewport, description="뷰포트 상태")
    # 기존 Canvas 속성 (선택적)
    width: Optional[float] = Field(default=1200.0, gt=0, le=10000, description="Canvas 너비")
    height: Optional[float] = Field(default=800.0, gt=0, le=10000, description="Canvas 높이")
    background_color: Optional[str] = Field(default="#FFFFFF", description="배경 색상")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 메타데이터")

    @field_validator('background_color')
    @classmethod
    def validate_background_color(cls, v):
        """배경 색상 형식 검증"""
        if not v.startswith('#') or len(v) not in [4, 7, 9]:
            raise ValueError('색상은 #RGB, #RRGGBB, #RRGGBBAA 형식이어야 합니다')
        return v

class CanvasUpdateRequest(BaseModel):
    """Canvas 수정 요청 스키마 - ReactFlow 통합"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Canvas 이름")
    description: Optional[str] = Field(default=None, description="Canvas 설명")
    # ReactFlow 데이터 구조 (새로운 스키마 사용)
    nodes: Optional[List[ReactFlowNode]] = Field(default=None, description="ReactFlow 노드 목록")
    edges: Optional[List[ReactFlowEdge]] = Field(default=None, description="ReactFlow 엣지 목록")
    viewport: Optional[ReactFlowViewport] = Field(default=None, description="뷰포트 상태")
    # 기존 Canvas 속성 (선택적)
    width: Optional[float] = Field(default=None, gt=0, le=10000, description="Canvas 너비")
    height: Optional[float] = Field(default=None, gt=0, le=10000, description="Canvas 높이")
    background_color: Optional[str] = Field(default=None, description="배경 색상")
    zoom_level: Optional[float] = Field(default=None, ge=0.1, le=5.0, description="확대/축소 레벨")
    pan_x: Optional[float] = Field(default=None, description="X축 이동 거리")
    pan_y: Optional[float] = Field(default=None, description="Y축 이동 거리")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="추가 메타데이터")

    @field_validator('background_color')
    @classmethod
    def validate_background_color(cls, v):
        """배경 색상 형식 검증"""
        if v is None:
            return v
        if not v.startswith('#') or len(v) not in [4, 7, 9]:
            raise ValueError('색상은 #RGB, #RRGGBB, #RRGGBBAA 형식이어야 합니다')
        return v

# ============================================================================
# 📤 응답 스키마
# ============================================================================

class CanvasResponse(BaseModel):
    """Canvas 응답 스키마 - ReactFlow 통합"""
    id: str = Field(..., description="Canvas ID")
    name: str = Field(..., description="Canvas 이름")
    description: Optional[str] = Field(default=None, description="Canvas 설명")
    # ReactFlow 데이터 구조 (새로운 스키마 사용)
    nodes: List[ReactFlowNode] = Field(default_factory=list, description="ReactFlow 노드 목록")
    edges: List[ReactFlowEdge] = Field(default_factory=list, description="ReactFlow 엣지 목록")
    viewport: ReactFlowViewport = Field(default_factory=ReactFlowViewport, description="뷰포트 상태")
    # 기존 Canvas 속성 (선택적)
    width: float = Field(..., description="Canvas 너비")
    height: float = Field(..., description="Canvas 높이")
    background_color: str = Field(..., description="배경 색상")
    zoom_level: float = Field(..., description="확대/축소 레벨")
    pan_x: float = Field(..., description="X축 이동 거리")
    pan_y: float = Field(..., description="Y축 이동 거리")
    created_at: str = Field(..., description="생성 시간")
    updated_at: str = Field(..., description="수정 시간")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")

class CanvasListResponse(BaseModel):
    """Canvas 목록 응답 스키마"""
    canvases: list[CanvasResponse] = Field(..., description="Canvas 목록")
    total: int = Field(..., description="전체 Canvas 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")

# ============================================================================
# 🔍 검색 스키마
# ============================================================================

class CanvasSearchRequest(BaseModel):
    """Canvas 검색 요청 스키마"""
    name: Optional[str] = Field(default=None, description="Canvas 이름 (부분 일치)")
    min_width: Optional[float] = Field(default=None, description="최소 너비")
    max_width: Optional[float] = Field(default=None, description="최대 너비")
    min_height: Optional[float] = Field(default=None, description="최소 높이")
    max_height: Optional[float] = Field(default=None, description="최대 높이")
    has_shapes: Optional[bool] = Field(default=None, description="도형 포함 여부")
    has_arrows: Optional[bool] = Field(default=None, description="화살표 포함 여부")
    page: int = Field(default=1, ge=1, description="페이지 번호")
    size: int = Field(default=20, ge=1, le=100, description="페이지 크기")

# ============================================================================
# 📊 통계 스키마
# ============================================================================

class CanvasStatsResponse(BaseModel):
    """Canvas 통계 응답 스키마"""
    total_canvases: int = Field(..., description="전체 Canvas 수")
    total_shapes: int = Field(..., description="전체 도형 수")
    total_arrows: int = Field(..., description="전체 화살표 수")
    average_canvas_size: Dict[str, float] = Field(..., description="평균 Canvas 크기")
    most_used_colors: List[Dict[str, Any]] = Field(..., description="가장 많이 사용된 색상")
    canvas_usage_stats: Dict[str, int] = Field(..., description="Canvas 사용 통계")

# ============================================================================
# 🎯 특수 기능 스키마
# ============================================================================

class CanvasExportRequest(BaseModel):
    """Canvas 내보내기 요청 스키마"""
    format: str = Field(default="json", description="내보내기 형식 (json, svg, png)")
    include_shapes: bool = Field(default=True, description="도형 포함 여부")
    include_arrows: bool = Field(default=True, description="화살표 포함 여부")
    include_metadata: bool = Field(default=True, description="메타데이터 포함 여부")
    resolution: Optional[Dict[str, int]] = Field(default=None, description="이미지 해상도 (PNG용)")

class CanvasImportRequest(BaseModel):
    """Canvas 가져오기 요청 스키마"""
    data: str = Field(..., description="가져올 데이터 (JSON 문자열)")
    overwrite: bool = Field(default=False, description="기존 Canvas 덮어쓰기 여부")
    merge: bool = Field(default=False, description="기존 Canvas와 병합 여부")

class CanvasDuplicateRequest(BaseModel):
    """Canvas 복제 요청 스키마"""
    new_name: str = Field(..., min_length=1, max_length=100, description="새 Canvas 이름")
    include_shapes: bool = Field(default=True, description="도형 포함 여부")
    include_arrows: bool = Field(default=True, description="화살표 포함 여부")
    include_metadata: bool = Field(default=True, description="메타데이터 포함 여부")

class CanvasMergeRequest(BaseModel):
    """Canvas 병합 요청 스키마"""
    source_canvas_ids: List[str] = Field(..., min_items=2, description="병합할 Canvas ID 목록")
    target_canvas_name: str = Field(..., min_length=1, max_length=100, description="결과 Canvas 이름")
    merge_strategy: str = Field(default="append", description="병합 전략 (append, replace, smart)")

# ============================================================================
# 🔧 관리 스키마
# ============================================================================

class CanvasBulkOperationRequest(BaseModel):
    """Canvas 일괄 작업 요청 스키마"""
    operation: str = Field(..., description="작업 유형 (delete, duplicate, export)")
    canvas_ids: List[str] = Field(..., min_items=1, description="대상 Canvas ID 목록")
    options: Optional[Dict[str, Any]] = Field(default=None, description="작업 옵션")

class CanvasTemplateRequest(BaseModel):
    """Canvas 템플릿 요청 스키마"""
    template_type: str = Field(..., description="템플릿 유형 (flowchart, diagram, mindmap)")
    size: str = Field(default="standard", description="템플릿 크기 (small, standard, large)")
    theme: str = Field(default="default", description="템플릿 테마")
    include_examples: bool = Field(default=True, description="예시 요소 포함 여부")
