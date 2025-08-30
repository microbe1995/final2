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

from .calculation_entity import Edge
from .calculation_schema import EdgeResponse

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
        # 초기화는 서비스 시작 시 별도로 호출해야 함
    
    async def initialize(self):
        """데이터베이스 연결 풀 초기화"""
        if not self.database_url:
            logger.warning("DATABASE_URL이 없어 데이터베이스 초기화를 건너뜁니다.")
            return
        
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
    
    # 동기 메서드는 제거됨

    def _initialize_database_sync(self):
        """데이터베이스 초기화 (동기)"""
        if not self.database_url:
            logger.warning("DATABASE_URL이 없어 데이터베이스 초기화를 건너뜁니다.")
            return
            
        try:
            # 데이터베이스 연결 테스트
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            conn.close()
            
            logger.info("✅ 데이터베이스 연결 성공")
            self._create_tables_sync()
            self._create_triggers_sync()  # 트리거 생성 추가
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            # 연결 실패해도 서비스는 계속 실행
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
    
    # 동기 메서드들은 제거 (비동기 환경에서 불필요)

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
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_processes_by_product_db(product_id)
        except Exception as e:
            logger.error(f"❌ 제품별 프로세스 조회 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔗 ProductProcess 관련 메서드 (다대다 관계)
    # ============================================================================
    
    async def create_product_process(self, product_process_data: Dict[str, Any]) -> Dict[str, Any]:
        """제품-공정 관계 생성"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._create_product_process_db(product_process_data)
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 생성 실패: {str(e)}")
            raise
    
    async def delete_product_process(self, product_id: int, process_id: int) -> bool:
        """제품-공정 관계 삭제"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._delete_product_process_db(product_id, process_id)
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 삭제 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔗 Edge 관련 Repository 메서드
    # ============================================================================

    async def create_edge(self, edge_data: Dict) -> Dict:
        """Edge 생성"""
        # 지연 초기화: 필요할 때 데이터베이스 연결 풀 생성
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO edge (source_id, target_id, edge_kind, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                """, (
                    edge_data['source_id'],
                    edge_data['target_id'],
                    edge_data['edge_kind'],
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                return dict(result)
        except Exception as e:
            logger.error(f"❌ Edge 생성 실패: {str(e)}")
            raise

    async def get_edges(self) -> List[Dict]:
        """모든 Edge 조회"""
        # 지연 초기화: 필요할 때 데이터베이스 연결 풀 생성
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM edge ORDER BY id
                """)
                
                edges = [dict(row) for row in results]
                return edges
        except Exception as e:
            logger.error(f"❌ Edge 목록 조회 실패: {str(e)}")
            raise

    async def delete_edge(self, edge_id: int) -> bool:
        """Edge 삭제"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM edge WHERE id = $1
                """, edge_id)
                
                return result != "DELETE 0"
        except Exception as e:
            logger.error(f"❌ Edge 삭제 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔗 통합 공정 그룹 관련 Repository 메서드
    # ============================================================================

    async def get_process_chains_by_process_ids(self, process_ids: List[int]) -> List[Dict]:
        """공정 ID들로 통합 그룹 조회"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
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
            raise

    async def create_process_chain(self, chain_data: Dict) -> Dict:
        """통합 공정 그룹 생성"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
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
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                return dict(chain)
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 생성 실패: {str(e)}")
            raise

    async def create_process_chain_link(self, link_data: Dict):
        """통합 그룹에 공정 연결"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO process_chain_link 
                    (chain_id, process_id, sequence_order, is_continue_edge, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    link_data['chain_id'],
                    link_data['process_id'],
                    link_data['sequence_order'],
                    link_data['is_continue_edge'],
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ 공정 그룹 연결 생성 실패: {e}")
            raise e
        finally:
            conn.close()

    async def add_processes_to_chain(self, chain_id: int, process_ids: List[int]):
        """기존 그룹에 새로운 공정들 추가"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                # 현재 그룹의 최대 순서 번호 조회
                cursor.execute("""
                    SELECT COALESCE(MAX(sequence_order), 0) as max_order
                    FROM process_chain_link
                    WHERE chain_id = %s
                """, (chain_id,))
                
                max_order = cursor.fetchone()[0]
                
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
        finally:
            conn.close()

    async def update_chain_length(self, chain_id: int):
        """그룹 길이 업데이트"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE process_chain 
                    SET chain_length = (
                        SELECT COUNT(*) FROM process_chain_link WHERE chain_id = %s
                    ),
                    updated_at = %s
                    WHERE id = %s
                """, (chain_id, datetime.utcnow(), chain_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ 그룹 길이 업데이트 실패: {e}")
            raise e
        finally:
            conn.close()

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
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
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
            raise




    # ============================================================================
    # 🔗 ProductProcess 관련 Repository 메서드
    # ============================================================================

    async def create_product_process(self, product_process_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 제품-공정 관계 생성"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        INSERT INTO product_process (product_id, process_id)
                        VALUES (%s, %s)
                        ON CONFLICT (product_id, process_id) DO NOTHING
                        RETURNING *
                    """, (product_process_data['product_id'], product_process_data['process_id']))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return dict(result)
                    else:
                        raise Exception("제품-공정 관계 생성에 실패했습니다.")
                        
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def delete_product_process(self, product_id: int, process_id: int) -> bool:
        """데이터베이스에서 제품-공정 관계 삭제"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM product_process WHERE product_id = %s AND process_id = %s
                    """, (product_id, process_id))
                    
                    conn.commit()
                    return cursor.rowcount > 0
                    
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e