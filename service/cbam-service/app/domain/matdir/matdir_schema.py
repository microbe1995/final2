from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# ============================================================================
# 📝 기존 MatDir 스키마
# ============================================================================

class MatDirCreateRequest(BaseModel):
    process_id: int = Field(..., description="공정 ID")
    mat_name: str = Field(..., description="투입된 원료명")
    mat_factor: Decimal = Field(..., description="배출계수")
    mat_amount: Decimal = Field(..., description="투입된 원료량")
    oxyfactor: Optional[Decimal] = Field(default=Decimal('1.0000'), description="산화계수 (기본값: 1)")

class MatDirUpdateRequest(BaseModel):
    mat_name: Optional[str] = Field(None, description="투입된 원료명")
    mat_factor: Optional[Decimal] = Field(None, description="배출계수")
    mat_amount: Optional[Decimal] = Field(None, description="투입된 원료량")
    oxyfactor: Optional[Decimal] = Field(None, description="산화계수")

class MatDirResponse(BaseModel):
    id: int
    process_id: int
    mat_name: str
    mat_factor: float
    mat_amount: float
    oxyfactor: float
    matdir_em: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MatDirCalculationRequest(BaseModel):
    mat_amount: Decimal = Field(..., description="투입된 원료량")
    mat_factor: Decimal = Field(..., description="배출계수")
    oxyfactor: Decimal = Field(default=Decimal('1.0000'), description="산화계수")

class MatDirCalculationResponse(BaseModel):
    matdir_em: float = Field(..., description="원료직접배출량")
    calculation_formula: str = Field(..., description="계산 공식")

# ============================================================================
# 🏗️ Material Master 스키마 (새로 추가)
# ============================================================================

class MaterialMasterSearchRequest(BaseModel):
    """원료 마스터 검색 요청"""
    mat_name: str = Field(..., description="원료명 (부분 검색 가능)")

class MaterialMasterResponse(BaseModel):
    """원료 마스터 데이터 응답"""
    id: int = Field(..., description="원료 마스터 ID")
    mat_name: str = Field(..., description="원료명")
    mat_engname: str = Field(..., description="원료 영문명")
    carbon_content: Optional[float] = Field(None, description="탄소 함량")
    mat_factor: float = Field(..., description="원료 배출계수")

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class MaterialMasterListResponse(BaseModel):
    """원료 마스터 목록 응답"""
    materials: List[MaterialMasterResponse] = Field(..., description="원료 마스터 목록")
    total_count: int = Field(..., description="총 원료 수")

class MaterialMasterFactorResponse(BaseModel):
    """원료 배출계수 조회 응답"""
    mat_name: str = Field(..., description="원료명")
    mat_factor: Optional[float] = Field(None, description="배출계수")
    carbon_content: Optional[float] = Field(None, description="탄소 함량")
    found: bool = Field(..., description="조회 성공 여부")
