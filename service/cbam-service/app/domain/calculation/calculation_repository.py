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
    # 🗄️ Database 메서드들
    # ============================================================================
    
    async def _create_product_db(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 제품 생성"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
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

    async def _create_install_db(self, install_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 사업장 생성"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO install (
                        install_name, reporting_year
                    ) VALUES (
                        %(install_name)s, %(reporting_year)s
                    ) RETURNING *
                """, install_data)
                
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    install_dict = dict(result)
                    return install_dict
                else:
                    raise Exception("사업장 생성에 실패했습니다.")
                    
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    async def _get_installs_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 사업장 목록 조회"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM install ORDER BY id
                """)
                
                results = cursor.fetchall()
                installs = []
                for row in results:
                    install_dict = dict(row)
                    installs.append(install_dict)
                
                return installs
                
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    async def _get_install_names_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 사업장명 목록 조회 (드롭다운용)"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, install_name FROM install ORDER BY install_name
                """)
                
                results = cursor.fetchall()
                install_names = []
                for row in results:
                    install_names.append(dict(row))
                
                return install_names
                
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    async def _get_install_db(self, install_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 사업장 조회"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM install WHERE id = %s
                """, (install_id,))
                
                result = cursor.fetchone()
                if result:
                    install_dict = dict(result)
                    return install_dict
                return None
                
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    async def _update_install_db(self, install_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 사업장 수정"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 동적으로 SET 절 생성
                set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
                values = list(update_data.values()) + [install_id]
                
                cursor.execute(f"""
                    UPDATE install SET {set_clause} 
                    WHERE id = %s RETURNING *
                """, values)
                
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    install_dict = dict(result)
                    return install_dict
                return None
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    async def _delete_install_db(self, install_id: int) -> bool:
        """데이터베이스에서 사업장 삭제 (연결된 제품들도 함께 삭제) - 다대다 관계 지원"""
        import psycopg2

        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            with conn.cursor() as cursor:
                # 1. 해당 사업장의 제품들과 연결된 공정들의 프로세스 입력 데이터 삭제
                cursor.execute("""
                    DELETE FROM process_input 
                    WHERE process_id IN (
                        SELECT DISTINCT pp.process_id 
                        FROM product_process pp
                        JOIN product p ON pp.product_id = p.id 
                        WHERE p.install_id = %s
                    )
                """, (install_id,))
                logger.info(f"🗑️ 사업장 {install_id}의 프로세스 입력 데이터 삭제 완료")

                # 2. 해당 사업장의 제품들과 연결된 제품-공정 관계 삭제
                cursor.execute("""
                    DELETE FROM product_process 
                    WHERE product_id IN (
                        SELECT id FROM product WHERE install_id = %s
                    )
                """, (install_id,))
                logger.info(f"🗑️ 사업장 {install_id}의 제품-공정 관계 삭제 완료")

                # 3. 해당 사업장의 제품들과 연결되지 않은 공정들 삭제 (고아 공정)
                cursor.execute("""
                    DELETE FROM process 
                    WHERE id NOT IN (
                        SELECT DISTINCT process_id FROM product_process
                    )
                """)
                logger.info(f"🗑️ 고아 공정들 삭제 완료")

                # 4. 해당 사업장의 제품들 삭제
                cursor.execute("""
                    DELETE FROM product WHERE install_id = %s
                """, (install_id,))
                logger.info(f"🗑️ 사업장 {install_id}의 제품들 삭제 완료")

                # 5. 마지막으로 사업장 삭제
                cursor.execute("""
                    DELETE FROM install WHERE id = %s
                """, (install_id,))

                conn.commit()
                deleted = cursor.rowcount > 0
                
                if deleted:
                    logger.info(f"✅ 사업장 {install_id} 삭제 성공")
                else:
                    logger.warning(f"⚠️ 사업장 {install_id}를 찾을 수 없음")
                
                return deleted

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ 사업장 삭제 중 오류 발생: {str(e)}")
            raise e
        finally:
            conn.close()

    # ============================================================================
    # 🔄 Process Database 메서드들
    # ============================================================================
    
    async def _create_process_db(self, process_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 공정 생성 (다대다 관계)"""
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
    
    async def _get_processes_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 프로세스 목록 조회 (다대다 관계)"""
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
    
    async def _get_process_db(self, process_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 프로세스 조회"""
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
    
    async def _update_process_db(self, process_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 프로세스 수정"""
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
    
    async def _delete_process_db(self, process_id: int) -> bool:
        """데이터베이스에서 프로세스 삭제 (다대다 관계 지원)"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor() as cursor:
                # 1. 먼저 해당 공정의 프로세스 입력 데이터 삭제
                cursor.execute("""
                    DELETE FROM process_input WHERE process_id = %s
                """, (process_id,))
                
                deleted_inputs = cursor.rowcount
                logger.info(f"🗑️ 공정 {process_id}의 프로세스 입력 {deleted_inputs}개 삭제 완료")
                
                # 2. 해당 공정과 연결된 제품-공정 관계 삭제
                cursor.execute("""
                    DELETE FROM product_process WHERE process_id = %s
                """, (process_id,))
                
                deleted_relations = cursor.rowcount
                logger.info(f"🗑️ 공정 {process_id}의 제품-공정 관계 {deleted_relations}개 삭제 완료")
                
                # 3. 마지막으로 공정 삭제
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
    
    async def _get_products_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 제품 목록 조회"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
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
    
    async def _get_product_names_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 제품명 목록 조회 (드롭다운용)"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, product_name FROM product ORDER BY product_name
                """)
                
                results = cursor.fetchall()
                product_names = []
                for row in results:
                    product_names.append(dict(row))
                
                return product_names
                
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    async def _get_product_db(self, product_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 제품 조회"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
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
    
    async def _update_product_db(self, product_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 제품 수정"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
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
    
    async def _delete_product_db(self, product_id: int) -> bool:
        """데이터베이스에서 제품 삭제"""
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

    # ============================================================================
    # 📥 ProcessInput Database 메서드들




    async def _get_processes_by_product_db(self, product_id: int) -> List[Dict[str, Any]]:
        """데이터베이스에서 특정 제품의 공정 목록 조회 (다대다 관계)"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 특정 제품과 연결된 모든 공정 조회
                cursor.execute("""
                    SELECT pr.id, pr.process_name, pr.start_period, pr.end_period, 
                           pr.created_at, pr.updated_at
                    FROM process pr
                    JOIN product_process pp ON pr.id = pp.process_id
                    WHERE pp.product_id = %s
                    ORDER BY pr.id
                """, (product_id,))
                
                processes = cursor.fetchall()
                result = []
                
                for process in processes:
                    process_dict = dict(process)
                    
                    # datetime.date 객체를 문자열로 변환
                    if 'start_period' in process_dict and process_dict['start_period']:
                        process_dict['start_period'] = process_dict['start_period'].isoformat()
                    if 'end_period' in process_dict and process_dict['end_period']:
                        process_dict['end_period'] = process_dict['end_period'].isoformat()
                    
                    # 해당 공정과 연결된 모든 제품들 조회
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
                    process_dict['products'] = []
                    
                    for product in products:
                        product_dict = dict(product)
                        # datetime.date 객체를 문자열로 변환
                        if 'prostart_period' in product_dict and product_dict['prostart_period']:
                            product_dict['prostart_period'] = product_dict['prostart_period'].isoformat()
                        if 'proend_period' in product_dict and product_dict['proend_period']:
                            product_dict['proend_period'] = product_dict['proend_period'].isoformat()
                        process_dict['products'].append(product_dict)
                    
                    result.append(process_dict)
                
                return result
                    
        except Exception as e:
            raise e
        finally:
            conn.close()

    # ============================================================================
    # 📊 배출량 계산 관련 메서드들
    # ============================================================================
    
    async def calculate_process_attrdir_emission(self, process_id: int) -> Dict[str, Any]:
        """공정별 직접귀속배출량 계산 및 저장"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from decimal import Decimal
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 1. 공정 정보 조회
                cursor.execute("""
                    SELECT id, process_name FROM process WHERE id = %s
                """, (process_id,))
                
                process = cursor.fetchone()
                if not process:
                    raise Exception(f"공정 ID {process_id}를 찾을 수 없습니다.")
                
                # 2. 해당 공정의 총 원료직접배출량 조회
                cursor.execute("""
                    SELECT COALESCE(SUM(matdir_em), 0) as total_matdir_emission
                    FROM matdir WHERE process_id = %s
                """, (process_id,))
                
                matdir_result = cursor.fetchone()
                total_matdir_emission = Decimal(str(matdir_result['total_matdir_emission'])) if matdir_result else Decimal('0')
                
                # 3. 해당 공정의 총 연료직접배출량 조회
                cursor.execute("""
                    SELECT COALESCE(SUM(fueldir_em), 0) as total_fueldir_emission
                    FROM fueldir WHERE process_id = %s
                """, (process_id,))
                
                fueldir_result = cursor.fetchone()
                total_fueldir_emission = Decimal(str(fueldir_result['total_fueldir_emission'])) if fueldir_result else Decimal('0')
                
                # 4. 직접귀속배출량 계산
                attrdir_em = total_matdir_emission + total_fueldir_emission
                
                # 5. process_attrdir_emission 테이블에 저장 또는 업데이트
                cursor.execute("""
                    INSERT INTO process_attrdir_emission 
                    (process_id, total_matdir_emission, total_fueldir_emission, attrdir_em, calculation_date)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (process_id) 
                    DO UPDATE SET 
                        total_matdir_emission = EXCLUDED.total_matdir_emission,
                        total_fueldir_emission = EXCLUDED.total_fueldir_emission,
                        attrdir_em = EXCLUDED.attrdir_em,
                        calculation_date = NOW(),
                        updated_at = NOW()
                    RETURNING id, process_id, total_matdir_emission, total_fueldir_emission, 
                              attrdir_em, calculation_date, created_at, updated_at
                """, (process_id, total_matdir_emission, total_fueldir_emission, attrdir_em))
                
                result = cursor.fetchone()
                conn.commit()
                
                logger.info(f"✅ 공정 {process_id} 직접귀속배출량 계산 완료: attrdir_em = {attrdir_em}")
                
                return dict(result) if result else {}
                
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ 공정별 배출량 요약 계산 중 오류: {str(e)}")
            raise e
        finally:
            conn.close()
    
    async def get_process_attrdir_emission(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정별 직접귀속배출량 조회"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, process_id, total_matdir_emission, total_fueldir_emission, 
                           attrdir_em, calculation_date, created_at, updated_at
                    FROM process_attrdir_emission 
                    WHERE process_id = %s
                """, (process_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ 공정별 배출량 요약 조회 중 오류: {str(e)}")
            raise e
        finally:
            conn.close()
    
    async def get_all_process_attrdir_emissions(self) -> List[Dict[str, Any]]:
        """모든 공정별 직접귀속배출량 조회"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT pae.id, pae.process_id, pae.total_matdir_emission, 
                           pae.total_fueldir_emission, pae.attrdir_em, 
                           pae.calculation_date, pae.created_at, pae.updated_at
                    FROM process_attrdir_emission pae
                    ORDER BY pae.process_id
                """)
                
                results = cursor.fetchall()
                return [dict(result) for result in results]
                
        except Exception as e:
            logger.error(f"❌ 모든 공정별 배출량 요약 조회 중 오류: {str(e)}")
            raise e
        finally:
            conn.close()
    
    async def calculate_product_total_emission(self, product_id: int) -> Dict[str, Any]:
        """제품별 총 배출량 계산"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from decimal import Decimal
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 1. 제품 정보 조회
                cursor.execute("""
                    SELECT id, product_name FROM product WHERE id = %s
                """, (product_id,))
                
                product = cursor.fetchone()
                if not product:
                    raise Exception(f"제품 ID {product_id}를 찾을 수 없습니다.")
                
                # 2. 해당 제품과 연결된 모든 공정의 배출량 합계 계산
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(pae.attrdir_em), 0) as total_emission,
                        COUNT(pae.process_id) as process_count
                    FROM product_process pp
                    LEFT JOIN process_attrdir_emission pae ON pp.process_id = pae.process_id
                    WHERE pp.product_id = %s
                """, (product_id,))
                
                result = cursor.fetchone()
                total_emission = Decimal(str(result['total_emission'])) if result else Decimal('0')
                process_count = result['process_count'] if result else 0
                
                # 3. 각 공정별 배출량 상세 정보 조회
                cursor.execute("""
                    SELECT 
                        p.id as process_id,
                        p.process_name,
                        COALESCE(pae.total_matdir_emission, 0) as total_matdir_emission,
                        COALESCE(pae.total_fueldir_emission, 0) as total_fueldir_emission,
                        COALESCE(pae.attrdir_em, 0) as attrdir_em
                    FROM product_process pp
                    JOIN process p ON pp.process_id = p.id
                    LEFT JOIN process_attrdir_emission pae ON pp.process_id = pae.process_id
                    WHERE pp.product_id = %s
                    ORDER BY p.id
                """, (product_id,))
                
                process_emissions = cursor.fetchall()
                
                return {
                    "product_id": product_id,
                    "product_name": product['product_name'],
                    "total_emission": float(total_emission),
                    "process_count": process_count,
                    "process_emissions": [dict(pe) for pe in process_emissions]
                }
                
        except Exception as e:
            logger.error(f"❌ 제품별 총 배출량 계산 중 오류: {str(e)}")
            raise e
        finally:
            conn.close()

    async def _get_process_with_products_db(self, process_id: int) -> Dict[str, Any]:
        """데이터베이스에서 특정 프로세스와 관련된 제품 목록을 함께 조회"""
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

    async def _create_product_process_db(self, product_process_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 제품-공정 관계 생성"""
        import psycopg2
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO product_process (product_id, process_id)
                    VALUES (%s, %s)
                    ON CONFLICT (product_id, process_id) DO NOTHING
                """, (product_process_data['product_id'], product_process_data['process_id']))
                
                conn.commit()
                return product_process_data # 생성된 관계 정보 반환
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    async def _delete_product_process_db(self, product_id: int, process_id: int) -> bool:
        """데이터베이스에서 제품-공정 관계 삭제"""
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