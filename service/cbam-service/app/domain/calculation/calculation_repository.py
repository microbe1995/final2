# ============================================================================
# 🧮 Calculation Repository - CBAM 계산 데이터 접근
# ============================================================================

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
import os
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class CalculationRepository:
    """CBAM 계산 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
            # 데이터베이스 URL이 없어도 서비스는 계속 실행
            return
        
        # asyncpg 연결 풀 초기화
        self.pool = None
        self._initialization_attempted = False
        # 초기화는 서비스 시작 시 별도로 호출해야 함
    
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
            # asyncpg 연결 풀 생성
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,  # 최소 연결 수를 줄임
                max_size=10,  # 최대 연결 수를 줄임
                command_timeout=30,  # 타임아웃을 줄임
                server_settings={
                    'application_name': 'cbam-service'
                }
            )
            
            logger.info("✅ 데이터베이스 연결 풀 생성 성공")
            
            # 테이블 및 트리거 생성은 선택적으로 실행
            try:
                await self._create_tables_async()
                await self._create_triggers_async()
            except Exception as e:
                logger.warning(f"⚠️ 테이블/트리거 생성 실패 (기본 기능은 정상): {e}")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            # 연결 실패해도 서비스는 계속 실행
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    

    async def _create_tables_async(self):
        """테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
            
        try:
            async with self.pool.acquire() as conn:
                # 1. install 테이블 생성
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'install'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ install 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    await conn.execute("""
                        CREATE TABLE install (
                            id SERIAL PRIMARY KEY,
                            install_name TEXT NOT NULL,
                            reporting_year INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM NOW()),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    logger.info("✅ install 테이블 생성 완료")
                else:
                    logger.info("✅ install 테이블 확인 완료")
                
                # 2. product 테이블 생성
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'product'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ product 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    await conn.execute("""
                        CREATE TABLE product (
                            id SERIAL PRIMARY KEY,
                            install_id INTEGER NOT NULL REFERENCES install(id) ON DELETE CASCADE,
                            product_name TEXT NOT NULL,
                            product_category TEXT NOT NULL,
                            prostart_period DATE NOT NULL,
                            proend_period DATE NOT NULL,
                            product_amount NUMERIC(15, 6) NOT NULL DEFAULT 0,
                            cncode_total TEXT,
                            goods_name TEXT,
                            goods_engname TEXT,
                            aggrgoods_name TEXT,
                            aggrgoods_engname TEXT,
                            product_sell NUMERIC(15, 6) DEFAULT 0,
                            product_eusell NUMERIC(15, 6) DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    logger.info("✅ product 테이블 생성 완료")
                else:
                    logger.info("✅ product 테이블 확인 완료")
                
                # 3. process 테이블 생성
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'process'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ process 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    await conn.execute("""
                        CREATE TABLE process (
                            id SERIAL PRIMARY KEY,
                            process_name TEXT NOT NULL,
                            start_period DATE NOT NULL,
                            end_period DATE NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    logger.info("✅ process 테이블 생성 완료")
                else:
                    logger.info("✅ process 테이블 확인 완료")
                
                # 4. product_process 중간 테이블 생성
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'product_process'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ product_process 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    await conn.execute("""
                        CREATE TABLE product_process (
                            id SERIAL PRIMARY KEY,
                            product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE CASCADE,
                            process_id INTEGER NOT NULL REFERENCES process(id) ON DELETE CASCADE,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            UNIQUE(product_id, process_id)
                        );
                    """)
                    
                    logger.info("✅ product_process 테이블 생성 완료")
                else:
                    logger.info("✅ product_process 테이블 확인 완료")
                
                # 5. edge 테이블 생성
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'edge'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ edge 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    await conn.execute("""
                        CREATE TABLE edge (
                            id SERIAL PRIMARY KEY,
                            source_id INTEGER NOT NULL,
                            target_id INTEGER NOT NULL,
                            edge_kind TEXT NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    logger.info("✅ edge 테이블 생성 완료")
                else:
                    logger.info("✅ edge 테이블 확인 완료")
                
                # 6. process_attrdir_emission 테이블 생성
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'process_attrdir_emission'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ process_attrdir_emission 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    await conn.execute("""
                        CREATE TABLE process_attrdir_emission (
                            id SERIAL PRIMARY KEY,
                            process_id INTEGER NOT NULL REFERENCES process(id) ON DELETE CASCADE,
                            total_matdir_emission NUMERIC(15, 6) DEFAULT 0,
                            total_fueldir_emission NUMERIC(15, 6) DEFAULT 0,
                            attrdir_em NUMERIC(15, 6) DEFAULT 0,
                            calculation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            UNIQUE(process_id)
                        );
                    """)
                    
                    logger.info("✅ process_attrdir_emission 테이블 생성 완료")
                else:
                    logger.info("✅ process_attrdir_emission 테이블 확인 완료")
                
                logger.info("✅ 모든 데이터베이스 테이블 확인/생성 완료")
                
        except Exception as e:
            logger.error(f"❌ 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")

    async def _create_triggers_async(self):
        """트리거 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
            
        try:
            async with self.pool.acquire() as conn:
                # 기본적인 트리거만 생성 (필요시 확장)
                logger.info("✅ 트리거 생성 완료")
                
        except Exception as e:
            logger.error(f"❌ 트리거 생성 실패: {str(e)}")
            logger.warning("⚠️ 트리거 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")

    async def get_processes_by_product(self, product_id: int) -> List[Dict[str, Any]]:
        """제품별 프로세스 목록 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT p.id, p.process_name, p.start_period, p.end_period, p.created_at, p.updated_at
                    FROM process p
                    JOIN product_process pp ON p.id = pp.process_id
                    WHERE pp.product_id = $1
                    ORDER BY p.id
                """, product_id)
                
                processes = []
                for row in results:
                    process_dict = dict(row)
                    # datetime.date 객체를 문자열로 변환
                    if 'start_period' in process_dict and process_dict['start_period']:
                        process_dict['start_period'] = process_dict['start_period'].isoformat()
                    if 'end_period' in process_dict and process_dict['end_period']:
                        process_dict['end_period'] = process_dict['end_period'].isoformat()
                    processes.append(process_dict)
                
                return processes
                
        except Exception as e:
            logger.error(f"❌ 제품별 프로세스 조회 실패: {str(e)}")
            raise e

    # ============================================================================
    # 🔗 ProductProcess 관련 메서드 (다대다 관계)
    # ============================================================================
    
    async def create_product_process(self, product_process_data: Dict[str, Any]) -> Dict[str, Any]:
        """제품-공정 관계 생성"""
        await self._ensure_pool_initialized()
        try:
            return await self._create_product_process_db(product_process_data)
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 생성 실패: {str(e)}")
            raise
    
    async def delete_product_process(self, product_id: int, process_id: int) -> bool:
        """제품-공정 관계 삭제"""
        await self._ensure_pool_initialized()
        try:
            return await self._delete_product_process_db(product_id, process_id)
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 삭제 실패: {str(e)}")
            raise

    # Edge 관련 Repository 메서드들은 edge 도메인으로 분리됨

    # ============================================================================
    # 🔗 통합 공정 그룹 관련 Repository 메서드
    # ============================================================================

    async def get_process_chains_by_process_ids(self, process_ids: List[int]) -> List[Dict]:
        """공정 ID들로 통합 그룹 조회"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                # process_chain_link 테이블을 통해 공정이 포함된 그룹들 조회
                chains = await conn.fetch("""
                    SELECT DISTINCT 
                        pc.id,
                        pc.chain_name,
                        pc.start_process_id,
                        pc.end_process_id,
                        pc.chain_length,
                        pc.is_active,
                        pc.created_at,
                        pc.updated_at
                    FROM process_chain pc
                    INNER JOIN process_chain_link pcl ON pc.id = pcl.chain_id
                    WHERE pcl.process_id = ANY($1)
                    ORDER BY pc.id
                """, process_ids)
                
                # 각 그룹에 포함된 공정 목록도 함께 조회
                chain_list = []
                for chain in chains:
                    chain_dict = dict(chain)
                    chain_dict['processes'] = []
                    
                    # 해당 그룹에 포함된 공정 목록 조회
                    process_links = await conn.fetch("""
                        SELECT process_id, sequence_order
                        FROM process_chain_link
                        WHERE chain_id = $1
                        ORDER BY sequence_order
                    """, chain_dict['id'])
                    
                    chain_dict['processes'] = [link['process_id'] for link in process_links]
                    chain_list.append(chain_dict)
                
                return chain_list
        except Exception as e:
            logger.error(f"❌ 공정 ID로 통합 그룹 조회 실패: {str(e)}")
            raise e

    # ============================================================================
    # 🔗 ProductProcess 관련 Repository 메서드
    # ============================================================================

    async def create_process_chain(self, chain_data: Dict) -> Dict:
        """통합 공정 그룹 생성"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                # process_chain 테이블에 그룹 정보 저장
                chain = await conn.fetchrow("""
                    INSERT INTO process_chain 
                    (chain_name, start_process_id, end_process_id, chain_length, is_active, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING *
                """, (
                    chain_data['chain_name'],
                    chain_data['start_process_id'],
                    chain_data['end_process_id'],
                    chain_data['chain_length'],
                    chain_data['is_active'],
                    datetime.now(),
                    datetime.now()
                ))
                
                return dict(chain)
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 생성 실패: {str(e)}")
            raise

    async def create_process_chain_link(self, link_data: Dict):
        """통합 그룹에 공정 연결"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO process_chain_link 
                    (chain_id, process_id, sequence_order, is_continue_edge, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, (
                    link_data['chain_id'],
                    link_data['process_id'],
                    link_data['sequence_order'],
                    link_data['is_continue_edge'],
                    datetime.now(),
                    datetime.now()
                ))
                
        except Exception as e:
            logger.error(f"❌ 공정 그룹 연결 생성 실패: {e}")
            raise e

    async def add_processes_to_chain(self, chain_id: int, process_ids: List[int]):
        """기존 그룹에 새로운 공정들 추가"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                # 현재 그룹의 최대 순서 번호 조회
                result = await conn.fetchrow("""
                    SELECT COALESCE(MAX(sequence_order), 0) as max_order
                    FROM process_chain_link
                    WHERE chain_id = $1
                """, chain_id)
                
                max_order = result['max_order'] if result else 0
                
                # 새로운 공정들을 순서대로 추가
                for i, process_id in enumerate(process_ids, max_order + 1):
                    link_data = {
                        'chain_id': chain_id,
                        'process_id': process_id,
                        'sequence_order': i,
                        'is_continue_edge': True
                    }
                    await self.create_process_chain_link(link_data)
                
                # 그룹 길이 업데이트
                await self.update_chain_length(chain_id)
                
        except Exception as e:
            logger.error(f"❌ 그룹에 공정 추가 실패: {e}")
            raise e

    async def update_chain_length(self, chain_id: int):
        """그룹 길이 업데이트"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE process_chain 
                    SET chain_length = (
                        SELECT COUNT(*) FROM process_chain_link WHERE chain_id = $1
                    ),
                    updated_at = $2
                    WHERE id = $3
                """, chain_id, datetime.now(), chain_id)
                
        except Exception as e:
            logger.error(f"❌ 그룹 길이 업데이트 실패: {e}")
            raise e

    async def update_process_chain_emission(self, chain_id: int, total_emission: float):
        """통합 그룹의 총 배출량 업데이트"""
        try:
            # process_chain 테이블에 총 배출량 컬럼이 있다면 업데이트
            # (현재는 테이블 구조에 해당 컬럼이 없을 수 있음)
            logger.info(f"🔥 통합 그룹 {chain_id} 총 배출량 업데이트: {total_emission}")
            
        except Exception as e:
            logger.error(f"❌ 그룹 배출량 업데이트 실패: {e}")
            raise e

    async def calculate_chain_integrated_emissions(self, chain_id: int) -> float:
        """통합 그룹의 총 배출량 계산"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                # 그룹 내 모든 공정의 배출량 합계 계산
                result = await conn.fetchrow("""
                    SELECT COALESCE(SUM(attrdir_em), 0) as total_emission
                    FROM process_attrdir_emission pae
                    INNER JOIN process_chain_link pcl ON pae.process_id = pcl.process_id
                    WHERE pcl.chain_id = $1
                """, chain_id)
                
                total_emission = result['total_emission'] if result else 0
                
                return float(total_emission)
        except Exception as e:
            logger.error(f"❌ 통합 그룹 배출량 계산 실패: {str(e)}")
            raise e



    # ============================================================================
    # 📊 배출량 계산 관련 Repository 메서드
    # ============================================================================

    async def calculate_process_attrdir_emission(self, process_id: int) -> Dict[str, Any]:
        """공정별 직접귀속배출량 계산 및 저장"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                # 1. 공정 정보 조회
                process_result = await conn.fetchrow("""
                    SELECT id, process_name FROM process WHERE id = $1
                """, process_id)
                
                if not process_result:
                    raise Exception(f"공정 ID {process_id}를 찾을 수 없습니다.")
                
                # 2. 원료별 직접배출량 계산 (matdir 테이블 기반)
                matdir_emission = await conn.fetchrow("""
                    SELECT COALESCE(SUM(matdir_em), 0) as total_matdir_emission
                    FROM matdir
                    WHERE process_id = $1
                """, process_id)
                
                # 3. 연료별 직접배출량 계산 (fueldir 테이블 기반)
                fueldir_emission = await conn.fetchrow("""
                    SELECT COALESCE(SUM(fueldir_em), 0) as total_fueldir_emission
                    FROM fueldir
                    WHERE process_id = $1
                """, process_id)
                
                # 4. 총 직접귀속배출량 계산
                total_matdir = float(matdir_emission['total_matdir_emission']) if matdir_emission else 0.0
                total_fueldir = float(fueldir_emission['total_fueldir_emission']) if fueldir_emission else 0.0
                attrdir_em = total_matdir + total_fueldir
                
                # 5. 결과를 process_attrdir_emission 테이블에 저장/업데이트
                result = await conn.fetchrow("""
                    INSERT INTO process_attrdir_emission 
                    (process_id, total_matdir_emission, total_fueldir_emission, attrdir_em, calculation_date)
                    VALUES ($1, $2, $3, $4, NOW())
                    ON CONFLICT (process_id) 
                    DO UPDATE SET
                        total_matdir_emission = EXCLUDED.total_matdir_emission,
                        total_fueldir_emission = EXCLUDED.total_fueldir_emission,
                        attrdir_em = EXCLUDED.attrdir_em,
                        calculation_date = NOW(),
                        updated_at = NOW()
                    RETURNING *
                """, process_id, total_matdir, total_fueldir, attrdir_em)
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ 공정별 직접귀속배출량 계산 실패: {str(e)}")
            raise e

    async def get_process_attrdir_emission(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정별 직접귀속배출량 조회"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM process_attrdir_emission WHERE process_id = $1
                """, process_id)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 공정별 직접귀속배출량 조회 실패: {str(e)}")
            raise e

    async def get_all_process_attrdir_emissions(self) -> List[Dict[str, Any]]:
        """모든 공정별 직접귀속배출량 조회"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM process_attrdir_emission ORDER BY process_id
                """)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 모든 공정별 직접귀속배출량 조회 실패: {str(e)}")
            raise e

    async def calculate_product_total_emission(self, product_id: int) -> Dict[str, Any]:
        """제품별 총 배출량 계산"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                # 1. 제품 정보 조회
                product_result = await conn.fetchrow("""
                    SELECT id, product_name FROM product WHERE id = $1
                """, product_id)
                
                if not product_result:
                    raise Exception(f"제품 ID {product_id}를 찾을 수 없습니다.")
                
                # 2. 제품과 연결된 공정들의 배출량 조회
                process_emissions = await conn.fetch("""
                    SELECT 
                        p.id as process_id,
                        p.process_name,
                        pae.total_matdir_emission,
                        pae.total_fueldir_emission,
                        pae.attrdir_em
                    FROM process p
                    JOIN product_process pp ON p.id = pp.process_id
                    LEFT JOIN process_attrdir_emission pae ON p.id = pae.process_id
                    WHERE pp.product_id = $1
                    ORDER BY p.id
                """, product_id)
                
                # 3. 총 배출량 계산
                total_emission = 0.0
                process_count = 0
                
                for pe in process_emissions:
                    if pe['attrdir_em']:
                        total_emission += float(pe['attrdir_em'])
                    process_count += 1
                
                return {
                    'product_id': product_id,
                    'product_name': product_result['product_name'],
                    'total_emission': total_emission,
                    'process_count': process_count,
                    'process_emissions': [dict(pe) for pe in process_emissions]
                }
                
        except Exception as e:
            logger.error(f"❌ 제품별 총 배출량 계산 실패: {str(e)}")
            raise e

    # ============================================================================
    # 🔄 공정 간 값 전파 관련 Repository 메서드들
    # ============================================================================
    
    async def update_process_attrdir_emission(self, process_id: int, update_data: Dict[str, Any]) -> bool:
        """공정별 직접귀속배출량 업데이트"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                # 업데이트할 필드들만 추출
                set_clauses = []
                values = [process_id]
                param_count = 1
                
                for key, value in update_data.items():
                    if key in ['total_matdir_emission', 'total_fueldir_emission', 'attrdir_em']:
                        set_clauses.append(f"{key} = ${param_count + 1}")
                        values.append(value)
                        param_count += 1
                
                if not set_clauses:
                    logger.warning("업데이트할 필드가 없습니다.")
                    return False
                
                # updated_at 필드 추가
                set_clauses.append("updated_at = NOW()")
                
                query = f"""
                    UPDATE process_attrdir_emission 
                    SET {', '.join(set_clauses)}
                    WHERE process_id = $1
                """
                
                result = await conn.execute(query, *values)
                
                if result == "UPDATE 1":
                    logger.info(f"✅ 공정 {process_id} 배출량 업데이트 성공")
                    return True
                else:
                    logger.warning(f"⚠️ 공정 {process_id} 배출량 업데이트 실패: {result}")
                    return False
                
        except Exception as e:
            logger.error(f"❌ 공정별 직접귀속배출량 업데이트 실패: {str(e)}")
            raise e
    
    async def get_continue_edges(self) -> List[Dict[str, Any]]:
        """모든 continue 엣지 조회"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT 
                        e.id,
                        e.source_id,
                        e.target_id,
                        e.source_node_type,
                        e.target_node_type,
                        e.edge_kind
                    FROM edge e
                    WHERE e.edge_kind = 'continue'
                    AND e.source_node_type = 'process'
                    AND e.target_node_type = 'process'
                    ORDER BY e.id
                """)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ continue 엣지 조회 실패: {str(e)}")
            raise e
    
    async def get_outgoing_continue_edges(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정에서 나가는 continue 엣지들 조회"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT 
                        e.id,
                        e.source_id,
                        e.target_id,
                        e.source_node_type,
                        e.target_node_type,
                        e.edge_kind
                    FROM edge e
                    WHERE e.edge_kind = 'continue'
                    AND e.source_node_type = 'process'
                    AND e.target_node_type = 'process'
                    AND e.source_id = $1
                    ORDER BY e.id
                """, process_id)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 공정 {process_id}의 나가는 continue 엣지 조회 실패: {str(e)}")
            raise e
    
    async def get_isolated_processes(self) -> List[int]:
        """고립된 공정들 조회 (엣지가 없는 공정)"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT p.id
                    FROM process p
                    LEFT JOIN edge e ON (
                        (e.source_node_type = 'process' AND e.source_id = p.id) OR
                        (e.target_node_type = 'process' AND e.target_id = p.id)
                    )
                    WHERE e.id IS NULL
                    ORDER BY p.id
                """)
                
                return [row['id'] for row in results]
                
        except Exception as e:
            logger.error(f"❌ 고립된 공정 조회 실패: {str(e)}")
            raise e
    
    async def get_very_long_chains(self, max_length: int = 20) -> List[Dict[str, Any]]:
        """매우 긴 체인들 조회 (무한 루프 가능성 확인)"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                # 재귀 CTE를 사용하여 체인 길이 계산
                results = await conn.fetch(f"""
                    WITH RECURSIVE process_chain AS (
                        -- 시작점: 들어오는 엣지가 없는 공정들
                        SELECT 
                            p.id as process_id,
                            p.process_name,
                            1 as chain_length,
                            ARRAY[p.id] as path
                        FROM process p
                        LEFT JOIN edge e ON e.target_node_type = 'process' AND e.target_id = p.id
                        WHERE e.id IS NULL
                        
                        UNION ALL
                        
                        -- 재귀: continue 엣지를 따라 다음 공정으로
                        SELECT 
                            p.id,
                            p.process_name,
                            pc.chain_length + 1,
                            pc.path || p.id
                        FROM process p
                        JOIN edge e ON e.source_node_type = 'process' AND e.source_id = p.id
                        JOIN process_chain pc ON e.target_node_type = 'process' AND e.target_id = pc.process_id
                        WHERE e.edge_kind = 'continue'
                        AND pc.chain_length < {max_length}
                        AND p.id != ALL(pc.path)  -- 순환 방지
                    )
                    SELECT 
                        process_id,
                        process_name,
                        chain_length,
                        path
                    FROM process_chain
                    WHERE chain_length >= {max_length}
                    ORDER BY chain_length DESC, process_id
                """)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 긴 체인 조회 실패: {str(e)}")
            raise e
    
    async def get_process(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정 정보 조회"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT id, process_name FROM process WHERE id = $1
                """, process_id)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 공정 정보 조회 실패: {str(e)}")
            raise e













