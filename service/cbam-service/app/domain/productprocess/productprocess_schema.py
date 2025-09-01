# ============================================================================
# 🔗 ProductProcess Schema - 제품-공정 관계 스키마
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ============================================================================
# 🔗 ProductProcess 관련 스키마
# ============================================================================

class ProductProcessCreateRequest(BaseModel):
    """제품-공정 관계 생성 요청"""
    product_id: int = Field(..., description="제품 ID")
    process_id: int = Field(..., description="공정 ID")
    consumption_amount: Optional[float] = Field(0.0, description="제품 소비량")

class ProductProcessResponse(BaseModel):
    """제품-공정 관계 응답"""
    id: int = Field(..., description="관계 ID")
    product_id: int = Field(..., description="제품 ID")
    process_id: int = Field(..., description="공정 ID")
    consumption_amount: Optional[float] = Field(0.0, description="제품 소비량")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")
    
    class Config:
        from_attributes = True

class ProductProcessUpdateRequest(BaseModel):
    """제품-공정 관계 수정 요청"""
    product_id: Optional[int] = Field(None, description="제품 ID")
    process_id: Optional[int] = Field(None, description="공정 ID")
    consumption_amount: Optional[float] = Field(None, description="제품 소비량")

class ProductProcessSearchRequest(BaseModel):
    """제품-공정 관계 검색 요청"""
    product_id: Optional[int] = Field(None, description="제품 ID로 검색")
    process_id: Optional[int] = Field(None, description="공정 ID로 검색")
    skip: int = Field(0, ge=0, description="건너뛸 레코드 수")
    limit: int = Field(100, ge=1, le=1000, description="조회할 레코드 수")

class ProductProcessFullResponse(ProductProcessResponse):
    """제품-공정 관계 전체 응답 (관계 정보 포함)"""
    product_name: Optional[str] = Field(None, description="제품명")
    process_name: Optional[str] = Field(None, description="공정명")

class ProductProcessByProductResponse(BaseModel):
    """제품별 제품-공정 관계 응답"""
    product_id: int
    product_name: str
    processes: List[ProductProcessFullResponse]

class ProductProcessByProcessResponse(BaseModel):
    """공정별 제품-공정 관계 응답"""
    process_id: int
    process_name: str
    products: List[ProductProcessFullResponse]

class ProductProcessStatsResponse(BaseModel):
    """제품-공정 관계 통계 응답"""
    total_relations: int = Field(..., description="전체 관계 수")
    total_products: int = Field(..., description="관련 제품 수")
    total_processes: int = Field(..., description="관련 공정 수")
