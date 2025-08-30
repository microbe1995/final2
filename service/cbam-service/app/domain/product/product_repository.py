# ============================================================================
# 🏭 Install Repository - 사업장 데이터 접근
# ============================================================================

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg

from .install_schema import InstallCreateRequest, InstallUpdateRequest

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
    
    async def initialize(self):
        """데이터베이스 연결 풀 초기화"""
        if not self.database_url:
            logger.warning("DATABASE_URL이 없어 데이터베이스 초기화를 건너뜁니다.")
            return
        
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
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._create_install_db(install_data)
        except Exception as e:
            logger.error(f"❌ 사업장 생성 실패: {str(e)}")
            raise
    
    async def get_installs(self) -> List[Dict[str, Any]]:
        """사업장 목록 조회"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_installs_db()
        except Exception as e:
            logger.error(f"❌ 사업장 목록 조회 실패: {str(e)}")
            raise
    
    async def get_install_names(self) -> List[Dict[str, Any]]:
        """사업장명 목록 조회 (드롭다운용)"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_install_names_db()
        except Exception as e:
            logger.error(f"❌ 사업장명 목록 조회 실패: {str(e)}")
            raise
    
    async def get_install(self, install_id: int) -> Optional[Dict[str, Any]]:
        """특정 사업장 조회"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_install_db(install_id)
        except Exception as e:
            logger.error(f"❌ 사업장 조회 실패: {str(e)}")
            raise
    
    async def update_install(self, install_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """사업장 수정"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._update_install_db(install_id, update_data)
        except Exception as e:
            logger.error(f"❌ 사업장 수정 실패: {str(e)}")
            raise
    
    async def delete_install(self, install_id: int) -> bool:
        """사업장 삭제"""
        try:
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
            logger.error(f"❌ 사업장 목록 조회 실패: {str(e)}")
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
        """데이터베이스에서 사업장 삭제"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM install WHERE id = $1
                """, install_id)
                
                return result != "DELETE 0"
        except Exception as e:
            logger.error(f"❌ 사업장 삭제 실패: {str(e)}")
            raise

# 📦 Product Repository - 제품 데이터 접근
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
from .product_schema import ProductCreateRequest, ProductUpdateRequest

logger = logging.getLogger(__name__)

