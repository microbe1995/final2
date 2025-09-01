# ============================================================================
# 📦 Edge Repository - 엣지 데이터 접근
# ============================================================================

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import asyncpg

logger = logging.getLogger(__name__)

class EdgeRepository:
    """엣지 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.pool = None
        self._initialization_attempted = False
        
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
    
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
            
            # 테이블 생성 확인
            await self._create_edge_table_async()
            
        except Exception as e:
            logger.error(f"❌ Edge 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
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
                        CREATE INDEX idx_edge_source ON edge(source_node_type, source_id);
                        CREATE INDEX idx_edge_target ON edge(target_node_type, target_id);
                        CREATE INDEX idx_edge_kind ON edge(edge_kind);
                    """)
                    
                    logger.info("✅ edge 테이블 생성 완료")
                else:
                    logger.info("✅ edge 테이블 확인 완료")
                    
        except Exception as e:
            logger.error(f"❌ edge 테이블 생성 실패: {str(e)}")
            raise e
    
    # ============================================================================
    # 🔗 Edge CRUD 메서드들
    # ============================================================================
    
    async def create_edge(self, edge_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 생성"""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $6)
                    RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                """
                
                now = datetime.utcnow()
                row = await conn.fetchrow(
                    query,
                    edge_data['source_node_type'],
                    edge_data['source_id'],
                    edge_data['target_node_type'],
                    edge_data['target_id'],
                    edge_data['edge_kind'],
                    now
                )
                
                if row:
                    result = {
                        'id': row['id'],
                        'source_node_type': row['source_node_type'],
                        'source_id': row['source_id'],
                        'target_node_type': row['target_node_type'],
                        'target_id': row['target_id'],
                        'edge_kind': row['edge_kind'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    }
                    logger.info(f"✅ 엣지 생성 완료: ID {row['id']}")
                    return result
                else:
                    logger.error("엣지 생성 실패: 데이터베이스에서 결과를 반환하지 않았습니다.")
                    return None
                    
        except Exception as e:
            logger.error(f"엣지 생성 실패: {e}")
            raise e
    
    async def get_edges(self) -> List[Dict[str, Any]]:
        """모든 엣지 조회"""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    FROM edge
                    ORDER BY id
                """
                rows = await conn.fetch(query)
                
                return [
                    {
                        'id': row['id'],
                        'source_node_type': row['source_node_type'],
                        'source_id': row['source_id'],
                        'target_node_type': row['target_node_type'],
                        'target_id': row['target_id'],
                        'edge_kind': row['edge_kind'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"엣지 조회 실패: {e}")
            return []
    
    async def get_edge(self, edge_id: int) -> Optional[Dict[str, Any]]:
        """특정 엣지 조회"""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    FROM edge
                    WHERE id = $1
                """
                row = await conn.fetchrow(query, edge_id)
                
                if row:
                    return {
                        'id': row['id'],
                        'source_node_type': row['source_node_type'],
                        'source_id': row['source_id'],
                        'target_node_type': row['target_node_type'],
                        'target_id': row['target_id'],
                        'edge_kind': row['edge_kind'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    }
                return None
        except Exception as e:
            logger.error(f"엣지 {edge_id} 조회 실패: {e}")
            return None
    
    async def update_edge(self, edge_id: int, edge_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 수정"""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                # 업데이트할 필드들을 동적으로 구성
                update_fields = []
                params = []
                param_count = 1
                
                if edge_data.get('source_node_type') is not None:
                    update_fields.append(f"source_node_type = ${param_count}")
                    params.append(edge_data['source_node_type'])
                    param_count += 1
                
                if edge_data.get('source_id') is not None:
                    update_fields.append(f"source_id = ${param_count}")
                    params.append(edge_data['source_id'])
                    param_count += 1
                
                if edge_data.get('target_node_type') is not None:
                    update_fields.append(f"target_node_type = ${param_count}")
                    params.append(edge_data['target_node_type'])
                    param_count += 1
                
                if edge_data.get('target_id') is not None:
                    update_fields.append(f"target_id = ${param_count}")
                    params.append(edge_data['target_id'])
                    param_count += 1
                
                if edge_data.get('edge_kind') is not None:
                    update_fields.append(f"edge_kind = ${param_count}")
                    params.append(edge_data['edge_kind'])
                    param_count += 1
                
                # updated_at 필드 추가
                update_fields.append(f"updated_at = ${param_count}")
                params.append(datetime.utcnow())
                param_count += 1
                
                # ID 파라미터 추가
                params.append(edge_id)
                
                if update_fields:
                    query = f"""
                        UPDATE edge 
                        SET {', '.join(update_fields)}
                        WHERE id = ${param_count}
                        RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    """
                    
                    row = await conn.fetchrow(query, *params)
                    
                    if row:
                        result = {
                            'id': row['id'],
                            'source_node_type': row['source_node_type'],
                            'source_id': row['source_id'],
                            'target_node_type': row['target_node_type'],
                            'target_id': row['target_id'],
                            'edge_kind': row['edge_kind'],
                            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                            'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                        }
                        logger.info(f"✅ 엣지 {edge_id} 수정 완료")
                        return result
                
                return None
                
        except Exception as e:
            logger.error(f"엣지 {edge_id} 수정 실패: {e}")
            raise e
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제"""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    DELETE FROM edge 
                    WHERE id = $1
                    RETURNING id
                """
                
                row = await conn.fetchrow(query, edge_id)
                
                if row:
                    logger.info(f"✅ 엣지 {edge_id} 삭제 완료")
                    return True
                else:
                    logger.warning(f"엣지 {edge_id} 삭제 실패: 해당 엣지를 찾을 수 없습니다.")
                    return False
                    
        except Exception as e:
            logger.error(f"엣지 {edge_id} 삭제 실패: {e}")
            raise e
    
    # ============================================================================
    # 🔗 배출량 전파 관련 메서드들
    # ============================================================================
    
    async def get_process_emission_data(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정의 배출량 데이터를 조회합니다."""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT 
                        process_id,
                        attrdir_em,
                        cumulative_emission,
                        total_matdir_emission,
                        total_fueldir_emission
                    FROM process_attrdir_emission 
                    WHERE process_id = $1
                """
                row = await conn.fetchrow(query, process_id)
                
                if row:
                    return {
                        'process_id': row['process_id'],
                        'attrdir_em': float(row['attrdir_em']) if row['attrdir_em'] else 0.0,
                        'cumulative_emission': float(row['cumulative_emission']) if row['cumulative_emission'] else 0.0,
                        'total_matdir_emission': float(row['total_matdir_emission']) if row['total_matdir_emission'] else 0.0,
                        'total_fueldir_emission': float(row['total_fueldir_emission']) if row['total_fueldir_emission'] else 0.0
                    }
                return None
                
        except Exception as e:
            logger.error(f"공정 {process_id} 배출량 데이터 조회 실패: {e}")
            return None
    
    async def get_continue_edges(self, source_process_id: int) -> List[Dict[str, Any]]:
        """특정 공정에서 나가는 continue 엣지들을 조회합니다."""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT 
                        id,
                        source_node_type,
                        source_id,
                        target_node_type,
                        target_id,
                        edge_kind
                    FROM edge 
                    WHERE source_node_type = 'process' 
                    AND source_id = $1 
                    AND edge_kind = 'continue'
                """
                rows = await conn.fetch(query, source_process_id)
                
                return [
                    {
                        'id': row['id'],
                        'source_node_type': row['source_node_type'],
                        'source_id': row['source_id'],
                        'target_node_type': row['target_node_type'],
                        'target_id': row['target_id'],
                        'edge_kind': row['edge_kind']
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"공정 {source_process_id}의 continue 엣지 조회 실패: {e}")
            return []
    
    async def update_process_cumulative_emission(self, process_id: int, cumulative_emission: float) -> bool:
        """공정의 누적 배출량을 업데이트합니다."""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    UPDATE process_attrdir_emission 
                    SET 
                        cumulative_emission = $2,
                        updated_at = NOW()
                    WHERE process_id = $1
                """
                await conn.execute(query, process_id, cumulative_emission)
                
                logger.info(f"공정 {process_id} 누적 배출량 업데이트: {cumulative_emission}")
                return True
                
        except Exception as e:
            logger.error(f"공정 {process_id} 누적 배출량 업데이트 실패: {e}")
            return False
