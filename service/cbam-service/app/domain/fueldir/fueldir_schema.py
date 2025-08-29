from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# ============================================================================
# 📝 기존 FuelDir 스키마
# ============================================================================

class FuelDirCreateRequest(BaseModel):
    """연료직접배출량 생성 요청"""
    process_id: int = Field(..., description="공정 ID")
    fuel_name: str = Field(..., min_length=1, max_length=255, description="투입된 연료명")
    fuel_factor: Decimal = Field(..., ge=0, description="배출계수")
    fuel_amount: Decimal = Field(..., ge=0, description="투입된 연료량")
    fuel_oxyfactor: Optional[Decimal] = Field(default=1.0000, ge=0, description="산화계수 (기본값: 1.0000)")

    @validator('fuel_factor', 'fuel_amount', 'fuel_oxyfactor', pre=True)
    def validate_decimal(cls, v):
        if isinstance(v, str):
            return Decimal(v)
        return v

class FuelDirUpdateRequest(BaseModel):
    """연료직접배출량 수정 요청"""
    fuel_name: Optional[str] = Field(None, min_length=1, max_length=255, description="투입된 연료명")
    fuel_factor: Optional[Decimal] = Field(None, ge=0, description="배출계수")
    fuel_amount: Optional[Decimal] = Field(None, ge=0, description="투입된 연료량")
    fuel_oxyfactor: Optional[Decimal] = Field(None, ge=0, description="산화계수")

    @validator('fuel_factor', 'fuel_amount', 'fuel_oxyfactor', pre=True)
    def validate_decimal(cls, v):
        if v is not None and isinstance(v, str):
            return Decimal(v)
        return v

class FuelDirCalculationRequest(BaseModel):
    """연료직접배출량 계산 요청"""
    fuel_amount: Decimal = Field(..., ge=0, description="투입된 연료량")
    fuel_factor: Decimal = Field(..., ge=0, description="배출계수")
    fuel_oxyfactor: Optional[Decimal] = Field(default=1.0000, ge=0, description="산화계수 (기본값: 1.0000)")

    @validator('fuel_amount', 'fuel_factor', 'fuel_oxyfactor', pre=True)
    def validate_decimal(cls, v):
        if isinstance(v, str):
            return Decimal(v)
        return v

# ============================================================================
# 📤 기존 응답 스키마
# ============================================================================

class FuelDirResponse(BaseModel):
    """연료직접배출량 응답"""
    id: int
    process_id: int
    fuel_name: str
    fuel_factor: Decimal
    fuel_amount: Decimal
    fuel_oxyfactor: Decimal
    fueldir_em: Optional[Decimal]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat() if v else None
        }

class FuelDirCalculationResponse(BaseModel):
    """연료직접배출량 계산 응답"""
    fuel_amount: Decimal
    fuel_factor: Decimal
    fuel_oxyfactor: Decimal
    fueldir_em: Decimal
    calculation_formula: str

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }

# ============================================================================
# 📊 기존 통계 및 요약 스키마
# ============================================================================

class FuelDirSummaryResponse(BaseModel):
    """연료직접배출량 요약 응답"""
    total_count: int
    total_emission: Decimal
    average_emission: Decimal
    process_count: int

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class FuelDirProcessTotalResponse(BaseModel):
    """공정별 총 연료직접배출량 응답"""
    process_id: int
    total_fueldir_emission: Decimal
    fuel_count: int

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }

# ============================================================================
# 🏗️ Fuel Master 스키마 (새로 추가)
# ============================================================================

class FuelMasterSearchRequest(BaseModel):
    """연료 마스터 검색 요청"""
    fuel_name: str = Field(..., description="연료명 (부분 검색 가능)")

class FuelMasterResponse(BaseModel):
    """연료 마스터 데이터 응답"""
    id: int = Field(..., description="연료 마스터 ID")
    fuel_name: str = Field(..., description="연료명")
    fuel_engname: str = Field(..., description="연료 영문명")
    fuel_factor: float = Field(..., description="연료 배출계수")
    net_calory: Optional[float] = Field(None, description="순발열량")

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class FuelMasterListResponse(BaseModel):
    """연료 마스터 목록 응답"""
    fuels: List[FuelMasterResponse] = Field(..., description="연료 마스터 목록")
    total_count: int = Field(..., description="총 연료 수")

class FuelMasterFactorResponse(BaseModel):
    """연료 배출계수 조회 응답"""
    fuel_name: str = Field(..., description="연료명")
    fuel_factor: float = Field(..., description="배출계수")
    net_calory: Optional[float] = Field(None, description="순발열량")
    found: bool = Field(..., description="조회 성공 여부")
