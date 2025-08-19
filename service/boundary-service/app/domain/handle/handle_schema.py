# ============================================================================
# 🔘 Handle Schema - ReactFlow 핸들 API 스키마
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

# ============================================================================
# 🎯 핸들 타입 및 위치 열거형
# ============================================================================

class HandleType(str, Enum):
    """핸들 타입"""
    SOURCE = "source"
    TARGET = "target"
    DEFAULT = "default"

class HandlePosition(str, Enum):
    """핸들 위치"""
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

# ============================================================================
# 📝 핸들 요청/응답 스키마
# ============================================================================

class HandleCreateRequest(BaseModel):
    """핸들 생성 요청"""
    
    node_id: str = Field(..., description="노드 ID")
    flow_id: str = Field(..., description="플로우 ID")
    type: HandleType = Field(HandleType.DEFAULT, description="핸들 타입")
    position: HandlePosition = Field(HandlePosition.LEFT, description="핸들 위치")
    
    # 선택적 필드
    style: Optional[Dict[str, Any]] = Field(None, description="핸들 스타일")
    data: Optional[Dict[str, Any]] = Field(None, description="핸들 데이터")
    is_connectable: Optional[bool] = Field(True, description="연결 가능 여부")
    is_valid_connection: Optional[bool] = Field(True, description="유효한 연결 여부")
    
    @validator('node_id', 'flow_id')
    def validate_ids(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("ID는 비어있을 수 없습니다")
        return v.strip()

class HandleUpdateRequest(BaseModel):
    """핸들 수정 요청"""
    
    type: Optional[HandleType] = Field(None, description="핸들 타입")
    position: Optional[HandlePosition] = Field(None, description="핸들 위치")
    style: Optional[Dict[str, Any]] = Field(None, description="핸들 스타일")
    data: Optional[Dict[str, Any]] = Field(None, description="핸들 데이터")
    is_connectable: Optional[bool] = Field(None, description="연결 가능 여부")
    is_valid_connection: Optional[bool] = Field(None, description="유효한 연결 여부")

class HandleResponse(BaseModel):
    """핸들 응답"""
    
    id: str
    node_id: str
    flow_id: str
    type: HandleType
    position: HandlePosition
    style: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]
    is_connectable: bool
    is_valid_connection: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True

# ============================================================================
# 📋 핸들 목록 및 통계 스키마
# ============================================================================

class HandleListResponse(BaseModel):
    """핸들 목록 응답"""
    
    handles: List[HandleResponse]
    total: int
    page: Optional[int] = None
    size: Optional[int] = None

class HandleStatsResponse(BaseModel):
    """핸들 통계 응답"""
    
    total_handles: int
    source_handles: int
    target_handles: int
    left_handles: int
    right_handles: int
    top_handles: int
    bottom_handles: int
    connectable_handles: int
    valid_connection_handles: int

# ============================================================================
# 🔗 핸들 연결 관련 스키마
# ============================================================================

class HandleConnectionRequest(BaseModel):
    """핸들 연결 요청"""
    
    source_handle_id: str = Field(..., description="시작 핸들 ID")
    target_handle_id: str = Field(..., description="끝 핸들 ID")
    flow_id: str = Field(..., description="플로우 ID")
    
    @validator('source_handle_id', 'target_handle_id', 'flow_id')
    def validate_ids(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("ID는 비어있을 수 없습니다")
        return v.strip()

class HandleConnectionResponse(BaseModel):
    """핸들 연결 응답"""
    
    success: bool
    message: str
    connection_id: Optional[str] = None
    error_details: Optional[str] = None

# ============================================================================
# 🎯 ReactFlow 전용 핸들 스키마
# ============================================================================

class ReactFlowHandleResponse(BaseModel):
    """ReactFlow 핸들 응답 (프론트엔드 호환)"""
    
    id: str
    type: HandleType
    position: HandlePosition
    style: Optional[Dict[str, Any]]
    data: Optional[Dict[str, Any]]
    is_connectable: bool
    is_valid_connection: bool
    
    class Config:
        from_attributes = True
