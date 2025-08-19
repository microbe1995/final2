# ============================================================================
# 📋 CBAM 산정경계 설정 스키마
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

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


