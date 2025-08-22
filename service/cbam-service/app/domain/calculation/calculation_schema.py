# ============================================================================
# 🧮 Calculation Schema - CBAM 계산 데이터 검증 및 직렬화
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

# ============================================================================
# 🔥 연료 계산 스키마
# ============================================================================

class FuelCalculationRequest(BaseModel):
    """연료 계산 요청"""
    fuel_name: str = Field(..., description="연료명")
    fuel_amount: float = Field(..., gt=0, description="연료량 (톤)")
    
    @validator('fuel_name')
    def validate_fuel_name(cls, v):
        if not v or not v.strip():
            raise ValueError("연료명은 필수입니다")
        return v.strip()

class FuelCalculationResponse(BaseModel):
    """연료 배출량 계산 응답"""
    emission: float = Field(..., description="계산된 배출량 (tCO2)")
    fuel_name: str = Field(..., description="연료명")
    fuel_emfactor: float = Field(..., description="배출계수 (tCO2/TJ)")
    net_calory: float = Field(..., description="순발열량 (TJ/Gg)")
    calculation_formula: str = Field(default="연료량(톤) × 순발열량(TJ/Gg) × 배출계수(tCO2/TJ) × 1e-3")

# ============================================================================
# 🧱 원료 계산 스키마
# ============================================================================

class MaterialCalculationRequest(BaseModel):
    """원료 배출량 계산 요청"""
    material_name: str = Field(..., description="원료명")
    material_amount: float = Field(..., gt=0, description="원료량 (톤)")
    
    @validator('material_name')
    def validate_material_name(cls, v):
        if not v or not v.strip():
            raise ValueError("원료명은 필수입니다")
        return v.strip()

class MaterialCalculationResponse(BaseModel):
    """원료 배출량 계산 응답"""
    emission: float = Field(..., description="계산된 배출량 (tCO2)")
    material_name: str = Field(..., description="원료명")
    em_factor: float = Field(..., description="배출계수 (tCO2/톤)")
    calculation_formula: str = Field(default="원료량(톤) × 배출계수(tCO2/톤)")

# ============================================================================
# 🔗 전구물질 스키마
# ============================================================================

class PrecursorData(BaseModel):
    """전구물질 데이터"""
    id: Optional[int] = None
    user_id: str = Field(..., description="사용자 ID")
    precursor: str = Field(..., description="전구물질명")
    precursor_eng: Optional[str] = Field(default="", description="전구물질명(영문)")
    cn1: Optional[str] = Field(default="", description="CN코드1")
    cn2: Optional[str] = Field(default="", description="CN코드2")
    cn3: Optional[str] = Field(default="", description="CN코드3")
    direct: float = Field(default=0.0, description="직접 배출계수 (tCO2/톤)")
    indirect: float = Field(default=0.0, description="간접 배출계수 (tCO2/톤)")
    final_country_code: Optional[str] = Field(default="", description="최종 국가 코드")
    created_at: Optional[datetime] = None
    
    @validator('precursor')
    def validate_precursor_name(cls, v):
        if not v or not v.strip():
            raise ValueError("전구물질명은 필수입니다")
        return v.strip()
    
    class Config:
        from_attributes = True

class PrecursorListRequest(BaseModel):
    """전구물질 목록 요청"""
    precursors: List[PrecursorData] = Field(..., description="전구물질 목록")

class PrecursorResponse(BaseModel):
    """전구물질 응답"""
    id: int
    user_id: str
    precursor: str
    precursor_eng: str
    cn1: str
    cn2: str
    cn3: str
    direct: float = Field(default=0.0, description="직접 배출계수 (tCO2/톤)")
    indirect: float = Field(default=0.0, description="간접 배출계수 (tCO2/톤)")
    final_country_code: str
    created_at: str
    
    class Config:
        from_attributes = True

class PrecursorListResponse(BaseModel):
    """전구물질 목록 응답"""
    precursors: List[PrecursorResponse]
    total: int = Field(..., description="전체 개수")

class PrecursorCalculationRequest(BaseModel):
    """전구물질 계산 요청"""
    precursor_name: str = Field(..., description="전구물질명")
    precursor_amount: float = Field(..., gt=0, description="전구물질 사용량 (톤)")
    direct: float = Field(..., ge=0, description="직접 배출계수 (tCO2/톤)")
    indirect: float = Field(default=0.0, ge=0, description="간접 배출계수 (tCO2/톤)")
    
    @validator('precursor_name')
    def validate_precursor_name(cls, v):
        if not v or not v.strip():
            raise ValueError("전구물질명은 필수입니다")
        return v.strip()

class PrecursorCalculationResponse(BaseModel):
    """전구물질 계산 응답"""
    emission: float = Field(..., description="계산된 배출량 (tCO2)")
    precursor_name: str = Field(..., description="전구물질명")
    direct: float = Field(..., description="직접 배출계수 (tCO2/톤)")
    indirect: float = Field(..., description="간접 배출계수 (tCO2/톤)")
    calculation_formula: str = Field(default="전구물질량(톤) × (직접배출계수 + 간접배출계수)")

