# ============================================================================
# 🔄 SourceStream Schema - 통합 공정 그룹 데이터 스키마
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# ============================================================================
# 🔄 ProcessChain 스키마 (통합 공정 그룹)
# ============================================================================

class ProcessChainBase(BaseModel):
    """통합 공정 그룹 기본 스키마"""
    chain_name: str = Field(..., description="그룹명 (예: '압연1-용해 그룹')")
    start_process_id: int = Field(..., description="시작 공정 ID")
    end_process_id: int = Field(..., description="종료 공정 ID")
    chain_length: int = Field(default=1, description="그룹 내 공정 개수")
    is_active: bool = Field(default=True, description="활성 상태")

class ProcessChainCreate(ProcessChainBase):
    """통합 공정 그룹 생성 스키마"""
    pass

class ProcessChainUpdate(BaseModel):
    """통합 공정 그룹 수정 스키마"""
    chain_name: Optional[str] = Field(None, description="그룹명")
    start_process_id: Optional[int] = Field(None, description="시작 공정 ID")
    end_process_id: Optional[int] = Field(None, description="종료 공정 ID")
    chain_length: Optional[int] = Field(None, description="그룹 내 공정 개수")
    is_active: Optional[bool] = Field(None, description="활성 상태")

class ProcessChainResponse(ProcessChainBase):
    """통합 공정 그룹 응답 스키마"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============================================================================
# 🔗 ProcessChainLink 스키마 (그룹 내 공정 멤버)
# ============================================================================

class ProcessChainLinkBase(BaseModel):
    """통합 공정 그룹 링크 기본 스키마"""
    chain_id: int = Field(..., description="그룹 ID")
    process_id: int = Field(..., description="공정 ID")
    sequence_order: int = Field(..., description="그룹 내 순서")
    is_continue_edge: bool = Field(default=True, description="continue 엣지 여부")

class ProcessChainLinkCreate(ProcessChainLinkBase):
    """통합 공정 그룹 링크 생성 스키마"""
    pass

class ProcessChainLinkUpdate(BaseModel):
    """통합 공정 그룹 링크 수정 스키마"""
    chain_id: Optional[int] = Field(None, description="그룹 ID")
    process_id: Optional[int] = Field(None, description="공정 ID")
    sequence_order: Optional[int] = Field(None, description="그룹 내 순서")
    is_continue_edge: Optional[bool] = Field(None, description="continue 엣지 여부")

class ProcessChainLinkResponse(ProcessChainLinkBase):
    """통합 공정 그룹 링크 응답 스키마"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============================================================================
# 📊 IntegratedProcessGroupEmission 스키마 (통합 그룹 배출량)
# ============================================================================

class IntegratedProcessGroupEmissionBase(BaseModel):
    """통합 공정 그룹 배출량 기본 스키마 (누적이 아님!)"""
    chain_id: int = Field(..., description="그룹 ID")
    process_id: int = Field(..., description="공정 ID")
    integrated_matdir_emission: Decimal = Field(default=0, description="그룹의 총 원료배출량")
    integrated_fueldir_emission: Decimal = Field(default=0, description="그룹의 총 연료배출량")
    integrated_attrdir_em: Decimal = Field(default=0, description="그룹의 총 직접귀속배출량")
    group_processes: Optional[str] = Field(None, description="그룹에 속한 공정들 (JSON)")

class IntegratedProcessGroupEmissionCreate(IntegratedProcessGroupEmissionBase):
    """통합 공정 그룹 배출량 생성 스키마"""
    pass

class IntegratedProcessGroupEmissionUpdate(BaseModel):
    """통합 공정 그룹 배출량 수정 스키마"""
    chain_id: Optional[int] = Field(None, description="그룹 ID")
    process_id: Optional[int] = Field(None, description="공정 ID")
    integrated_matdir_emission: Optional[Decimal] = Field(None, description="그룹의 총 원료배출량")
    integrated_fueldir_emission: Optional[Decimal] = Field(None, description="그룹의 총 연료배출량")
    integrated_attrdir_em: Optional[Decimal] = Field(None, description="그룹의 총 직접귀속배출량")
    group_processes: Optional[str] = Field(None, description="그룹에 속한 공정들 (JSON)")

class IntegratedProcessGroupEmissionResponse(IntegratedProcessGroupEmissionBase):
    """통합 공정 그룹 배출량 응답 스키마"""
    id: int
    calculation_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============================================================================
# 🔄 SourceStream 스키마
# ============================================================================

