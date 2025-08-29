# ============================================================================
# 🔄 ProcessChain Schema - 통합 공정 그룹 데이터 스키마
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
    chain_name: str = Field(..., description="그룹명")
    start_process_id: int = Field(..., description="시작 공정 ID")
    end_process_id: int = Field(..., description="종료 공정 ID")
    chain_length: int = Field(1, description="그룹 내 공정 개수")
    is_active: bool = Field(True, description="활성 상태")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chain_name": "압연1-용해 그룹",
                "start_process_id": 156,
                "end_process_id": 157,
                "chain_length": 2,
                "is_active": True
            }
        }

class ProcessChainCreate(ProcessChainBase):
    """통합 공정 그룹 생성 스키마"""
    pass

class ProcessChainUpdate(BaseModel):
    """통합 공정 그룹 수정 스키마"""
    chain_name: Optional[str] = None
    start_process_id: Optional[int] = None
    end_process_id: Optional[int] = None
    chain_length: Optional[int] = None
    is_active: Optional[bool] = None

class ProcessChainResponse(ProcessChainBase):
    """통합 공정 그룹 응답 스키마"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============================================================================
# 🔗 ProcessChainLink 스키마 (그룹 내 공정 연결)
# ============================================================================

class ProcessChainLinkBase(BaseModel):
    """통합 공정 그룹 링크 기본 스키마"""
    chain_id: int = Field(..., description="그룹 ID")
    process_id: int = Field(..., description="공정 ID")
    sequence_order: int = Field(..., description="그룹 내 순서")
    is_continue_edge: bool = Field(True, description="continue 엣지 여부")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chain_id": 1,
                "process_id": 156,
                "sequence_order": 1,
                "is_continue_edge": True
            }
        }

class ProcessChainLinkCreate(ProcessChainLinkBase):
    """통합 공정 그룹 링크 생성 스키마"""
    pass

class ProcessChainLinkUpdate(BaseModel):
    """통합 공정 그룹 링크 수정 스키마"""
    sequence_order: Optional[int] = None
    is_continue_edge: Optional[bool] = None

class ProcessChainLinkResponse(ProcessChainLinkBase):
    """통합 공정 그룹 링크 응답 스키마"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============================================================================
# 🔍 ProcessChain 분석 및 탐지 스키마
# ============================================================================

class ProcessChainAnalysisRequest(BaseModel):
    """통합 공정 그룹 분석 요청 스키마"""
    chain_id: int = Field(..., description="분석할 그룹 ID")
    include_emissions: bool = Field(True, description="배출량 포함 여부")
    include_process_details: bool = Field(False, description="공정 상세 정보 포함 여부")

class ProcessChainAnalysisResponse(BaseModel):
    """통합 공정 그룹 분석 응답 스키마"""
    chain_info: ProcessChainResponse
    processes: List[Dict[str, Any]]
    total_emission: Optional[float] = None
    analysis_summary: Dict[str, Any]

class ChainDetectionRequest(BaseModel):
    """통합 공정 그룹 탐지 요청 스키마"""
    max_chain_length: int = Field(10, description="최대 그룹 길이")
    include_inactive: bool = Field(False, description="비활성 공정 포함 여부")
    recalculate_existing: bool = Field(False, description="기존 그룹 재계산 여부")

class ChainDetectionResponse(BaseModel):
    """통합 공정 그룹 탐지 응답 스키마"""
    detected_chains: int = Field(..., description="탐지된 그룹 수")
    total_processes: int = Field(..., description="총 공정 수")
    detection_summary: Dict[str, Any]

class AutoDetectAndCalculateRequest(BaseModel):
    """자동 탐지 및 계산 요청 스키마"""
    max_chain_length: int = Field(10, description="최대 그룹 길이")
    include_inactive: bool = Field(False, description="비활성 공정 포함 여부")
    recalculate_existing: bool = Field(False, description="기존 그룹 재계산 여부")

class AutoDetectAndCalculateResponse(BaseModel):
    """자동 탐지 및 계산 응답 스키마"""
    detected_chains: int = Field(..., description="탐지된 그룹 수")
    total_integrated_emission: float = Field(..., description="총 통합 배출량")
    calculation_summary: Dict[str, Any]
