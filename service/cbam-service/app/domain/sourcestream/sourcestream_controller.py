# ============================================================================
# 🔄 SourceStream Controller - 통합 공정 그룹 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
import logging

from .sourcestream_service import SourceStreamService
from .sourcestream_schema import (
    ProcessChainCreate, ProcessChainUpdate, ProcessChainResponse,
    ProcessChainLinkCreate, ProcessChainLinkUpdate, ProcessChainLinkResponse,
    SourceStreamCreate, SourceStreamUpdate, SourceStreamResponse,
    ProcessChainAnalysisRequest, ProcessChainAnalysisResponse,
    IntegratedEmissionCalculationRequest, IntegratedEmissionCalculationResponse,
    ChainDetectionRequest, ChainDetectionResponse,
    AutoDetectAndCalculateRequest, AutoDetectAndCalculateResponse
)

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sourcestream", tags=["SourceStream"])

# 서비스 인스턴스 생성
sourcestream_service = SourceStreamService()

# ============================================================================
# 🔄 ProcessChain API 엔드포인트 (통합 공정 그룹)
# ============================================================================

@router.post("/chain", response_model=ProcessChainResponse, status_code=status.HTTP_201_CREATED)
async def create_process_chain(chain_data: ProcessChainCreate):
    """통합 공정 그룹 생성"""
    try:
        logger.info(f"📝 통합 공정 그룹 생성 API 호출: {chain_data.dict()}")
        result = await sourcestream_service.create_process_chain(chain_data)
        logger.info(f"✅ 통합 공정 그룹 생성 API 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 생성 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 생성 실패: {str(e)}")

@router.get("/chain/{chain_id}", response_model=ProcessChainResponse)
async def get_process_chain(chain_id: int):
    """통합 공정 그룹 조회"""
    try:
        logger.info(f"📋 통합 공정 그룹 조회 API 호출: ID {chain_id}")
        result = await sourcestream_service.get_process_chain(chain_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"그룹 ID {chain_id}를 찾을 수 없습니다.")
        logger.info(f"✅ 통합 공정 그룹 조회 API 성공: ID {chain_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 조회 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 조회 실패: {str(e)}")

@router.get("/chain", response_model=List[ProcessChainResponse])
async def get_all_process_chains():
    """모든 통합 공정 그룹 조회"""
    try:
        logger.info("📋 모든 통합 공정 그룹 조회 API 호출")
        result = await sourcestream_service.get_all_process_chains()
        logger.info(f"✅ 모든 통합 공정 그룹 조회 API 성공: {len(result)}개")
        return result
    except Exception as e:
        logger.error(f"❌ 모든 통합 공정 그룹 조회 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 목록 조회 실패: {str(e)}")

@router.put("/chain/{chain_id}", response_model=ProcessChainResponse)
async def update_process_chain(chain_id: int, update_data: ProcessChainUpdate):
    """통합 공정 그룹 수정"""
    try:
        logger.info(f"📝 통합 공정 그룹 수정 API 호출: ID {chain_id}")
        result = await sourcestream_service.update_process_chain(chain_id, update_data)
        if not result:
            raise HTTPException(status_code=404, detail=f"그룹 ID {chain_id}를 찾을 수 없습니다.")
        logger.info(f"✅ 통합 공정 그룹 수정 API 성공: ID {chain_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 수정 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 수정 실패: {str(e)}")

