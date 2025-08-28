from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

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
