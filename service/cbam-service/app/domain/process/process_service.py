# 🔄 Process Service - 공정 비즈니스 로직
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.process.process_repository import ProcessRepository
from app.domain.process.process_schema import (
    ProcessCreateRequest, ProcessResponse, ProcessUpdateRequest
)

logger = logging.getLogger(__name__)

class ProcessService:
    """공정 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.process_repository = ProcessRepository()
        logger.info("✅ Process 서비스 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.process_repository.initialize()
            logger.info("✅ Process 서비스 데이터베이스 연결 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Process 서비스 데이터베이스 초기화 실패 (서비스는 계속 실행): {e}")
            logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    async def create_process(self, request: ProcessCreateRequest) -> ProcessResponse:
        """공정 생성 (다대다 관계)"""
        try:
            process_data = {
                "process_name": request.process_name,
                "start_period": request.start_period,
                "end_period": request.end_period,
                "product_ids": getattr(request, 'product_ids', [])  # 다대다 관계를 위한 제품 ID 목록
            }
            
            saved_process = await self.process_repository.create_process(process_data)
            if saved_process:
                return ProcessResponse(**saved_process)
            else:
                raise Exception("공정 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error creating process: {e}")
            raise e
    
    async def get_processes(self) -> List[ProcessResponse]:
        """프로세스 목록 조회"""
        try:
            processes = await self.process_repository.get_processes()
            return [ProcessResponse(**process) for process in processes]
        except Exception as e:
            logger.error(f"Error getting processes: {e}")
            raise e
    
    async def get_process(self, process_id: int) -> Optional[ProcessResponse]:
        """특정 프로세스 조회"""
        try:
            process = await self.process_repository.get_process(process_id)
            if process:
                return ProcessResponse(**process)
            return None
        except Exception as e:
            logger.error(f"Error getting process {process_id}: {e}")
            raise e
    
    async def update_process(self, process_id: int, request: ProcessUpdateRequest) -> Optional[ProcessResponse]:
        """프로세스 수정"""
        try:
            # None이 아닌 필드만 업데이트 데이터에 포함
            update_data = {}
            if request.process_name is not None:
                update_data["process_name"] = request.process_name
            if request.start_period is not None:
                update_data["start_period"] = request.start_period
            if request.end_period is not None:
                update_data["end_period"] = request.end_period
            
            if not update_data:
                raise Exception("업데이트할 데이터가 없습니다.")
            
            updated_process = await self.process_repository.update_process(process_id, update_data)
            if updated_process:
                return ProcessResponse(**updated_process)
            return None
        except Exception as e:
            logger.error(f"Error updating process {process_id}: {e}")
            raise e
    
    async def delete_process(self, process_id: int) -> bool:
        """프로세스 삭제"""
        try:
            return await self.process_repository.delete_process(process_id)
        except Exception as e:
            logger.error(f"Error deleting process {process_id}: {e}")
            raise e
