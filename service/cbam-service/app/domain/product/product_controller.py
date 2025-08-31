# ============================================================================
# 🏭 Product Controller - 제품 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List

from app.domain.product.product_service import ProductService
from app.domain.product.product_schema import (
    ProductCreateRequest, ProductResponse, ProductUpdateRequest, ProductNameResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/product", tags=["Product"])

# 서비스 인스턴스는 요청 시마다 생성 (모듈 레벨 초기화 방지)
def get_product_service():
    """Product 서비스 인스턴스 반환"""
    return ProductService()

# ============================================================================
# 🏭 Product 관련 엔드포인트
# ============================================================================

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
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 조회 성공: ID {product_id}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest):
    """제품 생성"""
    try:
        logger.info(f"📝 제품 생성 요청: {request.product_name}")
        product_service = get_product_service()
        product = await product_service.create_product(request)
        if not product:
            raise HTTPException(status_code=400, detail="제품 생성에 실패했습니다")
        
        logger.info(f"✅ 제품 생성 성공: ID {product.id}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, request: ProductUpdateRequest):
    """제품 수정"""
    try:
        logger.info(f"📝 제품 수정 요청: ID {product_id}")
        product_service = get_product_service()
        product = await product_service.update_product(product_id, request)
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 수정 성공: ID {product_id}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """제품 삭제"""
    try:
        logger.info(f"🗑️ 제품 삭제 요청: ID {product_id}")
        product_service = get_product_service()
        success = await product_service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 삭제 성공: ID {product_id}")
        return {"message": "제품이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🔍 검색 및 필터링 엔드포인트
# ============================================================================

@router.get("/install/{install_id}", response_model=List[ProductResponse])
async def get_products_by_install(install_id: int):
    """사업장별 제품 목록 조회"""
    try:
        logger.info(f"🔍 사업장별 제품 조회 요청: 사업장 ID {install_id}")
        product_service = get_product_service()
        products = await product_service.get_products_by_install(install_id)
        logger.info(f"✅ 사업장별 제품 조회 성공: 사업장 ID {install_id} → {len(products)}개")
        return products
    except Exception as e:
        logger.error(f"❌ 사업장별 제품 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장별 제품 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/search/{search_term}", response_model=List[ProductResponse])
async def search_products(search_term: str):
    """제품 검색"""
    try:
        logger.info(f"🔍 제품 검색 요청: 검색어 '{search_term}'")
        product_service = get_product_service()
        products = await product_service.search_products(search_term)
        logger.info(f"✅ 제품 검색 성공: 검색어 '{search_term}' → {len(products)}개")
        return products
    except Exception as e:
        logger.error(f"❌ 제품 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 검색 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📊 통계 및 요약 엔드포인트
# ============================================================================

@router.get("/stats/summary")
async def get_product_summary():
    """제품 통계 요약"""
    try:
        logger.info("📊 제품 통계 요약 요청")
        product_service = get_product_service()
        all_products = await product_service.get_products()
        
        # 카테고리별 통계
        category_stats = {}
        for product in all_products:
            category = product.product_category
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        # 총 제품 수
        total_products = len(all_products)
        
        summary = {
            "total_products": total_products,
            "category_stats": category_stats,
            "categories_count": len(category_stats)
        }
        
        logger.info(f"✅ 제품 통계 요약 성공: 총 {total_products}개, 카테고리 {len(category_stats)}개")
        return summary
        
    except Exception as e:
        logger.error(f"❌ 제품 통계 요약 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 통계 요약 중 오류가 발생했습니다: {str(e)}")
