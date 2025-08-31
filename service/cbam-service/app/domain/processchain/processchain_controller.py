# ============================================================================
# 🏭 Process Chain Controller - 공정 체인 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
import logging
from datetime import datetime

from app.domain.processchain.processchain_service import ProcessChainService
from app.domain.processchain.processchain_schema import (
    ProcessChainCreate, ProcessChainUpdate, ProcessChainResponse,
    ProcessChainLinkCreate, ProcessChainLinkUpdate, ProcessChainLinkResponse,
    ProcessChainAnalysisRequest, ProcessChainAnalysisResponse,
    ChainDetectionRequest, ChainDetectionResponse,
    AutoDetectAndCalculateRequest, AutoDetectAndCalculateResponse
)

logger = logging.getLogger(__name__)

# Gateway를 통해 접근하므로 prefix 제거 (경로 중복 방지)
router = APIRouter(tags=["Process Chain"])

# 서비스 인스턴스 생성
processchain_service = ProcessChainService()

# ============================================================================
# 🔄 ProcessChain API 엔드포인트 (통합 공정 그룹)
# ============================================================================

@router.post("/chain", response_model=ProcessChainResponse, status_code=status.HTTP_201_CREATED)
async def create_process_chain(chain_data: ProcessChainCreate):
    """통합 공정 그룹 생성"""
    try:
        logger.info(f"📝 통합 공정 그룹 생성 API 호출: {chain_data.dict()}")
        result = await processchain_service.create_process_chain(chain_data)
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
        result = await processchain_service.get_process_chain(chain_id)
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
        result = await processchain_service.get_all_process_chains()
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
        result = await processchain_service.update_process_chain(chain_id, update_data)
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
        success = await processchain_service.delete_process_chain(chain_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"그룹 ID {chain_id}를 찾을 수 없습니다.")
        logger.info(f"✅ 통합 공정 그룹 삭제 API 성공: ID {chain_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 삭제 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 삭제 실패: {str(e)}")

# ============================================================================
# 🔗 ProcessChainLink API 엔드포인트 (그룹 내 공정 연결)
# ============================================================================

@router.post("/chain/{chain_id}/link", response_model=ProcessChainLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_process_chain_link(chain_id: int, link_data: ProcessChainLinkCreate):
    """통합 공정 그룹에 공정 연결"""
    try:
        logger.info(f"🔗 공정 연결 생성 API 호출: 그룹 {chain_id}, 공정 {link_data.process_id}")
        result = await processchain_service.create_process_chain_link(link_data)
        logger.info(f"✅ 공정 연결 생성 API 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 공정 연결 생성 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"공정 연결 생성 실패: {str(e)}")

@router.get("/chain/{chain_id}/links", response_model=List[ProcessChainLinkResponse])
async def get_chain_links(chain_id: int):
    """통합 공정 그룹의 공정 연결 목록 조회"""
    try:
        logger.info(f"📋 공정 연결 목록 조회 API 호출: 그룹 {chain_id}")
        result = await processchain_service.get_chain_links(chain_id)
        logger.info(f"✅ 공정 연결 목록 조회 API 성공: 그룹 {chain_id}, {len(result)}개")
        return result
    except Exception as e:
        logger.error(f"❌ 공정 연결 목록 조회 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"공정 연결 목록 조회 실패: {str(e)}")

# ============================================================================
# 🔍 ProcessChain 분석 및 탐지 API 엔드포인트
# ============================================================================

@router.post("/chain/detect", response_model=ChainDetectionResponse)
async def detect_process_chains(request: ChainDetectionRequest):
    """통합 공정 그룹 자동 탐지"""
    try:
        logger.info(f"🔍 통합 공정 그룹 자동 탐지 API 호출: {request.dict()}")
        result = await processchain_service.detect_process_chains(request)
        logger.info(f"✅ 통합 공정 그룹 자동 탐지 API 성공: {result.detected_chains}개 그룹")
        return result
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 자동 탐지 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 자동 탐지 실패: {str(e)}")

@router.post("/chain/auto-detect-and-calculate", response_model=AutoDetectAndCalculateResponse)
async def auto_detect_and_calculate_chains(request: AutoDetectAndCalculateRequest):
    """통합 공정 그룹 자동 탐지 및 배출량 계산"""
    try:
        logger.info(f"🔍 통합 공정 그룹 자동 탐지 및 계산 API 호출: {request.dict()}")
        result = await processchain_service.auto_detect_and_calculate_chains(request)
        logger.info(f"✅ 통합 공정 그룹 자동 탐지 및 계산 API 성공: {result.detected_chains}개 그룹")
        return result
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 자동 탐지 및 계산 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 자동 탐지 및 계산 실패: {str(e)}")

@router.post("/chain/analyze", response_model=ProcessChainAnalysisResponse)
async def analyze_process_chain(request: ProcessChainAnalysisRequest):
    """통합 공정 그룹 분석"""
    try:
        logger.info(f"📊 통합 공정 그룹 분석 API 호출: 그룹 {request.chain_id}")
        result = await processchain_service.analyze_process_chain(request)
        logger.info(f"✅ 통합 공정 그룹 분석 API 성공: 그룹 {request.chain_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 통합 공정 그룹 분석 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"통합 공정 그룹 분석 실패: {str(e)}")
        

# ============================================================================
# 🏥 헬스 체크 및 테스트 API 엔드포인트
# ============================================================================

@router.get("/health")
async def health_check():
    """processchain 헬스 체크"""
    try:
        logger.info("🏥 processchain 헬스 체크 API 호출")
        return {
            "status": "healthy",
            "service": "processchain",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ processchain 헬스 체크 API 실패: {e}")
        raise HTTPException(status_code=500, detail=f"헬스 체크 실패: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """processchain 테스트 엔드포인트"""
    logger.info("🧪 processchain 테스트 API 호출")
    return {
        "message": "processchain 라우터가 정상적으로 등록되었습니다!",
        "timestamp": datetime.utcnow().isoformat()
    }
