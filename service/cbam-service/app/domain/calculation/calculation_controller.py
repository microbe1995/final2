# ============================================================================
# 🎮 Calculation Controller - Product API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from loguru import logger
import time

from .calculation_service import CalculationService
from .calculation_schema import ProductCreateRequest, ProductResponse, ProductUpdateRequest

router = APIRouter(prefix="", tags=["Product"])

# 서비스 인스턴스 생성
calculation_service = CalculationService()

# ============================================================================
# 📦 Product 관련 엔드포인트 (단수형으로 통일)
# ============================================================================

@router.get("/product", response_model=List[ProductResponse])
async def get_products():
    """제품 목록 조회"""
    try:
        logger.info("📋 제품 목록 조회 요청")
        products = await calculation_service.get_products()
        logger.info(f"✅ 제품 목록 조회 성공: {len(products)}개")
        return products
    except Exception as e:
        logger.error(f"❌ 제품 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/product/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """특정 제품 조회"""
    try:
        logger.info(f"📋 제품 조회 요청: ID {product_id}")
        product = await calculation_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 조회 성공: ID {product_id}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/product", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest):
    """제품 생성"""
    try:
        logger.info(f"📦 제품 생성 요청: {request.product_name}")
        result = await calculation_service.create_product(request)
        logger.info(f"✅ 제품 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 제품 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/product/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, request: ProductUpdateRequest):
    """제품 수정"""
    try:
        logger.info(f"📝 제품 수정 요청: ID {product_id}")
        result = await calculation_service.update_product(product_id, request)
        if not result:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 수정 성공: ID {product_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/product/{product_id}")
async def delete_product(product_id: int):
    """제품 삭제"""
    try:
        logger.info(f"🗑️ 제품 삭제 요청: ID {product_id}")
        success = await calculation_service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 삭제 성공: ID {product_id}")
        return {"message": "제품이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 삭제 중 오류가 발생했습니다: {str(e)}")