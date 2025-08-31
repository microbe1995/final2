# 🔄 Process Schema - 공정 API 스키마
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Dict, Any

class ProcessCreateRequest(BaseModel):
    """프로세스 생성 요청"""
    process_name: str = Field(..., description="공정명")
    start_period: Optional[date] = Field(None, description="시작일")
    end_period: Optional[date] = Field(None, description="종료일")
    product_ids: Optional[List[int]] = Field([], description="연결할 제품 ID 목록 (다대다 관계)")

class ProcessResponse(BaseModel):
    """프로세스 응답"""
    id: int = Field(..., description="공정 ID")
    process_name: str = Field(..., description="공정명")
    start_period: Optional[date] = Field(None, description="시작일")
    end_period: Optional[date] = Field(None, description="종료일")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")
    # 다대다 관계를 위한 제품 정보 (순환 참조 방지를 위해 Dict 사용)
    products: Optional[List[Dict[str, Any]]] = Field(None, description="연결된 제품들")

class ProcessUpdateRequest(BaseModel):
    """프로세스 수정 요청"""
    process_name: Optional[str] = Field(None, description="공정명")
    start_period: Optional[date] = Field(None, description="시작일")
    end_period: Optional[date] = Field(None, description="종료일")
    
    class Config:
        from_attributes = True
