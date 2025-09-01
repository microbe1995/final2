# ============================================================================
# 📋 Edge Schema - 엣지 API 스키마
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EdgeCreateRequest(BaseModel):
    """엣지 생성 요청"""
    source_node_type: str = Field(..., description="소스 노드 타입")
    source_id: int = Field(..., description="소스 노드 ID")
    target_node_type: str = Field(..., description="타겟 노드 타입")
    
    target_id: int = Field(..., description="타겟 노드 ID")
    edge_kind: str = Field(..., description="엣지 종류 (consume/produce/continue)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_node_type": "process",
                "source_id": 1,
                "target_node_type": "product",
                "target_id": 2,
                "edge_kind": "continue"
            }
        }

class EdgeResponse(BaseModel):
    """엣지 응답"""
    id: int = Field(..., description="엣지 ID")
    source_node_type: str = Field(..., description="소스 노드 타입")
    source_id: int = Field(..., description="소스 노드 ID")
    target_node_type: str = Field(..., description="타겟 노드 타입")
    target_id: int = Field(..., description="타겟 노드 ID")
    edge_kind: str = Field(..., description="엣지 종류")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")
    
    class Config:
        from_attributes = True

class EdgeUpdateRequest(BaseModel):
    """엣지 수정 요청"""
    source_node_type: Optional[str] = Field(None, description="소스 노드 타입")
    source_id: Optional[int] = Field(None, description="소스 노드 ID")
    target_node_type: Optional[str] = Field(None, description="타겟 노드 타입")
    target_id: Optional[int] = Field(None, description="타겟 노드 ID")
    edge_kind: Optional[str] = Field(None, description="엣지 종류")
