# ============================================================================
# 🔧 CBAM 산정경계 설정 서비스
# ============================================================================

from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import uuid
from datetime import datetime

from app.domain.boundary.boundary_schema import (
    CalculationBoundary, DataAllocation
)

# ============================================================================
# 🌍 산정경계 설정 서비스
# ============================================================================

class CalculationBoundaryService:
    """산정경계 설정 서비스"""
    
    @staticmethod
    def create_boundary_configuration(boundary_data: Dict[str, Any]) -> Dict[str, Any]:
        """산정경계 설정 생성"""
        
        # 기본 산정경계 생성
        boundary_id = f"BOUND_{uuid.uuid4().hex[:8].upper()}"
        
        boundary = {
            "boundary_id": boundary_id,
            "boundary_name": boundary_data.get("boundary_name", f"산정경계_{boundary_id}"),
            "boundary_type": boundary_data.get("boundary_type", "통합"),
            "included_processes": boundary_data.get("included_processes", []),
            "excluded_processes": boundary_data.get("excluded_processes", []),
            "shared_utilities": boundary_data.get("shared_utilities", []),
            "allocation_method": boundary_data.get("allocation_method", "가동시간 기준"),
            "description": boundary_data.get("description", "CBAM 산정경계 설정"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"산정경계 설정 생성: {boundary_id}")
        return boundary
    
    @staticmethod
    def validate_boundary_configuration(boundary_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """산정경계 설정 검증"""
        errors = []
        
        # 필수 필드 검증
        if not boundary_data.get("boundary_name"):
            errors.append("산정경계명은 필수입니다")
        
        if not boundary_data.get("boundary_type"):
            errors.append("경계 유형은 필수입니다")
        
        # 경계 유형 검증
        valid_types = ["개별", "통합"]
        if boundary_data.get("boundary_type") not in valid_types:
            errors.append(f"경계 유형은 다음 중 하나여야 합니다: {', '.join(valid_types)}")
        
        # 포함 공정 검증
        included_processes = boundary_data.get("included_processes", [])
        if not included_processes:
            errors.append("최소 1개 이상의 공정이 포함되어야 합니다")
        
        return len(errors) == 0, errors

# ============================================================================
# 🔄 데이터 할당 서비스
# ============================================================================

class DataAllocationService:
    """데이터 할당 서비스"""
    
    @staticmethod
    def create_allocation_plan(allocation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """데이터 할당 계획 생성"""
        allocations = []
        
        shared_resources = allocation_data.get("shared_resources", [])
        boundary_id = allocation_data.get("boundary_id", "")
        
        for resource in shared_resources:
            allocation_id = f"ALLOC_{uuid.uuid4().hex[:8].upper()}"
            
            # 할당 방법 결정
            allocation_method = "가동시간 기준"
            resource_type = DataAllocationService._get_resource_type(resource)
            
            if "전력" in resource:
                allocation_method = "전력사용량 기준"
            elif "열" in resource:
                allocation_method = "열사용량 기준"
            
            # 기본 할당 계획 생성
            allocation = {
                "allocation_id": allocation_id,
                "boundary_id": boundary_id,
                "shared_resource": resource,
                "resource_type": resource_type,
                "total_consumption": allocation_data.get("total_consumption", 100.0),
                "unit": allocation_data.get("unit", "톤"),
                "allocation_method": allocation_method,
                "allocation_factors": allocation_data.get("allocation_factors", {}),
                "measurement_reliability": allocation_data.get("measurement_reliability", "법정계량기"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            allocations.append(allocation)
            logger.info(f"데이터 할당 계획 생성: {allocation_id} - {resource}")
        
        return allocations
    
    @staticmethod
    def validate_allocation_plan(allocation_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """데이터 할당 계획 검증"""
        errors = []
        
        # 필수 필드 검증
        if not allocation_data.get("shared_resources"):
            errors.append("공유 자원 목록은 필수입니다")
        
        if not allocation_data.get("boundary_id"):
            errors.append("산정경계 ID는 필수입니다")
        
        # 총 소비량 검증
        total_consumption = allocation_data.get("total_consumption", 0)
        if total_consumption <= 0:
            errors.append("총 소비량은 0보다 커야 합니다")
        
        # 할당 비율 검증
        allocation_factors = allocation_data.get("allocation_factors", {})
        if allocation_factors:
            total_factor = sum(allocation_factors.values())
            if abs(total_factor - 1.0) > 0.01:  # 1% 오차 허용
                errors.append("할당 비율의 합은 1.0이어야 합니다")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _get_resource_type(resource_name: str) -> str:
        """자원 유형 판별"""
        resource_lower = resource_name.lower()
        
        if any(keyword in resource_lower for keyword in ["연료", "가스", "석탄", "코크스"]):
            return "연료"
        elif any(keyword in resource_lower for keyword in ["전력", "전기"]):
            return "전력"
        elif any(keyword in resource_lower for keyword in ["열", "스팀", "냉각", "보일러"]):
            return "열"
        else:
            return "원료"


