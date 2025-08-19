"""
CBAM 산정경계 저장소 - 산정경계 설정 및 데이터 할당 관련 데이터 접근 로직

주요 기능:
- 산정경계 설정 관리
- 데이터 할당 계획 관리
- PostgreSQL 및 메모리 저장소 지원
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, text

from app.common.database.connection import db_connection
from app.domain.boundary.boundary_entity import (
    CalculationBoundaryEntity,
    DataAllocationEntity
)

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 📚 산정경계 및 데이터 할당 저장소 클래스
# ============================================================================

class BoundaryRepository:
    """
    산정경계 및 데이터 할당 저장소
    
    주요 기능:
    - 산정경계 설정 CRUD
    - 데이터 할당 계획 CRUD
    - PostgreSQL 및 메모리 저장소 지원
    """
    
    def __init__(self, use_database: bool = True):
        """
        산정경계 저장소 초기화
        
        Args:
            use_database: PostgreSQL 사용 여부 (기본값: True)
        """
        self.use_database = use_database
        
        # 메모리 저장소는 항상 초기화 (fallback용)
        self._boundaries: Dict[str, Dict[str, Any]] = {}
        self._data_allocations: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} 산정경계 및 데이터 할당 저장소 사용")
    
    # ============================================================================
    # 🌍 산정경계 설정 CRUD 메서드
    # ============================================================================
    
    async def create_boundary(self, boundary_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        산정경계 설정 생성
        
        Args:
            boundary_data: 생성할 산정경계 정보
            
        Returns:
            Dict[str, Any]: 생성된 산정경계 정보
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._create_boundary_db(boundary_data)
            else:
                return await self._create_boundary_memory(boundary_data)
        except Exception as e:
            logger.error(f"❌ 산정경계 설정 생성 실패: {str(e)}")
            raise
    
    async def get_boundary_by_id(self, boundary_id: str) -> Optional[Dict[str, Any]]:
        """
        산정경계 ID로 조회
        
        Args:
            boundary_id: 조회할 산정경계 ID
            
        Returns:
            Optional[Dict[str, Any]]: 산정경계 정보 또는 None
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_boundary_by_id_db(boundary_id)
            else:
                return self._boundaries.get(boundary_id)
        except Exception as e:
            logger.error(f"❌ 산정경계 ID 조회 실패: {boundary_id} - {str(e)}")
            return None
    
    async def update_boundary(self, boundary_id: str, boundary_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        산정경계 설정 업데이트
        
        Args:
            boundary_id: 업데이트할 산정경계 ID
            boundary_data: 업데이트할 산정경계 정보
            
        Returns:
            Optional[Dict[str, Any]]: 업데이트된 산정경계 정보
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._update_boundary_db(boundary_id, boundary_data)
            else:
                return await self._update_boundary_memory(boundary_id, boundary_data)
        except Exception as e:
            logger.error(f"❌ 산정경계 설정 업데이트 실패: {boundary_id} - {str(e)}")
            raise
    
    async def delete_boundary(self, boundary_id: str) -> bool:
        """
        산정경계 설정 삭제
        
        Args:
            boundary_id: 삭제할 산정경계 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._delete_boundary_db(boundary_id)
            else:
                return await self._delete_boundary_memory(boundary_id)
        except Exception as e:
            logger.error(f"❌ 산정경계 설정 삭제 실패: {boundary_id} - {str(e)}")
            return False
    
    # ============================================================================
    # 🔄 데이터 할당 CRUD 메서드
    # ============================================================================
    
    async def create_allocation(self, allocation_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 할당 계획 생성"""
        try:
            if self.use_database and db_connection.engine:
                return await self._create_allocation_db(allocation_data)
            else:
                return await self._create_allocation_memory(allocation_data)
        except Exception as e:
            logger.error(f"❌ 데이터 할당 계획 생성 실패: {str(e)}")
            raise
    
    async def get_allocation_by_id(self, allocation_id: str) -> Optional[Dict[str, Any]]:
        """데이터 할당 계획 조회"""
        try:
            if self.use_database and db_connection.engine:
                return await self._get_allocation_by_id_db(allocation_id)
            else:
                return self._data_allocations.get(allocation_id)
        except Exception as e:
            logger.error(f"❌ 데이터 할당 계획 조회 실패: {allocation_id} - {str(e)}")
            return None
    
    async def get_allocations_by_boundary(self, boundary_id: str) -> List[Dict[str, Any]]:
        """산정경계별 데이터 할당 계획 목록 조회"""
        try:
            if self.use_database and db_connection.engine:
                return await self._get_allocations_by_boundary_db(boundary_id)
            else:
                return [a for a in self._data_allocations.values() if a.get('boundary_id') == boundary_id]
        except Exception as e:
            logger.error(f"❌ 산정경계별 데이터 할당 계획 조회 실패: {boundary_id} - {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드 - 산정경계
    # ============================================================================
    
    async def _create_boundary_db(self, boundary_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 산정경계 설정 생성"""
        try:
            async with db_connection.get_session_context() as session:
                boundary_entity = CalculationBoundaryEntity(
                    id=boundary_data.get('id'),
                    company_id=boundary_data.get('company_id'),
                    boundary_id=boundary_data.get('boundary_id'),
                    boundary_name=boundary_data.get('boundary_name'),
                    boundary_type=boundary_data.get('boundary_type'),
                    included_processes=boundary_data.get('included_processes'),
                    excluded_processes=boundary_data.get('excluded_processes'),
                    shared_utilities=boundary_data.get('shared_utilities'),
                    allocation_method=boundary_data.get('allocation_method'),
                    description=boundary_data.get('description')
                )
                
                session.add(boundary_entity)
                await session.commit()
                await session.refresh(boundary_entity)
                
                logger.info(f"✅ PostgreSQL 산정경계 설정 생성 성공: {boundary_entity.boundary_name}")
                return boundary_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 산정경계 설정 생성 실패: {str(e)}")
            raise
    
    async def _get_boundary_by_id_db(self, boundary_id: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 산정경계 ID로 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(CalculationBoundaryEntity).where(CalculationBoundaryEntity.boundary_id == boundary_id)
                )
                boundary_data = result.scalar_one_or_none()
                
                if boundary_data:
                    return boundary_data.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 산정경계 ID 조회 실패: {str(e)}")
            return None
    
    async def _update_boundary_db(self, boundary_id: str, boundary_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 산정경계 설정 업데이트"""
        try:
            async with db_connection.get_session_context() as session:
                # 업데이트할 필드만 추출
                update_fields = {k: v for k, v in boundary_data.items() if k != 'boundary_id'}
                if update_fields:
                    update_fields['updated_at'] = datetime.utcnow()
                    
                    await session.execute(
                        update(CalculationBoundaryEntity).where(CalculationBoundaryEntity.boundary_id == boundary_id).values(**update_fields)
                    )
                    await session.commit()
                
                # 업데이트된 데이터 조회
                result = await session.execute(
                    select(CalculationBoundaryEntity).where(CalculationBoundaryEntity.boundary_id == boundary_id)
                )
                updated_boundary = result.scalar_one_or_none()
                
                if updated_boundary:
                    logger.info(f"✅ PostgreSQL 산정경계 설정 업데이트 성공: {boundary_id}")
                    return updated_boundary.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 산정경계 설정 업데이트 실패: {str(e)}")
            raise
    
    async def _delete_boundary_db(self, boundary_id: str) -> bool:
        """PostgreSQL에서 산정경계 설정 삭제"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    delete(CalculationBoundaryEntity).where(CalculationBoundaryEntity.boundary_id == boundary_id)
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 산정경계 설정 삭제 성공: {boundary_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 산정경계 설정 삭제 실패: 산정경계를 찾을 수 없음 {boundary_id}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 산정경계 설정 삭제 실패: {str(e)}")
            return False
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드 - 데이터 할당
    # ============================================================================
    
    async def _create_allocation_db(self, allocation_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 데이터 할당 계획 생성"""
        try:
            async with db_connection.get_session_context() as session:
                allocation_entity = DataAllocationEntity(
                    id=allocation_data.get('id'),
                    boundary_id=allocation_data.get('boundary_id'),
                    allocation_id=allocation_data.get('allocation_id'),
                    shared_resource=allocation_data.get('shared_resource'),
                    resource_type=allocation_data.get('resource_type'),
                    total_consumption=allocation_data.get('total_consumption'),
                    unit=allocation_data.get('unit'),
                    allocation_method=allocation_data.get('allocation_method'),
                    allocation_factors=allocation_data.get('allocation_factors'),
                    measurement_reliability=allocation_data.get('measurement_reliability')
                )
                
                session.add(allocation_entity)
                await session.commit()
                await session.refresh(allocation_entity)
                
                logger.info(f"✅ PostgreSQL 데이터 할당 계획 생성 성공: {allocation_entity.shared_resource}")
                return allocation_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 데이터 할당 계획 생성 실패: {str(e)}")
            raise
    
    async def _get_allocation_by_id_db(self, allocation_id: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 데이터 할당 계획 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(DataAllocationEntity).where(DataAllocationEntity.allocation_id == allocation_id)
                )
                allocation_data = result.scalar_one_or_none()
                
                if allocation_data:
                    return allocation_data.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 데이터 할당 계획 조회 실패: {str(e)}")
            return None
    
    async def _get_allocations_by_boundary_db(self, boundary_id: str) -> List[Dict[str, Any]]:
        """PostgreSQL에서 산정경계별 데이터 할당 계획 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(DataAllocationEntity).where(DataAllocationEntity.boundary_id == boundary_id)
                )
                allocations_data = result.scalars().all()
                
                allocations = [allocation.to_dict() for allocation in allocations_data]
                
                return allocations
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 산정경계별 데이터 할당 계획 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_boundary_memory(self, boundary_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 산정경계 설정 생성"""
        boundary_id = boundary_data.get('boundary_id')
        self._boundaries[boundary_id] = boundary_data
        
        logger.info(f"✅ 메모리 산정경계 설정 생성: {boundary_data.get('boundary_name')}")
        return boundary_data
    
    async def _update_boundary_memory(self, boundary_id: str, boundary_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """메모리에서 산정경계 설정 업데이트"""
        if boundary_id in self._boundaries:
            self._boundaries[boundary_id].update(boundary_data)
            self._boundaries[boundary_id]['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ 메모리 산정경계 설정 업데이트 성공: {boundary_id}")
            return self._boundaries[boundary_id]
        else:
            return None
    
    async def _delete_boundary_memory(self, boundary_id: str) -> bool:
        """메모리에서 산정경계 설정 삭제"""
        if boundary_id in self._boundaries:
            del self._boundaries[boundary_id]
            
            logger.info(f"✅ 메모리 산정경계 설정 삭제 성공: {boundary_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 산정경계 설정 삭제 실패: 산정경계를 찾을 수 없음 {boundary_id}")
            return False
    
    async def _create_allocation_memory(self, allocation_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 데이터 할당 계획 생성"""
        allocation_id = allocation_data.get('allocation_id')
        self._data_allocations[allocation_id] = allocation_data
        
        logger.info(f"✅ 메모리 데이터 할당 계획 생성: {allocation_data.get('shared_resource')}")
        return allocation_data
