# ============================================================================
# 📋 Calculation Schema - Product 데이터 모델
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# ============================================================================
# 🏭 Install 관련 스키마
# ============================================================================

class InstallNameResponse(BaseModel):
    """사업장명 응답 (드롭다운용)"""
    id: int = Field(..., description="사업장 ID")
    name: str = Field(..., description="사업장명")

class InstallCreateRequest(BaseModel):
    """사업장 생성 요청"""
    name: str = Field(..., description="사업장명")

class InstallResponse(BaseModel):
    """사업장 응답"""
    id: int = Field(..., description="사업장 ID")
    name: str = Field(..., description="사업장명")

class InstallUpdateRequest(BaseModel):
    """사업장 수정 요청"""
    name: Optional[str] = Field(None, description="사업장명")

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
    goods_name: Optional[str] = Field(None, description="상품명")
    aggrgoods_name: Optional[str] = Field(None, description="집계 상품명")
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
    goods_name: Optional[str] = Field(None, description="상품명")
    aggrgoods_name: Optional[str] = Field(None, description="집계 상품명")
    product_sell: Optional[float] = Field(None, description="제품 판매량")
    product_eusell: Optional[float] = Field(None, description="제품 EU 판매량")

class ProductUpdateRequest(BaseModel):
    """제품 수정 요청"""
    install_id: Optional[int] = Field(None, description="사업장 ID")
    product_name: Optional[str] = Field(None, description="제품명")
    product_category: Optional[str] = Field(None, description="제품 카테고리")
    prostart_period: Optional[str] = Field(None, description="기간 시작일")
    proend_period: Optional[str] = Field(None, description="기간 종료일")
    product_amount: Optional[float] = Field(None, description="제품 수량")
    product_cncode: Optional[str] = Field(None, description="제품 CN 코드")
    goods_name: Optional[str] = Field(None, description="상품명")
    aggrgoods_name: Optional[str] = Field(None, description="집계 상품명")
    product_sell: Optional[float] = Field(None, description="제품 판매량")
    product_eusell: Optional[float] = Field(None, description="제품 EU 판매량")

# ============================================================================
# 🔄 Process 관련 스키마
# ============================================================================

class ProcessCreateRequest(BaseModel):
    """프로세스 생성 요청"""
    product_id: int = Field(..., description="제품 ID")
    process_name: str = Field(..., description="프로세스명")
    start_period: date = Field(..., description="시작일")
    end_period: date = Field(..., description="종료일")

class ProcessResponse(BaseModel):
    """프로세스 응답"""
    id: int = Field(..., description="프로세스 ID")
    product_id: int = Field(..., description="제품 ID")
    process_name: str = Field(..., description="프로세스명")
    start_period: str = Field(..., description="시작일")
    end_period: str = Field(..., description="종료일")

class ProcessUpdateRequest(BaseModel):
    """프로세스 수정 요청"""
    product_id: Optional[int] = Field(None, description="제품 ID")
    process_name: Optional[str] = Field(None, description="프로세스명")
    start_period: Optional[str] = Field(None, description="시작일")
    end_period: Optional[str] = Field(None, description="종료일")