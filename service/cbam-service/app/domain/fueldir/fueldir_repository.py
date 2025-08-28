# ============================================================================
# 📦 FuelDir Repository - 연료직접배출량 데이터 접근
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

class FuelDirRepository:
    """연료직접배출량 데이터 접근 클래스"""
    
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
        if not self._check_database_connection():
            logger.error("데이터베이스 연결을 확인할 수 없습니다.")
            return

        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # fueldir 테이블 생성
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS fueldir (
                id SERIAL PRIMARY KEY,
                process_id INTEGER NOT NULL,
                fuel_name VARCHAR(255) NOT NULL,
                fuel_factor DECIMAL(10,6) NOT NULL,
                fuel_amount DECIMAL(15,6) NOT NULL,
                fuel_oxyfactor DECIMAL(5,4) DEFAULT 1.0000,
                fueldir_em DECIMAL(15,6) DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_fueldir_process FOREIGN KEY (process_id) REFERENCES process(id) ON DELETE CASCADE
            );
            """
            
            cursor.execute(create_table_sql)
            logger.info("✅ fueldir 테이블 생성 완료")
            
            # 인덱스 생성
            index_sql = """
            CREATE INDEX IF NOT EXISTS idx_fueldir_process_id ON fueldir(process_id);
            CREATE INDEX IF NOT EXISTS idx_fueldir_fuel_name ON fueldir(fuel_name);
            CREATE INDEX IF NOT EXISTS idx_fueldir_created_at ON fueldir(created_at);
            """
            
            cursor.execute(index_sql)
            logger.info("✅ fueldir 테이블 인덱스 생성 완료")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"fueldir 테이블 초기화 실패: {e}")
            raise

    async def create_fueldir(self, fueldir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """연료직접배출량 데이터 생성"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return None
            
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            insert_sql = """
            INSERT INTO fueldir (process_id, fuel_name, fuel_factor, fuel_amount, fuel_oxyfactor, fueldir_em)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """
            
            cursor.execute(insert_sql, (
                fueldir_data['process_id'],
                fueldir_data['fuel_name'],
                fueldir_data['fuel_factor'],
                fueldir_data['fuel_amount'],
                fueldir_data.get('fuel_oxyfactor', 1.0000),
                fueldir_data.get('fueldir_em', 0)
            ))
            
            result = cursor.fetchone()
            conn.commit()
            
            cursor.close()
            conn.close()
            
            if result:
                logger.info(f"✅ 연료직접배출량 데이터 생성 성공: ID {result['id']}")
                return dict(result)
            else:
                logger.error("❌ 연료직접배출량 데이터 생성 실패")
                return None
                
        except Exception as e:
            logger.error(f"❌ 연료직접배출량 데이터 생성 중 오류: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return None

    async def get_fueldirs(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 연료직접배출량 데이터 조회"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return []
            
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            select_sql = """
            SELECT * FROM fueldir 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(select_sql, (limit, skip))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 연료직접배출량 데이터 조회 성공: {len(results)}개")
            return [dict(result) for result in results]
            
        except Exception as e:
            logger.error(f"❌ 연료직접배출량 데이터 조회 중 오류: {e}")
            return []

    async def get_fueldirs_by_process(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 연료직접배출량 데이터 조회"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return []
            
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            select_sql = """
            SELECT * FROM fueldir 
            WHERE process_id = %s 
            ORDER BY created_at DESC
            """
            
            cursor.execute(select_sql, (process_id,))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ 공정별 연료직접배출량 데이터 조회 성공: Process ID {process_id}, {len(results)}개")
            return [dict(result) for result in results]
            
        except Exception as e:
            logger.error(f"❌ 공정별 연료직접배출량 데이터 조회 중 오류: {e}")
            return []

    async def get_fueldir(self, fueldir_id: int) -> Optional[Dict[str, Any]]:
        """특정 연료직접배출량 데이터 조회"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return None
            
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            select_sql = "SELECT * FROM fueldir WHERE id = %s"
            cursor.execute(select_sql, (fueldir_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                logger.info(f"✅ 연료직접배출량 데이터 조회 성공: ID {fueldir_id}")
                return dict(result)
            else:
                logger.warning(f"⚠️ 연료직접배출량 데이터를 찾을 수 없음: ID {fueldir_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 연료직접배출량 데이터 조회 중 오류: {e}")
            return None

    async def update_fueldir(self, fueldir_id: int, fueldir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """연료직접배출량 데이터 수정"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return None
            
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 업데이트할 필드들만 동적으로 구성
            update_fields = []
            update_values = []
            
            for key, value in fueldir_data.items():
                if value is not None and key != 'id':
                    update_fields.append(f"{key} = %s")
                    update_values.append(value)
            
            if not update_fields:
                logger.warning("업데이트할 필드가 없습니다.")
                return None
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(fueldir_id)
            
            update_sql = f"""
            UPDATE fueldir 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING *
            """
            
            cursor.execute(update_sql, update_values)
            result = cursor.fetchone()
            
            if result:
                conn.commit()
                logger.info(f"✅ 연료직접배출량 데이터 수정 성공: ID {fueldir_id}")
                cursor.close()
                conn.close()
                return dict(result)
            else:
                conn.rollback()
                logger.warning(f"⚠️ 수정할 연료직접배출량 데이터를 찾을 수 없음: ID {fueldir_id}")
                cursor.close()
                conn.close()
                return None
                
        except Exception as e:
            logger.error(f"❌ 연료직접배출량 데이터 수정 중 오류: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return None

    async def delete_fueldir(self, fueldir_id: int) -> bool:
        """연료직접배출량 데이터 삭제"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return False
            
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            delete_sql = "DELETE FROM fueldir WHERE id = %s"
            cursor.execute(delete_sql, (fueldir_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"✅ 연료직접배출량 데이터 삭제 성공: ID {fueldir_id}")
                cursor.close()
                conn.close()
                return True
            else:
                conn.rollback()
                logger.warning(f"⚠️ 삭제할 연료직접배출량 데이터를 찾을 수 없음: ID {fueldir_id}")
                cursor.close()
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"❌ 연료직접배출량 데이터 삭제 중 오류: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False

    async def get_total_fueldir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 연료직접배출량 계산"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return Decimal('0')
            
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            select_sql = """
            SELECT COALESCE(SUM(fueldir_em), 0) as total_emission
            FROM fueldir 
            WHERE process_id = %s
            """
            
            cursor.execute(select_sql, (process_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            total_emission = Decimal(str(result[0])) if result and result[0] else Decimal('0')
            logger.info(f"✅ 공정별 총 연료직접배출량 계산 성공: Process ID {process_id}, 총 배출량: {total_emission}")
            return total_emission
            
        except Exception as e:
            logger.error(f"❌ 공정별 총 연료직접배출량 계산 중 오류: {e}")
            return Decimal('0')

    async def get_fueldir_summary(self) -> Dict[str, Any]:
        """연료직접배출량 통계 요약"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return {}
            
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            select_sql = """
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(fueldir_em), 0) as total_emission,
                COALESCE(AVG(fueldir_em), 0) as average_emission,
                COUNT(DISTINCT process_id) as process_count
            FROM fueldir
            """
            
            cursor.execute(select_sql)
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                summary = {
                    "total_count": result[0],
                    "total_emission": float(result[1]) if result[1] else 0.0,
                    "average_emission": float(result[2]) if result[2] else 0.0,
                    "process_count": result[3]
                }
                logger.info(f"✅ 연료직접배출량 통계 요약 생성 성공: {summary}")
                return summary
            else:
                return {}
                
        except Exception as e:
            logger.error(f"❌ 연료직접배출량 통계 요약 생성 중 오류: {e}")
            return {}
