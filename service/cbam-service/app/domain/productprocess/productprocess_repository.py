# ============================================================================
# 🔗 ProductProcess Repository - 제품-공정 관계 데이터 접근
# ============================================================================

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
import os

logger = logging.getLogger(__name__)

class ProductProcessRepository:
    """제품-공정 관계 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
            return
        
        # asyncpg 연결 풀 초기화
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
            # asyncpg 연결 풀 생성
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'application_name': 'cbam-service'
                }
            )
            
            logger.info("✅ ProductProcess 데이터베이스 연결 풀 생성 성공")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")

    # ============================================================================
    # 🔗 ProductProcess 관련 Repository 메서드
    # ============================================================================

    async def create_product_process(self, product_process_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 제품-공정 관계 생성"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO product_process (product_id, process_id)
                    VALUES ($1, $2)
                    ON CONFLICT (product_id, process_id) DO NOTHING
                    RETURNING *
                """, (product_process_data['product_id'], product_process_data['process_id']))
                
                if result:
                    logger.info(f"✅ 제품-공정 관계 생성 성공: 제품 ID {product_process_data['product_id']}, 공정 ID {product_process_data['process_id']}")
                    return dict(result)
                else:
                    raise Exception("제품-공정 관계 생성에 실패했습니다.")
                    
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 생성 실패: {str(e)}")
            raise e

    async def delete_product_process(self, product_id: int, process_id: int) -> bool:
        """데이터베이스에서 제품-공정 관계 삭제"""
        await self._ensure_pool_initialized()
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM product_process WHERE product_id = $1 AND process_id = $2
                """, (product_id, process_id))
                
                success = result != "DELETE 0"
                if success:
                    logger.info(f"✅ 제품-공정 관계 삭제 성공: 제품 ID {product_id}, 공정 ID {process_id}")
                else:
                    logger.warning(f"⚠️ 제품-공정 관계를 찾을 수 없음: 제품 ID {product_id}, 공정 ID {process_id}")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 삭제 실패: {str(e)}")
            raise e

    async def get_product_process_by_id(self, relation_id: int) -> Optional[Dict[str, Any]]:
        """ID로 제품-공정 관계 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT pp.*, p.product_name, proc.process_name
                    FROM product_process pp
                    LEFT JOIN product p ON pp.product_id = p.id
                    LEFT JOIN process proc ON pp.process_id = proc.id
                    WHERE pp.id = $1
                """, relation_id)
                
                if result:
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 조회 실패: {str(e)}")
            raise

    async def get_all_product_processes(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 제품-공정 관계 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT pp.*, p.product_name, proc.process_name
                    FROM product_process pp
                    LEFT JOIN product p ON pp.product_id = p.id
                    LEFT JOIN process proc ON pp.process_id = proc.id
                    ORDER BY pp.product_id, pp.process_id
                    LIMIT $1 OFFSET $2
                """, limit, skip)
                
                return [dict(result) for result in results]
                
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 목록 조회 실패: {str(e)}")
            raise

    async def get_product_processes_by_product(self, product_id: int) -> List[Dict[str, Any]]:
        """제품별 제품-공정 관계 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT pp.*, p.product_name, proc.process_name
                    FROM product_process pp
                    LEFT JOIN product p ON pp.product_id = p.id
                    LEFT JOIN process proc ON pp.process_id = proc.id
                    WHERE pp.product_id = $1
                    ORDER BY pp.process_id
                """, product_id)
                
                return [dict(result) for result in results]
                
        except Exception as e:
            logger.error(f"❌ 제품별 제품-공정 관계 조회 실패: {str(e)}")
            raise

    async def get_product_processes_by_process(self, process_id: int) -> List[Dict[str, Any]]:
        """공정별 제품-공정 관계 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT pp.*, p.product_name, proc.process_name
                    FROM product_process pp
                    LEFT JOIN product p ON pp.product_id = p.id
                    LEFT JOIN process proc ON pp.process_id = proc.id
                    WHERE pp.process_id = $1
                    ORDER BY pp.product_id
                """, process_id)
                
                return [dict(result) for result in results]
                
        except Exception as e:
            logger.error(f"❌ 공정별 제품-공정 관계 조회 실패: {str(e)}")
            raise

    async def search_product_processes(self, **filters) -> List[Dict[str, Any]]:
        """제품-공정 관계 검색"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                where_conditions = []
                values = []
                param_count = 0
                
                if filters.get('product_id'):
                    param_count += 1
                    where_conditions.append(f"pp.product_id = ${param_count}")
                    values.append(filters['product_id'])
                
                if filters.get('process_id'):
                    param_count += 1
                    where_conditions.append(f"pp.process_id = ${param_count}")
                    values.append(filters['process_id'])
                
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                
                query = f"""
                    SELECT pp.*, p.product_name, proc.process_name
                    FROM product_process pp
                    LEFT JOIN product p ON pp.product_id = p.id
                    LEFT JOIN process proc ON pp.process_id = proc.id
                    WHERE {where_clause}
                    ORDER BY pp.product_id, pp.process_id
                    LIMIT ${param_count + 1} OFFSET ${param_count + 2}
                """
                
                values.extend([filters.get('limit', 100), filters.get('skip', 0)])
                
                results = await conn.fetch(query, *values)
                return [dict(result) for result in results]
                
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 검색 실패: {str(e)}")
            raise

    async def get_product_process_stats(self) -> Dict[str, Any]:
        """제품-공정 관계 통계 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_relations,
                        COUNT(DISTINCT product_id) as total_products,
                        COUNT(DISTINCT process_id) as total_processes
                    FROM product_process
                """)
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 통계 조회 실패: {str(e)}")
            raise

    async def create_product_processes_batch(self, relations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """제품-공정 관계 일괄 생성"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                created_count = 0
                failed_count = 0
                errors = []
                
                for relation in relations:
                    try:
                        await conn.execute("""
                            INSERT INTO product_process (product_id, process_id)
                            VALUES ($1, $2)
                            ON CONFLICT (product_id, process_id) DO NOTHING
                        """, relation['product_id'], relation['process_id'])
                        
                        created_count += 1
                        
                    except Exception as e:
                        failed_count += 1
                        errors.append(f"Relation {relation}: {str(e)}")
                
                logger.info(f"✅ 제품-공정 관계 일괄 생성 완료: {created_count}개 성공, {failed_count}개 실패")
                
                return {
                    "created_count": created_count,
                    "failed_count": failed_count,
                    "errors": errors
                }
                
        except Exception as e:
            logger.error(f"❌ 제품-공정 관계 일괄 생성 실패: {str(e)}")
            raise
