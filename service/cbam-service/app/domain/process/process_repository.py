# 🔄 Process Repository - 공정 데이터 접근
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
from app.domain.process.process_schema import ProcessCreateRequest, ProcessUpdateRequest

logger = logging.getLogger(__name__)

class ProcessRepository:
    """공정 데이터 접근 클래스"""
    
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
                min_size=1, max_size=10, command_timeout=30,
                server_settings={'application_name': 'cbam-service-process'}
            )
            logger.info("✅ Process 데이터베이스 연결 풀 생성 성공")
            
            try:
                await self._create_process_table_async()
            except Exception as e:
                logger.warning(f"⚠️ Process 테이블 생성 실패 (기본 기능은 정상): {e}")
                
        except Exception as e:
            logger.error(f"❌ Process 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
    async def _create_process_table_async(self):
        """Process 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # process 테이블 존재 확인
                result = await conn.fetchval("""
                    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'process');
                """)
                
                if not result:
                    logger.info("⚠️ process 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    await conn.execute("""
                        CREATE TABLE process (
                            id SERIAL PRIMARY KEY,
                            process_name TEXT NOT NULL,
                            start_period DATE,  -- 🔴 수정: NULL 허용
                            end_period DATE,    -- 🔴 수정: NULL 허용
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    logger.info("✅ process 테이블 생성 완료")
                else:
                    logger.info("✅ process 테이블 확인 완료")
                    # 🔴 추가: 기존 테이블의 start_period, end_period를 NULL 허용으로 변경
                    try:
                        await conn.execute("""
                            ALTER TABLE process 
                            ALTER COLUMN start_period DROP NOT NULL,
                            ALTER COLUMN end_period DROP NOT NULL
                        """)
                        logger.info("✅ process 테이블 스키마 업데이트 완료 (start_period, end_period를 NULL 허용)")
                    except Exception as e:
                        logger.info(f"ℹ️ process 테이블 스키마는 이미 최신 상태입니다: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Process 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")
    
    # ============================================================================
    # 🔄 Process 관련 Repository 메서드
    # ============================================================================
    
    async def create_process(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """공정 생성"""
        await self._ensure_pool_initialized()
        try:
            return await self._create_process_db(process_data)
        except Exception as e:
            logger.error(f"❌ 공정 생성 실패: {str(e)}")
            raise
    
    async def get_processes(self) -> List[Dict[str, Any]]:
        """공정 목록 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_processes_db()
        except Exception as e:
            logger.error(f"❌ 공정 목록 조회 실패: {str(e)}")
            raise
    
    async def get_process(self, process_id: int) -> Optional[Dict[str, Any]]:
        """특정 공정 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 공정 조회 실패: {str(e)}")
            raise
    
    async def update_process(self, process_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """공정 수정"""
        await self._ensure_pool_initialized()
        try:
            return await self._update_process_db(process_id, update_data)
        except Exception as e:
            logger.error(f"❌ 공정 수정 실패: {str(e)}")
            raise
    
    async def delete_process(self, process_id: int) -> bool:
        """공정 삭제"""
        await self._ensure_pool_initialized()
        
        try:
            return await self._delete_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 공정 삭제 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🔄 Process 관련 Private Database 메서드
    # ============================================================================
    
    async def _create_process_db(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 공정 생성 (다대다 관계)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 1. 공정 생성 (start_period, end_period는 선택적)
                params = (
                    process_data['process_name'], 
                    process_data.get('start_period'), 
                    process_data.get('end_period')
                )
                result = await conn.fetchrow("""
                    INSERT INTO process (
                        process_name, start_period, end_period
                    ) VALUES (
                        $1, $2, $3
                    ) RETURNING *
                """, *params)
                
                if not result:
                    raise Exception("공정 생성에 실패했습니다.")
                
                process_dict = dict(result)
                process_id = process_dict['id']
                
                # 2. 제품-공정 관계 생성 (다대다 관계)
                if 'product_ids' in process_data and process_data['product_ids']:
                    for product_id in process_data['product_ids']:
                        await conn.execute("""
                            INSERT INTO product_process (product_id, process_id)
                            VALUES ($1, $2)
                            ON CONFLICT (product_id, process_id) DO NOTHING
                        """, product_id, process_id)
                
                # 3. 생성된 공정 정보 반환 (제품 정보 포함)
                return await self._get_process_with_products_db(process_id)
                
        except Exception as e:
            logger.error(f"❌ 공정 생성 실패: {str(e)}")
            raise
    
    async def _get_processes_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 프로세스 목록 조회 (다대다 관계)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 모든 공정 조회
                results = await conn.fetch("""
                    SELECT id, process_name, start_period, end_period, created_at, updated_at
                    FROM process
                    ORDER BY id
                """)
                
                processes = []
                for row in results:
                    process_dict = dict(row)
                    
                    # 해당 공정과 연결된 제품들 조회
                    product_results = await conn.fetch("""
                        SELECT p.id, p.install_id, p.product_name, p.product_category, 
                               p.prostart_period, p.proend_period, p.product_amount,
                               p.cncode_total, p.goods_name, p.aggrgoods_name,
                               p.product_sell, p.product_eusell, p.created_at, p.updated_at
                        FROM product p
                        JOIN product_process pp ON p.id = pp.product_id
                        WHERE pp.process_id = $1
                    """, process_dict['id'])
                    
                    products = [dict(product) for product in product_results]
                    process_dict['products'] = products
                    
                    # datetime.date 객체는 그대로 유지 (스키마에서 date 타입으로 정의됨)
                    
                    processes.append(process_dict)
                
                return processes
                
        except Exception as e:
            logger.error(f"❌ 공정 목록 조회 실패: {str(e)}")
            raise
    
    async def _get_process_db(self, process_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 프로세스 조회"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM process WHERE id = $1
                """, process_id)
                
                if result:
                    process_dict = dict(result)
                    # datetime.date 객체는 그대로 유지 (스키마에서 date 타입으로 정의됨)
                    return process_dict
                return None
                
        except Exception as e:
            logger.error(f"❌ 공정 조회 실패: {str(e)}")
            raise
    
    async def _update_process_db(self, process_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 프로세스 수정"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 동적으로 SET 절 생성
                set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(update_data.keys())])
                values = list(update_data.values()) + [process_id]
                
                query = f"""
                    UPDATE process SET {set_clause} 
                    WHERE id = ${len(update_data) + 1} RETURNING *
                """
                
                result = await conn.fetchrow(query, *values)
                
                if result:
                    process_dict = dict(result)
                    # datetime.date 객체는 그대로 유지 (스키마에서 date 타입으로 정의됨)
                    return process_dict
                return None
                
        except Exception as e:
            logger.error(f"❌ 공정 수정 실패: {str(e)}")
            raise
    
    async def _delete_process_db(self, process_id: int) -> bool:
        """데이터베이스에서 프로세스 삭제"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 먼저 해당 공정이 존재하는지 확인
                result = await conn.fetchrow("""
                    SELECT id, process_name FROM process WHERE id = $1
                """, process_id)
                
                if not result:
                    logger.warning(f"⚠️ 공정 ID {process_id}를 찾을 수 없습니다.")
                    return False
                
                logger.info(f"🗑️ 공정 삭제 시작: ID {process_id}, 이름: {result['process_name']}")
                
                # 먼저 해당 공정과 연결된 제품-공정 관계들을 삭제
                await conn.execute("""
                    DELETE FROM product_process WHERE process_id = $1
                """, process_id)
                
                logger.info(f"🗑️ 연결된 제품-공정 관계 삭제 완료")
                
                # 그 다음 공정 삭제
                deleted_processes = await conn.execute("""
                    DELETE FROM process WHERE id = $1
                """, process_id)
                
                logger.info(f"🗑️ 공정 삭제 완료")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ 공정 삭제 실패: {str(e)}")
            raise
    
    async def _get_process_with_products_db(self, process_id: int) -> Optional[Dict[str, Any]]:
        """제품 정보를 포함한 공정 조회"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 공정 정보 조회
                process_result = await conn.fetchrow("""
                    SELECT * FROM process WHERE id = $1
                """, process_id)
                
                if not process_result:
                    return None
                
                process_dict = dict(process_result)
                
                # 연결된 제품들 조회
                product_results = await conn.fetch("""
                    SELECT p.id, p.install_id, p.product_name, p.product_category, 
                           p.prostart_period, p.proend_period, p.product_amount,
                           p.cncode_total, p.goods_name, p.aggrgoods_name,
                           p.product_sell, p.product_eusell, p.created_at, p.updated_at
                    FROM product p
                    JOIN product_process pp ON p.id = pp.product_id
                    WHERE pp.process_id = $1
                """, process_id)
                
                products = [dict(product) for product in product_results]
                process_dict['products'] = products
                
                # datetime.date 객체는 그대로 유지 (스키마에서 date 타입으로 정의됨)
                
                return process_dict
                
        except Exception as e:
            logger.error(f"❌ 공정 조회 실패: {str(e)}")
            raise
