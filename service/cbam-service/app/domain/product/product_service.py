# ============================================================================
# 🏭 Install Service - 사업장 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .install_repository import InstallRepository
from .install_schema import (
    InstallCreateRequest, InstallResponse, InstallUpdateRequest, InstallNameResponse
)

logger = logging.getLogger(__name__)

class InstallService:
    """사업장 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.install_repository = InstallRepository()
        logger.info("✅ Install 서비스 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.install_repository.initialize()
            logger.info("✅ Install 서비스 데이터베이스 연결 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Install 서비스 데이터베이스 초기화 실패 (서비스는 계속 실행): {e}")
            logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    # ============================================================================
    # 🏭 Install 관련 메서드
    # ============================================================================
    
    async def create_install(self, request: InstallCreateRequest) -> InstallResponse:
        """사업장 생성"""
        try:
            install_data = {
                "install_name": request.install_name,
                "reporting_year": request.reporting_year
            }
            
            saved_install = await self.install_repository.create_install(install_data)
            if saved_install:
                return InstallResponse(**saved_install)
            else:
                raise Exception("사업장 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error creating install: {e}")
            raise e
    
    async def get_installs(self) -> List[InstallResponse]:
        """사업장 목록 조회"""
        try:
            installs = await self.install_repository.get_installs()
            return [InstallResponse(**install) for install in installs]
        except Exception as e:
            logger.error(f"Error getting installs: {e}")
            raise e
    
    async def get_install_names(self) -> List[InstallNameResponse]:
        """사업장명 목록 조회 (드롭다운용)"""
        try:
            install_names = await self.install_repository.get_install_names()
            return [InstallNameResponse(**install) for install in install_names]
        except Exception as e:
            logger.error(f"Error getting install names: {e}")
            raise e
    
    async def get_install(self, install_id: int) -> Optional[InstallResponse]:
        """특정 사업장 조회"""
        try:
            install = await self.install_repository.get_install(install_id)
            if install:
                return InstallResponse(**install)
            return None
        except Exception as e:
            logger.error(f"Error getting install {install_id}: {e}")
            raise e
    
    async def update_install(self, install_id: int, request: InstallUpdateRequest) -> Optional[InstallResponse]:
        """사업장 수정"""
        try:
            # None이 아닌 필드만 업데이트 데이터에 포함
            update_data = {}
            if request.install_name is not None:
                update_data["install_name"] = request.install_name
            if request.reporting_year is not None:
                update_data["reporting_year"] = request.reporting_year
            
            if not update_data:
                raise Exception("업데이트할 데이터가 없습니다.")
            
            updated_install = await self.install_repository.update_install(install_id, update_data)
            if updated_install:
                return InstallResponse(**updated_install)
            return None
        except Exception as e:
            logger.error(f"Error updating install {install_id}: {e}")
            raise e
    
    async def delete_install(self, install_id: int) -> bool:
        """사업장 삭제"""
        try:
            success = await self.install_repository.delete_install(install_id)
            if success:
                logger.info(f"✅ 사업장 삭제 성공: ID {install_id}")
            else:
                logger.warning(f"⚠️ 사업장 삭제 실패: ID {install_id} (존재하지 않음)")
            return success
        except Exception as e:
            logger.error(f"Error deleting install {install_id}: {e}")
            raise e

# 📦 Product Service - 제품 비즈니스 로직
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from .product_repository import ProductRepository
from .product_schema import (
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
                "cncode_total": request.cncode_total,
                "goods_name": request.goods_name,
                "goods_engname": request.goods_engname,
                "aggrgoods_name": request.aggrgoods_name,
                "aggrgoods_engname": request.aggrgoods_engname,
                "product_sell": request.product_sell,
                "product_eusell": request.product_eusell
            }
            
            saved_product = await self.product_repository.create_product(product_data)
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
            products = await self.product_repository.get_products()
            return [ProductResponse(**product) for product in products]
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise e
    
    async def get_product_names(self) -> List[ProductNameResponse]:
        """제품명 목록 조회 (드롭다운용)"""
        try:
            product_names = await self.product_repository.get_product_names()
            return [ProductNameResponse(**name) for name in product_names]
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
            # None이 아닌 값만 필터링
            update_data = {k: v for k, v in request.dict().items() if v is not None}
            
            if not update_data:
                raise Exception("수정할 데이터가 없습니다.")
            
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
            return await self.product_repository.delete_product(product_id)
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            raise e
