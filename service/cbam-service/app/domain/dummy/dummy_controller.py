# ============================================================================
# �� Dummy Controller - 핵심 기능만 포함
# ============================================================================

from fastapi import APIRouter, HTTPException, Query
import logging
from typing import List

from app.domain.dummy.dummy_service import DummyService

logger = logging.getLogger(__name__)

# Gateway를 통해 접근하므로 prefix 제거 (경로 중복 방지)
router = APIRouter(tags=["Dummy"])

# 싱글톤 서비스 인스턴스 (성능 최적화)
_dummy_service_instance = None

def get_dummy_service():
    """Dummy 서비스 인스턴스 반환 (싱글톤 패턴)"""
    global _dummy_service_instance
    if _dummy_service_instance is None:
        _dummy_service_instance = DummyService()
        logger.info("✅ Dummy Service 싱글톤 인스턴스 생성")
    return _dummy_service_instance

async def ensure_service_initialized():
    """서비스가 초기화되었는지 확인하고, 필요시 초기화"""
    service = get_dummy_service()
    
    # 서비스 초기화 상태 확인
    if not hasattr(service, '_initialized') or not service._initialized:
        try:
            await service.initialize()
            service._initialized = True
            logger.info("✅ Dummy Service 초기화 완료")
        except Exception as e:
            logger.error(f"❌ Dummy Service 초기화 실패: {e}")
            raise Exception(f"Dummy Service 초기화 실패: {e}")
    
    return service

# ============================================================================
# 🎯 핵심 기능 엔드포인트
# ============================================================================

@router.get("", response_model=List[dict])
async def get_all_dummy_data():
    """Dummy 테이블의 모든 데이터 조회"""
    try:
        logger.info("🎭 전체 더미 데이터 조회 요청")
        
        dummy_service = await ensure_service_initialized()
        all_data = await dummy_service.get_all_dummy_data()
        
        logger.info(f"✅ 전체 더미 데이터 조회 성공: {len(all_data)}개")
        return all_data
        
    except Exception as e:
        logger.error(f"❌ 전체 더미 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/products/names", response_model=List[str])
async def get_dummy_product_names():
    """Dummy 테이블에서 고유한 제품명 목록 조회"""
    try:
        logger.info("🎭 고유 제품명 목록 조회 요청")
        
        dummy_service = await ensure_service_initialized()
        product_names = await dummy_service.get_unique_product_names()
        
        logger.info(f"✅ 고유 제품명 목록 조회 성공: {len(product_names)}개")
        return product_names
        
    except Exception as e:
        logger.error(f"❌ 고유 제품명 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/products/names/by-period", response_model=List[str])
async def get_dummy_product_names_by_period(
    start_date: str = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="종료 날짜 (YYYY-MM-DD)")
):
    """Dummy 테이블에서 기간별 고유한 제품명 목록 조회"""
    try:
        logger.info(f"🎭 기간별 고유 제품명 목록 조회 요청: {start_date} ~ {end_date}")
        
        dummy_service = await ensure_service_initialized()
        product_names = await dummy_service.get_unique_product_names_by_period(start_date, end_date)
        
        logger.info(f"✅ 기간별 고유 제품명 목록 조회 성공: {len(product_names)}개")
        return product_names
        
    except Exception as e:
        logger.error(f"❌ 기간별 고유 제품명 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/processes/names", response_model=List[str])
async def get_dummy_process_names():
    """Dummy 테이블에서 고유한 공정명 목록 조회"""
    try:
        logger.info("🎭 고유 공정명 목록 조회 요청")
        
        dummy_service = await ensure_service_initialized()
        process_names = await dummy_service.get_unique_process_names()
        
        logger.info(f"✅ 고유 공정명 목록 조회 성공: {len(process_names)}개")
        return process_names
        
    except Exception as e:
        logger.error(f"❌ 고유 공정명 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/processes/names/by-period", response_model=List[str])
async def get_dummy_process_names_by_period(
    start_period: str = Query(..., description="시작 기간 (YYYY-MM-DD)"),
    end_period: str = Query(..., description="종료 기간 (YYYY-MM-DD)")
):
    """Dummy 테이블에서 기간별 고유한 공정명 목록 조회"""
    try:
        logger.info(f"🎭 기간별 고유 공정명 목록 조회 요청: {start_period} ~ {end_period}")
        
        dummy_service = await ensure_service_initialized()
        process_names = await dummy_service.get_unique_process_names_by_period(start_period, end_period)
        
        logger.info(f"✅ 기간별 고유 공정명 목록 조회 성공: {len(process_names)}개")
        return process_names
        
    except Exception as e:
        logger.error(f"❌ 기간별 고유 공정명 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/products/{product_name}/processes")
async def get_processes_by_product(product_name: str):
    """특정 제품의 공정 목록 조회"""
    try:
        logger.info(f"🔍 제품 '{product_name}'의 공정 목록 조회 요청")
        
        dummy_service = await ensure_service_initialized()
        processes = await dummy_service.get_unique_processes_by_product(product_name)
        
        logger.info(f"✅ 제품 '{product_name}'의 공정 목록 조회 성공: {len(processes)}개")
        return {
            "success": True,
            "data": {
                "product_name": product_name,
                "processes": processes,
                "count": len(processes)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 제품 '{product_name}'의 공정 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"제품 '{product_name}'의 공정 목록 조회에 실패했습니다: {str(e)}"
        )
