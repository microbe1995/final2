"""
CBAM 산정경계 저장소 - CBAM 관련 데이터의 데이터 접근 로직
boundary 서비스에서 CBAM 산정경계 정보를 저장하고 조회

주요 기능:
- 기업 정보 생성/조회/수정/삭제
- CBAM 제품 관리
- 생산 공정 정보 관리
- 배출원 및 배출량 데이터 관리
- PostgreSQL 및 메모리 저장소 지원
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

import json
import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, text

from ...common.database.connection import db_connection
from ..boundary.boundary_entity import (
    CompanyEntity,
    CBAMProductEntity,
    ProductionProcessEntity,
    CalculationBoundaryEntity,
    EmissionSourceEntity,
    SourceStreamEntity,
    ReportingPeriodEntity,
    DataAllocationEntity
)

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 📚 CBAM 산정경계 저장소 클래스
# ============================================================================

class BoundaryRepository:
    """
    CBAM 산정경계 데이터 저장소
    
    주요 기능:
    - 기업 정보 CRUD
    - CBAM 제품 관리
    - 생산 공정 데이터 관리
    - 배출원 관리
    - PostgreSQL 및 메모리 저장소 지원
    """
    
    def __init__(self, use_database: bool = True):
        """
        CBAM 산정경계 저장소 초기화
        
        Args:
            use_database: PostgreSQL 사용 여부 (기본값: True)
        """
        self.use_database = use_database
        
        # 메모리 저장소는 항상 초기화 (fallback용)
        self._companies: dict = {}
        self._products: dict = {}
        self._processes: dict = {}
        self._boundaries: dict = {}
        self._emission_sources: dict = {}
        self._source_streams: dict = {}
        self._reporting_periods: dict = {}
        self._data_allocations: dict = {}
        
        logger.info(f"✅ {'PostgreSQL' if use_database else '메모리'} CBAM 산정경계 저장소 사용")
    
    # ============================================================================
    # 🏭 기업 정보 CRUD 메서드
    # ============================================================================
    
    async def create_company(self, company_data: dict) -> dict:
        """
        기업 정보 생성
        
        Args:
            company_data: 생성할 기업 정보
            
        Returns:
            dict: 생성된 기업 정보
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._create_company_db(company_data)
            else:
                return await self._create_company_memory(company_data)
        except Exception as e:
            logger.error(f"❌ 기업 정보 생성 실패: {str(e)}")
            raise
    
    async def get_company_by_id(self, company_id: str) -> Optional[dict]:
        """
        기업 ID로 기업 조회
        
        Args:
            company_id: 조회할 기업 ID
            
        Returns:
            Optional[dict]: 기업 정보 또는 None
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_company_by_id_db(company_id)
            else:
                return self._companies.get(company_id)
        except Exception as e:
            logger.error(f"❌ 기업 ID 조회 실패: {company_id} - {str(e)}")
            return None
    
    async def update_company(self, company_id: str, company_data: dict) -> Optional[dict]:
        """
        기업 정보 업데이트
        
        Args:
            company_id: 업데이트할 기업 ID
            company_data: 업데이트할 기업 정보
            
        Returns:
            Optional[dict]: 업데이트된 기업 정보
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._update_company_db(company_id, company_data)
            else:
                return await self._update_company_memory(company_id, company_data)
        except Exception as e:
            logger.error(f"❌ 기업 정보 업데이트 실패: {company_id} - {str(e)}")
            raise
    
    async def delete_company(self, company_id: str) -> bool:
        """
        기업 정보 삭제
        
        Args:
            company_id: 삭제할 기업 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._delete_company_db(company_id)
            else:
                return await self._delete_company_memory(company_id)
        except Exception as e:
            logger.error(f"❌ 기업 정보 삭제 실패: {company_id} - {str(e)}")
            return False
    
    async def get_all_companies(self) -> List[dict]:
        """
        모든 기업 조회
        
        Returns:
            List[dict]: 기업 목록
        """
        try:
            if self.use_database and db_connection.engine:
                return await self._get_all_companies_db()
            else:
                return list(self._companies.values())
        except Exception as e:
            logger.error(f"❌ 모든 기업 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 📦 CBAM 제품 CRUD 메서드
    # ============================================================================
    
    async def create_product(self, product_data: dict) -> dict:
        """CBAM 제품 생성"""
        try:
            if self.use_database and db_connection.engine:
                return await self._create_product_db(product_data)
            else:
                return await self._create_product_memory(product_data)
        except Exception as e:
            logger.error(f"❌ CBAM 제품 생성 실패: {str(e)}")
            raise
    
    async def get_products_by_company(self, company_id: str) -> List[dict]:
        """기업별 CBAM 제품 목록 조회"""
        try:
            if self.use_database and db_connection.engine:
                return await self._get_products_by_company_db(company_id)
            else:
                return [p for p in self._products.values() if p.get('company_id') == company_id]
        except Exception as e:
            logger.error(f"❌ 기업별 CBAM 제품 조회 실패: {company_id} - {str(e)}")
            return []
    
    # ============================================================================
    # 🏭 생산 공정 CRUD 메서드
    # ============================================================================
    
    async def create_process(self, process_data: dict) -> dict:
        """생산 공정 생성"""
        try:
            if self.use_database and db_connection.engine:
                return await self._create_process_db(process_data)
            else:
                return await self._create_process_memory(process_data)
        except Exception as e:
            logger.error(f"❌ 생산 공정 생성 실패: {str(e)}")
            raise
    
    async def get_processes_by_product(self, product_id: str) -> List[dict]:
        """제품별 생산 공정 목록 조회"""
        try:
            if self.use_database and db_connection.engine:
                return await self._get_processes_by_product_db(product_id)
            else:
                return [p for p in self._processes.values() if p.get('product_id') == product_id]
        except Exception as e:
            logger.error(f"❌ 제품별 생산 공정 조회 실패: {product_id} - {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드 - 기업 정보
    # ============================================================================
    
    async def _create_company_db(self, company_data: dict) -> dict:
        """PostgreSQL에 기업 정보 생성"""
        try:
            async with db_connection.get_session_context() as session:
                company_entity = CompanyEntity(
                    id=company_data.get('id'),
                    company_name=company_data.get('company_name'),
                    business_address=company_data.get('business_address'),
                    business_number=company_data.get('business_number'),
                    representative_name=company_data.get('representative_name'),
                    contact_email=company_data.get('contact_email'),
                    contact_phone=company_data.get('contact_phone')
                )
                
                session.add(company_entity)
                await session.commit()
                await session.refresh(company_entity)
                
                logger.info(f"✅ PostgreSQL 기업 정보 생성 성공: {company_entity.company_name}")
                return company_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 기업 정보 생성 실패: {str(e)}")
            raise
    
    async def _get_company_by_id_db(self, company_id: str) -> Optional[dict]:
        """PostgreSQL에서 기업 ID로 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(CompanyEntity).where(CompanyEntity.id == company_id)
                )
                company_data = result.scalar_one_or_none()
                
                if company_data:
                    return company_data.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 기업 ID 조회 실패: {str(e)}")
            return None
    
    async def _update_company_db(self, company_id: str, company_data: dict) -> Optional[dict]:
        """PostgreSQL에서 기업 정보 업데이트"""
        try:
            async with db_connection.get_session_context() as session:
                # 업데이트할 필드만 추출
                update_fields = {}
                if 'company_name' in company_data:
                    update_fields['company_name'] = company_data['company_name']
                if 'business_address' in company_data:
                    update_fields['business_address'] = company_data['business_address']
                if 'representative_name' in company_data:
                    update_fields['representative_name'] = company_data['representative_name']
                if 'contact_email' in company_data:
                    update_fields['contact_email'] = company_data['contact_email']
                if 'contact_phone' in company_data:
                    update_fields['contact_phone'] = company_data['contact_phone']
                
                if update_fields:
                    update_fields['updated_at'] = datetime.utcnow()
                    
                    await session.execute(
                        update(CompanyEntity).where(CompanyEntity.id == company_id).values(**update_fields)
                    )
                    await session.commit()
                
                # 업데이트된 데이터 조회
                result = await session.execute(
                    select(CompanyEntity).where(CompanyEntity.id == company_id)
                )
                updated_company = result.scalar_one_or_none()
                
                if updated_company:
                    logger.info(f"✅ PostgreSQL 기업 정보 업데이트 성공: {company_id}")
                    return updated_company.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 기업 정보 업데이트 실패: {str(e)}")
            raise
    
    async def _delete_company_db(self, company_id: str) -> bool:
        """PostgreSQL에서 기업 정보 삭제"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    delete(CompanyEntity).where(CompanyEntity.id == company_id)
                )
                await session.commit()
                
                deleted_count = result.rowcount
                if deleted_count > 0:
                    logger.info(f"✅ PostgreSQL 기업 정보 삭제 성공: {company_id}")
                    return True
                else:
                    logger.warning(f"⚠️ PostgreSQL 기업 정보 삭제 실패: 기업을 찾을 수 없음 {company_id}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 기업 정보 삭제 실패: {str(e)}")
            return False
    
    async def _get_all_companies_db(self) -> List[dict]:
        """PostgreSQL에서 모든 기업 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(select(CompanyEntity))
                companies_data = result.scalars().all()
                
                companies = [company.to_dict() for company in companies_data]
                
                return companies
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 모든 기업 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드 - CBAM 제품
    # ============================================================================
    
    async def _create_product_db(self, product_data: dict) -> dict:
        """PostgreSQL에 CBAM 제품 생성"""
        try:
            async with db_connection.get_session_context() as session:
                product_entity = CBAMProductEntity(
                    id=product_data.get('id'),
                    company_id=product_data.get('company_id'),
                    product_name=product_data.get('product_name'),
                    product_code=product_data.get('product_code'),
                    cbam_code=product_data.get('cbam_code'),
                    description=product_data.get('description'),
                    production_capacity=product_data.get('production_capacity'),
                    annual_production=product_data.get('annual_production'),
                    unit=product_data.get('unit')
                )
                
                session.add(product_entity)
                await session.commit()
                await session.refresh(product_entity)
                
                logger.info(f"✅ PostgreSQL CBAM 제품 생성 성공: {product_entity.product_name}")
                return product_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL CBAM 제품 생성 실패: {str(e)}")
            raise
    
    async def _get_products_by_company_db(self, company_id: str) -> List[dict]:
        """PostgreSQL에서 기업별 CBAM 제품 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(CBAMProductEntity).where(CBAMProductEntity.company_id == company_id)
                )
                products_data = result.scalars().all()
                
                products = [product.to_dict() for product in products_data]
                
                return products
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 기업별 CBAM 제품 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🗄️ PostgreSQL 데이터베이스 메서드 - 생산 공정
    # ============================================================================
    
    async def _create_process_db(self, process_data: dict) -> dict:
        """PostgreSQL에 생산 공정 생성"""
        try:
            async with db_connection.get_session_context() as session:
                process_entity = ProductionProcessEntity(
                    id=process_data.get('id'),
                    product_id=process_data.get('product_id'),
                    process_name=process_data.get('process_name'),
                    process_code=process_data.get('process_code'),
                    description=process_data.get('description'),
                    facility_location=process_data.get('facility_location'),
                    process_type=process_data.get('process_type'),
                    input_materials=process_data.get('input_materials'),
                    output_products=process_data.get('output_products'),
                    energy_consumption=process_data.get('energy_consumption'),
                    operating_hours=process_data.get('operating_hours')
                )
                
                session.add(process_entity)
                await session.commit()
                await session.refresh(process_entity)
                
                logger.info(f"✅ PostgreSQL 생산 공정 생성 성공: {process_entity.process_name}")
                return process_entity.to_dict()
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 생산 공정 생성 실패: {str(e)}")
            raise
    
    async def _get_processes_by_product_db(self, product_id: str) -> List[dict]:
        """PostgreSQL에서 제품별 생산 공정 조회"""
        try:
            async with db_connection.get_session_context() as session:
                result = await session.execute(
                    select(ProductionProcessEntity).where(ProductionProcessEntity.product_id == product_id)
                )
                processes_data = result.scalars().all()
                
                processes = [process.to_dict() for process in processes_data]
                
                return processes
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL 제품별 생산 공정 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 💾 메모리 저장소 메서드
    # ============================================================================
    
    async def _create_company_memory(self, company_data: dict) -> dict:
        """메모리에 기업 정보 생성"""
        company_id = company_data.get('id')
        self._companies[company_id] = company_data
        
        logger.info(f"✅ 메모리 기업 정보 생성: {company_data.get('company_name')}")
        return company_data
    
    async def _update_company_memory(self, company_id: str, company_data: dict) -> Optional[dict]:
        """메모리에서 기업 정보 업데이트"""
        if company_id in self._companies:
            self._companies[company_id].update(company_data)
            self._companies[company_id]['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ 메모리 기업 정보 업데이트 성공: {company_id}")
            return self._companies[company_id]
        else:
            return None
    
    async def _delete_company_memory(self, company_id: str) -> bool:
        """메모리에서 기업 정보 삭제"""
        if company_id in self._companies:
            del self._companies[company_id]
            
            logger.info(f"✅ 메모리 기업 정보 삭제 성공: {company_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 기업 정보 삭제 실패: 기업을 찾을 수 없음 {company_id}")
            return False
    
    async def _create_product_memory(self, product_data: dict) -> dict:
        """메모리에 CBAM 제품 생성"""
        product_id = product_data.get('id')
        self._products[product_id] = product_data
        
        logger.info(f"✅ 메모리 CBAM 제품 생성: {product_data.get('product_name')}")
        return product_data
    
    async def _create_process_memory(self, process_data: dict) -> dict:
        """메모리에 생산 공정 생성"""
        process_id = process_data.get('id')
        self._processes[process_id] = process_data
        
        logger.info(f"✅ 메모리 생산 공정 생성: {process_data.get('process_name')}")
        return process_data
