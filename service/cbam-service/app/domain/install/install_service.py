# ============================================================================
# 🏭 Install Service - 사업장 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.install.install_repository import InstallRepository
from app.domain.install.install_schema import (
    InstallCreateRequest, InstallResponse, InstallUpdateRequest, InstallNameResponse
)

logger = logging.getLogger(__name__)

class InstallService:
    """사업장 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.install_repository = InstallRepository()
        logger.info("✅ Install 서비스 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.install_repository.initialize()
            logger.info("✅ Install 서비스 데이터베이스 연결 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Install 서비스 데이터베이스 초기화 실패 (서비스는 계속 실행): {e}")
            logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    # ============================================================================
    # 🏭 Install 관련 메서드
    # ============================================================================
    
    async def create_install(self, request: InstallCreateRequest) -> InstallResponse:
        """사업장 생성"""
        try:
            install_data = {
                "install_name": request.install_name,
                "reporting_year": request.reporting_year
            }
            
            saved_install = await self.install_repository.create_install(install_data)
            if saved_install:
                return InstallResponse(**saved_install)
            else:
                raise Exception("사업장 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error creating install: {e}")
            raise e
    
    async def get_installs(self) -> List[InstallResponse]:
        """사업장 목록 조회"""
        try:
            installs = await self.install_repository.get_installs()
            return [InstallResponse(**install) for install in installs]
        except Exception as e:
            logger.error(f"Error getting installs: {e}")
            raise e
    
    async def get_install_names(self) -> List[InstallNameResponse]:
        """사업장명 목록 조회 (드롭다운용)"""
        try:
            install_names = await self.install_repository.get_install_names()
            return [InstallNameResponse(**install) for install in install_names]
        except Exception as e:
            logger.error(f"Error getting install names: {e}")
            raise e
    
    async def get_install(self, install_id: int) -> Optional[InstallResponse]:
        """특정 사업장 조회"""
        try:
            install = await self.install_repository.get_install(install_id)
            if install:
                return InstallResponse(**install)
            return None
        except Exception as e:
            logger.error(f"Error getting install {install_id}: {e}")
            raise e
    
    async def update_install(self, install_id: int, request: InstallUpdateRequest) -> Optional[InstallResponse]:
        """사업장 수정"""
        try:
            # None이 아닌 필드만 업데이트 데이터에 포함
            update_data = {}
            if request.install_name is not None:
                update_data["install_name"] = request.install_name
            if request.reporting_year is not None:
                update_data["reporting_year"] = request.reporting_year
            
            if not update_data:
                raise Exception("업데이트할 데이터가 없습니다.")
            
            updated_install = await self.install_repository.update_install(install_id, update_data)
            if updated_install:
                return InstallResponse(**updated_install)
            return None
        except Exception as e:
            logger.error(f"Error updating install {install_id}: {e}")
            raise e
    
    async def delete_install(self, install_id: int) -> bool:
        """사업장 삭제"""
        try:
            success = await self.install_repository.delete_install(install_id)
            if success:
                logger.info(f"✅ 사업장 삭제 성공: ID {install_id}")
            else:
                logger.warning(f"⚠️ 사업장 삭제 실패: ID {install_id} (존재하지 않음)")
            return success
        except Exception as e:
            logger.error(f"Error deleting install {install_id}: {e}")
            raise e
