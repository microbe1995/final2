# ============================================================================
# 🗄️ CBAM 산정경계 설정 엔티티
# ============================================================================

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Dict, Any
import uuid

Base = declarative_base()

# ============================================================================
# 🏭 기업 기본 정보 엔티티
# ============================================================================

class CompanyEntity(Base):
    """기업 기본 정보 엔티티"""
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String(200), nullable=False, comment="기업명")
    business_address = Column(Text, nullable=False, comment="사업장 주소")
    business_number = Column(String(20), nullable=False, unique=True, comment="사업자등록번호")
    representative_name = Column(String(100), nullable=False, comment="대표자명")
    contact_email = Column(String(200), nullable=False, comment="연락처 이메일")
    contact_phone = Column(String(20), nullable=False, comment="연락처 전화번호")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "business_address": self.business_address,
            "business_number": self.business_number,
            "representative_name": self.representative_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 📦 CBAM 대상 제품 엔티티
# ============================================================================

class CBAMProductEntity(Base):
    """CBAM 대상 제품 엔티티"""
    __tablename__ = "cbam_products"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), nullable=False, comment="기업 ID")
    product_name = Column(String(200), nullable=False, comment="제품명")
    hs_code = Column(String(10), nullable=False, comment="HS 코드 (6자리)")
    cn_code = Column(String(10), nullable=False, comment="CN 코드 (8자리)")
    is_cbam_target = Column(Boolean, nullable=False, default=False, comment="CBAM 대상 여부")
    product_category = Column(String(100), nullable=False, comment="제품 카테고리")
    unit = Column(String(20), nullable=False, comment="단위")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "product_name": self.product_name,
            "hs_code": self.hs_code,
            "cn_code": self.cn_code,
            "is_cbam_target": self.is_cbam_target,
            "product_category": self.product_category,
            "unit": self.unit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# ⚙️ 생산 공정 엔티티
# ============================================================================

class ProductionProcessEntity(Base):
    """생산 공정 엔티티"""
    __tablename__ = "production_processes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), nullable=False, comment="기업 ID")
    process_id = Column(String(50), nullable=False, comment="공정 ID")
    process_name = Column(String(200), nullable=False, comment="공정명")
    main_products = Column(JSON, nullable=False, comment="주요 생산품 목록")
    input_materials = Column(JSON, nullable=False, comment="주요 투입 원료")
    input_fuels = Column(JSON, nullable=False, comment="주요 투입 연료")
    energy_flows = Column(JSON, nullable=False, comment="에너지/물질 흐름")
    has_shared_utility = Column(Boolean, nullable=False, default=False, comment="공동 사용 유틸리티 설비 유무")
    produces_cbam_target = Column(Boolean, nullable=False, default=False, comment="CBAM 대상 제품 생산 여부")
    has_measurement = Column(Boolean, nullable=False, default=False, comment="계측기 유무")
    measurement_reliability = Column(String(100), nullable=True, comment="계측기 신뢰도")
    process_order = Column(Integer, nullable=False, comment="공정 순서")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "process_id": self.process_id,
            "process_name": self.process_name,
            "main_products": self.main_products,
            "input_materials": self.input_materials,
            "input_fuels": self.input_fuels,
            "energy_flows": self.energy_flows,
            "has_shared_utility": self.has_shared_utility,
            "produces_cbam_target": self.produces_cbam_target,
            "has_measurement": self.has_measurement,
            "measurement_reliability": self.measurement_reliability,
            "process_order": self.process_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

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
# 📊 배출원 및 소스 스트림 엔티티
# ============================================================================

class EmissionSourceEntity(Base):
    """배출원 엔티티"""
    __tablename__ = "emission_sources"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    boundary_id = Column(String(36), nullable=False, comment="산정경계 ID")
    source_id = Column(String(50), nullable=False, comment="배출원 ID")
    source_name = Column(String(200), nullable=False, comment="배출원명")
    source_type = Column(String(100), nullable=False, comment="배출원 유형")
    ghg_types = Column(JSON, nullable=False, comment="배출 온실가스 종류")
    process_id = Column(String(50), nullable=False, comment="소속 공정 ID")
    measurement_method = Column(String(100), nullable=True, comment="측정 방법")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "boundary_id": self.boundary_id,
            "source_id": self.source_id,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "ghg_types": self.ghg_types,
            "process_id": self.process_id,
            "measurement_method": self.measurement_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class SourceStreamEntity(Base):
    """소스 스트림 엔티티"""
    __tablename__ = "source_streams"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    boundary_id = Column(String(36), nullable=False, comment="산정경계 ID")
    stream_id = Column(String(50), nullable=False, comment="스트림 ID")
    stream_name = Column(String(200), nullable=False, comment="스트림명")
    stream_type = Column(String(50), nullable=False, comment="스트림 유형 (연료/원료)")
    carbon_content = Column(Float, nullable=False, comment="탄소 함량 (%)")
    is_precursor = Column(Boolean, nullable=False, default=False, comment="전구물질 여부")
    precursor_process_id = Column(String(50), nullable=True, comment="전구물질 생산 공정 ID")
    unit = Column(String(20), nullable=False, comment="단위")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "boundary_id": self.boundary_id,
            "stream_id": self.stream_id,
            "stream_name": self.stream_name,
            "stream_type": self.stream_type,
            "carbon_content": self.carbon_content,
            "is_precursor": self.is_precursor,
            "precursor_process_id": self.precursor_process_id,
            "unit": self.unit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 📅 보고 기간 설정 엔티티
# ============================================================================

class ReportingPeriodEntity(Base):
    """보고 기간 설정 엔티티"""
    __tablename__ = "reporting_periods"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), nullable=False, comment="기업 ID")
    period_id = Column(String(50), nullable=False, comment="기간 ID")
    period_name = Column(String(200), nullable=False, comment="기간명")
    period_type = Column(String(50), nullable=False, comment="기간 유형 (역년/회계연도/국내제도)")
    start_date = Column(DateTime(timezone=True), nullable=False, comment="시작일")
    end_date = Column(DateTime(timezone=True), nullable=False, comment="종료일")
    duration_months = Column(Integer, nullable=False, comment="기간 (월)")
    description = Column(Text, nullable=True, comment="기간 설명")
    is_active = Column(Boolean, nullable=False, default=True, comment="활성 여부")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "period_id": self.period_id,
            "period_name": self.period_name,
            "period_type": self.period_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "duration_months": self.duration_months,
            "description": self.description,
            "is_active": self.is_active,
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

# ============================================================================
# 📋 CBAM 산정경계 설정 세션 엔티티
# ============================================================================

class CBAMBoundarySessionEntity(Base):
    """CBAM 산정경계 설정 세션 엔티티"""
    __tablename__ = "cbam_boundary_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), nullable=False, comment="기업 ID")
    session_name = Column(String(200), nullable=False, comment="세션명")
    current_step = Column(String(50), nullable=False, default="company_info", comment="현재 단계")
    step_data = Column(JSON, nullable=False, default=dict, comment="단계별 데이터")
    validation_errors = Column(JSON, nullable=False, default=list, comment="검증 오류 목록")
    recommendations = Column(JSON, nullable=False, default=list, comment="권장사항 목록")
    next_steps = Column(JSON, nullable=False, default=list, comment="다음 단계 목록")
    status = Column(String(20), nullable=False, default="in_progress", comment="상태")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="생성일시")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="수정일시")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "session_name": self.session_name,
            "current_step": self.current_step,
            "step_data": self.step_data,
            "validation_errors": self.validation_errors,
            "recommendations": self.recommendations,
            "next_steps": self.next_steps,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
