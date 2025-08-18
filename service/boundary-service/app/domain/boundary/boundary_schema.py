# ============================================================================
# 📋 CBAM 산정경계 설정 스키마
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

# ============================================================================
# 🏭 기업 기본 정보 스키마
# ============================================================================

class CompanyInfo(BaseModel):
    """기업 기본 정보"""
    company_name: str = Field(..., description="기업명")
    business_address: str = Field(..., description="사업장 주소")
    business_number: str = Field(..., description="사업자등록번호")
    representative_name: str = Field(..., description="대표자명")
    contact_email: str = Field(..., description="연락처 이메일")
    contact_phone: str = Field(..., description="연락처 전화번호")
    
    class Config:
        schema_extra = {
            "example": {
                "company_name": "포스코",
                "business_address": "경상북도 포항시 남구 포스코대로 6261",
                "business_number": "1234567890",
                "representative_name": "김철수",
                "contact_email": "contact@posco.com",
                "contact_phone": "02-1234-5678"
            }
        }

# ============================================================================
# 📦 CBAM 대상 제품 스키마
# ============================================================================

class CBAMProduct(BaseModel):
    """CBAM 대상 제품 정보"""
    product_name: str = Field(..., description="제품명")
    hs_code: str = Field(..., description="HS 코드 (6자리)")
    cn_code: str = Field(..., description="CN 코드 (8자리)")
    is_cbam_target: bool = Field(..., description="CBAM 대상 여부")
    product_category: str = Field(..., description="제품 카테고리")
    unit: str = Field(..., description="단위 (톤, kg 등)")
    
    class Config:
        schema_extra = {
            "example": {
                "product_name": "열간압연 평판제품",
                "hs_code": "7208",
                "cn_code": "72081000",
                "is_cbam_target": True,
                "product_category": "철강제품",
                "unit": "톤"
            }
        }

# ============================================================================
# ⚙️ 생산 공정 스키마
# ============================================================================

class ProductionProcess(BaseModel):
    """생산 공정 정보"""
    process_id: str = Field(..., description="공정 ID")
    process_name: str = Field(..., description="공정명")
    main_products: List[str] = Field(..., description="주요 생산품 목록")
    input_materials: List[str] = Field(..., description="주요 투입 원료")
    input_fuels: List[str] = Field(..., description="주요 투입 연료")
    energy_flows: List[str] = Field(..., description="에너지/물질 흐름")
    has_shared_utility: bool = Field(..., description="공동 사용 유틸리티 설비 유무")
    produces_cbam_target: bool = Field(..., description="CBAM 대상 제품 생산 여부")
    has_measurement: bool = Field(..., description="계측기 유무")
    measurement_reliability: str = Field(..., description="계측기 신뢰도")
    process_order: int = Field(..., description="공정 순서")
    
    class Config:
        schema_extra = {
            "example": {
                "process_id": "PROC_001",
                "process_name": "소결공정",
                "main_products": ["소결광"],
                "input_materials": ["철광석", "석회석", "코크스"],
                "input_fuels": ["코크스", "천연가스"],
                "energy_flows": ["열", "폐가스"],
                "has_shared_utility": True,
                "produces_cbam_target": True,
                "has_measurement": True,
                "measurement_reliability": "법정계량기",
                "process_order": 1
            }
        }

# ============================================================================
# 🌍 산정경계 설정 스키마
# ============================================================================

class CalculationBoundary(BaseModel):
    """산정경계 설정 정보"""
    boundary_id: str = Field(..., description="경계 ID")
    boundary_name: str = Field(..., description="경계명")
    boundary_type: str = Field(..., description="경계 유형 (개별/통합)")
    included_processes: List[str] = Field(..., description="포함된 공정 ID 목록")
    excluded_processes: List[str] = Field(..., description="제외된 공정 ID 목록")
    shared_utilities: List[str] = Field(..., description="공동 사용 유틸리티")
    allocation_method: str = Field(..., description="데이터 할당 방법")
    description: str = Field(..., description="경계 설정 설명")
    
    class Config:
        schema_extra = {
            "example": {
                "boundary_id": "BOUND_001",
                "boundary_name": "철강제품 생산 경계",
                "boundary_type": "통합",
                "included_processes": ["PROC_001", "PROC_002", "PROC_003"],
                "excluded_processes": ["PROC_004"],
                "shared_utilities": ["보일러", "발전소"],
                "allocation_method": "가동시간 기준 할당",
                "description": "철강제품 생산을 위한 통합 산정경계"
            }
        }

