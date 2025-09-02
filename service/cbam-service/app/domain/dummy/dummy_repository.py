# ============================================================================
# 📦 Dummy Repository - Dummy 데이터 접근
# ============================================================================

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import asyncpg

logger = logging.getLogger(__name__)

class DummyRepository:
    """Dummy 데이터 접근 클래스 (asyncpg 연결 풀)"""
    
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
                    'application_name': 'cbam-service-dummy'
                }
            )
            logger.info("✅ Dummy 데이터베이스 연결 풀 생성 성공")
            
            # 테이블 생성은 선택적으로 실행
            try:
                await self._create_dummy_table_async()
            except Exception as e:
                logger.warning(f"⚠️ 테이블 생성 실패 (기본 기능은 정상): {e}")
            
        except Exception as e:
            logger.error(f"❌ Dummy 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            logger.info("🔄 Dummy 연결 풀 초기화 시작")
            await self.initialize()
        
        if not self.pool:
            logger.error("❌ Dummy 연결 풀이 초기화되지 않았습니다.")
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다. DATABASE_URL 환경변수를 확인해주세요.")
        
        logger.info("✅ Dummy 연결 풀 정상 상태 확인")
    
    async def _create_dummy_table_async(self):
        """dummy_data 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # dummy_data 테이블이 이미 존재하는지 확인
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'dummy_data'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ dummy_data 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    # dummy_data 테이블 생성
                    await conn.execute("""
                        CREATE TABLE dummy_data (
                            id SERIAL PRIMARY KEY,
                            로트번호 VARCHAR(100) NOT NULL,
                            생산품명 VARCHAR(200) NOT NULL,
                            생산수량 NUMERIC(10,2) NOT NULL,
                            투입일 DATE,
                            종료일 DATE,
                            공정 VARCHAR(100) NOT NULL,
                            투입물명 VARCHAR(200) NOT NULL,
                            수량 NUMERIC(10,2) NOT NULL,
                            단위 VARCHAR(50) NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    # 인덱스 생성
                    await conn.execute("CREATE INDEX idx_dummy_로트번호 ON dummy_data(로트번호);")
                    await conn.execute("CREATE INDEX idx_dummy_생산품명 ON dummy_data(생산품명);")
                    await conn.execute("CREATE INDEX idx_dummy_공정 ON dummy_data(공정);")
                    await conn.execute("CREATE INDEX idx_dummy_투입물명 ON dummy_data(투입물명);")
                    
                    logger.info("✅ dummy_data 테이블 생성 완료")
                else:
                    logger.info("✅ dummy_data 테이블이 이미 존재합니다.")
                    
        except Exception as e:
            logger.error(f"❌ dummy_data 테이블 생성 실패: {str(e)}")
            raise
    
    async def create_dummy_data(self, data: Dict[str, Any]) -> Optional[int]:
        """Dummy 데이터 생성"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO dummy_data (
                        로트번호, 생산품명, 생산수량, 투입일, 종료일, 
                        공정, 투입물명, 수량, 단위
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING id;
                """
                
                result = await conn.fetchval(
                    query,
                    data['로트번호'],
                    data['생산품명'],
                    data['생산수량'],
                    data.get('투입일'),
                    data.get('종료일'),
                    data['공정'],
                    data['투입물명'],
                    data['수량'],
                    data['단위']
                )
                
                logger.info(f"✅ Dummy 데이터 생성 성공: ID {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 생성 실패: {str(e)}")
            raise
    
    async def get_dummy_data_by_id(self, data_id: int) -> Optional[Dict[str, Any]]:
        """ID로 Dummy 데이터 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM dummy_data WHERE id = $1;"
                row = await conn.fetchrow(query, data_id)
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 조회 실패: {str(e)}")
            raise
    
    async def get_all_dummy_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """모든 Dummy 데이터 조회 (페이징)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM dummy_data ORDER BY id DESC LIMIT $1 OFFSET $2;"
                rows = await conn.fetch(query, limit, offset)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 목록 조회 실패: {str(e)}")
            raise
    
    async def update_dummy_data(self, data_id: int, data: Dict[str, Any]) -> bool:
        """Dummy 데이터 수정"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                # 업데이트할 필드들만 동적으로 구성
                update_fields = []
                values = []
                param_count = 1
                
                for key, value in data.items():
                    if key in ['로트번호', '생산품명', '생산수량', '투입일', '종료일', '공정', '투입물명', '수량', '단위']:
                        update_fields.append(f"{key} = ${param_count}")
                        values.append(value)
                        param_count += 1
                
                if not update_fields:
                    logger.warning("업데이트할 필드가 없습니다.")
                    return False
                
                # updated_at 필드 추가
                update_fields.append("updated_at = NOW()")
                
                query = f"""
                    UPDATE dummy_data 
                    SET {', '.join(update_fields)}
                    WHERE id = ${param_count};
                """
                values.append(data_id)
                
                result = await conn.execute(query, *values)
                
                if result == "UPDATE 1":
                    logger.info(f"✅ Dummy 데이터 수정 성공: ID {data_id}")
                    return True
                else:
                    logger.warning(f"⚠️ Dummy 데이터 수정 실패: ID {data_id}를 찾을 수 없음")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 수정 실패: {str(e)}")
            raise
    
    async def delete_dummy_data(self, data_id: int) -> bool:
        """Dummy 데이터 삭제"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                query = "DELETE FROM dummy_data WHERE id = $1;"
                result = await conn.execute(query, data_id)
                
                if result == "DELETE 1":
                    logger.info(f"✅ Dummy 데이터 삭제 성공: ID {data_id}")
                    return True
                else:
                    logger.warning(f"⚠️ Dummy 데이터 삭제 실패: ID {data_id}를 찾을 수 없음")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 삭제 실패: {str(e)}")
            raise
    
    async def search_dummy_data(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Dummy 데이터 검색"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT * FROM dummy_data 
                    WHERE 로트번호 ILIKE $1 
                       OR 생산품명 ILIKE $1 
                       OR 공정 ILIKE $1 
                       OR 투입물명 ILIKE $1
                    ORDER BY id DESC 
                    LIMIT $2;
                """
                
                search_pattern = f"%{search_term}%"
                rows = await conn.fetch(query, search_pattern, limit)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 검색 실패: {str(e)}")
            raise
    
    async def get_dummy_data_count(self) -> int:
        """Dummy 데이터 총 개수 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT COUNT(*) FROM dummy_data;"
                result = await conn.fetchval(query)
                
                return result or 0
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 개수 조회 실패: {str(e)}")
            raise
    
    async def close(self):
        """연결 풀 종료"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ Dummy 연결 풀 종료")
