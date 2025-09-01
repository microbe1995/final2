# ============================================================================
# 📦 Edge Repository - 엣지 데이터 접근
# ============================================================================

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg

logger = logging.getLogger(__name__)

class EdgeRepository:
    """엣지 데이터 접근 클래스 (asyncpg 연결 풀)"""
    
    def __init__(self, db_session=None):
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
                    'application_name': 'cbam-service-edge'
                }
            )
            logger.info("✅ Edge 데이터베이스 연결 풀 생성 성공")
            
            # 테이블 생성은 선택적으로 실행
            try:
                await self._create_edge_table_async()
            except Exception as e:
                logger.warning(f"⚠️ 테이블 생성 실패 (기본 기능은 정상): {e}")
            
        except Exception as e:
            logger.error(f"❌ Edge 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            logger.info("🔄 Edge 연결 풀 초기화 시작")
            await self.initialize()
        
        if not self.pool:
            logger.error("❌ Edge 연결 풀이 초기화되지 않았습니다.")
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다. DATABASE_URL 환경변수를 확인해주세요.")
        
        logger.info("✅ Edge 연결 풀 정상 상태 확인")
    
    async def _create_edge_table_async(self):
        """edge 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # edge 테이블이 이미 존재하는지 확인
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'edge'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ edge 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    # edge 테이블 생성
                    await conn.execute("""
                        CREATE TABLE edge (
                            id SERIAL PRIMARY KEY,
                            source_node_type VARCHAR(50) NOT NULL,
                            source_id INTEGER NOT NULL,
                            target_node_type VARCHAR(50) NOT NULL,
                            target_id INTEGER NOT NULL,
                            edge_kind VARCHAR(50) NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    # 인덱스 생성
                    await conn.execute("""
                        CREATE INDEX idx_edge_kind ON edge (edge_kind);
                        CREATE INDEX idx_edge_source_id ON edge (source_id);
                        CREATE INDEX idx_edge_source_node_type ON edge (source_node_type);
                        CREATE INDEX idx_edge_target_id ON edge (target_id);
                        CREATE INDEX idx_edge_target_node_type ON edge (target_node_type);
                    """)
                    
                    logger.info("✅ edge 테이블 생성 완료")
                else:
                    logger.info("✅ edge 테이블이 이미 존재합니다.")
                    
        except Exception as e:
            logger.error(f"❌ edge 테이블 생성 실패: {str(e)}")
    
    # ============================================================================
    # 📋 기본 CRUD 작업
    # ============================================================================
    
    async def create_edge(self, edge_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 생성"""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                """
                
                row = await conn.fetchrow(
                    query,
                    edge_data['source_node_type'],
                    edge_data['source_id'],
                    edge_data['target_node_type'],
                    edge_data['target_id'],
                    edge_data['edge_kind']
                )
                
                if row:
                    logger.info(f"✅ 엣지 생성 성공: ID {row['id']}")
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"❌ 엣지 생성 실패: {str(e)}")
            return None
    
    async def get_edges(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 엣지 조회 (페이지네이션)"""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    FROM edge
                    ORDER BY id
                    LIMIT $1 OFFSET $2
                """
                
                rows = await conn.fetch(query, limit, skip)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ 엣지 목록 조회 실패: {str(e)}")
            return []
    
    async def get_edge(self, edge_id: int) -> Optional[Dict[str, Any]]:
        """특정 엣지 조회"""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    FROM edge
                    WHERE id = $1
                """
                
                row = await conn.fetchrow(query, edge_id)
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"❌ 엣지 {edge_id} 조회 실패: {str(e)}")
            return None
    
    async def update_edge(self, edge_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 수정"""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                # 업데이트할 필드들만 추출
                set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_data.keys())])
                set_clause += ", updated_at = NOW()"
                
                query = f"""
                    UPDATE edge
                    SET {set_clause}
                    WHERE id = $1
                    RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                """
                
                params = [edge_id] + list(update_data.values())
                row = await conn.fetchrow(query, *params)
                
                if row:
                    logger.info(f"✅ 엣지 {edge_id} 수정 성공")
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"❌ 엣지 {edge_id} 수정 실패: {str(e)}")
            return None
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제"""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = "DELETE FROM edge WHERE id = $1"
                result = await conn.execute(query, edge_id)
                
                if result == "DELETE 1":
                    logger.info(f"✅ 엣지 {edge_id} 삭제 성공")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"❌ 엣지 {edge_id} 삭제 실패: {str(e)}")
            return False
    
    # ============================================================================
    # 🔍 검색 및 필터링
    # ============================================================================
    
    async def get_edges_by_type(self, edge_kind: str) -> List[Dict[str, Any]]:
        """타입별 엣지 조회"""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    FROM edge
                    WHERE edge_kind = $1
                    ORDER BY id
                """
                
                rows = await conn.fetch(query, edge_kind)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ 타입별 엣지 조회 실패: {str(e)}")
            return []
    
    async def get_edges_by_node(self, node_id: int) -> List[Dict[str, Any]]:
        """노드와 연결된 엣지 조회"""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    FROM edge
                    WHERE source_id = $1 OR target_id = $1
                    ORDER BY id
                """
                
                rows = await conn.fetch(query, node_id)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ 노드별 엣지 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🔗 배출량 전파 관련 메서드들
    # ============================================================================
    
    async def get_process_emission_data(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정의 배출량 데이터를 조회합니다."""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    SELECT p.id, p.process_name, pae.attrdir_em, pae.cumulative_emission, pae.calculation_date
                    FROM process p
                    LEFT JOIN process_attrdir_emission pae ON p.id = pae.process_id
                    WHERE p.id = $1
                """
                
                row = await conn.fetchrow(query, process_id)
                
                if row:
                    return {
                        'process_id': row['id'],
                        'process_name': row['process_name'],
                        'attrdir_em': float(row['attrdir_em']) if row['attrdir_em'] else 0.0,
                        'cumulative_emission': float(row['cumulative_emission']) if row['cumulative_emission'] else 0.0,
                        'calculation_date': row['calculation_date'].isoformat() if row['calculation_date'] else None
                    }
                return None
                
        except Exception as e:
            logger.error(f"❌ 공정 {process_id} 배출량 데이터 조회 실패: {str(e)}")
            return None
    
    async def get_continue_edges(self, source_process_id: int) -> List[Dict[str, Any]]:
        """특정 공정에서 나가는 continue 엣지들을 조회합니다."""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind
                    FROM edge
                    WHERE source_id = $1 AND edge_kind = 'continue'
                    ORDER BY id
                """
                
                rows = await conn.fetch(query, source_process_id)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ 공정 {source_process_id}의 continue 엣지 조회 실패: {str(e)}")
            return []
    
    async def update_process_cumulative_emission(self, process_id: int, cumulative_emission: float) -> bool:
        """공정의 누적 배출량을 업데이트합니다."""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    UPDATE process_attrdir_emission
                    SET cumulative_emission = $1, calculation_date = NOW()
                    WHERE process_id = $2
                """
                
                result = await conn.execute(query, cumulative_emission, process_id)
                
                if result == "UPDATE 1":
                    logger.info(f"✅ 공정 {process_id} 누적 배출량 업데이트 성공: {cumulative_emission}")
                    return True
                else:
                    logger.warning(f"⚠️ 공정 {process_id}의 배출량 데이터가 없어 새로 생성합니다")
                    # 배출량 데이터가 없으면 새로 생성
                    insert_query = """
                        INSERT INTO process_attrdir_emission (process_id, cumulative_emission, calculation_date)
                        VALUES ($1, $2, NOW())
                    """
                    
                    await conn.execute(insert_query, process_id, cumulative_emission)
                    return True
                    
        except Exception as e:
            logger.error(f"❌ 공정 {process_id} 누적 배출량 업데이트 실패: {str(e)}")
            return False
    
    async def get_processes_connected_to_product(self, product_id: int) -> List[Dict[str, Any]]:
        """제품에 연결된 모든 공정들을 조회합니다."""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    SELECT e.source_id as process_id, e.edge_kind
                    FROM edge e
                    WHERE e.target_id = $1 AND e.edge_kind = 'produce'
                    ORDER BY e.source_id
                """
                
                rows = await conn.fetch(query, product_id)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ 제품 {product_id}에 연결된 공정 조회 실패: {str(e)}")
            return []
    
    async def update_product_emission(self, product_id: int, total_emission: float) -> bool:
        """제품의 배출량을 업데이트합니다."""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    UPDATE product
                    SET attr_em = $1, updated_at = NOW()
                    WHERE id = $2
                """
                
                result = await conn.execute(query, total_emission, product_id)
                
                if result == "UPDATE 1":
                    logger.info(f"✅ 제품 {product_id} 배출량 업데이트 성공: {total_emission}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"❌ 제품 {product_id} 배출량 업데이트 실패: {str(e)}")
            return False
    
    async def get_product_data(self, product_id: int) -> Optional[Dict[str, Any]]:
        """제품 데이터를 조회합니다."""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, product_name, product_amount, product_sell, product_eusell, attr_em
                    FROM product
                    WHERE id = $1
                """
                
                row = await conn.fetchrow(query, product_id)
                
                if row:
                    return {
                        'id': row['id'],
                        'product_name': row['product_name'],
                        'product_amount': float(row['product_amount']) if row['product_amount'] else 0.0,
                        'product_sell': float(row['product_sell']) if row['product_sell'] else 0.0,
                        'product_eusell': float(row['product_eusell']) if row['product_eusell'] else 0.0,
                        'attr_em': float(row['attr_em']) if row['attr_em'] else 0.0
                    }
                return None
                
        except Exception as e:
            logger.error(f"❌ 제품 {product_id} 데이터 조회 실패: {str(e)}")
            return None
    
    async def get_processes_consuming_product(self, product_id: int) -> List[Dict[str, Any]]:
        """제품을 소비하는 모든 공정들을 조회합니다."""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                # 제품의 to_next_process 계산
                product_query = """
                    SELECT product_amount, product_sell, product_eusell, attr_em
                    FROM product
                    WHERE id = $1
                """
                product_row = await conn.fetchrow(product_query, product_id)
                
                if not product_row:
                    logger.warning(f"제품 {product_id}를 찾을 수 없습니다")
                    return []
                
                # to_next_process = product_amount - product_sell - product_eusell
                to_next_process = (float(product_row['product_amount']) - 
                                 float(product_row['product_sell']) - 
                                 float(product_row['product_eusell']))
                
                # 제품을 소비하는 공정들을 조회 (consumption_amount 사용)
                query = """
                    SELECT e.target_id as process_id, e.edge_kind, 
                           COALESCE(pp.consumption_amount, 0) as consumption_amount
                    FROM edge e
                    LEFT JOIN product_process pp ON e.target_id = pp.process_id AND e.source_id = pp.product_id
                    WHERE e.source_id = $1 AND e.edge_kind = 'consume'
                    ORDER BY e.target_id
                """
                
                rows = await conn.fetch(query, product_id)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"제품 {product_id}를 소비하는 공정 조회 실패: {str(e)}")
            return []
    
    async def update_process_material_amount(self, process_id: int, product_id: int, amount: float) -> bool:
        """공정의 원료 투입량을 업데이트합니다."""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                query = """
                    UPDATE product_process
                    SET consumption_amount = $1, updated_at = NOW()
                    WHERE process_id = $2 AND product_id = $3
                """
                
                result = await conn.execute(query, amount, process_id, product_id)
                
                if result == "UPDATE 1":
                    logger.info(f"공정 {process_id}의 제품 {product_id} 투입량 업데이트 성공: {amount}")
                    return True
                else:
                    logger.warning(f"공정 {process_id}의 제품 {product_id} 관계가 없어 새로 생성합니다")
                    # 관계가 없으면 새로 생성
                    insert_query = """
                        INSERT INTO product_process (process_id, product_id, consumption_amount)
                        VALUES ($1, $2, $3)
                    """
                    
                    await conn.execute(insert_query, process_id, product_id, amount)
                    return True
                    
        except Exception as e:
            logger.error(f"공정 {process_id}의 제품 {product_id} 투입량 업데이트 실패: {str(e)}")
            return False
