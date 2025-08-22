# ============================================================================
# 🔗 Edge Schema - ReactFlow 엣지 데이터 검증 및 직렬화
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

# ============================================================================
# 🔗 엣지 기본 스키마
# ============================================================================

class EdgePosition(BaseModel):
    """엣지 연결 위치"""
    x: float
    y: float

class EdgeData(BaseModel):
    """엣지 데이터"""
    label: Optional[str] = None
    processType: Optional[str] = "standard"
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class EdgeStyle(BaseModel):
    """엣지 스타일"""
    stroke: Optional[str] = None
    strokeWidth: Optional[float] = None
    strokeDasharray: Optional[str] = None
    opacity: Optional[float] = None

# ============================================================================
# 🔗 엣지 요청 스키마
# ============================================================================

class EdgeCreateRequest(BaseModel):
    """엣지 생성 요청"""
    id: Optional[str] = None
    flow_id: str = Field(..., description="플로우 ID")
    source: str = Field(..., description="시작 노드 ID")
    target: str = Field(..., description="끝 노드 ID")
    type: Optional[str] = "default"
    data: Optional[EdgeData] = None
    style: Optional[EdgeStyle] = None
    animated: Optional[bool] = False
    hidden: Optional[bool] = False
    deletable: Optional[bool] = True
    
    @validator('source')
    def validate_source(cls, v):
        if not v or not v.strip():
            raise ValueError("시작 노드 ID는 필수입니다")
        return v.strip()
    
    @validator('target')
    def validate_target(cls, v):
        if not v or not v.strip():
            raise ValueError("끝 노드 ID는 필수입니다")
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        if v:
            valid_types = ['default', 'straight', 'step', 'smoothstep', 'bezier', 'processEdge']
            if v not in valid_types:
                return 'default'  # 유효하지 않은 타입은 기본값으로
        return v or 'default'

class EdgeUpdateRequest(BaseModel):
    """엣지 수정 요청"""
    source: Optional[str] = None
    target: Optional[str] = None
    type: Optional[str] = None
    data: Optional[EdgeData] = None
    style: Optional[EdgeStyle] = None
    animated: Optional[bool] = None
    hidden: Optional[bool] = None
    deletable: Optional[bool] = None
    selected: Optional[bool] = None

class EdgeBatchUpdateRequest(BaseModel):
    """엣지 일괄 수정 요청"""
    edges: List[Dict[str, Any]] = Field(..., description="수정할 엣지 목록")

# ============================================================================
# 🔗 엣지 응답 스키마
# ============================================================================

class EdgeResponse(BaseModel):
    """엣지 응답"""
    id: str
    flow_id: str
    source: str
    target: str
    type: str = "default"
    style: Optional[str] = None
    animated: bool = False
    label: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "edge_1",
                "flow_id": "flow_123",
                "source": "node_1",
                "target": "node_2",
                "type": "default",
                "style": "stroke: #333; stroke-width: 2;",
                "animated": False,
                "label": "Connection",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class EdgeListResponse(BaseModel):
    """엣지 목록 응답"""
    edges: List[EdgeResponse]
    total: int

class ReactFlowEdgeResponse(BaseModel):
    """ReactFlow 형식 엣지 응답"""
    id: str
    source: str
    target: str
    type: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    style: Optional[Dict[str, Any]] = None
    animated: Optional[bool] = None
    hidden: Optional[bool] = None
    deletable: Optional[bool] = None
    selected: Optional[bool] = None

# ============================================================================
# 🔗 엣지 검색 및 통계 스키마
# ============================================================================

class EdgeSearchRequest(BaseModel):
    """엣지 검색 요청"""
    flow_id: Optional[str] = None
    source: Optional[str] = None
    target: Optional[str] = None
    type: Optional[str] = None
    animated: Optional[bool] = None
    hidden: Optional[bool] = None

class EdgeStatsResponse(BaseModel):
    """엣지 통계 응답"""
    total_edges: int
    edges_by_type: Dict[str, int]
    animated_edges: int
    hidden_edges: int
    average_edges_per_flow: float

# ============================================================================
# 🔗 연결 관련 스키마 (onConnect 핸들러 지원)
# ============================================================================

class ConnectionRequest(BaseModel):
    """연결 요청 (onConnect 핸들러용)"""
    source: str = Field(..., description="시작 노드 ID")
    target: str = Field(..., description="끝 노드 ID")
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None
    
    @validator('source')
    def validate_source(cls, v):
        if not v or not v.strip():
            raise ValueError("시작 노드 ID는 필수입니다")
        return v.strip()
    
    @validator('target') 
    def validate_target(cls, v):
        if not v or not v.strip():
            raise ValueError("끝 노드 ID는 필수입니다")
        return v.strip()

class ConnectionResponse(BaseModel):
    """연결 응답"""
    edge: EdgeResponse
    message: str = "연결이 성공적으로 생성되었습니다"

# ============================================================================
# 🔗 엣지 변경사항 스키마 (onEdgesChange 핸들러 지원)
# ============================================================================

class EdgeChangeRequest(BaseModel):
    """엣지 변경사항 요청"""
    id: str
    type: str  # 'add', 'remove', 'select', 'position' 등
    item: Optional[Dict[str, Any]] = None

class EdgeChangesRequest(BaseModel):
    """엣지 변경사항 목록 요청"""
    changes: List[EdgeChangeRequest] = Field(..., description="엣지 변경사항 목록")

class EdgeChangesResponse(BaseModel):
    """엣지 변경사항 응답"""
    processed_changes: int
    updated_edges: List[EdgeResponse]
    message: str = "엣지 변경사항이 성공적으로 처리되었습니다"