# ============================================================================
# 📊 배출원 및 소스 스트림 스키마
# ============================================================================

class EmissionSource(BaseModel):
    """배출원 정보"""
    source_id: str = Field(..., description="배출원 ID")
    source_name: str = Field(..., description="배출원명")
    source_type: str = Field(..., description="배출원 유형")
    ghg_types: List[str] = Field(..., description="배출 온실가스 종류")
    process_id: str = Field(..., description="소속 공정 ID")
    measurement_method: str = Field(..., description="측정 방법")
    
    class Config:
        schema_extra = {
            "example": {
                "source_id": "EMIT_001",
                "source_name": "고로",
                "source_type": "연소설비",
                "ghg_types": ["CO2"],
                "process_id": "PROC_002",
                "measurement_method": "연속측정"
            }
        }

class SourceStream(BaseModel):
    """소스 스트림 정보"""
    stream_id: str = Field(..., description="스트림 ID")
    stream_name: str = Field(..., description="스트림명")
    stream_type: str = Field(..., description="스트림 유형 (연료/원료)")
    carbon_content: float = Field(..., description="탄소 함량 (%)")
    is_precursor: bool = Field(..., description="전구물질 여부")
    precursor_process_id: Optional[str] = Field(None, description="전구물질 생산 공정 ID")
    unit: str = Field(..., description="단위")
    
    class Config:
        schema_extra = {
            "example": {
                "stream_id": "STREAM_001",
                "stream_name": "코크스",
                "stream_type": "연료",
                "carbon_content": 85.5,
                "is_precursor": False,
                "unit": "톤"
            }
        }

# ============================================================================
# 📅 보고 기간 설정 스키마
# ============================================================================

class ReportingPeriod(BaseModel):
    """보고 기간 설정"""
    period_id: str = Field(..., description="기간 ID")
    period_name: str = Field(..., description="기간명")
    period_type: str = Field(..., description="기간 유형 (역년/회계연도/국내제도)")
    start_date: datetime = Field(..., description="시작일")
    end_date: datetime = Field(..., description="종료일")
    duration_months: int = Field(..., description="기간 (월)")
    description: str = Field(..., description="기간 설명")
    
    @validator('duration_months')
    def validate_duration(cls, v):
        if v < 3 or v > 12:
            raise ValueError('보고 기간은 3개월 이상 12개월 이하여야 합니다')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "period_id": "PERIOD_001",
                "period_name": "2024년 회계연도",
                "period_type": "회계연도",
                "start_date": "2024-01-01T00:00:00",
                "end_date": "2024-12-31T23:59:59",
                "duration_months": 12,
                "description": "2024년 1월 1일부터 12월 31일까지"
            }
        }

# ============================================================================
# 🔄 데이터 할당 스키마
# ============================================================================

class DataAllocation(BaseModel):
    """데이터 할당 정보"""
    allocation_id: str = Field(..., description="할당 ID")
    shared_resource: str = Field(..., description="공유 자원명")
    resource_type: str = Field(..., description="자원 유형 (연료/전력/열/원료)")
    total_consumption: float = Field(..., description="총 소비량")
    unit: str = Field(..., description="단위")
    allocation_method: str = Field(..., description="할당 방법")
    allocation_factors: Dict[str, float] = Field(..., description="공정별 할당 비율")
    measurement_reliability: str = Field(..., description="측정 신뢰도")
    
    class Config:
        schema_extra = {
            "example": {
                "allocation_id": "ALLOC_001",
                "shared_resource": "보일러 연료",
                "resource_type": "연료",
                "total_consumption": 1000.0,
                "unit": "톤",
                "allocation_method": "가동시간 기준",
                "allocation_factors": {
                    "PROC_001": 0.4,
                    "PROC_002": 0.6
                },
                "measurement_reliability": "법정계량기"
            }
        }

