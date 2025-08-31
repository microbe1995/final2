# ============================================================================
# 🏭 Process Controller - 공정 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List, Optional

from app.domain.process.process_service import ProcessService
from app.domain.process.process_schema import (
    ProcessCreateRequest, ProcessResponse, ProcessUpdateRequest
)

logger = logging.getLogger(__name__)

# Gateway를 통해 접근하므로 /process 경로로 설정 (prefix 없음)
router = APIRouter(tags=["Process"])

def get_process_service():
    """Process 서비스 인스턴스 반환"""
    return ProcessService()

@router.get("/", response_model=List[ProcessResponse])
async def get_processes(
    process_name: Optional[str] = None,
    product_id: Optional[int] = None
):
    """프로세스 목록 조회 (선택적 필터링)"""
    try:
        logger.info(f"📋 프로세스 목록 조회 요청 - process_name: {process_name}, product_id: {product_id}")
        process_service = get_process_service()
        processes = await process_service.get_processes()
        
        # 필터링 적용
        if process_name:
            processes = [p for p in processes if process_name.lower() in p.process_name.lower()]
        if product_id is not None:
            processes = [p for p in processes if p.products and any(prod.get('id') == product_id for prod in p.products)]
        
        logger.info(f"✅ 프로세스 목록 조회 성공: {len(processes)}개")
        return processes
    except Exception as e:
        logger.error(f"❌❌ 프로세스 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/{process_id}", response_model=ProcessResponse)
async def get_process(process_id: int):
    """특정 프로세스 조회"""
    try:
        logger.info(f"📋 프로세스 조회 요청: ID {process_id}")
        process_service = get_process_service()
        process = await process_service.get_process(process_id)
        
        if not process:
            logger.warning(f"⚠️ 프로세스를 찾을 수 없음: ID {process_id}")
            raise HTTPException(status_code=404, detail="프로세스를 찾을 수 없습니다.")
        
        logger.info(f"✅ 프로세스 조회 성공: ID {process_id}")
        return process
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 조회 실패: ID {process_id}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/", response_model=ProcessResponse)
async def create_process(request: ProcessCreateRequest):
    """프로세스 생성"""
    try:
        logger.info(f"🔄 프로세스 생성 요청: {request.process_name}")
        process_service = get_process_service()
        process = await process_service.create_process(request)
        logger.info(f"✅ 프로세스 생성 성공: ID {process.id}")
        return process
    except Exception as e:
        logger.error(f"❌ 프로세스 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/{process_id}", response_model=ProcessResponse)
async def update_process(process_id: int, request: ProcessUpdateRequest):
    """프로세스 수정"""
    try:
        logger.info(f"📝 프로세스 수정 요청: ID {process_id}")
        process_service = get_process_service()
        process = await process_service.update_process(process_id, request)
        
        if not process:
            logger.warning(f"⚠️ 수정할 프로세스를 찾을 수 없음: ID {process_id}")
            raise HTTPException(status_code=404, detail="수정할 프로세스를 찾을 수 없습니다.")
        
        logger.info(f"✅ 프로세스 수정 성공: ID {process_id}")
        return process
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 수정 실패: ID {process_id}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/{process_id}")
async def delete_process(process_id: int):
    """프로세스 삭제"""
    try:
        logger.info(f"🗑️ 프로세스 삭제 요청: ID {process_id}")
        process_service = get_process_service()
        success = await process_service.delete_process(process_id)
        
        if not success:
            logger.warning(f"⚠️ 삭제할 프로세스를 찾을 수 없음: ID {process_id}")
            raise HTTPException(status_code=404, detail="삭제할 프로세스를 찾을 수 없습니다.")
        
        logger.info(f"✅ 프로세스 삭제 성공: ID {process_id}")
        return {"message": "프로세스가 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 삭제 실패: ID {process_id}, 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 삭제 중 오류가 발생했습니다: {str(e)}")

process_router = router
__all__ = ["router", "process_router"]
