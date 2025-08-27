# ============================================================================
# 📋 Calculation Schema - Product 데이터 모델
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import date, datetime

if TYPE_CHECKING:
    from .calculation_schema import ProcessResponse, ProductResponse

# ============================================================================
# 🏭 Install 관련 스키마
# ============================================================================

class InstallNameResponse(BaseModel):
    """사업장명 응답 (드롭다운용)"""
    id: int = Field(..., description="사업장 ID")
    install_name: str = Field(..., description="사업장명")

class InstallCreateRequest(BaseModel):
    """사업장 생성 요청"""
    install_name: str = Field(..., description="사업장명")
    reporting_year: int = Field(default=datetime.now().year, description="보고기간 (년도)")

class InstallResponse(BaseModel):
    """사업장 응답"""
    id: int = Field(..., description="사업장 ID")
    install_name: str = Field(..., description="사업장명")
    reporting_year: int = Field(..., description="보고기간 (년도)")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")

class InstallUpdateRequest(BaseModel):
    """사업장 수정 요청"""
    install_name: Optional[str] = Field(None, description="사업장명")
    reporting_year: Optional[int] = Field(None, description="보고기간 (년도)")

# ============================================================================
# 📦 Product 관련 스키마
# ============================================================================

class ProductNameResponse(BaseModel):
    """제품명 응답 (드롭다운용)"""
    id: int = Field(..., description="제품 ID")
    product_name: str = Field(..., description="제품명")

class ProductCreateRequest(BaseModel):
    """제품 생성 요청"""
    install_id: int = Field(..., description="사업장 ID")
    product_name: str = Field(..., description="제품명")
    product_category: str = Field(..., description="제품 카테고리 (단순제품/복합제품)")
    prostart_period: date = Field(..., description="기간 시작일")
    proend_period: date = Field(..., description="기간 종료일")
    product_amount: float = Field(..., description="제품 수량")
    product_cncode: Optional[str] = Field(None, description="제품 CN 코드")
    goods_name: Optional[str] = Field(None, description="품목명")
    aggrgoods_name: Optional[str] = Field(None, description="품목군명")
    product_sell: Optional[float] = Field(None, description="제품 판매량")
    product_eusell: Optional[float] = Field(None, description="제품 EU 판매량")

class ProductResponse(BaseModel):
    """제품 응답"""
    id: int = Field(..., description="제품 ID")
    install_id: int = Field(..., description="사업장 ID")
    product_name: str = Field(..., description="제품명")
    product_category: str = Field(..., description="제품 카테고리")
    prostart_period: str = Field(..., description="기간 시작일")
    proend_period: str = Field(..., description="기간 종료일")
    product_amount: float = Field(..., description="제품 수량")
    product_cncode: Optional[str] = Field(None, description="제품 CN 코드")
    goods_name: Optional[str] = Field(None, description="품목명")
    aggrgoods_name: Optional[str] = Field(None, description="품목군명")
    product_sell: Optional[float] = Field(None, description="제품 판매량")
    product_eusell: Optional[float] = Field(None, description="제품 EU 판매량")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")
    # 다대다 관계를 위한 공정 정보
    processes: Optional[List[Dict[str, Any]]] = Field(None, description="연결된 공정들")

class ProductUpdateRequest(BaseModel):
    """제품 수정 요청"""
    install_id: Optional[int] = Field(None, description="사업장 ID")
    product_name: Optional[str] = Field(None, description="제품명")
    product_category: Optional[str] = Field(None, description="제품 카테고리")
    prostart_period: Optional[str] = Field(None, description="기간 시작일")
    proend_period: Optional[str] = Field(None, description="기간 종료일")
    product_amount: Optional[float] = Field(None, description="제품 수량")
    product_cncode: Optional[str] = Field(None, description="제품 CN 코드")
    goods_name: Optional[str] = Field(None, description="품목명")
    aggrgoods_name: Optional[str] = Field(None, description="품목군명")
    product_sell: Optional[float] = Field(None, description="제품 판매량")
    product_eusell: Optional[float] = Field(None, description="제품 EU 판매량")

# ============================================================================
# 🔗 ProductProcess 관련 스키마
# ============================================================================

