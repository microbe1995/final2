# ============================================================================
# 🔗 Edge Repository - 엣지 데이터 접근
# ============================================================================

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
from app.domain.edge.edge_schema import EdgeCreateRequest, EdgeUpdateRequest

logger = logging.getLogger(__name__)

class EdgeRepository:
    """엣지 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
            return
        
        self.pool = None
        self._initialization_attempted = False
        logger.info("✅ Edge Repository 초기화 완료")
    
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
            logger.info("✅ Edge Repository 데이터베이스 연결 풀 초기화 완료")
            
            # 테이블 생성
            try:
                await self._create_edge_table_async()
            except Exception as e:
                logger.warning(f"⚠️ Edge 테이블 생성 실패 (기본 기능은 정상): {e}")
            
        except Exception as e:
            logger.error(f"❌ Edge Repository 초기화 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
    async def _create_edge_table_async(self):
        """Edge 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS edge (
                        id SERIAL PRIMARY KEY,
                        source_node_type TEXT NOT NULL,
                        source_id INTEGER NOT NULL,
                        target_node_type TEXT NOT NULL,
                        target_id INTEGER NOT NULL,
                        edge_kind TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # 인덱스 생성
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_edge_source_node_type ON edge(source_node_type)
                """)
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_edge_source_id ON edge(source_id)
                """)
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_edge_target_node_type ON edge(target_node_type)
                """)
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_edge_target_id ON edge(target_id)
                """)
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_edge_kind ON edge(edge_kind)
                """)
                
                logger.info("✅ Edge 테이블 및 인덱스 생성 완료")
                
        except Exception as e:
            logger.error(f"❌ Edge 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")
    
    async def create_edge(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """엣지 생성"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                """, 
                    edge_data.get('source_node_type'),  # 🔴 수정: 개별 인수로 전달
                    edge_data.get('source_id'),  # 🔴 수정: 개별 인수로 전달
                    edge_data.get('target_node_type'),  # 🔴 수정: 개별 인수로 전달
                    edge_data.get('target_id'),  # 🔴 수정: 개별 인수로 전달
                    edge_data.get('edge_kind')   # 🔴 수정: 개별 인수로 전달
                )
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ 엣지 생성 실패: {str(e)}")
            raise e
    
    async def get_edges(self) -> List[Dict[str, Any]]:
        """모든 엣지 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM edge ORDER BY id
                """)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 엣지 조회 실패: {str(e)}")
            raise e
    
    async def get_edge(self, edge_id: int) -> Optional[Dict[str, Any]]:
        """특정 엣지 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM edge WHERE id = $1
                """, edge_id)  # 🔴 수정: 개별 인수로 전달
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 엣지 조회 실패: {str(e)}")
            raise e
    
    async def update_edge(self, edge_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 업데이트"""
        await self._ensure_pool_initialized()
        
        try:
            # 동적으로 업데이트할 필드와 값을 구성
            set_clauses = []
            values = [edge_id]  # 첫 번째 값은 WHERE 조건의 edge_id
            
            if 'source_node_type' in update_data:
                set_clauses.append("source_node_type = $" + str(len(values) + 1))
                values.append(update_data['source_node_type'])
            if 'source_id' in update_data:
                set_clauses.append("source_id = $" + str(len(values) + 1))
                values.append(update_data['source_id'])
            if 'target_node_type' in update_data:
                set_clauses.append("target_node_type = $" + str(len(values) + 1))
                values.append(update_data['target_node_type'])
            if 'target_id' in update_data:
                set_clauses.append("target_id = $" + str(len(values) + 1))
                values.append(update_data['target_id'])
            if 'edge_kind' in update_data:
                set_clauses.append("edge_kind = $" + str(len(values) + 1))
                values.append(update_data['edge_kind'])
            
            set_clauses.append("updated_at = NOW()")
            
            query = f"""
                UPDATE edge 
                SET {', '.join(set_clauses)}
                WHERE id = $1
                RETURNING *
            """
            
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(query, *values)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 엣지 업데이트 실패: {str(e)}")
            raise e
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM edge WHERE id = $1
                """, edge_id)  # 🔴 수정: 개별 인수로 전달
                
                return result != "DELETE 0"
                
        except Exception as e:
            logger.error(f"❌ 엣지 삭제 실패: {str(e)}")
            raise e
    
    async def get_edges_by_type(self, edge_kind: str) -> List[Dict[str, Any]]:
        """타입별 엣지 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM edge WHERE edge_kind = $1 ORDER BY id
                """, edge_kind)  # 🔴 수정: 개별 인수로 전달
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 타입별 엣지 조회 실패: {str(e)}")
            raise e
    
    async def get_edges_by_node(self, node_id: int) -> List[Dict[str, Any]]:
        """노드와 연결된 엣지 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM edge 
                    WHERE source_id = $1 OR target_id = $1 
                    ORDER BY id
                """, node_id)  # 🔴 수정: 개별 인수로 전달
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 노드별 엣지 조회 실패: {str(e)}")
            raise e
