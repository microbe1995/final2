# ============================================================================
# 🎭 Dummy Service - Dummy 데이터 관리 서비스
# ============================================================================

import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, date

from app.domain.dummy.dummy_repository import DummyRepository
from app.domain.dummy.dummy_schema import DummyDataCreateRequest, DummyDataUpdateRequest, DummyDataResponse

logger = logging.getLogger(__name__)

class DummyService:
    """Dummy 데이터 관리 서비스 (Repository 패턴)"""
    
    def __init__(self):
        self.repository = DummyRepository()
        self._initialized = False
        logger.info("✅ Dummy Service 초기화 완료")
    
    async def initialize(self):
        """서비스 초기화"""
        await self.repository.initialize()
        self._initialized = True
        logger.info("✅ Dummy Service 초기화 완료")
    
    async def create_dummy_data(self, data: DummyDataCreateRequest) -> Optional[int]:
        """Dummy 데이터 생성"""
        try:
            # Pydantic 모델을 딕셔너리로 변환
            data_dict = data.model_dump()
            
            # 날짜 필드 처리
            if data.투입일:
                data_dict['투입일'] = data.투입일
            if data.종료일:
                data_dict['종료일'] = data.종료일
            
            result = await self.repository.create_dummy_data(data_dict)
            if result:
                logger.info(f"✅ Dummy 데이터 생성 성공: ID {result}")
                return result
            else:
                logger.error("❌ Dummy 데이터 생성 실패")
                return None
                
        except Exception as e:
            logger.error(f"Dummy 데이터 생성 실패: {e}")
            return None
    
    async def get_dummy_data_by_id(self, data_id: int) -> Optional[DummyDataResponse]:
        """ID로 Dummy 데이터 조회"""
        try:
            data = await self.repository.get_dummy_data_by_id(data_id)
            if data:
                return DummyDataResponse(**data)
            return None
            
        except Exception as e:
            logger.error(f"Dummy 데이터 조회 실패: {e}")
            return None
    
    async def get_all_dummy_data(self, limit: int = 100, offset: int = 0) -> List[DummyDataResponse]:
        """모든 Dummy 데이터 조회 (페이징)"""
        try:
            data_list = await self.repository.get_all_dummy_data(limit, offset)
            return [DummyDataResponse(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"Dummy 데이터 목록 조회 실패: {e}")
            return []
    
    async def update_dummy_data(self, data_id: int, data: DummyDataUpdateRequest) -> bool:
        """Dummy 데이터 수정"""
        try:
            # None이 아닌 필드만 필터링
            update_data = {}
            for field, value in data.model_dump().items():
                if value is not None:
                    update_data[field] = value
            
            if not update_data:
                logger.warning("업데이트할 필드가 없습니다.")
                return False
            
            success = await self.repository.update_dummy_data(data_id, update_data)
            if success:
                logger.info(f"✅ Dummy 데이터 수정 성공: ID {data_id}")
                return True
            else:
                logger.error(f"❌ Dummy 데이터 수정 실패: ID {data_id}")
                return False
                
        except Exception as e:
            logger.error(f"Dummy 데이터 수정 실패: {e}")
            return False
    
    async def delete_dummy_data(self, data_id: int) -> bool:
        """Dummy 데이터 삭제"""
        try:
            success = await self.repository.delete_dummy_data(data_id)
            if success:
                logger.info(f"✅ Dummy 데이터 삭제 성공: ID {data_id}")
                return True
            else:
                logger.error(f"❌ Dummy 데이터 삭제 실패: ID {data_id}")
                return False
                
        except Exception as e:
            logger.error(f"Dummy 데이터 삭제 실패: {e}")
            return False
    
    async def search_dummy_data(self, search_term: str, limit: int = 100) -> List[DummyDataResponse]:
        """Dummy 데이터 검색"""
        try:
            data_list = await self.repository.search_dummy_data(search_term, limit)
            return [DummyDataResponse(**data) for data in data_list]
            
        except Exception as e:
            logger.error(f"Dummy 데이터 검색 실패: {e}")
            return []
    
    async def get_dummy_data_count(self) -> int:
        """Dummy 데이터 총 개수 조회"""
        try:
            return await self.repository.get_dummy_data_count()
        except Exception as e:
            logger.error(f"Dummy 데이터 개수 조회 실패: {e}")
            return 0
    
    async def get_dummy_data_by_process(self, process_name: str, limit: int = 100) -> List[DummyDataResponse]:
        """공정별 Dummy 데이터 조회"""
        try:
            # 검색을 통해 공정별 데이터 조회
            data_list = await self.repository.search_dummy_data(process_name, limit)
            # 공정명이 정확히 일치하는 데이터만 필터링
            filtered_data = [
                data for data in data_list 
                if data['공정'] == process_name
            ]
            return [DummyDataResponse(**data) for data in filtered_data]
            
        except Exception as e:
            logger.error(f"공정별 Dummy 데이터 조회 실패: {e}")
            return []
    
    async def get_all_dummy_data(self) -> List[dict]:
        """전체 더미 데이터 조회"""
        try:
            logger.info("🔍 전체 더미 데이터 조회 요청")
            
            all_data = await self.repository.get_all_dummy_data()
            
            logger.info(f"✅ 전체 더미 데이터 조회 성공: {len(all_data)}개")
            return all_data
            
        except Exception as e:
            logger.error(f"❌ 전체 더미 데이터 조회 실패: {str(e)}")
            return []

    async def get_unique_product_names(self) -> List[str]:
        """고유한 제품명 목록 조회"""
        try:
            product_names = await self.repository.get_unique_product_names()
            logger.info(f"✅ 고유 제품명 목록 조회 성공: {len(product_names)}개")
            return product_names
            
        except Exception as e:
            logger.error(f"❌ 고유 제품명 목록 조회 실패: {e}")
            return []

    async def get_unique_product_names_by_period(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[str]:
        """기간별 고유한 제품명 목록 조회"""
        try:
            logger.info(f"🔍 기간별 제품명 목록 조회 요청: {start_date} ~ {end_date}")
            
            product_names = await self.repository.get_unique_product_names_by_period(start_date, end_date)
            
            logger.info(f"✅ 기간별 제품명 목록 조회 성공: {len(product_names)}개")
            return product_names
            
        except Exception as e:
            logger.error(f"❌ 기간별 제품명 목록 조회 실패: {str(e)}")
            raise

    async def get_unique_process_names(self) -> List[str]:
        """고유한 공정명 목록 조회"""
        try:
            logger.info("🔍 고유 공정명 목록 조회 요청")
            
            process_names = await self.repository.get_unique_process_names()
            
            logger.info(f"✅ 고유 공정명 목록 조회 성공: {len(process_names)}개")
            return process_names
            
        except Exception as e:
            logger.error(f"❌ 고유 공정명 목록 조회 실패: {str(e)}")
            raise

    async def get_unique_process_names_by_period(self, start_period: str, end_period: str) -> List[str]:
        """기간별 고유한 공정명 목록 조회"""
        try:
            logger.info(f"🔍 기간별 공정명 목록 조회 요청: {start_period} ~ {end_period}")
            
            process_names = await self.repository.get_unique_process_names_by_period(start_period, end_period)
            
            logger.info(f"✅ 기간별 공정명 목록 조회 성공: {len(process_names)}개")
            return process_names
            
        except Exception as e:
            logger.error(f"❌ 기간별 공정명 목록 조회 실패: {str(e)}")
            raise

    async def get_unique_processes_by_product(self, product_name: str) -> List[str]:
        """특정 제품의 고유한 공정 목록 조회"""
        try:
            logger.info(f"🔍 제품 '{product_name}'의 공정 목록 조회 요청")
            
            processes = await self.repository.get_unique_processes_by_product(product_name)
            
            logger.info(f"✅ 제품 '{product_name}'의 공정 목록 조회 성공: {len(processes)}개")
            return processes
            
        except Exception as e:
            logger.error(f"❌ 제품 '{product_name}'의 공정 목록 조회 실패: {str(e)}")
            raise

    async def get_dummy_data_by_product(self, product_name: str, limit: int = 100) -> List[DummyDataResponse]:
        """생산품별 Dummy 데이터 조회"""
        try:
            # 검색을 통해 생산품별 데이터 조회
            data_list = await self.repository.search_dummy_data(product_name, limit)
            # 생산품명이 정확히 일치하는 데이터만 필터링
            filtered_data = [
                data for data in data_list 
                if data['생산품명'] == product_name
            ]
            return [DummyDataResponse(**data) for data in filtered_data]
            
        except Exception as e:
            logger.error(f"생산품별 Dummy 데이터 조회 실패: {e}")
            return []
    
    async def close(self):
        """서비스 종료"""
        await self.repository.close()
        logger.info("✅ Dummy Service 종료")
