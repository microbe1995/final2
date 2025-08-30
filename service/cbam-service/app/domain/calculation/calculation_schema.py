# ============================================================================
# 📋 Calculation Schema - CBAM 계산 데이터 모델
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import date, datetime

if TYPE_CHECKING:
    from .calculation_schema import ProcessResponse, ProductResponse



# ============================================================================
# 🔗 ProductProcess 관련 스키마
# ============================================================================

class ProductProcessCreateRequest(BaseModel):
    """제품-공정 관계 생성 요청"""
    product_id: int = Field(..., description="제품 ID")
    process_id: int = Field(..., description="공정 ID")

class ProductProcessResponse(BaseModel):
    """제품-공정 관계 응답"""
    id: int = Field(..., description="관계 ID")
    product_id: int = Field(..., description="제품 ID")
    process_id: int = Field(..., description="공정 ID")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")



# ============================================================================
# 📊 ProcessAttrdirEmission 관련 스키마
# ============================================================================

class ProcessAttrdirEmissionCreateRequest(BaseModel):
    """공정별 직접귀속배출량 생성 요청"""
    process_id: int = Field(..., description="공정 ID")
    total_matdir_emission: float = Field(0.0, description="총 원료직접배출량")
    total_fueldir_emission: float = Field(0.0, description="총 연료직접배출량")
    attrdir_em: float = Field(0.0, description="직접귀속배출량")

class ProcessAttrdirEmissionResponse(BaseModel):
    """공정별 직접귀속배출량 응답"""
    id: int = Field(..., description="요약 ID")
    process_id: int = Field(..., description="공정 ID")
    total_matdir_emission: float = Field(..., description="총 원료직접배출량")
    total_fueldir_emission: float = Field(..., description="총 연료직접배출량")
    attrdir_em: float = Field(..., description="직접귀속배출량")
    calculation_date: Optional[datetime] = Field(None, description="계산 일시")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")

class ProcessAttrdirEmissionUpdateRequest(BaseModel):
    """공정별 직접귀속배출량 수정 요청"""
    total_matdir_emission: Optional[float] = Field(None, description="총 원료직접배출량")
    total_fueldir_emission: Optional[float] = Field(None, description="총 연료직접배출량")
    attrdir_em: Optional[float] = Field(None, description="직접귀속배출량")

# ============================================================================
# 🧮 배출량 계산 관련 스키마
# ============================================================================

class ProcessEmissionCalculationRequest(BaseModel):
    """공정별 배출량 계산 요청"""
    process_id: int = Field(..., description="공정 ID")

class ProcessEmissionCalculationResponse(BaseModel):
    """공정별 배출량 계산 응답"""
    process_id: int = Field(..., description="공정 ID")
    process_name: str = Field(..., description="공정명")
    total_matdir_emission: float = Field(..., description="총 원료직접배출량")
    total_fueldir_emission: float = Field(..., description="총 연료직접배출량")
    attrdir_em: float = Field(..., description="직접귀속배출량")
    calculation_formula: str = Field(..., description="계산 공식")
    calculation_date: datetime = Field(..., description="계산 일시")

class ProductEmissionCalculationRequest(BaseModel):
    """제품별 배출량 계산 요청"""
    product_id: int = Field(..., description="제품 ID")

class ProductEmissionCalculationResponse(BaseModel):
    """제품별 배출량 계산 응답"""
    product_id: int = Field(..., description="제품 ID")
    product_name: str = Field(..., description="제품명")
    total_emission: float = Field(..., description="총 배출량")
    process_emissions: List[ProcessEmissionCalculationResponse] = Field(..., description="공정별 배출량 목록")
    calculation_formula: str = Field(..., description="계산 공식")
    calculation_date: datetime = Field(..., description="계산 일시")

# ============================================================================
# 🔗 Edge 관련 스키마
# ============================================================================

class EdgeCreateRequest(BaseModel):
    """Edge 생성 요청 스키마"""
    source_id: int
    target_id: int
    edge_kind: str  # consume/produce/continue
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_id": 1,
                "target_id": 2,
                "edge_kind": "continue"
            }
        }

class EdgeResponse(BaseModel):
    """Edge 응답 스키마"""
    id: int
    source_id: int
    target_id: int
    edge_kind: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True