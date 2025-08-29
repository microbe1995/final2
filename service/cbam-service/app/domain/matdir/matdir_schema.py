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
# 🔍 원료-배출계수 매핑 관련 스키마 (@mapping/ 패턴과 동일)
# ============================================================================

class MaterialMappingResponse(BaseModel):
    """원료-배출계수 매핑 응답 (@mapping/의 HSCNMappingResponse와 동일 패턴)"""
    mat_name: str = Field(..., description="원료명")
    mat_factor: float = Field(..., description="배출계수")
    carbon_content: Optional[float] = Field(None, description="탄소 함량")
    mat_engname: Optional[str] = Field(None, description="원료 영문명")

class MaterialMappingCreateRequest(BaseModel):
    """원료-배출계수 매핑 생성 요청"""
    mat_name: str = Field(..., description="원료명", min_length=1)
    mat_factor: float = Field(..., description="배출계수", gt=0)
    carbon_content: Optional[float] = Field(None, description="탄소 함량")
    mat_engname: Optional[str] = Field(None, description="원료 영문명")

class MaterialMappingUpdateRequest(BaseModel):
    """원료-배출계수 매핑 수정 요청"""
    mat_name: Optional[str] = Field(None, description="원료명", min_length=1)
    mat_factor: Optional[float] = Field(None, description="배출계수", gt=0)
    carbon_content: Optional[float] = Field(None, description="탄소 함량")
    mat_engname: Optional[str] = Field(None, description="원료 영문명")

class MaterialMappingFullResponse(BaseModel):
    """원료-배출계수 매핑 전체 응답 (ID 포함)"""
    id: int = Field(..., description="매핑 ID")
    mat_name: str = Field(..., description="원료명")
    mat_factor: float = Field(..., description="배출계수")
    carbon_content: Optional[float] = Field(None, description="탄소 함량")
    mat_engname: Optional[str] = Field(None, description="원료 영문명")

# ============================================================================
# 🔍 원료명 조회 관련 스키마 (@mapping/ 패턴과 동일)
# ============================================================================

class MaterialNameLookupRequest(BaseModel):
    """원료명 조회 요청 (@mapping/의 HSCodeLookupRequest와 동일 패턴)"""
    mat_name: str = Field(..., description="원료명 (부분 검색 가능)", min_length=1)

class MaterialNameLookupResponse(BaseModel):
    """원료명 조회 응답 (@mapping/의 HSCodeLookupResponse와 동일 패턴)"""
    success: bool = Field(..., description="조회 성공 여부")
    data: List[MaterialMappingResponse] = Field(..., description="매핑 결과 목록")
    count: int = Field(..., description="조회된 결과 수")
    message: Optional[str] = Field(None, description="응답 메시지")


