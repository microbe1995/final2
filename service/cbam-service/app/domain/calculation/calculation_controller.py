# ============================================================================
# 🎮 Calculation Controller - Product API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from loguru import logger
import time

from .calculation_service import CalculationService
from .calculation_schema import ProductCreateRequest, ProductResponse

router = APIRouter(prefix="", tags=["Product"])

# 서비스 인스턴스 생성
calculation_service = CalculationService()

# ============================================================================
# 📦 Product 관련 엔드포인트
# ============================================================================

@router.get("/product", tags=["product"])
async def get_product_data():
    """제품 데이터 조회 (health 엔드포인트와 유사한 형태)"""
    try:
        logger.info("📋 제품 데이터 조회 요청")
        products = await calculation_service.get_products()
        
        # health 엔드포인트와 유사한 응답 형태
        response_data = {
            "status": "success",
            "service": "Cal_boundary Service",
            "version": "1.0.0",
            "timestamp": time.time(),
            "total_count": len(products),
            "products": [product.dict() for product in products]
        }
        
        logger.info(f"✅ 제품 데이터 조회 성공: {len(products)}개")
        return response_data
        
    except Exception as e:
        logger.error(f"❌ 제품 데이터 조회 실패: {str(e)}")
        return {
            "status": "error",
            "service": "Cal_boundary Service",
            "version": "1.0.0",
            "timestamp": time.time(),
            "message": "제품 데이터 조회 중 오류가 발생했습니다",
            "error": str(e),
            "products": []
        }

@router.post("/product", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest):
    """제품 생성"""
    try:
        logger.info(f"📦 제품 생성 요청: {request.name}")
        result = await calculation_service.create_product(request)
        logger.info(f"✅ 제품 생성 성공: {result.product_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 제품 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/products", response_model=List[ProductResponse])
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