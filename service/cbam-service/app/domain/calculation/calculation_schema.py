# ============================================================================
# 📋 Calculation Schema - CBAM 계산 데이터 모델
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import date, datetime

if TYPE_CHECKING:
    from app.domain.calculation.calculation_schema import ProcessResponse, ProductResponse


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
# 🔄 공정 간 값 전파 관련 스키마
# ============================================================================

class EmissionPropagationRequest(BaseModel):
    """배출량 전파 계산 요청"""
    source_process_id: int = Field(..., description="소스 공정 ID")
    target_process_id: int = Field(..., description="타겟 공정 ID")
    edge_kind: str = Field(..., description="엣지 종류 (continue/produce/consume)")
    propagation_amount: Optional[float] = Field(None, description="전파할 배출량 (자동 계산 시 None)")

class EmissionPropagationResponse(BaseModel):
    """배출량 전파 계산 응답"""
    source_process_id: int = Field(..., description="소스 공정 ID")
    target_process_id: int = Field(..., description="타겟 공정 ID")
    edge_kind: str = Field(..., description="엣지 종류")
    source_original_emission: float = Field(..., description="소스 공정 원본 배출량")
    target_original_emission: float = Field(..., description="타겟 공정 원본 배출량")
    propagated_amount: float = Field(..., description="전파된 배출량")
    target_new_emission: float = Field(..., description="타겟 공정 새로운 배출량")
    propagation_formula: str = Field(..., description="전파 계산 공식")
    calculation_date: datetime = Field(..., description="계산 일시")

class GraphRecalculationRequest(BaseModel):
    """전체 그래프 재계산 요청"""
    trigger_edge_id: Optional[int] = Field(None, description="트리거한 엣지 ID")
    recalculate_all: bool = Field(True, description="전체 재계산 여부")
    include_validation: bool = Field(True, description="순환 참조 검증 포함 여부")

class GraphRecalculationResponse(BaseModel):
    """전체 그래프 재계산 응답"""
    total_processes_calculated: int = Field(..., description="계산된 총 공정 수")
    total_emission_propagated: float = Field(..., description="전파된 총 배출량")
    propagation_chains: List[EmissionPropagationResponse] = Field(..., description="전파 체인 목록")
    validation_errors: List[str] = Field(..., description="검증 오류 목록")
    calculation_date: datetime = Field(..., description="계산 일시")
    status: str = Field(..., description="계산 상태")

class CircularReferenceError(BaseModel):
    """순환 참조 오류"""
    error_type: str = Field(..., description="오류 유형")
    error_message: str = Field(..., description="오류 메시지")
    affected_processes: List[int] = Field(..., description="영향받는 공정 ID 목록")
    cycle_path: List[int] = Field(..., description="순환 경로")

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

