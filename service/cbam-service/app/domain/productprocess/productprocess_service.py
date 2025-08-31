# ============================================================================
# 🔗 ProductProcess Service - 제품-공정 관계 비즈니스 로직
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.domain.productprocess.productprocess_repository import ProductProcessRepository
from app.domain.productprocess.productprocess_schema import (
    ProductProcessCreateRequest, ProductProcessResponse,
    ProductProcessUpdateRequest, ProductProcessSearchRequest,
    ProductProcessFullResponse, ProductProcessByProductResponse,
    ProductProcessByProcessResponse, ProductProcessStatsResponse
)

logger = logging.getLogger(__name__)

class ProductProcessService:
    """제품-공정 관계 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.product_process_repository = ProductProcessRepository()
        logger.info("✅ ProductProcess 서비스 초기화 완료")
    
    async def initialize(self):
        """서비스 초기화"""
        try:
            await self.product_process_repository.initialize()
            logger.info("✅ ProductProcess 서비스 데이터베이스 초기화 완료")
        except Exception as e:
            logger.error(f"❌ ProductProcess 서비스 초기화 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔗 ProductProcess 관련 메서드 (다대다 관계)
    # ============================================================================

    async def create_product_process(self, request: ProductProcessCreateRequest) -> ProductProcessResponse:
        """제품-공정 관계 생성"""
        try:
            logger.info(f"🔄 제품-공정 관계 생성 요청: 제품 ID {request.product_id}, 공정 ID {request.process_id}")
            
            # Repository를 통해 제품-공정 관계 생성
            saved_product_process = await self.product_process_repository.create_product_process({
                'product_id': request.product_id,
                'process_id': request.process_id
            })
            
            logger.info(f"✅ 제품-공정 관계 생성 성공: ID {saved_product_process['id']}")
            return ProductProcessResponse(**saved_product_process)
            
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 생성 실패: {str(e)}")
            raise

    async def get_product_process_by_id(self, relation_id: int) -> Optional[ProductProcessFullResponse]:
        """ID로 제품-공정 관계 조회"""
        try:
            logger.info(f"🔍 제품-공정 관계 조회 요청: ID {relation_id}")
            
            result = await self.product_process_repository.get_product_process_by_id(relation_id)
            
            if result:
                logger.info(f"✅ 제품-공정 관계 조회 성공: ID {relation_id}")
                return ProductProcessFullResponse(**result)
            else:
                logger.warning(f"⚠️ 제품-공정 관계를 찾을 수 없음: ID {relation_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 조회 실패: {str(e)}")
            raise

    async def get_all_product_processes(self, skip: int = 0, limit: int = 100) -> List[ProductProcessFullResponse]:
        """모든 제품-공정 관계 조회"""
        try:
            logger.info(f"🔍 제품-공정 관계 목록 조회 요청: skip={skip}, limit={limit}")
            
            results = await self.product_process_repository.get_all_product_processes(skip, limit)
            
            logger.info(f"✅ 제품-공정 관계 목록 조회 성공: {len(results)}개")
            return [ProductProcessFullResponse(**result) for result in results]
            
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 목록 조회 실패: {str(e)}")
            raise

    async def update_product_process(self, relation_id: int, request: ProductProcessUpdateRequest) -> Optional[ProductProcessResponse]:
        """제품-공정 관계 수정"""
        try:
            logger.info(f"🔄 제품-공정 관계 수정 요청: ID {relation_id}")
            
            # 업데이트할 필드들만 추출
            update_data = {}
            if request.product_id is not None:
                update_data['product_id'] = request.product_id
            if request.process_id is not None:
                update_data['process_id'] = request.process_id
            
            if not update_data:
                raise Exception("수정할 필드가 없습니다.")
            
            # 제품-공정 관계는 기본적으로 수정이 제한적이므로, 삭제 후 재생성하는 방식 사용
            # 기존 관계 조회
            existing = await self.product_process_repository.get_product_process_by_id(relation_id)
            if not existing:
                logger.warning(f"⚠️ 제품-공정 관계를 찾을 수 없음: ID {relation_id}")
                return None
            
            # 기존 관계 삭제
            await self.product_process_repository.delete_product_process(existing['product_id'], existing['process_id'])
            
            # 새로운 관계 생성
            new_data = {
                'product_id': update_data.get('product_id', existing['product_id']),
                'process_id': update_data.get('process_id', existing['process_id'])
            }
            
            result = await self.product_process_repository.create_product_process(new_data)
            
            logger.info(f"✅ 제품-공정 관계 수정 성공: ID {relation_id}")
            return ProductProcessResponse(**result)
                
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 수정 실패: {str(e)}")
            raise

    async def delete_product_process(self, product_id: int, process_id: int) -> bool:
        """제품-공정 관계 삭제"""
        try:
            logger.info(f"🗑️ 제품-공정 관계 삭제 요청: 제품 ID {product_id}, 공정 ID {process_id}")
            
            success = await self.product_process_repository.delete_product_process(product_id, process_id)
            
            if success:
                logger.info(f"✅ 제품-공정 관계 삭제 성공: 제품 ID {product_id}, 공정 ID {process_id}")
            else:
                logger.warning(f"⚠️ 제품-공정 관계를 찾을 수 없음: 제품 ID {product_id}, 공정 ID {process_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 삭제 실패: {str(e)}")
            raise

    async def get_product_processes_by_product(self, product_id: int) -> ProductProcessByProductResponse:
        """제품별 제품-공정 관계 조회"""
        try:
            logger.info(f"🔍 제품별 제품-공정 관계 조회 요청: 제품 ID {product_id}")
            
            relations = await self.product_process_repository.get_product_processes_by_product(product_id)
            
            # 제품명 가져오기 (첫 번째 결과에서)
            product_name = relations[0]['product_name'] if relations else "Unknown Product"
            
            logger.info(f"✅ 제품별 제품-공정 관계 조회 성공: {len(relations)}개")
            
            return ProductProcessByProductResponse(
                product_id=product_id,
                product_name=product_name,
                processes=[ProductProcessFullResponse(**relation) for relation in relations]
            )
            
        except Exception as e:
            logger.error(f"❌ 제품별 제품-공정 관계 조회 실패: {str(e)}")
            raise

    async def get_product_processes_by_process(self, process_id: int) -> ProductProcessByProcessResponse:
        """공정별 제품-공정 관계 조회"""
        try:
            logger.info(f"🔍 공정별 제품-공정 관계 조회 요청: 공정 ID {process_id}")
            
            relations = await self.product_process_repository.get_product_processes_by_process(process_id)
            
            # 공정명 가져오기 (첫 번째 결과에서)
            process_name = relations[0]['process_name'] if relations else "Unknown Process"
            
            logger.info(f"✅ 공정별 제품-공정 관계 조회 성공: {len(relations)}개")
            
            return ProductProcessByProcessResponse(
                process_id=process_id,
                process_name=process_name,
                products=[ProductProcessFullResponse(**relation) for relation in relations]
            )
            
        except Exception as e:
            logger.error(f"❌ 공정별 제품-공정 관계 조회 실패: {str(e)}")
            raise

    async def search_product_processes(self, request: ProductProcessSearchRequest) -> List[ProductProcessFullResponse]:
        """제품-공정 관계 검색"""
        try:
            logger.info(f"🔍 제품-공정 관계 검색 요청: {request}")
            
            filters = {
                'product_id': request.product_id,
                'process_id': request.process_id,
                'skip': request.skip,
                'limit': request.limit
            }
            
            # None 값 제거
            filters = {k: v for k, v in filters.items() if v is not None}
            
            results = await self.product_process_repository.search_product_processes(**filters)
            
            logger.info(f"✅ 제품-공정 관계 검색 성공: {len(results)}개")
            return [ProductProcessFullResponse(**result) for result in results]
            
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 검색 실패: {str(e)}")
            raise

    async def get_product_process_stats(self) -> ProductProcessStatsResponse:
        """제품-공정 관계 통계 조회"""
        try:
            logger.info("📊 제품-공정 관계 통계 조회 요청")
            
            stats = await self.product_process_repository.get_product_process_stats()
            
            logger.info("✅ 제품-공정 관계 통계 조회 성공")
            return ProductProcessStatsResponse(**stats)
            
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 통계 조회 실패: {str(e)}")
            raise

    async def create_product_processes_batch(self, relations: List[ProductProcessCreateRequest]) -> Dict[str, Any]:
        """제품-공정 관계 일괄 생성"""
        try:
            logger.info(f"🔄 제품-공정 관계 일괄 생성 요청: {len(relations)}개")
            
            # 스키마를 딕셔너리로 변환
            relations_data = []
            for relation in relations:
                relation_dict = {
                    'product_id': relation.product_id,
                    'process_id': relation.process_id
                }
                relations_data.append(relation_dict)
            
            result = await self.product_process_repository.create_product_processes_batch(relations_data)
            
            logger.info(f"✅ 제품-공정 관계 일괄 생성 완료: {result['created_count']}개 성공, {result['failed_count']}개 실패")
            return result
            
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 일괄 생성 실패: {str(e)}")
            raise
