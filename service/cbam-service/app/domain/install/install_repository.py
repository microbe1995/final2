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
            # 데이터 검증
            await self._validate_install_data(install_data)
            
            # 중복 검사
            await self._check_install_name_duplicate(install_data['install_name'])
            
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
            # 수정할 데이터 검증
            if 'install_name' in update_data:
                # 사업장명이 수정되는 경우 중복 검사
                await self._check_install_name_duplicate_for_update(update_data['install_name'], install_id)
                
                # 사업장명 정리 및 검증
                update_data['install_name'] = await self.validate_and_clean_install_name(update_data['install_name'])
            
            if 'reporting_year' in update_data:
                # 보고기간 검증
                reporting_year = update_data['reporting_year']
                if not isinstance(reporting_year, int):
                    raise ValueError("보고기간(년도)은 정수여야 합니다.")
                
                current_year = datetime.now().year
                if reporting_year < 1900 or reporting_year > current_year + 10:
                    raise ValueError(f"보고기간(년도)은 1900년부터 {current_year + 10}년 사이여야 합니다.")
            
            return await self._update_install_db(install_id, update_data)
        except Exception as e:
            logger.error(f"❌ 사업장 수정 실패: {str(e)}")
            raise
    
    async def delete_install(self, install_id: int) -> bool:
        """사업장 삭제"""
        await self._ensure_pool_initialized()
        try:
            # 먼저 데이터베이스 구조 테스트 실행
            logger.info(f"🧪 사업장 ID {install_id} 삭제 전 데이터베이스 구조 테스트...")
            test_result = await self.test_database_structure()
            
            # 테스트 결과에 따른 처리
            if not test_result['product_install_id_exists']:
                logger.error("❌ product.install_id 컬럼이 존재하지 않습니다. 데이터베이스 구조를 확인하세요.")
                raise Exception("데이터베이스 구조 오류: product.install_id 컬럼 없음")
            
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
                """, install_data['install_name'], install_data['reporting_year'])
                
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
                logger.info(f"🗑️ 사업장 ID {install_id} 삭제 시작 - 데이터베이스 구조 분석 중...")
                
                # 먼저 데이터베이스 구조 분석
                db_analysis = await self.analyze_database_structure()
                logger.info(f"📊 데이터베이스 구조 분석 결과:")
                logger.info(f"   - 테이블 개수: {len(db_analysis['table_names'])}")
                logger.info(f"   - 외래키 제약조건: {len(db_analysis['foreign_key_constraints'])}")
                logger.info(f"   - install 관련 외래키: {db_analysis['install_related_fks']}")
                
                # install ID 1과 연결된 데이터 확인
                if install_id == 1 and 'install_1_connections' in db_analysis:
                    connections = db_analysis['install_1_connections']
                    logger.info(f"🔗 install ID 1 연결 데이터:")
                    if 'products' in connections:
                        logger.info(f"   - 제품: {len(connections['products'])}개")
                    if 'processes' in connections:
                        logger.info(f"   - 프로세스: {len(connections['processes'])}개")
                
                # 외래키 제약조건에 따른 삭제 순서 결정
                delete_order = self._determine_delete_order(db_analysis, install_id)
                logger.info(f"🗑️ 삭제 순서: {delete_order}")
                
                # 순서대로 삭제 실행 (각 단계별로 개별 트랜잭션 사용)
                for step, (table_name, query, params) in enumerate(delete_order, 1):
                    try:
                        logger.info(f"📋 {step}단계: {table_name} 테이블 정리 중...")
                        async with conn.transaction():
                            result = await conn.execute(query, *params)
                            logger.info(f"✅ {table_name} 정리 완료: {result}")
                    except Exception as e:
                        logger.warning(f"⚠️ {table_name} 정리 실패 (건너뜀): {e}")
                        continue
                
                # 마지막으로 install 삭제
                try:
                    logger.info(f"📋 최종 단계: install 테이블에서 ID {install_id} 삭제")
                    async with conn.transaction():
                        result = await conn.execute("""
                            DELETE FROM install WHERE id = $1
                        """, install_id)
                        
                        if result == "DELETE 0":
                            logger.warning(f"⚠️ 삭제할 사업장 ID {install_id}를 찾을 수 없습니다")
                            return False
                        
                        logger.info(f"✅ 사업장 ID {install_id} 삭제 완료")
                        return True
                except Exception as e:
                    logger.error(f"❌ install 테이블 삭제 실패: {str(e)}")
                    raise
                    
        except Exception as e:
            logger.error(f"❌ 사업장 삭제 실패: {str(e)}")
            raise

    def _determine_delete_order(self, db_analysis: Dict[str, Any], install_id: int) -> List[tuple]:
        """데이터베이스 구조 분석 결과에 따른 삭제 순서 결정"""
        delete_order = []
        
        # 외래키 제약조건을 기반으로 삭제 순서 결정
        fk_constraints = db_analysis.get('foreign_key_constraints', {})
        
        # 1단계: product_process 관계 삭제 (가장 먼저)
        if 'product_process' in db_analysis['table_names']:
            delete_order.append((
                'product_process',
                "DELETE FROM product_process WHERE product_id IN (SELECT id FROM product WHERE install_id = $1)",
                (install_id,)
            ))
        
        # 2단계: edge 삭제 (product/process를 참조하는 것들)
        if 'edge' in db_analysis['table_names']:
            delete_order.append((
                'edge',
                "DELETE FROM edge e WHERE e.source_node_id IN (SELECT p.id FROM product p WHERE p.install_id = $1 UNION SELECT proc.id FROM process proc JOIN product_process pp ON proc.id = pp.process_id JOIN product pr ON pp.product_id = pr.id WHERE pr.install_id = $1) OR e.target_node_id IN (SELECT p.id FROM product p WHERE p.install_id = $1 UNION SELECT proc.id FROM process proc JOIN product_process pp ON proc.id = pp.process_id JOIN product pr ON pp.product_id = pr.id WHERE pr.install_id = $1)",
                (install_id, install_id, install_id, install_id)
            ))
        
        # 3단계: process 삭제 (product와 연결되지 않은 것들)
        if 'process' in db_analysis['table_names'] and 'product_process' in db_analysis['table_names']:
            delete_order.append((
                'process',
                "DELETE FROM process WHERE id NOT IN (SELECT DISTINCT process_id FROM product_process)",
                ()
            ))
        
        # 4단계: product 삭제 (install을 참조하는 것들)
        if 'product' in db_analysis['table_names']:
            delete_order.append((
                'product',
                "DELETE FROM product WHERE install_id = $1",
                (install_id,)
            ))
        
        return delete_order

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
                        SELECT p.id FROM product p WHERE p.install_id = $1
                        UNION
                        SELECT proc.id FROM process proc
                        JOIN product_process pp ON proc.id = pp.process_id
                        JOIN product pr ON pp.product_id = pr.id
                        WHERE pr.install_id = $1
                    ) OR e.target_node_id IN (
                        SELECT p.id FROM product p WHERE p.install_id = $1
                        UNION
                        SELECT proc.id FROM process proc
                        JOIN product_process pp ON proc.id = pp.process_id
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

    async def analyze_database_structure(self) -> Dict[str, Any]:
        """데이터베이스 구조 및 외래키 관계 상세 분석"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                logger.info("🔍 데이터베이스 구조 분석 시작...")
                
                # 1. 모든 테이블 목록 조회
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                table_names = [t['table_name'] for t in tables]
                logger.info(f"📋 발견된 테이블들: {table_names}")
                
                # 2. 각 테이블의 상세 구조 분석
                table_structures = {}
                foreign_key_constraints = {}
                
                for table_name in table_names:
                    # 테이블 컬럼 정보
                    columns = await conn.fetch("""
                        SELECT 
                            column_name, 
                            data_type, 
                            is_nullable,
                            column_default,
                            ordinal_position
                        FROM information_schema.columns
                        WHERE table_schema = 'public' AND table_name = $1
                        ORDER BY ordinal_position
                    """, table_name)
                    
                    table_structures[table_name] = [dict(col) for col in columns]
                    
                    # 외래키 제약조건 정보
                    fk_constraints = await conn.fetch("""
                        SELECT 
                            tc.constraint_name,
                            tc.table_name,
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name,
                            rc.delete_rule,
                            rc.update_rule
                        FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                        JOIN information_schema.referential_constraints AS rc
                            ON tc.constraint_name = rc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY' 
                            AND tc.table_name = $1
                    """, table_name)
                    
                    if fk_constraints:
                        foreign_key_constraints[table_name] = [dict(fk) for fk in fk_constraints]
                
                # 3. install 테이블과 관련된 외래키 관계 특별 분석
                install_related_fks = {}
                if 'product' in table_names:
                    # product 테이블에서 install을 참조하는 외래키
                    product_fks = await conn.fetch("""
                        SELECT 
                            tc.constraint_name,
                            tc.table_name,
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name,
                            rc.delete_rule,
                            rc.update_rule
                        FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                        JOIN information_schema.referential_constraints AS rc
                            ON tc.constraint_name = rc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY' 
                            AND tc.table_name = 'product'
                            AND ccu.table_name = 'install'
                    """)
                    
                    if product_fks:
                        install_related_fks['product_to_install'] = [dict(fk) for fk in product_fks]
                
                # 4. 실제 데이터 존재 여부 확인
                data_counts = {}
                for table_name in ['install', 'product', 'process', 'product_process', 'edge']:
                    if table_name in table_names:
                        try:
                            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                            data_counts[table_name] = count
                        except Exception as e:
                            data_counts[table_name] = f"Error: {str(e)}"
                
                # 5. install ID 1과 연결된 실제 데이터 확인
                install_1_connections = {}
                if 'product' in table_names:
                    try:
                        # install ID 1을 참조하는 제품들
                        products = await conn.fetch("""
                            SELECT id, install_id, name FROM product WHERE install_id = 1
                        """)
                        install_1_connections['products'] = [dict(p) for p in products]
                        
                        # 이 제품들과 연결된 프로세스들
                        if 'product_process' in table_names:
                            processes = await conn.fetch("""
                                SELECT DISTINCT p.id, p.name, pp.product_id
                                FROM process p
                                JOIN product_process pp ON p.id = pp.process_id
                                JOIN product pr ON pp.product_id = pr.id
                                WHERE pr.install_id = 1
                            """)
                            install_1_connections['processes'] = [dict(p) for p in processes]
                    except Exception as e:
                        install_1_connections['error'] = str(e)
                
                analysis_result = {
                    'table_names': table_names,
                    'table_structures': table_structures,
                    'foreign_key_constraints': foreign_key_constraints,
                    'install_related_fks': install_related_fks,
                    'data_counts': data_counts,
                    'install_1_connections': install_1_connections
                }
                
                logger.info("✅ 데이터베이스 구조 분석 완료")
                return analysis_result
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 구조 분석 실패: {str(e)}")
            raise

    async def test_database_structure(self) -> Dict[str, Any]:
        """데이터베이스 구조 간단 테스트"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                logger.info("🧪 데이터베이스 구조 테스트 시작...")
                
                # 1. 테이블 존재 여부 확인
                tables_to_check = ['install', 'product', 'process', 'product_process', 'edge']
                existing_tables = []
                
                for table in tables_to_check:
                    exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = $1
                        )
                    """, table)
                    if exists:
                        existing_tables.append(table)
                        logger.info(f"✅ {table} 테이블 존재")
                    else:
                        logger.warning(f"❌ {table} 테이블 없음")
                
                # 2. product 테이블의 install_id 컬럼 확인
                if 'product' in existing_tables:
                    try:
                        columns = await conn.fetch("""
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns
                            WHERE table_name = 'product'
                            ORDER BY ordinal_position
                        """)
                        logger.info(f"📋 product 테이블 컬럼: {[dict(col) for col in columns]}")
                        
                        # install_id 컬럼이 있는지 확인
                        install_id_exists = any(col['column_name'] == 'install_id' for col in columns)
                        if install_id_exists:
                            logger.info("✅ product.install_id 컬럼 존재")
                        else:
                            logger.warning("❌ product.install_id 컬럼 없음")
                            
                    except Exception as e:
                        logger.error(f"❌ product 테이블 컬럼 확인 실패: {e}")
                
                # 3. 외래키 제약조건 확인
                if 'product' in existing_tables:
                    try:
                        fk_constraints = await conn.fetch("""
                            SELECT 
                                tc.constraint_name,
                                tc.table_name,
                                kcu.column_name,
                                ccu.table_name AS foreign_table_name,
                                ccu.column_name AS foreign_column_name
                            FROM information_schema.table_constraints AS tc
                            JOIN information_schema.key_column_usage AS kcu
                                ON tc.constraint_name = kcu.constraint_name
                            JOIN information_schema.constraint_column_usage AS ccu
                                ON ccu.constraint_name = tc.constraint_name
                            WHERE tc.constraint_type = 'FOREIGN KEY' 
                                AND tc.table_name = 'product'
                        """)
                        
                        if fk_constraints:
                            logger.info(f"🔗 product 테이블 외래키 제약조건:")
                            for fk in fk_constraints:
                                logger.info(f"   - {fk['constraint_name']}: {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                        else:
                            logger.warning("⚠️ product 테이블에 외래키 제약조건 없음")
                            
                    except Exception as e:
                        logger.error(f"❌ 외래키 제약조건 확인 실패: {e}")
                
                # 4. 실제 데이터 확인
                data_info = {}
                for table in existing_tables:
                    try:
                        count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                        data_info[table] = count
                        logger.info(f"📊 {table} 테이블 데이터: {count}개")
                    except Exception as e:
                        data_info[table] = f"Error: {str(e)}"
                        logger.error(f"❌ {table} 테이블 데이터 확인 실패: {e}")
                
                # 5. install ID 1과 연결된 데이터 확인
                if 'product' in existing_tables:
                    try:
                        product_count = await conn.fetchval("""
                            SELECT COUNT(*) FROM product WHERE install_id = 1
                        """)
                        logger.info(f"🔗 install ID 1을 참조하는 제품: {product_count}개")
                        
                        if product_count > 0:
                            products = await conn.fetch("""
                                SELECT id, product_name, install_id FROM product WHERE install_id = 1
                            """)
                            logger.info(f"📋 연결된 제품들: {[dict(p) for p in products]}")
                            
                    except Exception as e:
                        logger.error(f"❌ install ID 1 연결 데이터 확인 실패: {e}")
                
                test_result = {
                    'existing_tables': existing_tables,
                    'data_info': data_info,
                    'product_install_id_exists': 'product' in existing_tables and any(
                        col['column_name'] == 'install_id' 
                        for col in await conn.fetch("""
                            SELECT column_name FROM information_schema.columns 
                            WHERE table_name = 'product'
                        """)
                    ) if 'product' in existing_tables else False
                }
                
                logger.info("✅ 데이터베이스 구조 테스트 완료")
                return test_result
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 구조 테스트 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔒 데이터 무결성 검증 메서드
    # ============================================================================

    async def _validate_install_data(self, install_data: Dict[str, Any]) -> None:
        """사업장 데이터 검증"""
        try:
            # install_name 검증
            if not install_data.get('install_name'):
                raise ValueError("사업장명은 필수입니다.")
            
            install_name = install_data['install_name'].strip()
            if len(install_name) == 0:
                raise ValueError("사업장명은 공백만으로 구성될 수 없습니다.")
            
            if len(install_name) > 100:  # 적절한 최대 길이 제한
                raise ValueError("사업장명은 100자를 초과할 수 없습니다.")
            
            # reporting_year 검증
            reporting_year = install_data.get('reporting_year')
            if reporting_year is None:
                raise ValueError("보고기간(년도)은 필수입니다.")
            
            if not isinstance(reporting_year, int):
                raise ValueError("보고기간(년도)은 정수여야 합니다.")
            
            current_year = datetime.now().year
            if reporting_year < 1900 or reporting_year > current_year + 10:
                raise ValueError(f"보고기간(년도)은 1900년부터 {current_year + 10}년 사이여야 합니다.")
            
            logger.info("✅ 사업장 데이터 검증 완료")
            
        except Exception as e:
            logger.error(f"❌ 사업장 데이터 검증 실패: {str(e)}")
            raise

    async def _check_install_name_duplicate(self, install_name: str) -> None:
        """사업장명 중복 검사"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
        
        try:
            async with self.pool.acquire() as conn:
                # 대소문자 구분 없이 중복 검사 (TRIM과 LOWER 사용)
                existing_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM install 
                    WHERE LOWER(TRIM(install_name)) = LOWER(TRIM($1))
                """, install_name)
                
                if existing_count > 0:
                    raise ValueError(f"사업장명 '{install_name}'은(는) 이미 존재합니다.")
                
                logger.info("✅ 사업장명 중복 검사 완료")
                
        except Exception as e:
            if "이미 존재합니다" in str(e):
                raise  # 중복 오류는 그대로 전달
            logger.error(f"❌ 사업장명 중복 검사 실패: {str(e)}")
            raise

    async def _check_install_name_duplicate_for_update(self, install_name: str, exclude_id: int) -> None:
        """사업장 수정 시 사업장명 중복 검사 (자기 자신 제외)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
        
        try:
            async with self.pool.acquire() as conn:
                # 자기 자신을 제외하고 중복 검사
                existing_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM install 
                    WHERE LOWER(TRIM(install_name)) = LOWER(TRIM($1))
                    AND id != $2
                """, install_name, exclude_id)
                
                if existing_count > 0:
                    raise ValueError(f"사업장명 '{install_name}'은(는) 이미 존재합니다.")
                
                logger.info("✅ 사업장 수정 시 중복 검사 완료")
                
        except Exception as e:
            if "이미 존재합니다" in str(e):
                raise  # 중복 오류는 그대로 전달
            logger.error(f"❌ 사업장 수정 시 중복 검사 실패: {str(e)}")
            raise

    async def validate_and_clean_install_name(self, install_name: str) -> str:
        """사업장명 검증 및 정리"""
        if not install_name:
            raise ValueError("사업장명은 필수입니다.")
        
        # 앞뒤 공백 제거
        cleaned_name = install_name.strip()
        
        if len(cleaned_name) == 0:
            raise ValueError("사업장명은 공백만으로 구성될 수 없습니다.")
        
        if len(cleaned_name) > 100:
            raise ValueError("사업장명은 100자를 초과할 수 없습니다.")
        
        # 특수문자나 위험한 문자 검증 (선택사항)
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '--', '/*', '*/']
        for char in dangerous_chars:
            if char in cleaned_name:
                raise ValueError(f"사업장명에 허용되지 않는 문자가 포함되어 있습니다: {char}")
        
        return cleaned_name