class PrecursorSaveResponse(BaseModel):
    """전구물질 저장 응답"""
    inserted_count: int = Field(..., description="저장된 전구물질 개수")
    success: bool = Field(default=True)
    message: str = Field(default="전구물질이 성공적으로 저장되었습니다")

# ============================================================================
# ⚡ 전력 사용 배출량 스키마
# ============================================================================

class ElectricityCalculationRequest(BaseModel):
    """전력 사용 배출량 계산 요청"""
    power_usage: float = Field(..., gt=0, description="전력 사용량 (MWh)")
    emission_factor: float = Field(default=0.4567, description="전력 배출계수 (tCO2/MWh)")
    
    @validator('emission_factor')
    def validate_emission_factor(cls, v):
        if v < 0:
            raise ValueError("배출계수는 0 이상이어야 합니다")
        return v

class ElectricityCalculationResponse(BaseModel):
    """전력 사용 배출량 계산 응답"""
    emission: float = Field(..., description="계산된 배출량 (tCO2)")
    power_usage: float = Field(..., description="전력 사용량 (MWh)")
    emission_factor: float = Field(..., description="전력 배출계수 (tCO2/MWh)")
    calculation_formula: str = Field(default="전력사용량(MWh) × 배출계수(tCO2/MWh)")

# ============================================================================
# 🏭 생산 공정 스키마
# ============================================================================

class ProductionProcess(BaseModel):
    """생산 공정 데이터"""
    process_order: int = Field(..., description="공정 순서")
    process_name: str = Field(..., description="공정명")
    start_date: str = Field(..., description="공정 시작일자")
    end_date: str = Field(..., description="공정 종료일자")
    duration_days: int = Field(..., description="공정 기간 (일)")
    input_material_name: Optional[str] = Field(default="", description="투입 원료명")
    input_material_amount: Optional[float] = Field(default=0.0, description="투입 원료량")
    input_fuel_name: Optional[str] = Field(default="", description="투입 연료명")
    input_fuel_amount: Optional[float] = Field(default=0.0, description="투입 연료량")
    power_usage: Optional[float] = Field(default=0.0, description="전력 사용량 (MWh)")
    direct_emission: float = Field(default=0.0, description="직접 귀속 배출량")
    indirect_emission: float = Field(default=0.0, description="간접 귀속 배출량")
    precursor_emission: float = Field(default=0.0, description="전구물질 배출량")
    total_emission: float = Field(default=0.0, description="총 배출량")

# ============================================================================
# 🎯 CBAM 종합 계산 스키마
# ============================================================================

class CBAmCalculationRequest(BaseModel):
    """CBAM 종합 계산 요청"""
    product_name: str = Field(..., description="제품명")
    product_type: str = Field(..., description="제품 타입 (단순/복합)")
    user_id: str = Field(..., description="사용자 ID")
    production_period: Dict[str, str] = Field(..., description="생산 기간")
    cn_code: Optional[str] = Field(default="", description="CN코드")
    production_quantity: float = Field(..., gt=0, description="생산량")
    processes: List[ProductionProcess] = Field(default=[], description="생산 공정 목록")
    fuels: List[Dict[str, Any]] = Field(default=[], description="연료 목록")
    materials: List[Dict[str, Any]] = Field(default=[], description="원료 목록")
    electricity: Optional[Dict[str, Any]] = Field(default=None, description="전력 정보")
    precursors: List[Dict[str, Any]] = Field(default=[], description="전구물질 목록")

class CBAMCalculationResponse(BaseModel):
    """CBAM 종합 계산 응답"""
    product_name: str = Field(..., description="제품명")
    product_type: str = Field(..., description="제품 타입")
    user_id: str = Field(..., description="사용자 ID")
    production_period: Dict[str, str] = Field(..., description="생산 기간")
    cn_code: str = Field(..., description="CN코드")
    production_quantity: float = Field(..., description="생산량")
    emission_per_product: float = Field(..., description="제품당 배출량")
    total_direct_emission: float = Field(..., description="총 직접 배출량")
    total_indirect_emission: float = Field(..., description="총 간접 배출량")
    total_precursor_emission: float = Field(..., description="총 전구물질 배출량")
    total_emission: float = Field(..., description="총 배출량")
    processes: List[ProductionProcess] = Field(default=[], description="생산 공정별 배출량")
    fuel_emissions: List[Dict[str, Any]] = Field(default=[], description="연료별 배출량")
    material_emissions: List[Dict[str, Any]] = Field(default=[], description="원료별 배출량")
    electricity_emission: Optional[Dict[str, Any]] = Field(default=None, description="전력 배출량")
    precursor_emissions: List[Dict[str, Any]] = Field(default=[], description="전구물질별 배출량")
    calculation_date: str = Field(..., description="계산 일시")
    calculation_formula: str = Field(default="직접배출량 + 간접배출량 + 전구물질배출량")

# ============================================================================
# 📊 통계 스키마
# ============================================================================

