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
        self.pool = None
        logger.info("✅ Edge Repository 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 풀 초기화"""
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise Exception("DATABASE_URL 환경변수가 설정되지 않았습니다.")
            
            self.pool = await asyncpg.create_pool(database_url)
            logger.info("✅ Edge Repository 데이터베이스 연결 풀 초기화 완료")
            
            # 테이블 생성
            await self._create_edge_table_async()
            
        except Exception as e:
            logger.error(f"❌ Edge Repository 초기화 실패: {str(e)}")
            raise e
    
    async def _create_edge_table_async(self):
        """Edge 테이블 생성 (비동기)"""
        try:
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS edge (
                        id SERIAL PRIMARY KEY,
                        source_id INTEGER NOT NULL,
                        target_id INTEGER NOT NULL,
                        edge_kind TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # 인덱스 생성
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_edge_source_id ON edge(source_id)
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
            raise e
    
    async def create_edge(self, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """엣지 생성"""
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO edge (source_id, target_id, edge_kind)
                    VALUES ($1, $2, $3)
                    RETURNING *
                """, (
                    edge_data.get('source_id'),
                    edge_data.get('target_id'),
                    edge_data.get('edge_kind')
                ))
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ 엣지 생성 실패: {str(e)}")
            raise e
    
    async def get_edges(self) -> List[Dict[str, Any]]:
        """모든 엣지 조회"""
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
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
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM edge WHERE id = $1
                """, (edge_id,))
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 엣지 조회 실패: {str(e)}")
            raise e
    
    async def update_edge(self, edge_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 업데이트"""
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    UPDATE edge 
                    SET source_id = $2, target_id = $3, edge_kind = $4, updated_at = NOW()
                    WHERE id = $1
                    RETURNING *
                """, (
                    edge_id,
                    update_data.get('source_id'),
                    update_data.get('target_id'),
                    update_data.get('edge_kind')
                ))
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 엣지 업데이트 실패: {str(e)}")
            raise e
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제"""
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM edge WHERE id = $1
                """, (edge_id,))
                
                return result != "DELETE 0"
                
        except Exception as e:
            logger.error(f"❌ 엣지 삭제 실패: {str(e)}")
            raise e
    
    async def get_edges_by_type(self, edge_kind: str) -> List[Dict[str, Any]]:
        """타입별 엣지 조회"""
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM edge WHERE edge_kind = $1 ORDER BY id
                """, (edge_kind,))
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 타입별 엣지 조회 실패: {str(e)}")
            raise e
    
    async def get_edges_by_node(self, node_id: int) -> List[Dict[str, Any]]:
        """노드와 연결된 엣지 조회"""
        if not self.pool:
            await self.initialize()
            if not self.pool:
                raise Exception("데이터베이스 연결 풀을 초기화할 수 없습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM edge 
                    WHERE source_id = $1 OR target_id = $1 
                    ORDER BY id
                """, (node_id,))
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 노드별 엣지 조회 실패: {str(e)}")
            raise e
