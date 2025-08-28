# ============================================================================
# 📦 MatDir Repository - 원료직접배출량 데이터 접근
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from decimal import Decimal

logger = logging.getLogger(__name__)

class MatDirRepository:
    """원료직접배출량 데이터 접근 클래스"""
    
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
            self._create_matdir_table()
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            # 연결 실패해도 서비스는 계속 실행
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
    
    def _create_matdir_table(self):
        """matdir 테이블 생성"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                # matdir 테이블이 이미 존재하는지 확인
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'matdir'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.info("⚠️ matdir 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    # matdir 테이블 생성
                    cursor.execute("""
                        CREATE TABLE matdir (
                            id SERIAL PRIMARY KEY,
                            process_id INTEGER NOT NULL,
                            mat_name VARCHAR(255) NOT NULL,
                            mat_factor NUMERIC(10, 6) NOT NULL,
                            mat_amount NUMERIC(15, 6) NOT NULL,
                            oxyfactor NUMERIC(5, 4) DEFAULT 1.0000,
                            matdir_em NUMERIC(15, 6) DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    logger.info("✅ matdir 테이블 생성 완료")
                else:
                    logger.info("✅ matdir 테이블 확인 완료")
                
                conn.commit()
                logger.info("✅ 데이터베이스 테이블 확인 완료")
                
        except Exception as e:
            logger.error(f"❌ matdir 테이블 확인/생성 실패: {str(e)}")
            raise

    async def create_matdir(self, matdir_data: Dict[str, Any]) -> Dict[str, Any]:
        """원료직접배출량 데이터 생성"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._create_matdir_db(matdir_data)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 생성 실패: {str(e)}")
            raise

    async def get_matdirs(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 원료직접배출량 데이터 조회"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_matdirs_db(skip, limit)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 목록 조회 실패: {str(e)}")
            raise

    async def get_matdirs_by_process(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 원료직접배출량 데이터 조회"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_matdirs_by_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 공정별 원료직접배출량 데이터 조회 실패: {str(e)}")
            raise

    async def get_matdir(self, matdir_id: int) -> Optional[Dict[str, Any]]:
        """특정 원료직접배출량 데이터 조회"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._get_matdir_db(matdir_id)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 조회 실패: {str(e)}")
            raise

    async def update_matdir(self, matdir_id: int, matdir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """원료직접배출량 데이터 수정"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._update_matdir_db(matdir_id, matdir_data)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 수정 실패: {str(e)}")
            raise

    async def delete_matdir(self, matdir_id: int) -> bool:
        """원료직접배출량 데이터 삭제"""
        if not self.database_url:
            raise Exception("데이터베이스가 연결되지 않았습니다.")
        try:
            return await self._delete_matdir_db(matdir_id)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 삭제 실패: {str(e)}")
            raise

    def calculate_matdir_emission(self, mat_amount: Decimal, mat_factor: Decimal, oxyfactor: Decimal = Decimal('1.0000')) -> Decimal:
        """원료직접배출량 계산: matdir_em = mat_amount * mat_factor * oxyfactor"""
        return mat_amount * mat_factor * oxyfactor

    async def get_total_matdir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 원료직접배출량 계산"""
        matdirs = await self.get_matdirs_by_process(process_id)
        total_emission = sum(Decimal(str(matdir['matdir_em'])) for matdir in matdirs if matdir['matdir_em'])
        return total_emission

    # ============================================================================
    # 🔧 실제 DB 작업 메서드들
    # ============================================================================

    async def _create_matdir_db(self, matdir_data: Dict[str, Any]) -> Dict[str, Any]:
        """원료직접배출량 데이터 생성 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    INSERT INTO matdir (
                        process_id, mat_name, mat_factor, mat_amount, 
                        oxyfactor, matdir_em, created_at, updated_at
                    ) VALUES (
                        %(process_id)s, %(mat_name)s, %(mat_factor)s, %(mat_amount)s,
                        %(oxyfactor)s, %(matdir_em)s, NOW(), NOW()
                    ) RETURNING *
                """
                
                cursor.execute(query, matdir_data)
                result = cursor.fetchone()
                conn.commit()
                
                logger.info(f"✅ MatDir 생성 성공: ID {result['id']}")
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ MatDir 생성 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _get_matdirs_db(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 원료직접배출량 데이터 조회 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM matdir 
                    ORDER BY created_at DESC 
                    OFFSET %s LIMIT %s
                """
                
                cursor.execute(query, (skip, limit))
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ MatDir 목록 조회 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _get_matdirs_by_process_db(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 원료직접배출량 데이터 조회 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM matdir 
                    WHERE process_id = %s 
                    ORDER BY created_at DESC
                """
                
                cursor.execute(query, (process_id,))
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 공정별 MatDir 조회 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _get_matdir_db(self, matdir_id: int) -> Optional[Dict[str, Any]]:
        """특정 원료직접배출량 데이터 조회 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM matdir WHERE id = %s"
                cursor.execute(query, (matdir_id,))
                result = cursor.fetchone()
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ MatDir 조회 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _update_matdir_db(self, matdir_id: int, matdir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """원료직접배출량 데이터 수정 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 업데이트할 필드들만 동적으로 생성
                set_clause = ", ".join([f"{key} = %s" for key in matdir_data.keys()])
                values = list(matdir_data.values()) + [matdir_id]
                
                query = f"""
                    UPDATE matdir 
                    SET {set_clause}, updated_at = NOW()
                    WHERE id = %s 
                    RETURNING *
                """
                
                cursor.execute(query, values)
                result = cursor.fetchone()
                conn.commit()
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ MatDir 수정 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _delete_matdir_db(self, matdir_id: int) -> bool:
        """원료직접배출량 데이터 삭제 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                query = "DELETE FROM matdir WHERE id = %s"
                cursor.execute(query, (matdir_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ MatDir 삭제 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()