class ProductProcessCreateRequest(BaseModel):
    """제품-공정 관계 생성 요청"""
    product_id: int = Field(..., description="제품 ID")
    process_id: int = Field(..., description="공정 ID")

class ProductProcessResponse(BaseModel):
    """제품-공정 관계 응답"""
    id: int = Field(..., description="관계 ID")
    product_id: int = Field(..., description="제품 ID")
    process_id: int = Field(..., description="공정 ID")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")

# ============================================================================
# 🔄 Process 관련 스키마
# ============================================================================

class ProcessCreateRequest(BaseModel):
    """프로세스 생성 요청"""
    process_name: str = Field(..., description="공정명")
    start_period: Optional[date] = Field(None, description="시작일")
    end_period: Optional[date] = Field(None, description="종료일")
    product_ids: Optional[List[int]] = Field([], description="연결할 제품 ID 목록 (다대다 관계)")

class ProcessResponse(BaseModel):
    """프로세스 응답"""
    id: int = Field(..., description="공정 ID")
    process_name: str = Field(..., description="공정명")
    start_period: Optional[str] = Field(None, description="시작일")
    end_period: Optional[str] = Field(None, description="종료일")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")
    # 다대다 관계를 위한 제품 정보 (순환 참조 방지를 위해 Dict 사용)
    products: Optional[List[Dict[str, Any]]] = Field(None, description="연결된 제품들")

class ProcessUpdateRequest(BaseModel):
    """프로세스 수정 요청"""
    process_name: Optional[str] = Field(None, description="공정명")
    start_period: Optional[date] = Field(None, description="시작일")
    end_period: Optional[date] = Field(None, description="종료일")

# ============================================================================
# 📥 ProcessInput 관련 스키마
# ============================================================================

class ProcessInputCreateRequest(BaseModel):
    """프로세스 입력 생성 요청"""
    process_id: int = Field(..., description="프로세스 ID")
    input_type: str = Field(..., description="입력 타입 (material, fuel, electricity)")
    input_name: str = Field(..., description="투입물명")
    amount: float = Field(..., description="수량")
    factor: Optional[float] = Field(None, description="배출계수")
    oxy_factor: Optional[float] = Field(None, description="산화계수")

class ProcessInputResponse(BaseModel):
    """프로세스 입력 응답"""
    id: int = Field(..., description="프로세스 입력 ID")
    process_id: int = Field(..., description="프로세스 ID")
    input_type: str = Field(..., description="입력 타입")
    input_name: str = Field(..., description="투입물명")
    input_amount: float = Field(..., description="투입물량")
    factor: Optional[float] = Field(None, description="배출계수")
    oxy_factor: Optional[float] = Field(None, description="산화계수")
    direm: Optional[float] = Field(None, description="직접배출량")
    indirem: Optional[float] = Field(None, description="간접배출량")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")

class ProcessInputUpdateRequest(BaseModel):
    """공정 입력 수정 요청"""
    input_type: Optional[str] = Field(None, description="입력 타입")
    input_name: Optional[str] = Field(None, description="입력명")
    input_amount: Optional[float] = Field(None, description="투입물량")
    factor: Optional[float] = Field(None, description="배출계수")
    oxy_factor: Optional[float] = Field(None, description="산화계수")

# ============================================================================
# 🧮 배출량 계산 관련 스키마
# ============================================================================

class EmissionCalculationRequest(BaseModel):
    """배출량 계산 요청"""
    process_id: int = Field(..., description="공정 ID")

class EmissionCalculationResponse(BaseModel):
    """배출량 계산 응답"""
    process_id: int = Field(..., description="공정 ID")
    total_direm: float = Field(..., description="총 직접배출량")
    total_indirem: float = Field(..., description="총 간접배출량")
    total_em: float = Field(..., description="총 배출량")
    calculation_details: List[Dict[str, Any]] = Field(..., description="계산 상세")

class ProductEmissionResponse(BaseModel):
    """제품별 배출량 응답"""
    product_id: int = Field(..., description="제품 ID")
    product_name: str = Field(..., description="제품명")
    total_em: float = Field(..., description="총 배출량")
    direm: float = Field(..., description="직접배출량")
    indirem: float = Field(..., description="간접배출량")
    processes: List[Dict[str, Any]] = Field(..., description="관련 프로세스")