class CalculationStatsResponse(BaseModel):
    """계산 통계 응답"""
    total_calculations: int = Field(..., description="전체 계산 수")
    fuel_calculations: int = Field(..., description="연료 계산 수")
    material_calculations: int = Field(..., description="원료 계산 수")
    total_precursors: int = Field(..., description="전체 전구물질 수")
    active_users: int = Field(..., description="활성 사용자 수")
    calculations_by_type: Dict[str, int] = Field(..., description="타입별 계산 수")
    last_updated: str = Field(..., description="마지막 업데이트 시간")

# ============================================================================
# 🗄️ 새로운 테이블 스키마들
# ============================================================================

class BoundaryCreateRequest(BaseModel):
    """경계 생성 요청"""
    name: str = Field(..., description="산정경계명")

class BoundaryResponse(BaseModel):
    """경계 응답"""
    boundary_id: int
    name: str
    created_at: Optional[str] = None

class ProductCreateRequest(BaseModel):
    """제품 생성 요청"""
    name: str = Field(..., description="제품명")
    cn_code: Optional[str] = Field(None, description="CBAM CN 코드")
    period_start: str = Field(..., description="실적 집계 시작일 (YYYY-MM-DD)")
    period_end: str = Field(..., description="실적 집계 종료일 (YYYY-MM-DD)")
    production_qty: Optional[float] = Field(None, description="생산량")
    sales_qty: Optional[float] = Field(None, description="외부판매량")
    export_qty: Optional[float] = Field(None, description="수출량")
    inventory_qty: Optional[float] = Field(None, description="재고량")
    defect_rate: Optional[float] = Field(None, description="불량률")

class ProductResponse(BaseModel):
    """제품 응답"""
    product_id: int
    name: str
    cn_code: Optional[str] = None
    period_start: str
    period_end: str
    production_qty: Optional[float] = None
    sales_qty: Optional[float] = None
    export_qty: Optional[float] = None
    inventory_qty: Optional[float] = None
    defect_rate: Optional[float] = None
    node_id: Optional[str] = None
    created_at: Optional[str] = None

class OperationCreateRequest(BaseModel):
    """공정 생성 요청"""
    name: str = Field(..., description="공정명")
    facility_id: Optional[int] = Field(None, description="소속 사업장")
    category: Optional[str] = Field(None, description="공정 분류")
    boundary_id: Optional[int] = Field(None, description="속한 경계")
    node_id: Optional[str] = Field(None, description="대상 operation 노드")
    input_kind: str = Field(..., description="입력 종류 (material/fuel/electricity)")
    material_id: Optional[int] = Field(None, description="투입 물질")
    fuel_id: Optional[int] = Field(None, description="투입 연료")
    quantity: float = Field(..., description="사용량")
    unit_id: Optional[int] = Field(None, description="단위")

class OperationResponse(BaseModel):
    """공정 응답"""
    operation_id: int
    name: str
    facility_id: Optional[int] = None
    category: Optional[str] = None
    boundary_id: Optional[int] = None
    node_id: Optional[str] = None
    input_kind: str
    material_id: Optional[int] = None
    fuel_id: Optional[int] = None
    quantity: float
    unit_id: Optional[int] = None
    created_at: Optional[str] = None

class NodeCreateRequest(BaseModel):
    """노드 생성 요청"""
    boundary_id: Optional[int] = Field(None, description="속한 경계")
    node_type: str = Field(..., description="노드 타입 (product/operation)")
    ref_id: int = Field(..., description="참조 ID")
    label: Optional[str] = Field(None, description="화면 표시용 라벨")
    pos_x: Optional[float] = Field(None, description="X 좌표")
    pos_y: Optional[float] = Field(None, description="Y 좌표")

class NodeResponse(BaseModel):
    """노드 응답"""
    node_id: str
    boundary_id: Optional[int] = None
    node_type: str
    ref_id: int
    label: Optional[str] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    created_at: Optional[str] = None

class EdgeCreateRequest(BaseModel):
    """엣지 생성 요청"""
    boundary_id: Optional[int] = Field(None, description="속한 경계")
    sourcenode_id: str = Field(..., description="시작 노드")
    targetnode_id: str = Field(..., description="도착 노드")
    flow_type: str = Field(..., description="흐름 유형")
    label: Optional[str] = Field(None, description="화면 표시용 라벨")

class EdgeResponse(BaseModel):
    """엣지 응답"""
    edge_id: str
    boundary_id: Optional[int] = None
    sourcenode_id: str
    targetnode_id: str
    flow_type: str
    label: Optional[str] = None
    created_at: Optional[str] = None

class ProductionEmissionCreateRequest(BaseModel):
    """생산 배출량 생성 요청"""
    product_id: int = Field(..., description="대상 제품")
    boundary_id: int = Field(..., description="대상 경계")
    result_unit_id: Optional[int] = Field(None, description="결과 단위")
    dir_emission: float = Field(..., description="간접귀속배출량")
    indir_emission: float = Field(..., description="직접귀속배출량")
    see: float = Field(..., description="제품 고유 내재배출량")

class ProductionEmissionResponse(BaseModel):
    """생산 배출량 응답"""
    prod_result_id: int
    product_id: int
    boundary_id: int
    result_unit_id: Optional[int] = None
    dir_emission: float
    indir_emission: float
    see: float
    created_at: Optional[str] = None