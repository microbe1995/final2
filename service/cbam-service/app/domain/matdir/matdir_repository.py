# ============================================================================
# 📦 MatDir Repository - 원료직접배출량 데이터 접근
# ============================================================================

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
from decimal import Decimal

logger = logging.getLogger(__name__)

class MatDirRepository:
    """원료직접배출량 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
            return
        
        self.pool = None
        self._initialization_attempted = False
    
    async def initialize(self):
        """데이터베이스 연결 풀 초기화"""
        if self._initialization_attempted:
            return  # 이미 초기화 시도했으면 다시 시도하지 않음
            
        if not self.database_url:
            logger.warning("DATABASE_URL이 없어 데이터베이스 초기화를 건너뜁니다.")
            self._initialization_attempted = True
            return
        
        self._initialization_attempted = True
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'application_name': 'cbam-service-matdir'
                }
            )
            logger.info("✅ MatDir 데이터베이스 연결 풀 생성 성공")
            
            # 테이블 생성은 선택적으로 실행
            try:
                await self._create_matdir_table_async()
            except Exception as e:
                logger.warning(f"⚠️ MatDir 테이블 생성 실패 (기본 기능은 정상): {e}")
            
        except Exception as e:
            logger.error(f"❌ MatDir 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
    async def _create_matdir_table_async(self):
        """matdir 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # matdir 테이블이 이미 존재하는지 확인
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'matdir'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ matdir 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    # matdir 테이블 생성
                    await conn.execute("""
                        CREATE TABLE matdir (
                            id SERIAL PRIMARY KEY,
                            process_id INTEGER NOT NULL,
                            mat_name VARCHAR(255) NOT NULL,
                            mat_factor NUMERIC(10, 6) NOT NULL,
                            mat_amount NUMERIC(15, 6) NOT NULL,
                            oxyfactor NUMERIC(5, 4) DEFAULT 1.0000,
                            matdir_em NUMERIC(15, 6) DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            CONSTRAINT fk_matdir_process FOREIGN KEY (process_id) REFERENCES process(id) ON DELETE CASCADE,
                            CONSTRAINT unique_matdir_process_material UNIQUE(process_id, mat_name)
                        );
                    """)
                    
                    # 인덱스 생성
                    await conn.execute("""
                        CREATE INDEX idx_matdir_process_id ON matdir(process_id);
                        CREATE INDEX idx_matdir_mat_name ON matdir(mat_name);
                        CREATE INDEX idx_matdir_process_material ON matdir(process_id, mat_name);
                        CREATE INDEX idx_matdir_created_at ON matdir(created_at);
                    """)
                    
                    logger.info("✅ matdir 테이블 생성 완료")
                else:
                    logger.info("✅ matdir 테이블이 이미 존재합니다.")
                    
        except Exception as e:
            logger.error(f"❌ matdir 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")

    # ============================================================================
    # 📋 기존 MatDir CRUD 메서드들
    # ============================================================================

    async def create_matdir(self, matdir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """원료직접배출량 데이터 생성 (중복 방지)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                # 중복 데이터 확인
                existing_record = await conn.fetchrow("""
                    SELECT id FROM matdir 
                    WHERE process_id = $1 AND mat_name = $2
                """, matdir_data['process_id'], matdir_data['mat_name'])
                
                if existing_record:
                    # 중복 데이터가 있으면 업데이트
                    logger.info(f"🔄 중복 데이터 발견, 업데이트: process_id={matdir_data['process_id']}, mat_name={matdir_data['mat_name']}")
                    result = await conn.fetchrow("""
                        UPDATE matdir 
                        SET mat_factor = $1, mat_amount = $2, oxyfactor = $3, matdir_em = $4, updated_at = NOW()
                        WHERE process_id = $5 AND mat_name = $6
                        RETURNING *
                    """, (
                        matdir_data['mat_factor'],
                        matdir_data['mat_amount'],
                        matdir_data.get('oxyfactor', 1.0000),
                        matdir_data.get('matdir_em', 0),
                        matdir_data['process_id'],
                        matdir_data['mat_name']
                    ))
                else:
                    # 새로운 데이터 삽입
                    result = await conn.fetchrow("""
                        INSERT INTO matdir (process_id, mat_name, mat_factor, mat_amount, oxyfactor, matdir_em)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING *
                    """, (
                        matdir_data['process_id'],
                        matdir_data['mat_name'],
                        matdir_data['mat_factor'],
                        matdir_data['mat_amount'],
                        matdir_data.get('oxyfactor', 1.0000),
                        matdir_data.get('matdir_em', 0)
                    ))
                
                action = "업데이트" if existing_record else "생성"
                logger.info(f"✅ MatDir {action} 성공: ID {result['id']}")
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ MatDir 생성/업데이트 실패: {str(e)}")
            raise

    async def get_matdirs(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 원료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_matdirs_db(skip, limit)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 목록 조회 실패: {str(e)}")
            raise

    async def get_matdirs_by_process(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 원료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_matdirs_by_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 공정별 원료직접배출량 데이터 조회 실패: {str(e)}")
            raise

    async def get_matdir(self, matdir_id: int) -> Optional[Dict[str, Any]]:
        """특정 원료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_matdir_db(matdir_id)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 조회 실패: {str(e)}")
            raise

    async def update_matdir(self, matdir_id: int, matdir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """원료직접배출량 데이터 수정"""
        await self._ensure_pool_initialized()
        try:
            return await self._update_matdir_db(matdir_id, matdir_data)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 수정 실패: {str(e)}")
            raise

    async def delete_matdir(self, matdir_id: int) -> bool:
        """원료직접배출량 데이터 삭제"""
        await self._ensure_pool_initialized()
        try:
            return await self._delete_matdir_db(matdir_id)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 삭제 실패: {str(e)}")
            raise

    def calculate_matdir_emission(self, mat_amount: Decimal, mat_factor: Decimal, oxyfactor: Decimal = Decimal('1.0000')) -> Decimal:
        """원료직접배출량 계산: matdir_em = mat_amount * mat_factor * oxyfactor"""
        return mat_amount * mat_factor * oxyfactor

    async def get_total_matdir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 원료직접배출량 계산"""
        matdirs = await self.get_matdirs_by_process(process_id)
        total_emission = sum(Decimal(str(matdir['matdir_em'])) for matdir in matdirs if matdir['matdir_em'])
        return total_emission

    # ============================================================================
    # 🏗️ Material Master 조회 메서드들 (새로 추가)
    # ============================================================================

    async def get_material_by_name(self, mat_name: str) -> Optional[Dict[str, Any]]:
        """원료명으로 마스터 데이터 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT id, mat_name, mat_engname, carbon_content, mat_factor
                    FROM material_master
                    WHERE mat_name = $1
                """, mat_name)
                
                if result:
                    logger.info(f"✅ 원료 마스터 조회 성공: {mat_name}")
                    return dict(result)
                else:
                    logger.warning(f"⚠️ 원료 마스터 데이터를 찾을 수 없음: {mat_name}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ 원료 마스터 조회 실패: {str(e)}")
            return None

    async def search_materials(self, search_term: str) -> List[Dict[str, Any]]:
        """원료명으로 검색 (부분 검색)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, mat_name, mat_engname, carbon_content, mat_factor
                    FROM material_master
                    WHERE mat_name ILIKE $1 OR mat_engname ILIKE $1
                    ORDER BY mat_name
                """, f'%{search_term}%')
                
                logger.info(f"✅ 원료 마스터 검색 성공: '{search_term}' → {len(results)}개 결과")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 원료 마스터 검색 실패: {str(e)}")
            return []

    async def get_all_materials(self) -> List[Dict[str, Any]]:
        """모든 원료 마스터 데이터 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, mat_name, mat_engname, carbon_content, mat_factor
                    FROM material_master
                    ORDER BY mat_name
                """)
                
                logger.info(f"✅ 모든 원료 마스터 조회 성공: {len(results)}개")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 모든 원료 마스터 조회 실패: {str(e)}")
            return []

    async def get_material_factor_by_name(self, mat_name: str) -> Optional[Dict[str, Any]]:
        """원료명으로 배출계수만 조회 (간단한 응답)"""
        try:
            material = await self.get_material_by_name(mat_name)
            if material:
                return {
                    'mat_name': material['mat_name'],
                    'mat_factor': float(material['mat_factor']),
                    'carbon_content': float(material['carbon_content']) if material['carbon_content'] else None,
                    'found': True
                }
            else:
                return {
                    'mat_name': mat_name,
                    'mat_factor': None,
                    'carbon_content': None,
                    'found': False
                }
                
        except Exception as e:
            logger.error(f"❌ 배출계수 조회 실패: {str(e)}")
            return {
                'mat_name': mat_name,
                'mat_factor': None,
                'carbon_content': None,
                'found': False
            }

    # ============================================================================
    # 📋 기존 DB 작업 메서드들
    # ============================================================================

    async def _get_matdirs_db(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 원료직접배출량 데이터 조회 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM matdir 
                    ORDER BY created_at DESC 
                    OFFSET $1 LIMIT $2
                """, skip, limit)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ MatDir 목록 조회 실패: {str(e)}")
            raise

    async def _get_matdirs_by_process_db(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 원료직접배출량 데이터 조회 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM matdir 
                    WHERE process_id = $1 
                    ORDER BY created_at DESC
                """, process_id)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 공정별 MatDir 조회 실패: {str(e)}")
            raise

    async def _get_matdir_db(self, matdir_id: int) -> Optional[Dict[str, Any]]:
        """특정 원료직접배출량 데이터 조회 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM matdir WHERE id = $1
                """, matdir_id)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ MatDir 조회 실패: {str(e)}")
            raise

    async def _update_matdir_db(self, matdir_id: int, matdir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """원료직접배출량 데이터 수정 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 업데이트할 필드들만 동적으로 생성
                set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(matdir_data.keys())])
                values = list(matdir_data.values()) + [matdir_id]
                
                query = f"""
                    UPDATE matdir 
                    SET {set_clause}, updated_at = NOW()
                    WHERE id = ${len(matdir_data) + 1} 
                    RETURNING *
                """
                
                result = await conn.fetchrow(query, *values)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ MatDir 수정 실패: {str(e)}")
            raise

    async def _delete_matdir_db(self, matdir_id: int) -> bool:
        """원료직접배출량 데이터 삭제 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM matdir WHERE id = $1
                """, matdir_id)
                
                return result != "DELETE 0"
                
        except Exception as e:
            logger.error(f"❌ MatDir 삭제 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔍 원료-배출계수 매핑 관련 메서드들 (@mapping/ 패턴과 동일)
    # ============================================================================

    async def create_material_mapping(self, mapping_data) -> Optional[Dict[str, Any]]:
        """원료-배출계수 매핑 생성"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO material_master (mat_name, mat_factor, carbon_content, mat_engname, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, NOW(), NOW())
                    RETURNING *
                """, (
                    mapping_data.mat_name,
                    mapping_data.mat_factor,
                    mapping_data.carbon_content,
                    mapping_data.mat_engname
                ))
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 원료-배출계수 매핑 생성 실패: {str(e)}")
            raise

    async def get_all_material_mappings(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 원료-배출계수 매핑 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM material_master 
                    ORDER BY created_at DESC 
                    LIMIT $1 OFFSET $2
                """, limit, skip)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 모든 원료-배출계수 매핑 조회 실패: {str(e)}")
            raise

    async def get_material_mapping(self, mapping_id: int) -> Optional[Dict[str, Any]]:
        """특정 원료-배출계수 매핑 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM material_master WHERE id = $1
                """, mapping_id)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 원료-배출계수 매핑 조회 실패: {str(e)}")
            raise

    async def update_material_mapping(self, mapping_id: int, mapping_data) -> Optional[Dict[str, Any]]:
        """원료-배출계수 매핑 수정"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                # 업데이트할 필드들만 동적으로 생성
                update_fields = []
                values = []
                
                if mapping_data.mat_name is not None:
                    update_fields.append("mat_name = $1")
                    values.append(mapping_data.mat_name)
                
                if mapping_data.mat_factor is not None:
                    update_fields.append("mat_factor = $2")
                    values.append(mapping_data.mat_factor)
                
                if mapping_data.carbon_content is not None:
                    update_fields.append("carbon_content = $3")
                    values.append(mapping_data.carbon_content)
                
                if mapping_data.mat_engname is not None:
                    update_fields.append("mat_engname = $4")
                    values.append(mapping_data.mat_engname)
                
                if not update_fields:
                    return await self.get_material_mapping(mapping_id)
                
                set_clause = ", ".join(update_fields)
                values.append(mapping_id)
                
                query = f"""
                    UPDATE material_master 
                    SET {set_clause}, updated_at = NOW()
                    WHERE id = ${len(values)} 
                    RETURNING *
                """
                
                result = await conn.fetchrow(query, *values)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 원료-배출계수 매핑 수정 실패: {str(e)}")
            raise

    async def delete_material_mapping(self, mapping_id: int) -> bool:
        """원료-배출계수 매핑 삭제"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM material_master WHERE id = $1
                """, mapping_id)
                
                return result != "DELETE 0"
                
        except Exception as e:
            logger.error(f"❌ 원료-배출계수 매핑 삭제 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔍 원료명 조회 관련 메서드들 (@mapping/ 패턴과 동일)
    # ============================================================================

    async def lookup_material_by_name(self, mat_name: str) -> List[Dict[str, Any]]:
        """원료명으로 배출계수 조회 (자동 매핑 기능)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM material_master 
                    WHERE mat_name ILIKE $1 
                    ORDER BY mat_name
                """, f"%{mat_name}%")
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 원료명 조회 실패: {str(e)}")
            raise
