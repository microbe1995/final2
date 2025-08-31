# ============================================================================
# 🎯 Mapping Service - HS-CN 매핑 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.domain.mapping.mapping_repository import HSCNMappingRepository
from app.domain.mapping.mapping_schema import (
    HSCNMappingCreateRequest, HSCNMappingUpdateRequest, HSCNMappingResponse,
    HSCNMappingFullResponse, HSCodeLookupResponse, MappingStatsResponse,
    HSCNMappingBatchCreateRequest, HSCNMappingBatchResponse
)

logger = logging.getLogger(__name__)

class HSCNMappingService:
    """HS-CN 매핑 비즈니스 로직 서비스"""
    
    def __init__(self, db: Session):
        self.repository = HSCNMappingRepository(db)
    
    # ============================================================================
    # 📋 기본 CRUD 작업
    # ============================================================================
    
    async def create_mapping(self, mapping_data: HSCNMappingCreateRequest) -> Optional[HSCNMappingFullResponse]:
        """HS-CN 매핑 생성"""
        try:
            # HS 코드 유효성 검증
            if not self._validate_hs_code(mapping_data.hscode):
                logger.error(f"❌ 유효하지 않은 HS 코드: {mapping_data.hscode}")
                return None
            
            # CN 코드 유효성 검증
            if not self._validate_cn_code(mapping_data.cncode_total):
                logger.error(f"❌ 유효하지 않은 CN 코드: {mapping_data.cncode_total}")
                return None
            
            mapping = await self.repository.create_mapping(mapping_data)
            if mapping:
                return HSCNMappingFullResponse(**mapping)
            return None
            
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 생성 실패: {str(e)}")
            return None
    
    async def get_mapping_by_id(self, mapping_id: int) -> Optional[HSCNMappingFullResponse]:
        """ID로 HS-CN 매핑 조회"""
        try:
            mapping = await self.repository.get_mapping_by_id(mapping_id)
            if mapping:
                return HSCNMappingFullResponse(**mapping)
            return None
            
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 조회 실패: {str(e)}")
            return None
    
    async def get_all_mappings(self, skip: int = 0, limit: int = 100) -> List[HSCNMappingFullResponse]:
        """모든 HS-CN 매핑 조회"""
        try:
            mappings = await self.repository.get_all_mappings(skip, limit)
            return [HSCNMappingFullResponse(**mapping) for mapping in mappings]
            
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 목록 조회 실패: {str(e)}")
            return []
    
    async def update_mapping(self, mapping_id: int, mapping_data: HSCNMappingUpdateRequest) -> Optional[HSCNMappingFullResponse]:
        """HS-CN 매핑 수정"""
        try:
            # HS 코드 유효성 검증 (제공된 경우)
            if mapping_data.hscode and not self._validate_hs_code(mapping_data.hscode):
                logger.error(f"❌ 유효하지 않은 HS 코드: {mapping_data.hscode}")
                return None
            
            # CN 코드 유효성 검증 (제공된 경우)
            if mapping_data.cncode_total and not self._validate_cn_code(mapping_data.cncode_total):
                logger.error(f"❌ 유효하지 않은 CN 코드: {mapping_data.cncode_total}")
                return None
            
            mapping = await self.repository.update_mapping(mapping_id, mapping_data)
            if mapping:
                return HSCNMappingFullResponse(**mapping)
            return None
            
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 수정 실패: {str(e)}")
            return None
    
    async def delete_mapping(self, mapping_id: int) -> bool:
        """HS-CN 매핑 삭제"""
        try:
            return await self.repository.delete_mapping(mapping_id)
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 삭제 실패: {str(e)}")
            return False
    
    # ============================================================================
    # 🔍 HS 코드 조회 기능
    # ============================================================================
    
    async def lookup_by_hs_code(self, hs_code: str) -> HSCodeLookupResponse:
        """HS 코드로 CN 코드 조회 (부분 검색 허용)"""
        try:
            # HS 코드 유효성 검증 (부분 검색 허용)
            if not self._validate_hs_code_10(hs_code):
                return HSCodeLookupResponse(
                    success=False,
                    data=[],
                    count=0,
                    message=f"유효하지 않은 HS 코드: {hs_code}"
                )
            
            mappings = await self.repository.lookup_by_hs_code(hs_code)
            
            # 응답 데이터 변환 (딕셔너리에서 키로 접근)
            response_data = []
            for mapping in mappings:
                response_data.append(HSCNMappingResponse(
                    cncode_total=mapping['cncode_total'],
                    goods_name=mapping.get('goods_name'),
                    goods_engname=mapping.get('goods_engname'),
                    aggregoods_name=mapping.get('aggregoods_name'),
                    aggregoods_engname=mapping.get('aggregoods_engname')
                ))
            
            return HSCodeLookupResponse(
                success=True,
                data=response_data,
                count=len(response_data),
                message=f"HS 코드 {hs_code}에 대한 {len(response_data)}개 매핑을 찾았습니다."
            )
            
        except Exception as e:
            logger.error(f"❌ HS 코드 조회 실패: {str(e)}")
            return HSCodeLookupResponse(
                success=False,
                data=[],
                count=0,
                message=f"HS 코드 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    async def search_by_hs_code(self, hs_code: str) -> List[HSCNMappingFullResponse]:
        """HS 코드로 검색"""
        try:
            mappings = await self.repository.search_by_hs_code(hs_code)
            return [HSCNMappingFullResponse(**mapping) for mapping in mappings]
        except Exception as e:
            logger.error(f"❌ HS 코드 검색 실패: {str(e)}")
            return []
    
    async def search_by_cn_code(self, cn_code: str) -> List[HSCNMappingFullResponse]:
        """CN 코드로 검색"""
        try:
            mappings = await self.repository.search_by_cn_code(cn_code)
            return [HSCNMappingFullResponse(**mapping) for mapping in mappings]
        except Exception as e:
            logger.error(f"❌ CN 코드 검색 실패: {str(e)}")
            return []
    
    async def search_by_goods_name(self, goods_name: str) -> List[HSCNMappingFullResponse]:
        """품목명으로 검색"""
        try:
            mappings = await self.repository.search_by_goods_name(goods_name)
            return [HSCNMappingFullResponse(**mapping) for mapping in mappings]
        except Exception as e:
            logger.error(f"❌ 품목명 검색 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_mapping_stats(self) -> MappingStatsResponse:
        """매핑 통계 조회"""
        try:
            stats = await self.repository.get_mapping_stats()
            return MappingStatsResponse(**stats)
        except Exception as e:
            logger.error(f"❌ 매핑 통계 조회 실패: {str(e)}")
            return MappingStatsResponse(
                total_mappings=0,
                unique_hscodes=0,
                unique_cncodes=0
            )
    
    # ============================================================================
    # 📦 일괄 처리
    # ============================================================================
    
    async def create_mappings_batch(self, batch_data: HSCNMappingBatchCreateRequest) -> HSCNMappingBatchResponse:
        """HS-CN 매핑 일괄 생성"""
        try:
            # 데이터 유효성 검증
            valid_mappings = []
            errors = []
            
            for mapping_data in batch_data.mappings:
                if not self._validate_hs_code(mapping_data.hscode):
                    errors.append(f"유효하지 않은 HS 코드: {mapping_data.hscode}")
                    continue
                
                if not self._validate_cn_code(mapping_data.cncode_total):
                    errors.append(f"유효하지 않은 CN 코드: {mapping_data.cncode_total}")
                    continue
                
                valid_mappings.append(mapping_data)
            
            if not valid_mappings:
                return HSCNMappingBatchResponse(
                    success=False,
                    created_count=0,
                    failed_count=len(batch_data.mappings),
                    errors=errors
                )
            
            # 일괄 생성 실행
            result = await self.repository.create_mappings_batch(valid_mappings)
            
            return HSCNMappingBatchResponse(
                success=result['created_count'] > 0,
                created_count=result['created_count'],
                failed_count=result['failed_count'] + len(errors),
                errors=result['errors'] + errors
            )
            
        except Exception as e:
            logger.error(f"❌ 일괄 매핑 생성 실패: {str(e)}")
            return HSCNMappingBatchResponse(
                success=False,
                created_count=0,
                failed_count=len(batch_data.mappings),
                errors=[f"일괄 처리 실패: {str(e)}"]
            )
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    def _validate_hs_code(self, hs_code: str) -> bool:
        """HS 코드 유효성 검증 (6자리)"""
        if not hs_code or len(hs_code) != 6:
            return False
        return hs_code.isdigit()
    
    def _validate_hs_code_10(self, hs_code: str) -> bool:
        """HS 코드 유효성 검증 (부분 검색 허용)"""
        if not hs_code:
            return False
        # 2자리 이상의 숫자만 허용 (부분 검색 가능)
        if len(hs_code) < 2 or not hs_code.isdigit():
            return False
        return True
    
    def _validate_cn_code(self, cn_code: str) -> bool:
        """CN 코드 유효성 검증 (8자리)"""
        if not cn_code or len(cn_code) != 8:
            return False
        return cn_code.isdigit()
