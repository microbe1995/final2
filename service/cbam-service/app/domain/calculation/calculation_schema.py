# ============================================================================
# 📋 Calculation Schema - Product 데이터 모델
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# ============================================================================
# 📦 Product 관련 스키마
# ============================================================================

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
    prostart_period: Optional[date] = Field(None, description="기간 시작일")
    proend_period: Optional[date] = Field(None, description="기간 종료일")
    product_amount: Optional[float] = Field(None, description="제품 수량")
    product_cncode: Optional[str] = Field(None, description="제품 CN 코드")
    goods_name: Optional[str] = Field(None, description="상품명")
    aggrgoods_name: Optional[str] = Field(None, description="집계 상품명")
    product_sell: Optional[float] = Field(None, description="제품 판매량")
    product_eusell: Optional[float] = Field(None, description="제품 EU 판매량")