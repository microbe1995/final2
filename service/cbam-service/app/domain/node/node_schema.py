# ============================================================================
# 🔵 Node Schema - ReactFlow 노드 스키마
# ============================================================================

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime

# ============================================================================
# 📍 노드 위치 스키마
# ============================================================================

class NodePosition(BaseModel):
    """노드 위치"""
    x: float = Field(..., description="X 좌표")
    y: float = Field(..., description="Y 좌표")

# ============================================================================
# 📊 노드 데이터 스키마
# ============================================================================

class NodeData(BaseModel):
    """노드 데이터"""
    label: str = Field(..., description="노드 레이블")
    description: Optional[str] = Field(default=None, description="노드 설명")
    color: Optional[str] = Field(default=None, description="노드 색상")
    icon: Optional[str] = Field(default=None, description="노드 아이콘")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="추가 메타데이터")

# ============================================================================
# 📝 요청 스키마
# ============================================================================

class NodeCreateRequest(BaseModel):
    """노드 생성 요청"""
    id: Optional[str] = Field(default=None, description="노드 ID (자동 생성 가능)")
    flow_id: str = Field(..., description="플로우 ID")
    type: str = Field(default="default", description="노드 타입")
    position: NodePosition = Field(..., description="노드 위치")
    data: NodeData = Field(..., description="노드 데이터")
    width: Optional[float] = Field(default=None, ge=10, le=1000, description="노드 너비")
    height: Optional[float] = Field(default=None, ge=10, le=1000, description="노드 높이")
    draggable: bool = Field(default=True, description="드래그 가능 여부")
    selectable: bool = Field(default=True, description="선택 가능 여부")
    deletable: bool = Field(default=True, description="삭제 가능 여부")
    style: Optional[Dict[str, Any]] = Field(default_factory=dict, description="노드 스타일")
    
    @field_validator('type')
    @classmethod
    def validate_node_type(cls, v):
        allowed_types = ["default", "input", "output", "custom"]
        if v not in allowed_types:
            raise ValueError(f"노드 타입은 {allowed_types} 중 하나여야 합니다")
        return v

class NodeUpdateRequest(BaseModel):
    """노드 수정 요청"""
    position: Optional[NodePosition] = Field(default=None, description="노드 위치")
    data: Optional[NodeData] = Field(default=None, description="노드 데이터")
    width: Optional[float] = Field(default=None, ge=10, le=1000, description="노드 너비")
    height: Optional[float] = Field(default=None, ge=10, le=1000, description="노드 높이")
    draggable: Optional[bool] = Field(default=None, description="드래그 가능 여부")
    selectable: Optional[bool] = Field(default=None, description="선택 가능 여부")
    deletable: Optional[bool] = Field(default=None, description="삭제 가능 여부")
    style: Optional[Dict[str, Any]] = Field(default=None, description="노드 스타일")

class NodeBatchUpdateRequest(BaseModel):
    """노드 일괄 수정 요청"""
    nodes: List[Dict[str, Any]] = Field(..., description="수정할 노드 목록")

# ============================================================================
# 📤 응답 스키마
# ============================================================================

class NodeResponse(BaseModel):
    """노드 응답"""
    id: str
    flow_id: str
    node_type: str
    position_x: float
    position_y: float
    width: Optional[float] = None
    height: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
    style: Optional[Dict[str, Any]] = None
    hidden: bool = False
    selected: bool = False
    deletable: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "node_1",
                "flow_id": "flow_123",
                "node_type": "input",
                "position_x": 250.0,
                "position_y": 25.0,
                "width": 150.0,
                "height": 40.0,
                "data": {"label": "Input Node"},
                "style": {"background": "#fff", "border": "1px solid #333"},
                "hidden": False,
                "selected": False,
                "deletable": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

class NodeListResponse(BaseModel):
    """노드 목록 응답"""
    nodes: List[NodeResponse] = Field(..., description="노드 목록")
    total: int = Field(..., description="전체 노드 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {
                        "id": "node_1",
                        "flow_id": "flow_123",
                        "node_type": "input",
                        "position_x": 250.0,
                        "position_y": 25.0,
                        "data": {"label": "Input Node"},
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 10
            }
        }

# ============================================================================
# 🔍 검색 스키마
# ============================================================================

class NodeSearchRequest(BaseModel):
    """노드 검색 요청"""
    flow_id: Optional[str] = Field(default=None, description="플로우 ID")
    node_type: Optional[str] = Field(default=None, description="노드 타입")
    label: Optional[str] = Field(default=None, description="노드 레이블 (부분 일치)")
    
# ============================================================================
# 📊 통계 스키마
# ============================================================================

class NodeStatsResponse(BaseModel):
    """노드 통계 응답"""
    total_nodes: int = Field(..., description="전체 노드 수")
    nodes_by_type: Dict[str, int] = Field(..., description="타입별 노드 수")
    flows_with_nodes: int = Field(..., description="노드가 있는 플로우 수")
    average_nodes_per_flow: float = Field(..., description="플로우당 평균 노드 수")

# ============================================================================
# 🔄 변경사항 스키마
# ============================================================================

class NodeChangesRequest(BaseModel):
    """노드 변경사항 요청"""
    added: List[Dict[str, Any]] = Field(default_factory=list, description="추가된 노드들")
    updated: List[Dict[str, Any]] = Field(default_factory=list, description="수정된 노드들")
    removed: List[str] = Field(default_factory=list, description="삭제된 노드 ID들")

class NodeChangesResponse(BaseModel):
    """노드 변경사항 응답"""
    added_nodes: List[NodeResponse] = Field(..., description="추가된 노드들")
    updated_nodes: List[NodeResponse] = Field(..., description="수정된 노드들")
    removed_node_ids: List[str] = Field(..., description="삭제된 노드 ID들")
    message: str = Field(default="노드 변경사항이 성공적으로 처리되었습니다", description="처리 결과 메시지")
