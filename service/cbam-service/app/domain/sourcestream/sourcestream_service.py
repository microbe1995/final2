# ============================================================================
# 🔄 SourceStream Service - 통합 공정 그룹 비즈니스 로직
# ============================================================================

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import json

from .sourcestream_repository import SourceStreamRepository
from .sourcestream_schema import (
    ProcessChainCreate, ProcessChainUpdate, ProcessChainResponse,
    ProcessChainLinkCreate, ProcessChainLinkUpdate, ProcessChainLinkResponse,
    SourceStreamCreate, SourceStreamUpdate, SourceStreamResponse,
    ProcessChainAnalysisRequest, ProcessChainAnalysisResponse,
    ChainDetectionRequest, ChainDetectionResponse,
    AutoDetectAndCalculateRequest, AutoDetectAndCalculateResponse
)

logger = logging.getLogger(__name__)

class SourceStreamService:
    """소스 스트림 서비스 - 통합 공정 그룹 비즈니스 로직"""
    
    def __init__(self):
        """서비스 초기화"""
        self.repository = SourceStreamRepository()
    
    # ============================================================================
    # 🔄 ProcessChain 관련 서비스 메서드 (통합 공정 그룹)
    # ============================================================================
    
    async def create_process_chain(self, chain_data: ProcessChainCreate) -> ProcessChainResponse:
        """통합 공정 그룹 생성"""
        try:
            logger.info(f"📝 통합 공정 그룹 생성 요청: {chain_data.dict()}")
            
            # 그룹 데이터 준비
            chain_dict = chain_data.dict()
            chain_dict["created_at"] = datetime.utcnow()
            chain_dict["updated_at"] = datetime.utcnow()
            
            # 그룹 생성
            chain = await self.repository.create_process_chain(chain_dict)
            
            logger.info(f"✅ 통합 공정 그룹 생성 성공: ID {chain.id}")
            return ProcessChainResponse(**chain.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 생성 실패: {e}")
            raise e
    
    async def get_process_chain(self, chain_id: int) -> Optional[ProcessChainResponse]:
        """통합 공정 그룹 조회"""
        try:
            chain = await self.repository.get_process_chain(chain_id)
            if not chain:
                return None
            
            return ProcessChainResponse(**chain.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 조회 실패: {e}")
            raise e
    
    async def get_all_process_chains(self) -> List[ProcessChainResponse]:
        """모든 통합 공정 그룹 조회"""
        try:
            chains = await self.repository.get_all_process_chains()
            return [ProcessChainResponse(**chain.to_dict()) for chain in chains]
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 목록 조회 실패: {e}")
            raise e
    
    async def update_process_chain(self, chain_id: int, update_data: ProcessChainUpdate) -> Optional[ProcessChainResponse]:
        """통합 공정 그룹 수정"""
        try:
            logger.info(f"📝 통합 공정 그룹 수정 요청: ID {chain_id}, 데이터: {update_data.dict(exclude_unset=True)}")
            
            # None이 아닌 값만 필터링
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            chain = await self.repository.update_process_chain(chain_id, update_dict)
            if not chain:
                return None
            
            logger.info(f"✅ 통합 공정 그룹 수정 성공: ID {chain_id}")
            return ProcessChainResponse(**chain.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 수정 실패: {e}")
            raise e
    
    async def delete_process_chain(self, chain_id: int) -> bool:
        """통합 공정 그룹 삭제"""
        try:
            logger.info(f"🗑️ 통합 공정 그룹 삭제 요청: ID {chain_id}")
            
            success = await self.repository.delete_process_chain(chain_id)
            
            if success:
                logger.info(f"✅ 통합 공정 그룹 삭제 성공: ID {chain_id}")
            else:
                logger.warning(f"⚠️ 통합 공정 그룹 삭제 실패: ID {chain_id}를 찾을 수 없음")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 삭제 실패: {e}")
            raise e
    
    # ============================================================================
    # 🔗 ProcessChainLink 관련 서비스 메서드 (그룹 내 공정 멤버)
    # ============================================================================
    
    async def create_process_chain_link(self, link_data: ProcessChainLinkCreate) -> ProcessChainLinkResponse:
        """통합 공정 그룹 링크 생성"""
        try:
            logger.info(f"📝 그룹 링크 생성 요청: {link_data.dict()}")
            
            # 링크 데이터 준비
            link_dict = link_data.dict()
            link_dict["created_at"] = datetime.utcnow()
            link_dict["updated_at"] = datetime.utcnow()
            
            # 링크 생성
            link = await self.repository.create_process_chain_link(link_dict)
            
            logger.info(f"✅ 그룹 링크 생성 성공: ID {link.id}")
            return ProcessChainLinkResponse(**link.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 그룹 링크 생성 실패: {e}")
            raise e
    
    async def get_chain_links(self, chain_id: int) -> List[ProcessChainLinkResponse]:
        """그룹에 속한 공정들 조회"""
        try:
            links = await self.repository.get_chain_links(chain_id)
            return [ProcessChainLinkResponse(**link.to_dict()) for link in links]
            
        except Exception as e:
            logger.error(f"❌ 그룹 링크 조회 실패: {e}")
            raise e
    
    # ============================================================================
    # 🔍 통합 공정 그룹 자동 탐지 서비스 메서드
    # ============================================================================
    
    async def detect_process_chains(self, request: ChainDetectionRequest) -> ChainDetectionResponse:
        """통합 공정 그룹 자동 탐지"""
        try:
            logger.info(f"🔍 통합 공정 그룹 탐지 요청: {request.dict()}")
            
            # 그룹 탐지
            detected_chains = await self.repository.detect_process_chains(request.max_chain_length)
            
            # 응답 데이터 변환
            chain_responses = []
            for chain_info in detected_chains:
                chain_response = ProcessChainResponse(
                    id=0,  # 아직 DB에 저장되지 않음
                    chain_name=f"탐지된그룹-{chain_info['start_process_id']}-{chain_info['end_process_id']}",
                    start_process_id=chain_info["start_process_id"],
                    end_process_id=chain_info["end_process_id"],
                    chain_length=chain_info["chain_length"],
                    is_active=True
                )
                chain_responses.append(chain_response)
            
            response = ChainDetectionResponse(
                detected_chains=chain_responses,
                total_chains=len(chain_responses),
                detection_date=datetime.utcnow()
            )
            
            logger.info(f"✅ 통합 공정 그룹 탐지 완료: {len(chain_responses)}개 발견")
            return response
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 탐지 실패: {e}")
            raise e
    
    async def auto_detect_and_calculate_chains(self, request: AutoDetectAndCalculateRequest) -> AutoDetectAndCalculateResponse:
        """통합 공정 그룹 자동 탐지 및 배출량 계산"""
        try:
            logger.info(f"🚀 통합 공정 그룹 자동 탐지 및 계산 요청: {request.dict()}")
            
            # 자동 탐지 및 계산 실행
            result = await self.repository.auto_detect_and_calculate_chains(request.max_chain_length)
            
            response = AutoDetectAndCalculateResponse(
                detected_chains=result["detected_chains"],
                total_calculated_processes=result["total_calculated_processes"],
                total_integrated_emission=result["total_integrated_emission"],
                calculation_date=datetime.utcnow(),
                status="success"
            )
            
            logger.info(f"✅ 통합 공정 그룹 자동 탐지 및 계산 완료: {result['detected_chains']}개 그룹")
            return response
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 자동 탐지 및 계산 실패: {e}")
            raise e
    
    # ============================================================================
    # 🔄 SourceStream 관련 서비스 메서드
    # ============================================================================
    
    async def create_source_stream(self, stream_data: SourceStreamCreate) -> SourceStreamResponse:
        """소스 스트림 생성"""
        try:
            logger.info(f"📝 소스 스트림 생성 요청: {stream_data.dict()}")
            
            # 스트림 데이터 준비
            stream_dict = stream_data.dict()
            stream_dict["created_at"] = datetime.utcnow()
            stream_dict["updated_at"] = datetime.utcnow()
            
            # 스트림 생성
            stream = await self.repository.create_source_stream(stream_dict)
            
            logger.info(f"✅ 소스 스트림 생성 성공: ID {stream.id}")
            return SourceStreamResponse(**stream.to_dict())
            
        except Exception as e:
            logger.error(f"❌ 소스 스트림 생성 실패: {e}")
            raise e
    
    async def get_source_streams(self, source_process_id: Optional[int] = None) -> List[SourceStreamResponse]:
        """소스 스트림 조회"""
        try:
            streams = await self.repository.get_source_streams(source_process_id)
            return [SourceStreamResponse(**stream.to_dict()) for stream in streams]
            
        except Exception as e:
            logger.error(f"❌ 소스 스트림 조회 실패: {e}")
            raise e
    
    # ============================================================================
    # 📊 통합 공정 그룹 분석 서비스 메서드
    # ============================================================================
    
    async def analyze_process_chain(self, request: ProcessChainAnalysisRequest) -> ProcessChainAnalysisResponse:
        """통합 공정 그룹 분석"""
        try:
            logger.info(f"📊 통합 공정 그룹 분석 요청: {request.dict()}")
            
            # 그룹 정보 조회
            chain = await self.repository.get_process_chain(request.start_process_id)
            if not chain:
                raise ValueError(f"통합 공정 그룹을 찾을 수 없습니다: start_process_id {request.start_process_id}")
            
            # 그룹 링크 조회
            links = await self.repository.get_chain_links(chain.id)
            
            # 그룹 배출량 계산
            emission_result = await self.repository.calculate_chain_integrated_emissions(chain.id)
            
            # 응답 구성
            chain_response = ProcessChainResponse(**chain.to_dict())
            link_responses = [ProcessChainLinkResponse(**link.to_dict()) for link in links]
            
            response = ProcessChainAnalysisResponse(
                chain=chain_response,
                integrated_emissions=[],  # 개별 배출량은 별도 테이블에 저장하지 않음
                total_integrated_emission=emission_result["integrated_attrdir_em"],
                analysis_date=datetime.utcnow()
            )
            
            logger.info(f"✅ 통합 공정 그룹 분석 완료: chain_id {chain.id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 분석 실패: {e}")
            raise e
