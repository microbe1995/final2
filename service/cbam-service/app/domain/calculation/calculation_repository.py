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

from .calculation_entity import Edge, EdgeResponse

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