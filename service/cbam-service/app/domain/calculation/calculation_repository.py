# ============================================================================
# 📦 Calculation Repository - Product 데이터 접근
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .calculation_entity import Edge
from .calculation_schema import EdgeResponse

logger = logging.getLogger(__name__)

class CalculationRepository:
    """Product 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
            # 데이터베이스 URL이 없어도 서비스는 계속 실행
            return
        
        try:
            self._initialize_database()
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            # 초기화 실패해도 서비스는 계속 실행
    
    def _check_database_connection(self) -> bool:
        """데이터베이스 연결 상태 확인"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return False
            
        try:
            import psycopg2
            conn = psycopg2.connect(self.database_url)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            return False

    def _initialize_database(self):
        """데이터베이스 초기화"""
        if not self.database_url:
            logger.warning("DATABASE_URL이 없어 데이터베이스 초기화를 건너뜁니다.")
            return
            
        try:
            import psycopg2
            
            # 데이터베이스 연결 테스트
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            conn.close()
            
            logger.info("✅ 데이터베이스 연결 성공")
            self._create_tables()
            self._create_triggers()  # 트리거 생성 추가
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            # 연결 실패해도 서비스는 계속 실행
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
    
    def _create_triggers(self):
        """자동 집계를 위한 트리거 생성"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                # 1. matdir 테이블 트리거 함수 생성
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION update_process_attrdir_emission_on_matdir_change()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        -- matdir 테이블 변경 시 해당 공정의 직접귀속배출량 자동 업데이트
                        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                            -- 해당 공정의 총 원료직접배출량과 총 연료직접배출량 계산
                            INSERT INTO process_attrdir_emission (process_id, total_matdir_emission, total_fueldir_emission, attrdir_em, calculation_date)
                            SELECT 
                                COALESCE(NEW.process_id, OLD.process_id) as process_id,
                                COALESCE(SUM(m.matdir_em), 0) as total_matdir_emission,
                                COALESCE(SUM(f.fueldir_em), 0) as total_fueldir_emission,
                                COALESCE(SUM(m.matdir_em), 0) + COALESCE(SUM(f.fueldir_em), 0) as attrdir_em,
                                NOW() as calculation_date
                            FROM (SELECT DISTINCT process_id FROM matdir WHERE process_id = COALESCE(NEW.process_id, OLD.process_id)) p
                            LEFT JOIN matdir m ON p.process_id = m.process_id
                            LEFT JOIN fueldir f ON p.process_id = f.process_id
                            GROUP BY p.process_id
                            ON CONFLICT (process_id) 
                            DO UPDATE SET 
                                total_matdir_emission = EXCLUDED.total_matdir_emission,
                                total_fueldir_emission = EXCLUDED.total_fueldir_emission,
                                attrdir_em = EXCLUDED.attrdir_em,
                                calculation_date = NOW(),
                                updated_at = NOW();
                        ELSIF TG_OP = 'DELETE' THEN
                            -- 삭제 시에도 해당 공정의 직접귀속배출량 업데이트
                            INSERT INTO process_attrdir_emission (process_id, total_matdir_emission, total_fueldir_emission, attrdir_em, calculation_date)
                            SELECT 
                                OLD.process_id as process_id,
                                COALESCE(SUM(m.matdir_em), 0) as total_matdir_emission,
                                COALESCE(SUM(f.fueldir_em), 0) as total_fueldir_emission,
                                COALESCE(SUM(m.matdir_em), 0) + COALESCE(SUM(f.fueldir_em), 0) as attrdir_em,
                                NOW() as calculation_date
                            FROM (SELECT DISTINCT process_id FROM matdir WHERE process_id = OLD.process_id) p
                            LEFT JOIN matdir m ON p.process_id = m.process_id
                            LEFT JOIN fueldir f ON p.process_id = f.process_id
                            GROUP BY p.process_id
                            ON CONFLICT (process_id) 
                            DO UPDATE SET 
                                total_matdir_emission = EXCLUDED.total_matdir_emission,
                                total_fueldir_emission = EXCLUDED.total_fueldir_emission,
                                attrdir_em = EXCLUDED.attrdir_em,
                                calculation_date = NOW(),
                                updated_at = NOW();
                        END IF;
                        
                        RETURN COALESCE(NEW, OLD);
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                # 2. fueldir 테이블 트리거 함수 생성
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION update_process_attrdir_emission_on_fueldir_change()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        -- fueldir 테이블 변경 시 해당 공정의 직접귀속배출량 자동 업데이트
                        IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                            -- 해당 공정의 총 원료직접배출량과 총 연료직접배출량 계산
                            INSERT INTO process_attrdir_emission (process_id, total_matdir_emission, total_fueldir_emission, attrdir_em, calculation_date)
                            SELECT 
                                COALESCE(NEW.process_id, OLD.process_id) as process_id,
                                COALESCE(SUM(m.matdir_em), 0) as total_matdir_emission,
                                COALESCE(SUM(f.fueldir_em), 0) as total_fueldir_emission,
                                COALESCE(SUM(m.matdir_em), 0) + COALESCE(SUM(f.fueldir_em), 0) as attrdir_em,
                                NOW() as calculation_date
                            FROM (SELECT DISTINCT process_id FROM fueldir WHERE process_id = COALESCE(NEW.process_id, OLD.process_id)) p
                            LEFT JOIN matdir m ON p.process_id = m.process_id
                            LEFT JOIN fueldir f ON p.process_id = f.process_id
                            GROUP BY p.process_id
                            ON CONFLICT (process_id) 
                            DO UPDATE SET 
                                total_matdir_emission = EXCLUDED.total_matdir_emission,
                                total_fueldir_emission = EXCLUDED.total_fueldir_emission,
                                attrdir_em = EXCLUDED.attrdir_em,
                                calculation_date = NOW(),
                                updated_at = NOW();
                        ELSIF TG_OP = 'DELETE' THEN
                            -- 삭제 시에도 해당 공정의 직접귀속배출량 업데이트
                            INSERT INTO process_attrdir_emission (process_id, total_matdir_emission, total_fueldir_emission, attrdir_em, calculation_date)
                            SELECT 
                                OLD.process_id as process_id,
                                COALESCE(SUM(m.matdir_em), 0) as total_matdir_emission,
                                COALESCE(SUM(f.fueldir_em), 0) as total_fueldir_emission,
                                COALESCE(SUM(m.matdir_em), 0) + COALESCE(SUM(f.fueldir_em), 0) as attrdir_em,
                                NOW() as calculation_date
                            FROM (SELECT DISTINCT process_id FROM fueldir WHERE process_id = OLD.process_id) p
                            LEFT JOIN matdir m ON p.process_id = m.process_id
                            LEFT JOIN fueldir f ON p.process_id = f.process_id
                            GROUP BY p.process_id
                            ON CONFLICT (process_id) 
                            DO UPDATE SET 
                                total_matdir_emission = EXCLUDED.total_matdir_emission,
                                total_fueldir_emission = EXCLUDED.total_fueldir_emission,
                                attrdir_em = EXCLUDED.attrdir_em,
                                calculation_date = NOW(),
                                updated_at = NOW();
                        END IF;
                        
                        RETURN COALESCE(NEW, OLD);
                    END;
                    $$ LANGUAGE plpgsql;
                """)
                
                # 3. matdir 테이블에 트리거 생성
                cursor.execute("""
                    DROP TRIGGER IF EXISTS trigger_update_process_attrdir_emission_on_matdir ON matdir;
                    CREATE TRIGGER trigger_update_process_attrdir_emission_on_matdir
                    AFTER INSERT OR UPDATE OR DELETE ON matdir
                    FOR EACH ROW EXECUTE FUNCTION update_process_attrdir_emission_on_matdir_change();
                """)
                
                # 4. fueldir 테이블에 트리거 생성
                cursor.execute("""
                    DROP TRIGGER IF EXISTS trigger_update_process_attrdir_emission_on_fueldir ON fueldir;
                    CREATE TRIGGER trigger_update_process_attrdir_emission_on_fueldir
                    AFTER INSERT OR UPDATE OR DELETE ON fueldir
                    FOR EACH ROW EXECUTE FUNCTION update_process_attrdir_emission_on_fueldir_change();
                """)
                
                conn.commit()
                logger.info("✅ 자동 집계 트리거 생성 완료")
                
        except Exception as e:
            logger.error(f"❌ 트리거 생성 실패: {str(e)}")
            raise
        finally:
            conn.close()

    def _create_tables(self):
        """필요한 테이블들을 생성합니다"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                # 1. install 테이블 생성
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'install'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.info("⚠️ install 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    cursor.execute("""
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
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'product'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.info("⚠️ product 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    cursor.execute("""
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
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'process'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.info("⚠️ process 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    cursor.execute("""
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
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'product_process'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.info("⚠️ product_process 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    cursor.execute("""
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
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'edge'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.info("⚠️ edge 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    cursor.execute("""
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
                
                # 6. process_attrdir_emission 테이블 생성 (새로 추가)
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'process_attrdir_emission'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.info("⚠️ process_attrdir_emission 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    cursor.execute("""
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
                
                conn.commit()
                logger.info("✅ 모든 데이터베이스 테이블 확인/생성 완료")
                
        except Exception as e:
            logger.error(f"❌ 테이블 생성 실패: {str(e)}")
            raise
        finally:
            conn.close()

    # ============================================================================
    # 📦 Product 관련 메서드
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
        
        if not self._check_database_connection():
            raise Exception("데이터베이스 연결에 실패했습니다.")
            
        try:
            return await self._delete_product_db(product_id)
        except Exception as e:
            logger.error(f"❌ 제품 삭제 실패: {str(e)}")
            raise

    # ============================================================================
    # 🏭 Install 관련 메서드
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
    # 🔄 Process 관련 메서드
    # ============================================================================
    
    async def create_process(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """프로세스 생성"""
        try:
            return await self._create_process_db(process_data)
        except Exception as e:
            logger.error(f"❌ 프로세스 생성 실패: {str(e)}")
            raise
    
    async def get_processes(self) -> List[Dict[str, Any]]:
        """프로세스 목록 조회"""
        try:
            return await self._get_processes_db()
        except Exception as e:
            logger.error(f"❌ 프로세스 목록 조회 실패: {str(e)}")
            raise
    
    async def get_process(self, process_id: int) -> Optional[Dict[str, Any]]:
        """특정 프로세스 조회"""
        try:
            return await self._get_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 프로세스 조회 실패: {str(e)}")
            raise
    
    async def update_process(self, process_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """프로세스 수정"""
        try:
            return await self._update_process_db(process_id, update_data)
        except Exception as e:
            logger.error(f"❌ 프로세스 수정 실패: {str(e)}")
            raise
    
    async def delete_process(self, process_id: int) -> bool:
        """프로세스 삭제"""
        try:
            return await self._delete_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 프로세스 삭제 실패: {str(e)}")
            raise
    


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
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO edge (source_id, target_id, edge_kind, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    edge_data['source_id'],
                    edge_data['target_id'],
                    edge_data['edge_kind'],
                    datetime.utcnow(),
                    datetime.utcnow()
                ))
                
                result = cursor.fetchone()
                conn.commit()
                
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ Edge 생성 실패: {e}")
            raise e
        finally:
            conn.close()

    async def get_edges(self) -> List[Dict]:
        """모든 Edge 조회"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM edge ORDER BY id
                """)
                
                results = cursor.fetchall()
                edges = [dict(row) for row in results]
                return edges
                
        except Exception as e:
            logger.error(f"❌ Edge 목록 조회 실패: {e}")
            raise e
        finally:
            conn.close()

    async def delete_edge(self, edge_id: int) -> bool:
        """Edge 삭제"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM edge WHERE id = %s
                """, (edge_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ Edge 삭제 실패: {e}")
            raise e
        finally:
            conn.close()

    # ============================================================================
    # 🔗 통합 공정 그룹 관련 Repository 메서드
    # ============================================================================

    async def get_process_chains_by_process_ids(self, process_ids: List[int]) -> List[Dict]:
        """공정 ID들로 통합 그룹 조회"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # process_chain_link 테이블을 통해 공정이 포함된 그룹들 조회
                cursor.execute("""
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
                    WHERE pcl.process_id = ANY(%s)
                    ORDER BY pc.id
                """, (process_ids,))
                
                chains = cursor.fetchall()
                
                # 각 그룹에 포함된 공정 목록도 함께 조회
                chain_list = []
                for chain in chains:
                    chain_dict = dict(chain)
                    chain_dict['processes'] = []
                    
                    # 해당 그룹에 포함된 공정 목록 조회
                    cursor.execute("""
                        SELECT process_id, sequence_order
                        FROM process_chain_link
                        WHERE chain_id = %s
                        ORDER BY sequence_order
                    """, (chain_dict['id'],))
                    
                    process_links = cursor.fetchall()
                    chain_dict['processes'] = [link['process_id'] for link in process_links]
                    chain_list.append(chain_dict)
                
                return chain_list
                
        except Exception as e:
            logger.error(f"❌ 공정 ID로 통합 그룹 조회 실패: {e}")
            raise e
        finally:
            conn.close()

    async def create_process_chain(self, chain_data: Dict) -> Dict:
        """통합 공정 그룹 생성"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # process_chain 테이블에 그룹 정보 저장
                cursor.execute("""
                    INSERT INTO process_chain 
                    (chain_name, start_process_id, end_process_id, chain_length, is_active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                
                chain = cursor.fetchone()
                conn.commit()
                
                return dict(chain)
                
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 생성 실패: {e}")
            raise e
        finally:
            conn.close()

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
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                # 그룹 내 모든 공정의 배출량 합계 계산
                cursor.execute("""
                    SELECT COALESCE(SUM(attrdir_em), 0) as total_emission
                    FROM process_attrdir_emission pae
                    INNER JOIN process_chain_link pcl ON pae.process_id = pcl.process_id
                    WHERE pcl.chain_id = %s
                """, (chain_id,))
                
                result = cursor.fetchone()
                total_emission = result[0] if result else 0
                
                return float(total_emission)
                
        except Exception as e:
            logger.error(f"❌ 통합 그룹 배출량 계산 실패: {e}")
            raise e
        finally:
            conn.close()

    # ============================================================================
    # 🏭 Install 관련 Repository 메서드 (누락된 메서드들 추가)
    # ============================================================================

    async def _create_install_db(self, install_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 사업장 생성"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        INSERT INTO install (install_name, reporting_year)
                        VALUES (%s, %s)
                        RETURNING *
                    """, (install_data['install_name'], install_data['reporting_year']))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
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
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def _get_installs_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 사업장 목록 조회"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, install_name, reporting_year, created_at, updated_at
                        FROM install
                        ORDER BY created_at DESC
                    """)
                    
                    results = cursor.fetchall()
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
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def _get_install_names_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 사업장명 목록 조회 (드롭다운용)"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, install_name
                        FROM install
                        ORDER BY install_name ASC
                    """)
                    
                    results = cursor.fetchall()
                    return [dict(result) for result in results]
                    
            except Exception as e:
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def _get_install_db(self, install_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 사업장 조회"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT id, install_name, reporting_year, created_at, updated_at
                        FROM install
                        WHERE id = %s
                    """, (install_id,))
                    
                    result = cursor.fetchone()
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
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def _update_install_db(self, install_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 사업장 수정"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 동적으로 SET 절 생성
                    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
                    values = list(update_data.values()) + [install_id]
                    
                    cursor.execute(f"""
                        UPDATE install SET {set_clause}, updated_at = NOW()
                        WHERE id = %s RETURNING *
                    """, values)
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
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
                conn.rollback()
                raise e
            finally:
                conn.close()

    async def _delete_install_db(self, install_id: int) -> bool:
        """데이터베이스에서 사업장 삭제"""
        try:
            import psycopg2

            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM install WHERE id = %s
                    """, (install_id,))

                    conn.commit()
                    return cursor.rowcount > 0

            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    # ============================================================================
    # 📦 Product 관련 Repository 메서드
    # ============================================================================

    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 제품 생성"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO product (
                        install_id, product_name, product_category, 
                        prostart_period, proend_period, product_amount,
                        cncode_total, goods_name, aggrgoods_name,
                        product_sell, product_eusell
                    ) VALUES (
                        %(install_id)s, %(product_name)s, %(product_category)s,
                        %(prostart_period)s, %(proend_period)s, %(product_amount)s,
                        %(cncode_total)s, %(goods_name)s, %(aggrgoods_name)s,
                        %(product_sell)s, %(product_eusell)s
                    ) RETURNING *
                """, product_data)
                
                result = cursor.fetchone()
                conn.commit()
                
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
            conn.rollback()
            raise e
        finally:
            conn.close()

    async def get_products(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 제품 목록 조회"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM product ORDER BY id
                """)
                
                results = cursor.fetchall()
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
            raise e
        finally:
            conn.close()

    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 제품 조회"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM product WHERE id = %s
                """, (product_id,))
                
                result = cursor.fetchone()
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
            raise e
        finally:
            conn.close()

    async def update_product(self, product_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 제품 수정"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 동적으로 SET 절 생성
                set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
                values = list(update_data.values()) + [product_id]
                
                cursor.execute(f"""
                    UPDATE product SET {set_clause} 
                    WHERE id = %s RETURNING *
                """, values)
                
                result = cursor.fetchone()
                conn.commit()
                
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
            conn.rollback()
            raise e
        finally:
            conn.close()

    async def delete_product(self, product_id: int) -> bool:
        """데이터베이스에서 제품 삭제"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor() as cursor:
                    # 먼저 해당 제품이 존재하는지 확인
                    cursor.execute("""
                        SELECT id, product_name FROM product WHERE id = %s
                    """, (product_id,))
                    
                    product = cursor.fetchone()
                    if not product:
                        logger.warning(f"⚠️ 제품 ID {product_id}를 찾을 수 없습니다.")
                        return False
                    
                    logger.info(f"🗑️ 제품 삭제 시작: ID {product_id}, 이름: {product[1]}")
                    
                    # 먼저 해당 제품과 연결된 제품-공정 관계들을 삭제
                    cursor.execute("""
                        DELETE FROM product_process WHERE product_id = %s
                    """, (product_id,))
                    
                    deleted_relations = cursor.rowcount
                    logger.info(f"🗑️ 연결된 제품-공정 관계 {deleted_relations}개 삭제 완료")
                    
                    # 연결되지 않은 공정들 삭제 (고아 공정)
                    cursor.execute("""
                        DELETE FROM process 
                        WHERE id NOT IN (
                            SELECT DISTINCT process_id FROM product_process
                        )
                    """)
                    
                    deleted_orphan_processes = cursor.rowcount
                    logger.info(f"🗑️ 고아 공정 {deleted_orphan_processes}개 삭제 완료")
                    
                    # 그 다음 제품 삭제
                    cursor.execute("""
                        DELETE FROM product WHERE id = %s
                    """, (product_id,))
                    
                    deleted_products = cursor.rowcount
                    logger.info(f"🗑️ 제품 {deleted_products}개 삭제 완료")
                    
                    conn.commit()
                    return deleted_products > 0
                    
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ 제품 삭제 중 오류 발생: {str(e)}")
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    # ============================================================================
    # 🔄 Process 관련 Repository 메서드
    # ============================================================================

    async def create_process(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 공정 생성 (다대다 관계)"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 1. 공정 생성
                    cursor.execute("""
                        INSERT INTO process (
                            process_name, start_period, end_period
                        ) VALUES (
                            %(process_name)s, %(start_period)s, %(end_period)s
                        ) RETURNING *
                    """, process_data)
                    
                    process_result = cursor.fetchone()
                    if not process_result:
                        raise Exception("공정 생성에 실패했습니다.")
                    
                    process_dict = dict(process_result)
                    process_id = process_dict['id']
                    
                    # 2. 제품-공정 관계 생성 (다대다 관계)
                    if 'product_ids' in process_data and process_data['product_ids']:
                        for product_id in process_data['product_ids']:
                            cursor.execute("""
                                INSERT INTO product_process (product_id, process_id)
                                VALUES (%s, %s)
                                ON CONFLICT (product_id, process_id) DO NOTHING
                            """, (product_id, process_id))
                    
                    conn.commit()
                    
                    # 3. 생성된 공정 정보 반환 (제품 정보 포함)
                    return await self._get_process_with_products_db(process_id)
                    
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def get_processes(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 프로세스 목록 조회 (다대다 관계)"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 모든 공정 조회
                    cursor.execute("""
                        SELECT id, process_name, start_period, end_period, created_at, updated_at
                        FROM process
                        ORDER BY id
                    """)
                    
                    processes = cursor.fetchall()
                    result = []
                    
                    for process in processes:
                        process_dict = dict(process)
                        
                        # 해당 공정과 연결된 제품들 조회
                        cursor.execute("""
                            SELECT p.id, p.install_id, p.product_name, p.product_category, 
                                   p.prostart_period, p.proend_period, p.product_amount,
                                   p.cncode_total, p.goods_name, p.aggrgoods_name,
                                   p.product_sell, p.product_eusell, p.created_at, p.updated_at
                            FROM product p
                            JOIN product_process pp ON p.id = pp.product_id
                            WHERE pp.process_id = %s
                        """, (process_dict['id'],))
                        
                        products = cursor.fetchall()
                        process_dict['products'] = [dict(product) for product in products]
                        
                        # datetime.date 객체를 문자열로 변환
                        if 'start_period' in process_dict and process_dict['start_period']:
                            process_dict['start_period'] = process_dict['start_period'].isoformat()
                        if 'end_period' in process_dict and process_dict['end_period']:
                            process_dict['end_period'] = process_dict['end_period'].isoformat()
                        
                        # 제품들의 날짜도 변환
                        for product in process_dict['products']:
                            if 'prostart_period' in product and product['prostart_period']:
                                product['prostart_period'] = product['prostart_period'].isoformat()
                            if 'proend_period' in product and product['proend_period']:
                                product['proend_period'] = product['proend_period'].isoformat()
                        
                        result.append(process_dict)
                    
                    return result
                    
            except Exception as e:
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def get_process(self, process_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 프로세스 조회"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM process WHERE id = %s
                    """, (process_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        process_dict = dict(result)
                        # datetime.date 객체를 문자열로 변환
                        if 'start_period' in process_dict and process_dict['start_period']:
                            process_dict['start_period'] = process_dict['start_period'].isoformat()
                        if 'end_period' in process_dict and process_dict['end_period']:
                            process_dict['end_period'] = process_dict['end_period'].isoformat()
                        return process_dict
                    return None
                    
            except Exception as e:
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def update_process(self, process_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 프로세스 수정"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 동적으로 SET 절 생성
                    set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
                    values = list(update_data.values()) + [process_id]
                    
                    cursor.execute(f"""
                        UPDATE process SET {set_clause} 
                        WHERE id = %s RETURNING *
                    """, values)
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        process_dict = dict(result)
                        # datetime.date 객체를 문자열로 변환
                        if 'start_period' in process_dict and process_dict['start_period']:
                            process_dict['start_period'] = process_dict['start_period'].isoformat()
                        if 'end_period' in process_dict and process_dict['end_period']:
                            process_dict['end_period'] = process_dict['end_period'].isoformat()
                        return process_dict
                    return None
                    
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def delete_process(self, process_id: int) -> bool:
        """데이터베이스에서 프로세스 삭제 (다대다 관계 지원)"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            try:
                with conn.cursor() as cursor:
                    # 1. 해당 공정과 연결된 제품-공정 관계 삭제
                    cursor.execute("""
                        DELETE FROM product_process WHERE process_id = %s
                    """, (process_id,))
                    
                    deleted_relations = cursor.rowcount
                    logger.info(f"🗑️ 공정 {process_id}의 제품-공정 관계 {deleted_relations}개 삭제 완료")
                    
                    # 2. 마지막으로 공정 삭제
                    cursor.execute("""
                        DELETE FROM process WHERE id = %s
                    """, (process_id,))
                    
                    conn.commit()
                    deleted = cursor.rowcount > 0
                    
                    if deleted:
                        logger.info(f"✅ 공정 {process_id} 삭제 성공")
                    else:
                        logger.warning(f"⚠️ 공정 {process_id}를 찾을 수 없음")
                    
                    return deleted
                    
            except Exception as e:
                conn.rollback()
                logger.error(f"❌ 공정 삭제 중 오류 발생: {str(e)}")
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

    async def _get_process_with_products_db(self, process_id: int) -> Dict[str, Any]:
        """데이터베이스에서 공정과 연결된 제품들 조회"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 1. 공정 정보 조회
                    cursor.execute("""
                        SELECT id, process_name, start_period, end_period, created_at, updated_at
                        FROM process WHERE id = %s
                    """, (process_id,))
                    
                    process_result = cursor.fetchone()
                    if not process_result:
                        raise Exception("공정을 찾을 수 없습니다.")
                    
                    process_dict = dict(process_result)
                    
                    # datetime.date 객체를 문자열로 변환
                    if 'start_period' in process_dict and process_dict['start_period']:
                        process_dict['start_period'] = process_dict['start_period'].isoformat()
                    if 'end_period' in process_dict and process_dict['end_period']:
                        process_dict['end_period'] = process_dict['end_period'].isoformat()
                    
                    # 2. 관련된 제품들 조회
                    cursor.execute("""
                        SELECT p.id, p.install_id, p.product_name, p.product_category, 
                               p.prostart_period, p.proend_period, p.product_amount,
                               p.cncode_total, p.goods_name, p.aggrgoods_name,
                               p.product_sell, p.product_eusell, p.created_at, p.updated_at
                        FROM product p
                        JOIN product_process pp ON p.id = pp.product_id
                        WHERE pp.process_id = %s
                    """, (process_id,))
                    
                    products = cursor.fetchall()
                    process_dict['products'] = []
                    
                    for product in products:
                        product_dict = dict(product)
                        # datetime.date 객체를 문자열로 변환
                        if 'prostart_period' in product_dict and product_dict['prostart_period']:
                            product_dict['prostart_period'] = product_dict['prostart_period'].isoformat()
                        if 'proend_period' in product_dict and product_dict['proend_period']:
                            product_dict['proend_period'] = product_dict['proend_period'].isoformat()
                        process_dict['products'].append(product_dict)
                    
                    return process_dict
                    
            except Exception as e:
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            raise e

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