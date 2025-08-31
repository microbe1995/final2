# ============================================================================
# 🏭 Product Service - 제품 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.product.product_repository import ProductRepository
from app.domain.product.product_schema import (
    ProductCreateRequest, ProductResponse, ProductUpdateRequest, ProductNameResponse
)

logger = logging.getLogger(__name__)

class ProductService:
    """제품 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.product_repository = ProductRepository()
        logger.info("✅ Product 서비스 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.product_repository.initialize()
            logger.info("✅ Product 서비스 데이터베이스 연결 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Product 서비스 데이터베이스 초기화 실패 (서비스는 계속 실행): {e}")
            logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    # ============================================================================
    # 🏭 Product 관련 메서드
    # ============================================================================
    
    async def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        """제품 생성 (5개 핵심 필드만)"""
        try:
            # 🔴 수정: 5개 핵심 필드만 처리
            product_data = {
                "install_id": request.install_id,
                "product_name": request.product_name or "",
                "product_category": request.product_category or "",
                "prostart_period": request.prostart_period,
                "proend_period": request.proend_period
            }
            
            # 🔴 추가: 필수 필드 검증
            if not product_data["install_id"]:
                raise ValueError("install_id는 필수입니다")
            if not product_data["product_name"]:
                raise ValueError("product_name은 필수입니다")
            if not product_data["product_category"]:
                raise ValueError("product_category는 필수입니다")
            if not product_data["prostart_period"]:
                raise ValueError("prostart_period는 필수입니다")
            if not product_data["proend_period"]:
                raise ValueError("proend_period는 필수입니다")
            
            # 🔴 추가: 디버깅을 위한 데이터 로깅
            logger.info(f"🔍 제품 생성 데이터: {product_data}")
            logger.info(f"🔍 필드 개수: {len(product_data)}")
            
            # 🔴 추가: 각 필드의 타입과 값 확인
            for key, value in product_data.items():
                logger.info(f"🔍 {key}: {value} (타입: {type(value)})")
            
            logger.info(f"🔍 최종 제품 데이터: {product_data}")
            logger.info(f"🔍 최종 데이터 타입: {type(product_data)}")
            
            # 🔴 추가: repository 호출 전 최종 확인
            logger.info(f"🔍 Repository 호출: create_product({product_data})")
            
            saved_product = await self.product_repository.create_product(product_data)
            if saved_product:
                logger.info(f"✅ 제품 생성 성공: {saved_product}")
                return ProductResponse(**saved_product)
            else:
                raise Exception("제품 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"❌ 제품 생성 실패: {e}")
            logger.error(f"❌ 요청 데이터: {request}")
            raise e
    
    async def get_products(self) -> List[ProductResponse]:
        """제품 목록 조회"""
        try:
            products = await self.product_repository.get_products()
            return [ProductResponse(**product) for product in products]
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise e
    
    async def get_product_names(self) -> List[ProductNameResponse]:
        """제품명 목록 조회 (드롭다운용)"""
        try:
            product_names = await self.product_repository.get_product_names()
            return [ProductNameResponse(**product) for product in product_names]
        except Exception as e:
            logger.error(f"Error getting product names: {e}")
            raise e
    
    async def get_product(self, product_id: int) -> Optional[ProductResponse]:
        """특정 제품 조회"""
        try:
            product = await self.product_repository.get_product(product_id)
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
            if request.cncode_total is not None:
                update_data["cncode_total"] = request.cncode_total
            if request.goods_name is not None:
                update_data["goods_name"] = request.goods_name
            if request.goods_engname is not None:
                update_data["goods_engname"] = request.goods_engname
            if request.aggrgoods_name is not None:
                update_data["aggrgoods_name"] = request.aggrgoods_name
            if request.aggrgoods_engname is not None:
                update_data["aggrgoods_engname"] = request.aggrgoods_engname
            if request.product_sell is not None:
                update_data["product_sell"] = request.product_sell
            if request.product_eusell is not None:
                update_data["product_eusell"] = request.product_eusell
            
            if not update_data:
                raise Exception("업데이트할 데이터가 없습니다.")
            
            updated_product = await self.product_repository.update_product(product_id, update_data)
            if updated_product:
                return ProductResponse(**updated_product)
            return None
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            raise e
    
    async def delete_product(self, product_id: int) -> bool:
        """제품 삭제"""
        try:
            success = await self.product_repository.delete_product(product_id)
            if success:
                logger.info(f"✅ 제품 {product_id} 삭제 성공")
            else:
                logger.warning(f"⚠️ 제품 {product_id}를 찾을 수 없음")
            return success
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            raise e
    
    async def get_products_by_install(self, install_id: int) -> List[ProductResponse]:
        """사업장별 제품 목록 조회"""
        try:
            products = await self.product_repository.get_products_by_install(install_id)
            return [ProductResponse(**product) for product in products]
        except Exception as e:
            logger.error(f"Error getting products by install {install_id}: {e}")
            raise e
    
    async def search_products(self, search_term: str) -> List[ProductResponse]:
        """제품 검색"""
        try:
            products = await self.product_repository.search_products(search_term)
            return [ProductResponse(**product) for product in products]
        except Exception as e:
            logger.error(f"Error searching products with term '{search_term}': {e}")
            raise e
