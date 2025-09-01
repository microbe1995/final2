# ============================================================================
# 📦 Product Schema - 제품 API 스키마
# ============================================================================

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Dict, Any

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
    product_amount: Optional[float] = Field(0.0, description="제품 수량")
    cncode_total: Optional[str] = Field(None, description="제품 CN 코드")
    goods_name: Optional[str] = Field(None, description="품목명")
    goods_engname: Optional[str] = Field(None, description="품목영문명")
    aggrgoods_name: Optional[str] = Field(None, description="품목군명")
    aggrgoods_engname: Optional[str] = Field(None, description="품목군영문명")
    product_sell: Optional[float] = Field(0.0, description="제품 판매량")
    product_eusell: Optional[float] = Field(0.0, description="제품 EU 판매량")
    attr_em: Optional[float] = Field(0.0, description="제품 배출량")

class ProductResponse(BaseModel):
    """제품 응답"""
    id: int = Field(..., description="제품 ID")
    install_id: int = Field(..., description="사업장 ID")
    product_name: str = Field(..., description="제품명")
    product_category: str = Field(..., description="제품 카테고리")
    prostart_period: date = Field(..., description="기간 시작일")
    proend_period: date = Field(..., description="기간 종료일")
    product_amount: Optional[float] = Field(0.0, description="제품 수량")
    cncode_total: Optional[str] = Field(None, description="제품 CN 코드")
    goods_name: Optional[str] = Field(None, description="품목명")
    goods_engname: Optional[str] = Field(None, description="품목영문명")
    aggrgoods_name: Optional[str] = Field(None, description="품목군명")
    aggrgoods_engname: Optional[str] = Field(None, description="품목군영문명")
    product_sell: Optional[float] = Field(None, description="제품 판매량")
    product_eusell: Optional[float] = Field(None, description="제품 EU 판매량")
    attr_em: Optional[float] = Field(None, description="제품 배출량")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")
    # 다대다 관계를 위한 공정 정보
    processes: Optional[List[Dict[str, Any]]] = Field(None, description="연결된 공정들")

class ProductUpdateRequest(BaseModel):
    """제품 수정 요청"""
    install_id: Optional[int] = Field(None, description="사업장 ID")
    product_name: Optional[str] = Field(None, description="제품명")
    product_category: Optional[str] = Field(None, description="제품 카테고리")
    prostart_period: Optional[date] = Field(None, description="기간 시작일")
    proend_period: Optional[date] = Field(None, description="기간 종료일")
    product_amount: Optional[float] = Field(None, description="제품 수량")
    cncode_total: Optional[str] = Field(None, description="제품 CN 코드")
    goods_name: Optional[str] = Field(None, description="품목명")
    goods_engname: Optional[str] = Field(None, description="품목영문명")
    aggrgoods_name: Optional[str] = Field(None, description="품목군명")
    aggrgoods_engname: Optional[str] = Field(None, description="품목군영문명")
    product_sell: Optional[float] = Field(None, description="제품 판매량")
    product_eusell: Optional[float] = Field(None, description="제품 EU 판매량")
    attr_em: Optional[float] = Field(None, description="제품 배출량")

    class Config:
        from_attributes = True
