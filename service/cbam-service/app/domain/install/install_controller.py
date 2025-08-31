# ============================================================================
# 🏭 Install Controller - 사업장 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List

from app.domain.install.install_service import InstallService
from app.domain.install.install_schema import (
    InstallCreateRequest, InstallResponse, InstallUpdateRequest, InstallNameResponse
)

logger = logging.getLogger(__name__)

# prefix 없이 등록되므로 /install 경로로 시작
router = APIRouter(tags=["Install"])

# 서비스 인스턴스는 요청 시마다 생성 (모듈 레벨 초기화 방지)
def get_install_service():
    """Install 서비스 인스턴스 반환"""
    return InstallService()

# ============================================================================
# 🏭 Install 관련 엔드포인트
# ============================================================================

# 실제 경로: /install (사업장 목록 조회)
@router.get("/install", response_model=List[InstallResponse])
async def get_installs():
    """사업장 목록 조회"""
    try:
        logger.info("📋 사업장 목록 조회 요청")
        install_service = get_install_service()
        installs = await install_service.get_installs()
        logger.info(f"✅ 사업장 목록 조회 성공: {len(installs)}개")
        return installs
    except Exception as e:
        logger.error(f"❌ 사업장 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 목록 조회 중 오류가 발생했습니다: {str(e)}")

# 실제 경로: /install/names (사업장명 목록 조회)
@router.get("/install/names", response_model=List[InstallNameResponse])
async def get_install_names():
    """사업장명 목록 조회 (드롭다운용)"""
    try:
        logger.info("📋 사업장명 목록 조회 요청")
        install_service = get_install_service()
        install_names = await install_service.get_install_names()
        logger.info(f"✅ 사업장명 목록 조회 성공: {len(install_names)}개")
        return install_names
    except Exception as e:
        logger.error(f"❌ 사업장명 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장명 목록 조회 중 오류가 발생했습니다: {str(e)}")

# 실제 경로: /install (사업장 생성)
@router.post("/install", response_model=InstallResponse)
async def create_install(request: InstallCreateRequest):
    """사업장 생성"""
    try:
        logger.info(f"📝 사업장 생성 요청: {request.install_name}")
        install_service = get_install_service()
        install = await install_service.create_install(request)
        if not install:
            raise HTTPException(status_code=400, detail="사업장 생성에 실패했습니다")
        
        logger.info(f"✅ 사업장 생성 성공: ID {install.id}")
        return install
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 생성 중 오류가 발생했습니다: {str(e)}")

# 실제 경로: /install/{install_id} (특정 사업장 조회)
@router.get("/install/{install_id}", response_model=InstallResponse)
async def get_install(install_id: int):
    """특정 사업장 조회"""
    try:
        logger.info(f"📋 사업장 조회 요청: ID {install_id}")
        install_service = get_install_service()
        install = await install_service.get_install(install_id)
        if not install:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 조회 성공: ID {install_id}")
        return install
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 생성 중 오류가 발생했습니다: {str(e)}")

# 실제 경로: /install/{install_id} (사업장 수정)
@router.put("/install/{install_id}", response_model=InstallResponse)
async def update_install(install_id: int, request: InstallUpdateRequest):
    """사업장 수정"""
    try:
        logger.info(f"📝 사업장 수정 요청: ID {install_id}")
        install_service = get_install_service()
        install = await install_service.update_install(install_id, request)
        if not install:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 수정 성공: ID {install_id}")
        return install
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 생성 중 오류가 발생했습니다: {str(e)}")

# 실제 경로: /install/{install_id} (사업장 삭제)
@router.delete("/install/{install_id}")
async def delete_install(install_id: int):
    """사업장 삭제"""
    try:
        logger.info(f"🗑️ 사업장 삭제 요청: ID {install_id}")
        install_service = get_install_service()
        success = await install_service.delete_install(install_id)
        if not success:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 삭제 성공: ID {install_id}")
        return {"message": "사업장이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 Router Export
# ============================================================================

# install_router를 다른 모듈에서 import할 수 있도록 export
install_router = router
__all__ = ["router", "install_router"]
