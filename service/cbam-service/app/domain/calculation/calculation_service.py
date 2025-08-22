# ============================================================================
# 🧮 Calculation Service - Product 비즈니스 로직
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.calculation.calculation_repository import CalculationRepository
from app.domain.calculation.calculation_schema import ProductCreateRequest, ProductResponse

logger = logging.getLogger(__name__)

class CalculationService:
    """Product 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.calc_repository = CalculationRepository()
        logger.info("✅ Product 서비스 초기화 완료")
    
    # ============================================================================
    # 📦 Product 관련 메서드
    # ============================================================================
    
    async def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        """제품 생성"""
        try:
            product_data = {
                "name": request.name,
                "cn_code": request.cn_code,
                "period_start": request.period_start,
                "period_end": request.period_end,
                "production_qty": request.production_qty or 0,
                "sales_qty": request.sales_qty or 0,
                "export_qty": request.export_qty or 0,
                "inventory_qty": request.inventory_qty or 0,
                "defect_rate": request.defect_rate or 0,
                "node_id": None
            }
            
            saved_product = await self.calc_repository.create_product(product_data)
            if saved_product:
                return ProductResponse(**saved_product)
            else:
                raise Exception("제품 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise e
    
    async def get_products(self) -> List[ProductResponse]:
        """제품 목록 조회"""
        try:
            products = await self.calc_repository.get_products()
            if products:
                return [ProductResponse(**product) for product in products]
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []