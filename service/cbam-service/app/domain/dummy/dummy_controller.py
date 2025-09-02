# ============================================================================
# 🎭 Dummy Controller - Dummy 데이터 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException, Query
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.dummy.dummy_service import DummyService
from app.domain.dummy.dummy_schema import (
    DummyDataCreateRequest, DummyDataUpdateRequest, DummyDataResponse, DummyDataListResponse
)

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
    if not getattr(service, '_initialized', False):
        await service.initialize()
        service._initialized = True
        logger.info("✅ Dummy Service 초기화 완료")
    return service

# ============================================================================
# 📊 상태 확인 엔드포인트
# ============================================================================

@router.options("/")
async def options_dummy_data():
    """CORS preflight 요청 처리"""
    return {"message": "CORS preflight OK"}

@router.get("/health")
async def health_check():
    """Dummy 도메인 상태 확인"""
    try:
        logger.info("🏥 Dummy 도메인 헬스체크 요청")
        
        dummy_service = await ensure_service_initialized()
        
        # 데이터베이스 연결 확인
        try:
            await dummy_service.repository._ensure_pool_initialized()
            db_status = "healthy"
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            db_status = "unhealthy"
        
        # 기본 통계 조회 시도
        try:
            data_count = await dummy_service.get_dummy_data_count()
            api_status = "healthy"
        except Exception as e:
            logger.error(f"❌ API 기능 테스트 실패: {e}")
            api_status = "unhealthy"
            data_count = 0
        
        health_status = {
            "service": "dummy",
            "status": "healthy" if db_status == "healthy" and api_status == "healthy" else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": db_status,
                "api": api_status
            },
            "metrics": {
                "total_dummy_data": data_count
            }
        }
        
        logger.info(f"✅ Dummy 도메인 헬스체크 완료: {health_status['status']}")
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Dummy 도메인 헬스체크 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ============================================================================
# 📋 기본 CRUD 엔드포인트
# ============================================================================

@router.get("/{data_id}", response_model=DummyDataResponse)
async def get_dummy_data(data_id: int):
    """ID로 Dummy 데이터 조회"""
    try:
        logger.info(f"🎭 Dummy 데이터 조회 요청: ID {data_id}")
        
        dummy_service = await ensure_service_initialized()
        data = await dummy_service.get_dummy_data_by_id(data_id)
        
        if data:
            logger.info(f"✅ Dummy 데이터 조회 성공: ID {data_id}")
            return data
        else:
            raise HTTPException(status_code=404, detail=f"ID {data_id}의 Dummy 데이터를 찾을 수 없습니다.")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dummy 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("", response_model=DummyDataListResponse)
@router.get("/", response_model=DummyDataListResponse)
async def get_all_dummy_data(
    limit: int = Query(100, ge=1, le=1000, description="페이지 크기"),
    offset: int = Query(0, ge=0, description="오프셋"),
    search: Optional[str] = Query(None, description="검색어")
):
    """모든 Dummy 데이터 조회 (페이징 및 검색)"""
    try:
        logger.info(f"🎭 Dummy 데이터 목록 조회 요청: limit={limit}, offset={offset}, search={search}")
        
        dummy_service = await ensure_service_initialized()
        
        if search:
            # 검색 기능 사용
            data_list = await dummy_service.search_dummy_data(search, limit)
            total = await dummy_service.get_dummy_data_count()
        else:
            # 전체 목록 조회
            data_list = await dummy_service.get_all_dummy_data(limit, offset)
            total = await dummy_service.get_dummy_data_count()
        
        logger.info(f"✅ Dummy 데이터 목록 조회 성공: {len(data_list)}개")
        
        return DummyDataListResponse(
            items=data_list,
            total=total,
            page=(offset // limit) + 1 if limit > 0 else 1,
            size=limit
        )
        
    except Exception as e:
        logger.error(f"❌ Dummy 데이터 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.post("", response_model=DummyDataResponse, status_code=201)
@router.post("/", response_model=DummyDataResponse, status_code=201)
async def create_dummy_data(
    data: DummyDataCreateRequest
):
    """Dummy 데이터 생성"""
    try:
        logger.info(f"🎭 Dummy 데이터 생성 요청: {data.로트번호} - {data.생산품명}")
        
        dummy_service = await ensure_service_initialized()
        result_id = await dummy_service.create_dummy_data(data)
        
        if result_id:
            # 생성된 데이터 조회하여 반환
            created_data = await dummy_service.get_dummy_data_by_id(result_id)
            if created_data:
                logger.info(f"✅ Dummy 데이터 생성 성공: ID {result_id}")
                return created_data
            else:
                raise HTTPException(status_code=500, detail="데이터 생성 후 조회 실패")
        else:
            raise HTTPException(status_code=500, detail="Dummy 데이터 생성 실패")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dummy 데이터 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.put("/{data_id}", response_model=DummyDataResponse)
async def update_dummy_data(
    data_id: int,
    data: DummyDataUpdateRequest
):
    """Dummy 데이터 수정"""
    try:
        logger.info(f"🎭 Dummy 데이터 수정 요청: ID {data_id}")
        
        dummy_service = await ensure_service_initialized()
        success = await dummy_service.update_dummy_data(data_id, data)
        
        if success:
            # 수정된 데이터 조회하여 반환
            updated_data = await dummy_service.get_dummy_data_by_id(data_id)
            if updated_data:
                logger.info(f"✅ Dummy 데이터 수정 성공: ID {data_id}")
                return updated_data
            else:
                raise HTTPException(status_code=500, detail="데이터 수정 후 조회 실패")
        else:
            raise HTTPException(status_code=404, detail=f"ID {data_id}의 Dummy 데이터를 찾을 수 없습니다.")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dummy 데이터 수정 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.delete("/{data_id}")
async def delete_dummy_data(data_id: int):
    """Dummy 데이터 삭제"""
    try:
        logger.info(f"🎭 Dummy 데이터 삭제 요청: ID {data_id}")
        
        dummy_service = await ensure_service_initialized()
        success = await dummy_service.delete_dummy_data(data_id)
        
        if success:
            logger.info(f"✅ Dummy 데이터 삭제 성공: ID {data_id}")
            return {"message": f"ID {data_id}의 Dummy 데이터가 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail=f"ID {data_id}의 Dummy 데이터를 찾을 수 없습니다.")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dummy 데이터 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

# ============================================================================
# 🔍 고급 검색 엔드포인트
# ============================================================================

@router.get("/search/process/{process_name}", response_model=List[DummyDataResponse])
async def get_dummy_data_by_process(
    process_name: str,
    limit: int = Query(100, ge=1, le=1000, description="페이지 크기")
):
    """공정별 Dummy 데이터 조회"""
    try:
        logger.info(f"🎭 공정별 Dummy 데이터 조회 요청: {process_name}")
        
        dummy_service = await ensure_service_initialized()
        data_list = await dummy_service.get_dummy_data_by_process(process_name, limit)
        
        logger.info(f"✅ 공정별 Dummy 데이터 조회 성공: {process_name} - {len(data_list)}개")
        return data_list
        
    except Exception as e:
        logger.error(f"❌ 공정별 Dummy 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/search/product/{product_name}", response_model=List[DummyDataResponse])
async def get_dummy_data_by_product(
    product_name: str,
    limit: int = Query(100, ge=1, le=1000, description="페이지 크기")
):
    """생산품별 Dummy 데이터 조회"""
    try:
        logger.info(f"🎭 생산품별 Dummy 데이터 조회 요청: {product_name}")
        
        dummy_service = await ensure_service_initialized()
        data_list = await dummy_service.get_dummy_data_by_product(product_name, limit)
        
        logger.info(f"✅ 생산품별 Dummy 데이터 조회 성공: {product_name} - {len(data_list)}개")
        return data_list
        
    except Exception as e:
        logger.error(f"❌ 생산품별 Dummy 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/stats/count")
async def get_dummy_data_count():
    """Dummy 데이터 총 개수 조회"""
    try:
        logger.info("🎭 Dummy 데이터 개수 조회 요청")
        
        dummy_service = await ensure_service_initialized()
        count = await dummy_service.get_dummy_data_count()
        
        logger.info(f"✅ Dummy 데이터 개수 조회 성공: {count}개")
        return {"total_count": count}
        
    except Exception as e:
        logger.error(f"❌ Dummy 데이터 개수 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
