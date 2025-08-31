# ============================================================================
# 📦 Product Domain Package
# ============================================================================
"""
Product 도메인 패키지
제품(Product) 관련 기능을 제공합니다:
- 제품 생성, 조회, 수정, 삭제
- 제품명 목록 조회 (드롭다운용)
- 비동기 데이터베이스 연결 및 관리
"""
from app.domain.product.product_entity import Product
from app.domain.product.product_schema import (
    ProductCreateRequest, ProductResponse, ProductUpdateRequest, ProductNameResponse
)
from app.domain.product.product_repository import ProductRepository
from app.domain.product.product_service import ProductService
from app.domain.product.product_controller import router as product_router

__all__ = [
    "Product",
    "ProductCreateRequest", "ProductResponse", "ProductUpdateRequest", "ProductNameResponse",
    "ProductRepository",
    "ProductService",
    "product_router",
]
