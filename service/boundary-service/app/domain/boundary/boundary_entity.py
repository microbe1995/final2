# ============================================================================
# 🗄️ CBAM 산정경계 설정 엔티티
# ============================================================================

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from typing import Dict, Any
import uuid
from app.common.database_base import Base

# ============================================================================
# 🌍 산정경계 설정 엔티티
# ============================================================================

class CalculationBoundaryEntity(Base):
    """산정경계 설정 엔티티"""
    __tablename__ = "calculation_boundaries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), nullable=False, comment="기업 ID")
    boundary_id = Column(String(50), nullable=False, comment="경계 ID")
    boundary_name = Column(String(200), nullable=False, comment="경계명")
    boundary_type = Column(String(50), nullable=False, comment="경계 유형 (개별/통합)")
    included_processes = Column(JSON, nullable=False, comment="포함된 공정 ID 목록")
    excluded_processes = Column(JSON, nullable=False, comment="제외된 공정 ID 목록")
    shared_utilities = Column(JSON, nullable=False, comment="공동 사용 유틸리티")
    allocation_method = Column(String(100), nullable=False, comment="데이터 할당 방법")
    description = Column(Text, nullable=True, comment="경계 설정 설명")
    status = Column(String(20), nullable=False, default="draft", comment="상태 (draft/active/inactive)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "boundary_id": self.boundary_id,
            "boundary_name": self.boundary_name,
            "boundary_type": self.boundary_type,
            "included_processes": self.included_processes,
            "excluded_processes": self.excluded_processes,
            "shared_utilities": self.shared_utilities,
            "allocation_method": self.allocation_method,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }



# ============================================================================
# 🔄 데이터 할당 엔티티
# ============================================================================

class DataAllocationEntity(Base):
    """데이터 할당 엔티티"""
    __tablename__ = "data_allocations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    boundary_id = Column(String(36), nullable=False, comment="산정경계 ID")
    allocation_id = Column(String(50), nullable=False, comment="할당 ID")
    shared_resource = Column(String(200), nullable=False, comment="공유 자원명")
    resource_type = Column(String(50), nullable=False, comment="자원 유형 (연료/전력/열/원료)")
    total_consumption = Column(Float, nullable=False, comment="총 소비량")
    unit = Column(String(20), nullable=False, comment="단위")
    allocation_method = Column(String(100), nullable=False, comment="할당 방법")
    allocation_factors = Column(JSON, nullable=False, comment="공정별 할당 비율")
    measurement_reliability = Column(String(100), nullable=True, comment="측정 신뢰도")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "boundary_id": self.boundary_id,
            "allocation_id": self.allocation_id,
            "shared_resource": self.shared_resource,
            "resource_type": self.resource_type,
            "total_consumption": self.total_consumption,
            "unit": self.unit,
            "allocation_method": self.allocation_method,
            "allocation_factors": self.allocation_factors,
            "measurement_reliability": self.measurement_reliability,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