class SourceStreamBase(BaseModel):
    """소스 스트림 기본 스키마"""
    source_process_id: int = Field(..., description="소스 공정 ID")
    target_process_id: int = Field(..., description="타겟 공정 ID")
    stream_type: str = Field(..., description="스트림 타입 (material, energy, waste)")
    stream_name: str = Field(..., description="스트림명")
    stream_amount: Decimal = Field(default=0, description="스트림량")
    unit: str = Field(..., description="단위")
    emission_factor: Decimal = Field(default=0, description="배출계수")
    calculated_emission: Decimal = Field(default=0, description="계산된 배출량")
    is_continue_stream: bool = Field(default=True, description="continue 스트림 여부")

class SourceStreamCreate(SourceStreamBase):
    """소스 스트림 생성 스키마"""
    pass

class SourceStreamUpdate(BaseModel):
    """소스 스트림 수정 스키마"""
    source_process_id: Optional[int] = Field(None, description="소스 공정 ID")
    target_process_id: Optional[int] = Field(None, description="타겟 공정 ID")
    stream_type: Optional[str] = Field(None, description="스트림 타입")
    stream_name: Optional[str] = Field(None, description="스트림명")
    stream_amount: Optional[Decimal] = Field(None, description="스트림량")
    unit: Optional[str] = Field(None, description="단위")
    emission_factor: Optional[Decimal] = Field(None, description="배출계수")
    calculated_emission: Optional[Decimal] = Field(None, description="계산된 배출량")
    is_continue_stream: Optional[bool] = Field(None, description="continue 스트림 여부")

class SourceStreamResponse(SourceStreamBase):
    """소스 스트림 응답 스키마"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============================================================================
# 🔄 통합 공정 그룹 관련 요청/응답 스키마
# ============================================================================

class ProcessChainWithLinksResponse(ProcessChainResponse):
    """통합 공정 그룹과 링크를 포함한 응답 스키마"""
    chain_links: List[ProcessChainLinkResponse] = []

class ProcessChainAnalysisRequest(BaseModel):
    """통합 공정 그룹 분석 요청 스키마"""
    start_process_id: int = Field(..., description="시작 공정 ID")
    end_process_id: int = Field(..., description="종료 공정 ID")
    include_integrated: bool = Field(default=True, description="통합 배출량 포함 여부")

class ProcessChainAnalysisResponse(BaseModel):
    """통합 공정 그룹 분석 응답 스키마"""
    chain: ProcessChainWithLinksResponse
    integrated_emissions: List[IntegratedProcessGroupEmissionResponse] = []
    total_integrated_emission: Decimal = Field(default=0, description="그룹의 총 배출량")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# 🔄 통합 공정 그룹 배출량 계산 관련 스키마
# ============================================================================

class IntegratedEmissionCalculationRequest(BaseModel):
    """통합 공정 그룹 배출량 계산 요청 스키마"""
    chain_id: int = Field(..., description="그룹 ID")
    recalculate_all: bool = Field(default=False, description="전체 재계산 여부")

class IntegratedEmissionCalculationResponse(BaseModel):
    """통합 공정 그룹 배출량 계산 응답 스키마"""
    chain_id: int
    calculated_processes: int = Field(description="계산된 공정 수")
    total_integrated_emission: Decimal = Field(description="그룹의 총 배출량")
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(description="계산 상태")

# ============================================================================
# 🔄 통합 공정 그룹 자동 탐지 관련 스키마
# ============================================================================

class ChainDetectionRequest(BaseModel):
    """통합 공정 그룹 자동 탐지 요청 스키마"""
    start_process_id: Optional[int] = Field(None, description="시작 공정 ID (선택사항)")
    max_chain_length: int = Field(default=10, description="최대 그룹 길이")
    include_inactive: bool = Field(default=False, description="비활성 그룹 포함 여부")

class ChainDetectionResponse(BaseModel):
    """통합 공정 그룹 자동 탐지 응답 스키마"""
    detected_chains: List[ProcessChainResponse] = []
    total_chains: int = Field(description="탐지된 총 그룹 수")
    detection_date: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# 🔄 통합 공정 그룹 자동 탐지 및 계산 스키마
# ============================================================================

class AutoDetectAndCalculateRequest(BaseModel):
    """통합 공정 그룹 자동 탐지 및 계산 요청 스키마"""
    max_chain_length: int = Field(default=10, description="최대 그룹 길이")
    include_inactive: bool = Field(default=False, description="비활성 그룹 포함 여부")
    recalculate_existing: bool = Field(default=False, description="기존 그룹 재계산 여부")

class AutoDetectAndCalculateResponse(BaseModel):
    """통합 공정 그룹 자동 탐지 및 계산 응답 스키마"""
    detected_chains: int = Field(description="탐지된 그룹 수")
    total_calculated_processes: int = Field(description="계산된 총 공정 수")
    total_integrated_emission: Decimal = Field(description="총 통합 배출량")
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(description="처리 상태")
