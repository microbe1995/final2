# ============================================================================
# 🏭 Install Repository - 사업장 데이터 접근
# ============================================================================

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg

from app.domain.install.install_schema import InstallCreateRequest, InstallUpdateRequest

logger = logging.getLogger(__name__)

class InstallRepository:
    """사업장 데이터 접근 클래스"""
    
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
                    'application_name': 'cbam-service-install'
                }
            )
            
            logger.info("✅ Install 데이터베이스 연결 풀 생성 성공")
            
            # 테이블 생성은 선택적으로 실행
            try:
                await self._create_install_table_async()
            except Exception as e:
                logger.warning(f"⚠️ Install 테이블 생성 실패 (기본 기능은 정상): {e}")
            
        except Exception as e:
            logger.error(f"❌ Install 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")

    async def _create_install_table_async(self):
        """Install 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
            
        try:
            async with self.pool.acquire() as conn:
                # install 테이블 생성
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
                
        except Exception as e:
            logger.error(f"❌ Install 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")

    # ============================================================================
    # 🏭 Install 관련 Repository 메서드
    # ============================================================================

    async def create_install(self, install_data: Dict[str, Any]) -> Dict[str, Any]:
        """사업장 생성"""
        await self._ensure_pool_initialized()
        try:
            return await self._create_install_db(install_data)
        except Exception as e:
            logger.error(f"❌ 사업장 생성 실패: {str(e)}")
            raise
    
    async def get_installs(self) -> List[Dict[str, Any]]:
        """사업장 목록 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_installs_db()
        except Exception as e:
            logger.error(f"❌ 사업장 목록 조회 실패: {str(e)}")
            raise
    
    async def get_install_names(self) -> List[Dict[str, Any]]:
        """사업장명 목록 조회 (드롭다운용)"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_install_names_db()
        except Exception as e:
            logger.error(f"❌ 사업장명 목록 조회 실패: {str(e)}")
            raise
    
    async def get_install(self, install_id: int) -> Optional[Dict[str, Any]]:
        """특정 사업장 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_install_db(install_id)
        except Exception as e:
            logger.error(f"❌ 사업장 조회 실패: {str(e)}")
            raise
    
    async def update_install(self, install_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """사업장 수정"""
        await self._ensure_pool_initialized()
        try:
            return await self._update_install_db(install_id, update_data)
        except Exception as e:
            logger.error(f"❌ 사업장 수정 실패: {str(e)}")
            raise
    
    async def delete_install(self, install_id: int) -> bool:
        """사업장 삭제"""
        await self._ensure_pool_initialized()
        try:
            # 삭제 전 연결된 데이터 확인
            connected_data = await self._get_connected_data_count(install_id)
            if connected_data['total'] > 0:
                logger.info(f"🗑️ 사업장 ID {install_id} 삭제 - 연결된 데이터: {connected_data}")
            
            return await self._delete_install_db(install_id)
        except Exception as e:
            logger.error(f"❌ 사업장 삭제 실패: {str(e)}")
            raise

    # ============================================================================
    # 🏭 Install 관련 데이터베이스 메서드
    # ============================================================================

    async def _create_install_db(self, install_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 사업장 생성"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO install (install_name, reporting_year)
                    VALUES ($1, $2)
                    RETURNING *
                """, (install_data['install_name'], install_data['reporting_year']))
                
                if result:
                    install_dict = dict(result)
                    # datetime 객체를 문자열로 변환
                    if 'created_at' in install_dict and install_dict['created_at']:
                        install_dict['created_at'] = install_dict['created_at'].isoformat()
                    if 'updated_at' in install_dict and install_dict['updated_at']:
                        install_dict['updated_at'] = install_dict['updated_at'].isoformat()
                    return install_dict
                else:
                    raise Exception("사업장 생성에 실패했습니다.")
        except Exception as e:
            logger.error(f"❌ 사업장 생성 실패: {str(e)}")
            raise

    async def _get_installs_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 사업장 목록 조회"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, install_name, reporting_year, created_at, updated_at
                    FROM install
                    ORDER BY created_at DESC
                """)
                
                installs = []
                for result in results:
                    install_dict = dict(result)
                    # datetime 객체를 문자열로 변환
                    if 'created_at' in install_dict and install_dict['created_at']:
                        install_dict['created_at'] = install_dict['created_at'].isoformat()
                    if 'updated_at' in install_dict and install_dict['updated_at']:
                        install_dict['updated_at'] = install_dict['updated_at'].isoformat()
                    installs.append(install_dict)
                
                return installs
        except Exception as e:
            logger.error(f"❌❌❌ 사업장 목록 조회 실패: {str(e)}")
            raise

    async def _get_install_names_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 사업장명 목록 조회 (드롭다운용)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, install_name
                    FROM install
                    ORDER BY install_name ASC
                """)
                
                return [dict(result) for result in results]
        except Exception as e:
            logger.error(f"❌ 사업장명 목록 조회 실패: {str(e)}")
            raise

    async def _get_install_db(self, install_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 사업장 조회"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT id, install_name, reporting_year, created_at, updated_at
                    FROM install
                    WHERE id = $1
                """, install_id)
                
                if result:
                    install_dict = dict(result)
                    # datetime 객체를 문자열로 변환
                    if 'created_at' in install_dict and install_dict['created_at']:
                        install_dict['created_at'] = install_dict['created_at'].isoformat()
                    if 'updated_at' in install_dict and install_dict['updated_at']:
                        install_dict['updated_at'] = install_dict['updated_at'].isoformat()
                    return install_dict
                return None
        except Exception as e:
            logger.error(f"❌ 사업장 조회 실패: {str(e)}")
            raise

    async def _update_install_db(self, install_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 사업장 수정"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 동적으로 SET 절 생성
                set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(update_data.keys())])
                values = list(update_data.values()) + [install_id]
                
                result = await conn.fetchrow(f"""
                    UPDATE install SET {set_clause}, updated_at = NOW()
                    WHERE id = ${len(update_data) + 1} RETURNING *
                """, *values)
                
                if result:
                    install_dict = dict(result)
                    # datetime 객체를 문자열로 변환
                    if 'created_at' in install_dict and install_dict['created_at']:
                        install_dict['created_at'] = install_dict['created_at'].isoformat()
                    if 'updated_at' in install_dict and install_dict['updated_at']:
                        install_dict['updated_at'] = install_dict['updated_at'].isoformat()
                    return install_dict
                return None
        except Exception as e:
            logger.error(f"❌ 사업장 수정 실패: {str(e)}")
            raise

    async def _delete_install_db(self, install_id: int) -> bool:
        """데이터베이스에서 사업장 삭제 (CASCADE 방식)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 트랜잭션 시작
                async with conn.transaction():
                    logger.info(f"🗑️ 사업장 ID {install_id} 삭제 시작 - 연결된 데이터 정리 중...")
                    
                    # 1단계: 연결된 product_process 관계 삭제
                    await conn.execute("""
                        DELETE FROM product_process 
                        WHERE product_id IN (
                            SELECT id FROM product WHERE install_id = $1
                        )
                    """, install_id)
                    logger.info(f"✅ product_process 관계 삭제 완료")
                    
                    # 2단계: 연결된 제품 삭제
                    await conn.execute("""
                        DELETE FROM product WHERE install_id = $1
                    """, install_id)
                    logger.info(f"✅ 연결된 제품 삭제 완료")
                    
                    # 3단계: 연결된 프로세스 삭제 (제품과 연결되지 않은 것들)
                    await conn.execute("""
                        DELETE FROM process 
                        WHERE id NOT IN (
                            SELECT DISTINCT process_id FROM product_process
                        )
                    """)
                    logger.info(f"✅ 연결되지 않은 프로세스 삭제 완료")
                    
                    # 4단계: 연결된 edge 삭제 (제품/프로세스와 연결되지 않은 것들)
                    await conn.execute("""
                        DELETE FROM edge 
                        WHERE source_node_id NOT IN (
                            SELECT id FROM product UNION SELECT id FROM process
                        ) OR target_node_id NOT IN (
                            SELECT id FROM product UNION SELECT id FROM process
                        )
                    """)
                    logger.info(f"✅ 연결되지 않은 edge 삭제 완료")
                    
                    # 5단계: 마지막으로 사업장 삭제
                    result = await conn.execute("""
                        DELETE FROM install WHERE id = $1
                    """, install_id)
                    
                    if result == "DELETE 0":
                        logger.warning(f"⚠️ 삭제할 사업장 ID {install_id}를 찾을 수 없습니다")
                        return False
                    
                    logger.info(f"✅ 사업장 ID {install_id} 삭제 완료")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ 사업장 삭제 실패: {str(e)}")
            raise

    async def _get_connected_data_count(self, install_id: int) -> Dict[str, int]:
        """사업장에 연결된 데이터 개수 확인"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 제품 개수
                product_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM product WHERE install_id = $1
                """, install_id)
                
                # 프로세스 개수 (제품과 연결된 것들)
                process_count = await conn.fetchval("""
                    SELECT COUNT(DISTINCT p.id) 
                    FROM process p
                    JOIN product_process pp ON p.id = pp.process_id
                    JOIN product pr ON pp.product_id = pr.id
                    WHERE pr.install_id = $1
                """, install_id)
                
                # Edge 개수
                edge_count = await conn.fetchval("""
                    SELECT COUNT(*) 
                    FROM edge e
                    WHERE e.source_node_id IN (
                        SELECT id FROM product WHERE install_id = $1
                        UNION
                        SELECT id FROM process p
                        JOIN product_process pp ON p.id = pp.process_id
                        JOIN product pr ON pp.product_id = pr.id
                        WHERE pr.install_id = $1
                    ) OR e.target_node_id IN (
                        SELECT id FROM product WHERE install_id = $1
                        UNION
                        SELECT id FROM process p
                        JOIN product_process pp ON p.id = pp.process_id
                        JOIN product pr ON pp.product_id = pr.id
                        WHERE pr.install_id = $1
                    )
                """, install_id)
                
                return {
                    'products': product_count or 0,
                    'processes': process_count or 0,
                    'edges': edge_count or 0,
                    'total': (product_count or 0) + (process_count or 0) + (edge_count or 0)
                }
                
        except Exception as e:
            logger.error(f"❌ 연결된 데이터 개수 확인 실패: {str(e)}")
            return {'products': 0, 'processes': 0, 'edges': 0, 'total': 0}