class ProductRepository:
    """제품 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
            return
        self.pool = None
    
    async def initialize(self):
        """데이터베이스 연결 풀 초기화"""
        if not self.database_url:
            logger.warning("DATABASE_URL이 없어 데이터베이스 초기화를 건너뜁니다.")
            return
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1, max_size=10, command_timeout=30,
                server_settings={'application_name': 'cbam-service-product'}
            )
            logger.info("✅ Product 데이터베이스 연결 풀 생성 성공")
            
            try:
                await self._create_product_table_async()
            except Exception as e:
                logger.warning(f"⚠️ Product 테이블 생성 실패 (기본 기능은 정상): {e}")
                
        except Exception as e:
            logger.error(f"❌ Product 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _create_product_table_async(self):
        """Product 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # product 테이블 존재 확인
                result = await conn.fetchval("""
                    SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'product');
                """)
                
                if not result:
                    logger.info("⚠️ product 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    await conn.execute("""
                        CREATE TABLE product (
                            id SERIAL PRIMARY KEY,
                            install_id INTEGER NOT NULL REFERENCES install(id),
                            product_name TEXT NOT NULL,
                            product_category TEXT NOT NULL,
                            prostart_period DATE NOT NULL,
                            proend_period DATE NOT NULL,
                            product_amount NUMERIC(15,6) NOT NULL DEFAULT 0,
                            cncode_total TEXT,
                            goods_name TEXT,
                            goods_engname TEXT,
                            aggrgoods_name TEXT,
                            aggrgoods_engname TEXT,
                            product_sell NUMERIC(15,6) DEFAULT 0,
                            product_eusell NUMERIC(15,6) DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    logger.info("✅ product 테이블 생성 완료")
                else:
                    logger.info("✅ product 테이블 확인 완료")
                    
        except Exception as e:
            logger.error(f"❌ Product 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")
    
    # ============================================================================
    # 📦 Product 관련 Repository 메서드
    # ============================================================================
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """제품 생성"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._create_product_db(product_data)
        except Exception as e:
            logger.error(f"❌ 제품 생성 실패: {str(e)}")
            raise
    
    async def get_products(self) -> List[Dict[str, Any]]:
        """제품 목록 조회"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_products_db()
        except Exception as e:
            logger.error(f"❌ 제품 목록 조회 실패: {str(e)}")
            raise
    
    async def get_product_names(self) -> List[Dict[str, Any]]:
        """제품명 목록 조회 (드롭다운용)"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_product_names_db()
        except Exception as e:
            logger.error(f"❌ 제품명 목록 조회 실패: {str(e)}")
            raise
    
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """특정 제품 조회"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_product_db(product_id)
        except Exception as e:
            logger.error(f"❌ 제품 조회 실패: {str(e)}")
            raise
    
    async def update_product(self, product_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """제품 수정"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._update_product_db(product_id, update_data)
        except Exception as e:
            logger.error(f"❌ 제품 수정 실패: {str(e)}")
            raise
    
    async def delete_product(self, product_id: int) -> bool:
        """제품 삭제"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        
        try:
            return await self._delete_product_db(product_id)
        except Exception as e:
            logger.error(f"❌ 제품 삭제 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 📦 Product 관련 Private Database 메서드
    # ============================================================================
    
    async def _create_product_db(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 제품 생성"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    INSERT INTO product (
                        install_id, product_name, product_category, 
                        prostart_period, proend_period, product_amount,
                        cncode_total, goods_name, aggrgoods_name,
                        product_sell, product_eusell
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
                    ) RETURNING *
                """, (
                    product_data['install_id'], product_data['product_name'], product_data['product_category'],
                    product_data['prostart_period'], product_data['proend_period'], product_data['product_amount'],
                    product_data['cncode_total'], product_data['goods_name'], product_data['aggrgoods_name'],
                    product_data['product_sell'], product_data['product_eusell']
                ))
                
                if result:
                    product_dict = dict(result)
                    # datetime.date 객체를 문자열로 변환
                    if 'prostart_period' in product_dict and product_dict['prostart_period']:
                        product_dict['prostart_period'] = product_dict['prostart_period'].isoformat()
                    if 'proend_period' in product_dict and product_dict['proend_period']:
                        product_dict['proend_period'] = product_dict['proend_period'].isoformat()
                    return product_dict
                else:
                    raise Exception("제품 생성에 실패했습니다.")
                    
        except Exception as e:
            logger.error(f"❌ 제품 생성 실패: {str(e)}")
            raise
    
    async def _get_products_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 제품 목록 조회"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM product ORDER BY id
                """)
                
                products = []
                for row in results:
                    product_dict = dict(row)
                    # datetime.date 객체를 문자열로 변환
                    if 'prostart_period' in product_dict and product_dict['prostart_period']:
                        product_dict['prostart_period'] = product_dict['prostart_period'].isoformat()
                    if 'proend_period' in product_dict and product_dict['proend_period']:
                        product_dict['proend_period'] = product_dict['proend_period'].isoformat()
                    products.append(product_dict)
                
                return products
                
        except Exception as e:
            logger.error(f"❌ 제품 목록 조회 실패: {str(e)}")
            raise
    
    async def _get_product_names_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 제품명 목록 조회 (드롭다운용)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, product_name FROM product ORDER BY product_name
                """)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 제품명 목록 조회 실패: {str(e)}")
            raise
    
    async def _get_product_db(self, product_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 제품 조회"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM product WHERE id = $1
                """, product_id)
                
                if result:
                    product_dict = dict(result)
                    # datetime.date 객체를 문자열로 변환
                    if 'prostart_period' in product_dict and product_dict['prostart_period']:
                        product_dict['prostart_period'] = product_dict['prostart_period'].isoformat()
                    if 'proend_period' in product_dict and product_dict['proend_period']:
                        product_dict['proend_period'] = product_dict['proend_period'].isoformat()
                    return product_dict
                return None
                
        except Exception as e:
            logger.error(f"❌ 제품 조회 실패: {str(e)}")
            raise
    
    async def _update_product_db(self, product_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 제품 수정"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 동적으로 SET 절 생성
                set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(update_data.keys())])
                values = list(update_data.values()) + [product_id]
                
                query = f"""
                    UPDATE product SET {set_clause} 
                    WHERE id = ${len(update_data) + 1} RETURNING *
                """
                
                result = await conn.fetchrow(query, *values)
                
                if result:
                    product_dict = dict(result)
                    # datetime.date 객체를 문자열로 변환
                    if 'prostart_period' in product_dict and product_dict['prostart_period']:
                        product_dict['prostart_period'] = product_dict['prostart_period'].isoformat()
                    if 'proend_period' in product_dict and product_dict['proend_period']:
                        product_dict['proend_period'] = product_dict['proend_period'].isoformat()
                    return product_dict
                return None
                
        except Exception as e:
            logger.error(f"❌ 제품 수정 실패: {str(e)}")
            raise
    
    async def _delete_product_db(self, product_id: int) -> bool:
        """데이터베이스에서 제품 삭제"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 먼저 해당 제품이 존재하는지 확인
                result = await conn.fetchrow("""
                    SELECT id, product_name FROM product WHERE id = $1
                """, product_id)
                
                if not result:
                    logger.warning(f"⚠️ 제품 ID {product_id}를 찾을 수 없습니다.")
                    return False
                
                logger.info(f"🗑️ 제품 삭제 시작: ID {product_id}, 이름: {result['product_name']}")
                
                # 먼저 해당 제품과 연결된 제품-공정 관계들을 삭제
                deleted_relations = await conn.execute("""
                    DELETE FROM product_process WHERE product_id = $1
                """, product_id)
                
                logger.info(f"🗑️ 연결된 제품-공정 관계 삭제 완료")
                
                # 연결되지 않은 공정들 삭제 (고아 공정)
                deleted_orphan_processes = await conn.execute("""
                    DELETE FROM process 
                    WHERE id NOT IN (
                        SELECT DISTINCT process_id FROM product_process
                    )
                """)
                
                logger.info(f"🗑️ 고아 공정 삭제 완료")
                
                # 그 다음 제품 삭제
                deleted_products = await conn.execute("""
                    DELETE FROM product WHERE id = $1
                """, product_id)
                
                logger.info(f"🗑️ 제품 삭제 완료")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ 제품 삭제 실패: {str(e)}")
            raise
