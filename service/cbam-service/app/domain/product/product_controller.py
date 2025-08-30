# ============================================================================
# 🏭 Install Controller - 사업장 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List

from .install_service import InstallService
from .install_schema import (
    InstallCreateRequest, InstallResponse, InstallUpdateRequest, InstallNameResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/install", tags=["Install"])

# 서비스 인스턴스는 요청 시마다 생성 (모듈 레벨 초기화 방지)
def get_install_service():
    """Install 서비스 인스턴스 반환"""
    return InstallService()

# ============================================================================
# 🏭 Install 관련 엔드포인트
# ============================================================================

@router.get("/", response_model=List[InstallResponse])
async def get_installs():
    """사업장 목록 조회"""
    try:
        logger.info("📋 사업장 목록 조회 요청")
        install_service = get_install_service()
        installs = await install_service.get_installs()
        logger.info(f"✅ 사업장 목록 조회 성공: {len(installs)}개")
        return installs
    except Exception as e:
        logger.error(f"❌ 사업장 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/names", response_model=List[InstallNameResponse])
async def get_install_names():
    """사업장명 목록 조회 (드롭다운용)"""
    try:
        logger.info("📋 사업장명 목록 조회 요청")
        install_service = get_install_service()
        install_names = await install_service.get_install_names()
        logger.info(f"✅ 사업장명 목록 조회 성공: {len(install_names)}개")
        return install_names
    except Exception as e:
        logger.error(f"❌ 사업장명 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장명 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/{install_id}", response_model=InstallResponse)
async def get_install(install_id: int):
    """특정 사업장 조회"""
    try:
        logger.info(f"📋 사업장 조회 요청: ID {install_id}")
        install_service = get_install_service()
        install = await install_service.get_install(install_id)
        if not install:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 조회 성공: ID {install_id}")
        return install
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/", response_model=InstallResponse)
async def create_install(request: InstallCreateRequest):
    """사업장 생성"""
    try:
        logger.info(f"📝 사업장 생성 요청: {request.install_name}")
        install_service = get_install_service()
        install = await install_service.create_install(request)
        if not install:
            raise HTTPException(status_code=400, detail="사업장 생성에 실패했습니다")
        
        logger.info(f"✅ 사업장 생성 성공: ID {install.id}")
        return install
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/{install_id}", response_model=InstallResponse)
async def update_install(install_id: int, request: InstallUpdateRequest):
    """사업장 수정"""
    try:
        logger.info(f"📝 사업장 수정 요청: ID {install_id}")
        install_service = get_install_service()
        install = await install_service.update_install(install_id, request)
        if not install:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 수정 성공: ID {install_id}")
        return install
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/{install_id}")
async def delete_install(install_id: int):
    """사업장 삭제"""
    try:
        logger.info(f"🗑️ 사업장 삭제 요청: ID {install_id}")
        install_service = get_install_service()
        success = await install_service.delete_install(install_id)
        if not success:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 삭제 성공: ID {install_id}")
        return {"message": "사업장이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 Router Export
# ============================================================================

# install_router를 다른 모듈에서 import할 수 있도록 export
install_router = router
__all__ = ["router", "install_router"]

# 📦 Product Controller - 제품 API 엔드포인트
from fastapi import APIRouter, HTTPException
import logging
from typing import List
from .product_service import ProductService
from .product_schema import (
    ProductCreateRequest, ProductResponse, ProductUpdateRequest, ProductNameResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/product", tags=["Product"])

def get_product_service():
    """Product 서비스 인스턴스 반환"""
    return ProductService()

@router.get("/", response_model=List[ProductResponse])
async def get_products():
    """제품 목록 조회"""
    try:
        logger.info("📋 제품 목록 조회 요청")
        product_service = get_product_service()
        products = await product_service.get_products()
        logger.info(f"✅ 제품 목록 조회 성공: {len(products)}개")
        return products
    except Exception as e:
        logger.error(f"❌ 제품 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/names", response_model=List[ProductNameResponse])
async def get_product_names():
    """제품명 목록 조회 (드롭다운용)"""
    try:
        logger.info("📋 제품명 목록 조회 요청")
        product_service = get_product_service()
        product_names = await product_service.get_product_names()
        logger.info(f"✅ 제품명 목록 조회 성공: {len(product_names)}개")
        return product_names
    except Exception as e:
        logger.error(f"❌ 제품명 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품명 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """특정 제품 조회"""
    try:
        logger.info(f"📋 제품 조회 요청: ID {product_id}")
        product_service = get_product_service()
        product = await product_service.get_product(product_id)
        
        if not product:
            logger.warning(f"⚠️ 제품을 찾을 수 없음: ID {product_id}")
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다.")
        
        logger.info(f"✅ 제품 조회 성공: ID {product_id}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 조회 실패: ID {product_id}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest):
    """제품 생성"""
    try:
        logger.info(f"📋 제품 생성 요청: {request.product_name}")
        product_service = get_product_service()
        product = await product_service.create_product(request)
        logger.info(f"✅ 제품 생성 성공: ID {product.id}")
        return product
    except Exception as e:
        logger.error(f"❌ 제품 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, request: ProductUpdateRequest):
    """제품 수정"""
    try:
        logger.info(f"📋 제품 수정 요청: ID {product_id}")
        product_service = get_product_service()
        product = await product_service.update_product(product_id, request)
        
        if not product:
            logger.warning(f"⚠️ 수정할 제품을 찾을 수 없음: ID {product_id}")
            raise HTTPException(status_code=404, detail="수정할 제품을 찾을 수 없습니다.")
        
        logger.info(f"✅ 제품 수정 성공: ID {product_id}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 수정 실패: ID {product_id}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """제품 삭제"""
    try:
        logger.info(f"📋 제품 삭제 요청: ID {product_id}")
        product_service = get_product_service()
        success = await product_service.delete_product(product_id)
        
        if not success:
            logger.warning(f"⚠️ 삭제할 제품을 찾을 수 없음: ID {product_id}")
            raise HTTPException(status_code=404, detail="삭제할 제품을 찾을 수 없습니다.")
        
        logger.info(f"✅ 제품 삭제 성공: ID {product_id}")
        return {"message": "제품이 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 삭제 실패: ID {product_id}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 삭제 중 오류가 발생했습니다: {str(e)}")

product_router = router
__all__ = ["router", "product_router"]
