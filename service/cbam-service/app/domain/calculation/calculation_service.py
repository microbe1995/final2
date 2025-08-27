# ============================================================================
# 🧮 Calculation Service - Product 비즈니스 로직
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.domain.calculation.calculation_repository import CalculationRepository
from app.domain.calculation.calculation_schema import ProductCreateRequest, ProductResponse, ProductUpdateRequest

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
                "install_id": request.install_id,
                "product_name": request.product_name,
                "product_category": request.product_category,
                "prostart_period": request.prostart_period,
                "proend_period": request.proend_period,
                "product_amount": request.product_amount,
                "product_cncode": request.product_cncode,
                "goods_name": request.goods_name,
                "aggrgoods_name": request.aggrgoods_name,
                "product_sell": request.product_sell,
                "product_eusell": request.product_eusell
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
            return [ProductResponse(**product) for product in products]
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise e
    
    async def get_product(self, product_id: int) -> Optional[ProductResponse]:
        """특정 제품 조회"""
        try:
            product = await self.calc_repository.get_product(product_id)
            if product:
                return ProductResponse(**product)
            return None
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            raise e
    
    async def update_product(self, product_id: int, request: ProductUpdateRequest) -> Optional[ProductResponse]:
        """제품 수정"""
        try:
            # None이 아닌 필드만 업데이트 데이터에 포함
            update_data = {}
            if request.install_id is not None:
                update_data["install_id"] = request.install_id
            if request.product_name is not None:
                update_data["product_name"] = request.product_name
            if request.product_category is not None:
                update_data["product_category"] = request.product_category
            if request.prostart_period is not None:
                update_data["prostart_period"] = request.prostart_period
            if request.proend_period is not None:
                update_data["proend_period"] = request.proend_period
            if request.product_amount is not None:
                update_data["product_amount"] = request.product_amount
            if request.product_cncode is not None:
                update_data["product_cncode"] = request.product_cncode
            if request.goods_name is not None:
                update_data["goods_name"] = request.goods_name
            if request.aggrgoods_name is not None:
                update_data["aggrgoods_name"] = request.aggrgoods_name
            if request.product_sell is not None:
                update_data["product_sell"] = request.product_sell
            if request.product_eusell is not None:
                update_data["product_eusell"] = request.product_eusell
            
            if not update_data:
                raise Exception("업데이트할 데이터가 없습니다.")
            
            updated_product = await self.calc_repository.update_product(product_id, update_data)
            if updated_product:
                return ProductResponse(**updated_product)
            return None
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            raise e
    
    async def delete_product(self, product_id: int) -> bool:
        """제품 삭제"""
        try:
            success = await self.calc_repository.delete_product(product_id)
            return success
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            raise e