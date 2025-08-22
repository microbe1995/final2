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
    name: str = Field(..., description="제품명")
    cn_code: Optional[str] = Field(None, description="CN 코드")
    period_start: Optional[date] = Field(None, description="기간 시작일")
    period_end: Optional[date] = Field(None, description="기간 종료일")
    production_qty: Optional[float] = Field(0, description="생산량")
    sales_qty: Optional[float] = Field(0, description="판매량")
    export_qty: Optional[float] = Field(0, description="수출량")
    inventory_qty: Optional[float] = Field(0, description="재고량")
    defect_rate: Optional[float] = Field(0, description="불량률")

class ProductResponse(BaseModel):
    """제품 응답"""
    product_id: int = Field(..., description="제품 ID")
    name: str = Field(..., description="제품명")
    cn_code: Optional[str] = Field(None, description="CN 코드")
    period_start: Optional[str] = Field(None, description="기간 시작일")
    period_end: Optional[str] = Field(None, description="기간 종료일")
    production_qty: float = Field(0, description="생산량")
    sales_qty: float = Field(0, description="판매량")
    export_qty: float = Field(0, description="수출량")
    inventory_qty: float = Field(0, description="재고량")
    defect_rate: float = Field(0, description="불량률")
    node_id: Optional[str] = Field(None, description="노드 ID")
    created_at: Optional[str] = Field(None, description="생성일시")