@router.delete("/chain/{chain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_process_chain(chain_id: int):
    """통합 공정 그룹 삭제"""
    try:
        logger.info(f"🗑️ 통합 공정 그룹 삭제 API 호출: ID {chain_id}")
        success = await sourcestream_service.delete_process_chain(chain_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"그룹 ID {chain_id}를 찾을 수 없습니다.")
        logger.info(f"✅ 통합 공정 그룹 삭제 API 성공: ID {chain_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 삭제 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 삭제 실패: {str(e)}")

# ============================================================================
# 🔗 ProcessChainLink API 엔드포인트 (그룹 내 공정 멤버)
# ============================================================================

@router.post("/chain-link", response_model=ProcessChainLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_process_chain_link(link_data: ProcessChainLinkCreate):
    """통합 공정 그룹 링크 생성"""
    try:
        logger.info(f"📝 그룹 링크 생성 API 호출: {link_data.dict()}")
        result = await sourcestream_service.create_process_chain_link(link_data)
        logger.info(f"✅ 그룹 링크 생성 API 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 그룹 링크 생성 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"그룹 링크 생성 실패: {str(e)}")

@router.get("/chain/{chain_id}/links", response_model=List[ProcessChainLinkResponse])
async def get_chain_links(chain_id: int):
    """그룹에 속한 공정들 조회"""
    try:
        logger.info(f"📋 그룹 링크 조회 API 호출: chain_id {chain_id}")
        result = await sourcestream_service.get_chain_links(chain_id)
        logger.info(f"✅ 그룹 링크 조회 API 성공: chain_id {chain_id}, {len(result)}개")
        return result
    except Exception as e:
        logger.error(f"❌ 그룹 링크 조회 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"그룹 링크 조회 실패: {str(e)}")

# ============================================================================
# 🔍 통합 공정 그룹 자동 탐지 API 엔드포인트
# ============================================================================

@router.post("/detect-chains", response_model=ChainDetectionResponse)
async def detect_process_chains(request: ChainDetectionRequest):
    """통합 공정 그룹 자동 탐지"""
    try:
        logger.info(f"🔍 통합 공정 그룹 탐지 API 호출: {request.dict()}")
        result = await sourcestream_service.detect_process_chains(request)
        logger.info(f"✅ 통합 공정 그룹 탐지 API 성공: {result.total_chains}개 발견")
        return result
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 탐지 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 탐지 실패: {str(e)}")

# ============================================================================
# 📊 통합 공정 그룹 배출량 계산 API 엔드포인트
# ============================================================================

@router.post("/calculate-emissions", response_model=IntegratedEmissionCalculationResponse)
async def calculate_chain_integrated_emissions(request: IntegratedEmissionCalculationRequest):
    """통합 공정 그룹 배출량 계산"""
    try:
        logger.info(f"🧮 통합 공정 그룹 배출량 계산 API 호출: {request.dict()}")
        result = await sourcestream_service.calculate_chain_integrated_emissions(request)
        logger.info(f"✅ 통합 공정 그룹 배출량 계산 API 성공: chain_id {request.chain_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 배출량 계산 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 배출량 계산 실패: {str(e)}")

@router.post("/auto-detect-and-calculate", response_model=AutoDetectAndCalculateResponse)
async def auto_detect_and_calculate_chains(request: AutoDetectAndCalculateRequest):
    """통합 공정 그룹 자동 탐지 및 배출량 계산"""
    try:
        logger.info(f"🚀 통합 공정 그룹 자동 탐지 및 계산 API 호출: {request.dict()}")
        result = await sourcestream_service.auto_detect_and_calculate_chains(request)
        logger.info(f"✅ 통합 공정 그룹 자동 탐지 및 계산 API 성공: {result.detected_chains}개 그룹")
        return result
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 자동 탐지 및 계산 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 자동 탐지 및 계산 실패: {str(e)}")

# ============================================================================
# 📊 통합 공정 그룹 분석 API 엔드포인트
# ============================================================================

@router.post("/analyze-chain", response_model=ProcessChainAnalysisResponse)
async def analyze_process_chain(request: ProcessChainAnalysisRequest):
    """통합 공정 그룹 분석"""
    try:
        logger.info(f"📊 통합 공정 그룹 분석 API 호출: {request.dict()}")
        result = await sourcestream_service.analyze_process_chain(request)
        logger.info(f"✅ 통합 공정 그룹 분석 API 성공: start_process_id {request.start_process_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 분석 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 분석 실패: {str(e)}")

# ============================================================================
# 🔄 SourceStream API 엔드포인트
# ============================================================================

@router.post("/stream", response_model=SourceStreamResponse, status_code=status.HTTP_201_CREATED)
async def create_source_stream(stream_data: SourceStreamCreate):
    """소스 스트림 생성"""
    try:
        logger.info(f"📝 소스 스트림 생성 API 호출: {stream_data.dict()}")
        result = await sourcestream_service.create_source_stream(stream_data)
        logger.info(f"✅ 소스 스트림 생성 API 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 소스 스트림 생성 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"소스 스트림 생성 실패: {str(e)}")

@router.get("/stream", response_model=List[SourceStreamResponse])
async def get_source_streams(source_process_id: int = None):
    """소스 스트림 조회"""
    try:
        logger.info(f"📋 소스 스트림 조회 API 호출: source_process_id {source_process_id}")
        result = await sourcestream_service.get_source_streams(source_process_id)
        logger.info(f"✅ 소스 스트림 조회 API 성공: {len(result)}개")
        return result
    except Exception as e:
        logger.error(f"❌ 소스 스트림 조회 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"소스 스트림 조회 실패: {str(e)}")

@router.put("/stream/{stream_id}", response_model=SourceStreamResponse)
async def update_source_stream(stream_id: int, update_data: SourceStreamUpdate):
    """소스 스트림 수정"""
    try:
        logger.info(f"📝 소스 스트림 수정 API 호출: ID {stream_id}")
        # TODO: update_source_stream 메서드 구현 필요
        raise HTTPException(status_code=501, detail="소스 스트림 수정 기능은 아직 구현되지 않았습니다.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 소스 스트림 수정 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"소스 스트림 수정 실패: {str(e)}")

@router.delete("/stream/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source_stream(stream_id: int):
    """소스 스트림 삭제"""
    try:
        logger.info(f"🗑️ 소스 스트림 삭제 API 호출: ID {stream_id}")
        # TODO: delete_source_stream 메서드 구현 필요
        raise HTTPException(status_code=501, detail="소스 스트림 삭제 기능은 아직 구현되지 않았습니다.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 소스 스트림 삭제 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"소스 스트림 삭제 실패: {str(e)}")

# ============================================================================
# 🔄 상태 확인 API 엔드포인트
# ============================================================================

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """헬스 체크"""
    try:
        logger.info("🏥 sourcestream 헬스 체크 API 호출")
        return {
            "status": "healthy",
            "service": "sourcestream",
            "message": "통합 공정 그룹 서비스가 정상적으로 작동 중입니다."
        }
    except Exception as e:
        logger.error(f"❌ sourcestream 헬스 체크 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"헬스 체크 실패: {str(e)}")