# ============================================================================
# 📋 CBAM 산정경계 설정 요청/응답 스키마
# ============================================================================

class CBAMBoundaryRequest(BaseModel):
    """CBAM 산정경계 설정 요청"""
    company_info: CompanyInfo
    target_products: List[CBAMProduct]
    production_processes: List[ProductionProcess]
    reporting_period: ReportingPeriod
    boundary_preferences: Dict[str, Any] = Field(..., description="경계 설정 선호사항")
    
    class Config:
        schema_extra = {
            "example": {
                "company_info": {
                    "company_name": "포스코",
                    "business_address": "경상북도 포항시 남구 포스코대로 6261",
                    "business_number": "1234567890",
                    "representative_name": "김철수",
                    "contact_email": "contact@posco.com",
                    "contact_phone": "02-1234-5678"
                },
                "target_products": [
                    {
                        "product_name": "열간압연 평판제품",
                        "hs_code": "7208",
                        "cn_code": "72081000",
                        "is_cbam_target": True,
                        "product_category": "철강제품",
                        "unit": "톤"
                    }
                ],
                "production_processes": [
                    {
                        "process_id": "PROC_001",
                        "process_name": "소결공정",
                        "main_products": ["소결광"],
                        "input_materials": ["철광석", "석회석", "코크스"],
                        "input_fuels": ["코크스", "천연가스"],
                        "energy_flows": ["열", "폐가스"],
                        "has_shared_utility": True,
                        "produces_cbam_target": True,
                        "has_measurement": True,
                        "measurement_reliability": "법정계량기",
                        "process_order": 1
                    }
                ],
                "reporting_period": {
                    "period_id": "PERIOD_001",
                    "period_name": "2024년 회계연도",
                    "period_type": "회계연도",
                    "start_date": "2024-01-01T00:00:00",
                    "end_date": "2024-12-31T23:59:59",
                    "duration_months": 12,
                    "description": "2024년 1월 1일부터 12월 31일까지"
                },
                "boundary_preferences": {
                    "boundary_type": "통합",
                    "allocation_method": "가동시간 기준",
                    "include_shared_utilities": True
                }
            }
        }

class CBAMBoundaryResponse(BaseModel):
    """CBAM 산정경계 설정 응답"""
    boundary_id: str
    boundary_configuration: CalculationBoundary
    emission_sources: List[EmissionSource]
    source_streams: List[SourceStream]
    data_allocations: List[DataAllocation]
    recommendations: List[str]
    validation_errors: List[str]
    next_steps: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "boundary_id": "BOUND_001",
                "boundary_configuration": {
                    "boundary_id": "BOUND_001",
                    "boundary_name": "철강제품 생산 경계",
                    "boundary_type": "통합",
                    "included_processes": ["PROC_001", "PROC_002", "PROC_003"],
                    "excluded_processes": ["PROC_004"],
                    "shared_utilities": ["보일러", "발전소"],
                    "allocation_method": "가동시간 기준 할당",
                    "description": "철강제품 생산을 위한 통합 산정경계"
                },
                "emission_sources": [],
                "source_streams": [],
                "data_allocations": [],
                "recommendations": [
                    "CBAM 대상 제품 생산 공정을 중심으로 경계를 설정하세요",
                    "공동 사용 유틸리티는 가상 분할을 통해 할당하세요"
                ],
                "validation_errors": [],
                "next_steps": [
                    "배출원 및 소스 스트림 식별",
                    "데이터 할당 계획 수립",
                    "계측기 설치 및 검증"
                ]
            }
        }
