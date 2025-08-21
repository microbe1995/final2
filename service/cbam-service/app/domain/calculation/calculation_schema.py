# ============================================================================
# 🧮 Calculation Schema - CBAM 계산 데이터 검증 및 직렬화
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

# ============================================================================
# 🔥 연료 계산 스키마
# ============================================================================

class FuelCalculationRequest(BaseModel):
    """연료 계산 요청"""
    fuel_name: str = Field(..., description="연료명")
    fuel_amount: float = Field(..., gt=0, description="연료량 (톤)")
    
    @validator('fuel_name')
    def validate_fuel_name(cls, v):
        if not v or not v.strip():
            raise ValueError("연료명은 필수입니다")
        return v.strip()

class FuelCalculationResponse(BaseModel):
    """연료 계산 응답"""
    emission: float = Field(..., description="계산된 배출량 (tCO2)")
    fuel_name: str = Field(..., description="연료명")
    emission_factor: float = Field(..., description="배출계수 (tCO2/TJ)")
    net_calorific_value: float = Field(..., description="순발열량 (TJ/Gg)")
    calculation_formula: str = Field(default="연료량(톤) × 순발열량(TJ/Gg) × 배출계수(tCO2/TJ) × 1e-3")

# ============================================================================
# 🧱 원료 계산 스키마
# ============================================================================

class MaterialCalculationRequest(BaseModel):
    """원료 계산 요청"""
    material_name: str = Field(..., description="원료명")
    material_amount: float = Field(..., gt=0, description="원료량 (톤)")
    
    @validator('material_name')
    def validate_material_name(cls, v):
        if not v or not v.strip():
            raise ValueError("원료명은 필수입니다")
        return v.strip()

class MaterialCalculationResponse(BaseModel):
    """원료 계산 응답"""
    emission: float = Field(..., description="계산된 배출량 (tCO2)")
    material_name: str = Field(..., description="원료명")
    direct_factor: float = Field(..., description="직접배출계수")
    calculation_formula: str = Field(default="원료량(톤) × 직접배출계수")

# ============================================================================
# 🔗 전구물질 스키마
# ============================================================================

class PrecursorData(BaseModel):
    """전구물질 데이터"""
    id: Optional[int] = None
    user_id: str = Field(..., description="사용자 ID")
    name: str = Field(..., description="전구물질명")
    name_en: Optional[str] = Field(default="", description="전구물질명(영문)")
    cn_code: Optional[str] = Field(default="", description="CN코드")
    cn_code1: Optional[str] = Field(default="", description="CN코드1")
    cn_code2: Optional[str] = Field(default="", description="CN코드2")
    production_routes: Optional[List[str]] = Field(default=[], description="생산경로")
    final_country_code: Optional[str] = Field(default="", description="최종국가코드")
    created_at: Optional[datetime] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("전구물질명은 필수입니다")
        return v.strip()
    
    class Config:
        from_attributes = True

class PrecursorListRequest(BaseModel):
    """전구물질 목록 요청"""
    precursors: List[PrecursorData] = Field(..., description="전구물질 목록")

class PrecursorResponse(BaseModel):
    """전구물질 응답"""
    id: int
    user_id: str
    name: str
    name_en: str
    cn_code: str
    cn_code1: str
    cn_code2: str
    production_routes: List[str]
    final_country_code: str
    created_at: str
    
    class Config:
        from_attributes = True

class PrecursorListResponse(BaseModel):
    """전구물질 목록 응답"""
    precursors: List[PrecursorResponse]
    total: int = Field(..., description="전체 개수")

class PrecursorSaveResponse(BaseModel):
    """전구물질 저장 응답"""
    inserted_count: int = Field(..., description="저장된 전구물질 개수")
    success: bool = Field(default=True)
    message: str = Field(default="전구물질이 성공적으로 저장되었습니다")

# ============================================================================
# 🎯 CBAM 종합 계산 스키마
# ============================================================================

class CBAmCalculationRequest(BaseModel):
    """CBAM 종합 계산 요청"""
    product_name: str = Field(..., description="제품명")
    product_type: str = Field(..., description="제품 타입")
    user_id: str = Field(..., description="사용자 ID")
    fuels: List[Dict[str, Any]] = Field(default=[], description="연료 목록")
    materials: List[Dict[str, Any]] = Field(default=[], description="원료 목록")
    electricity: Optional[Dict[str, Any]] = Field(default=None, description="전력 정보")
    precursors: List[Dict[str, Any]] = Field(default=[], description="전구물질 목록")

class CBAMCalculationResponse(BaseModel):
    """CBAM 종합 계산 응답"""
    product_name: str
    product_type: str
    user_id: str
    total_direct_emission: float = Field(..., description="총 직접 배출량")
    total_indirect_emission: float = Field(..., description="총 간접 배출량")
    total_precursor_emission: float = Field(..., description="총 전구물질 배출량")
    total_emission: float = Field(..., description="총 배출량")
    fuel_emissions: List[Dict[str, Any]] = Field(default=[], description="연료별 배출량")
    material_emissions: List[Dict[str, Any]] = Field(default=[], description="원료별 배출량")
    electricity_emission: Optional[Dict[str, Any]] = Field(default=None, description="전력 배출량")
    precursor_emissions: List[Dict[str, Any]] = Field(default=[], description="전구물질별 배출량")
    calculation_date: str = Field(..., description="계산 일시")
    calculation_formula: str = Field(default="직접배출량 + 간접배출량 + 전구물질배출량")

# ============================================================================
# 📊 통계 스키마
# ============================================================================

class CalculationStatsResponse(BaseModel):
    """계산 통계 응답"""
    total_calculations: int = Field(..., description="전체 계산 수")
    fuel_calculations: int = Field(..., description="연료 계산 수")
    material_calculations: int = Field(..., description="원료 계산 수")
    total_precursors: int = Field(..., description="전체 전구물질 수")
    active_users: int = Field(..., description="활성 사용자 수")
    calculations_by_type: Dict[str, int] = Field(..., description="타입별 계산 수")
    last_updated: str = Field(..., description="마지막 업데이트 시간")