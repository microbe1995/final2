# ============================================================================
# 📦 FuelDir Repository - 연료직접배출량 데이터 접근
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from decimal import Decimal

from app.config import settings

logger = logging.getLogger(__name__)

class FuelDirRepository:
    """연료직접배출량 데이터 접근 클래스"""
    
    def __init__(self):
        # 설정에서 데이터베이스 URL 가져오기
        self.database_url = settings.database_url
        
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
                CONSTRAINT fk_fueldir_process FOREIGN KEY (process_id) REFERENCES process(id) ON DELETE CASCADE,
                CONSTRAINT unique_fueldir_process_fuel UNIQUE(process_id, fuel_name)
            );
            """
            
            cursor.execute(create_table_sql)
            logger.info("✅ fueldir 테이블 생성 완료")
            
            # 인덱스 생성
            index_sql = """
            CREATE INDEX IF NOT EXISTS idx_fueldir_process_id ON fueldir(process_id);
            CREATE INDEX IF NOT EXISTS idx_fueldir_fuel_name ON fueldir(fuel_name);
            CREATE INDEX IF NOT EXISTS idx_fueldir_process_fuel ON fueldir(process_id, fuel_name);
            CREATE INDEX IF NOT EXISTS idx_fueldir_created_at ON fueldir(created_at);
            """
            
            cursor.execute(index_sql)
            logger.info("✅ fueldir 테이블 인덱스 생성 완료")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"fueldir 테이블 초기화 실패: {e}")
            raise

    # ============================================================================
    # 📋 기존 FuelDir CRUD 메서드들
    # ============================================================================

    async def create_fueldir(self, fueldir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """연료직접배출량 데이터 생성 (중복 방지)"""
        if not self.database_url:
            logger.error("DATABASE_URL이 설정되지 않았습니다.")
            return None
            
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 중복 데이터 확인
                cursor.execute("""
                    SELECT id FROM fueldir 
                    WHERE process_id = %s AND fuel_name = %s
                """, (fueldir_data['process_id'], fueldir_data['fuel_name']))
                
                existing_record = cursor.fetchone()
                
                if existing_record:
                    # 중복 데이터가 있으면 업데이트
                    logger.info(f"🔄 중복 데이터 발견, 업데이트: process_id={fueldir_data['process_id']}, fuel_name={fueldir_data['fuel_name']}")
                    query = """
                        UPDATE fueldir 
                        SET fuel_factor = %s, fuel_amount = %s, fuel_oxyfactor = %s, fueldir_em = %s, updated_at = NOW()
                        WHERE process_id = %s AND fuel_name = %s
                        RETURNING *
                    """
                    
                    cursor.execute(query, (
                        fueldir_data['fuel_factor'],
                        fueldir_data['fuel_amount'],
                        fueldir_data.get('fuel_oxyfactor', 1.0000),
                        fueldir_data.get('fueldir_em', 0),
                        fueldir_data['process_id'],
                        fueldir_data['fuel_name']
                    ))
                else:
                    # 새로운 데이터 삽입
                    query = """
                        INSERT INTO fueldir (process_id, fuel_name, fuel_factor, fuel_amount, fuel_oxyfactor, fueldir_em)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """
                    
                    cursor.execute(query, (
                        fueldir_data['process_id'],
                        fueldir_data['fuel_name'],
                        fueldir_data['fuel_factor'],
                        fueldir_data['fuel_amount'],
                        fueldir_data.get('fuel_oxyfactor', 1.0000),
                        fueldir_data.get('fueldir_em', 0)
                    ))
                
                result = cursor.fetchone()
                conn.commit()
                
                action = "업데이트" if existing_record else "생성"
                logger.info(f"✅ FuelDir {action} 성공: ID {result['id']}")
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ FuelDir 생성/업데이트 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def get_fueldirs(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 연료직접배출량 데이터 조회"""
        try:
            return await self._get_fueldirs_db(skip, limit)
        except Exception as e:
            logger.error(f"❌ FuelDir 목록 조회 실패: {str(e)}")
            return []

    async def get_fueldirs_by_process(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 연료직접배출량 데이터 조회"""
        try:
            return await self._get_fueldirs_by_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 공정별 FuelDir 조회 실패: {str(e)}")
            return []

    async def get_fueldir(self, fueldir_id: int) -> Optional[Dict[str, Any]]:
        """특정 연료직접배출량 데이터 조회"""
        try:
            return await self._get_fueldir_db(fueldir_id)
        except Exception as e:
            logger.error(f"❌ FuelDir 조회 실패: {str(e)}")
            return None

    async def update_fueldir(self, fueldir_id: int, fueldir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """연료직접배출량 데이터 수정"""
        try:
            return await self._update_fueldir_db(fueldir_id, fueldir_data)
        except Exception as e:
            logger.error(f"❌ FuelDir 수정 실패: {str(e)}")
            return None

    async def delete_fueldir(self, fueldir_id: int) -> bool:
        """연료직접배출량 데이터 삭제"""
        try:
            return await self._delete_fueldir_db(fueldir_id)
        except Exception as e:
            logger.error(f"❌ FuelDir 삭제 실패: {str(e)}")
            return False

    # ============================================================================
    # 🏗️ Fuel Master 조회 메서드들 (새로 추가)
    # ============================================================================

    async def get_fuel_by_name(self, fuel_name: str) -> Optional[Dict[str, Any]]:
        """연료명으로 마스터 데이터 조회"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT id, fuel_name, fuel_engname, fuel_factor, net_calory
                    FROM fuel_master
                    WHERE fuel_name = %s
                """
                
                cursor.execute(query, (fuel_name,))
                result = cursor.fetchone()
                
                if result:
                    logger.info(f"✅ 연료 마스터 조회 성공: {fuel_name}")
                    return dict(result)
                else:
                    logger.warning(f"⚠️ 연료 마스터 데이터를 찾을 수 없음: {fuel_name}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ 연료 마스터 조회 실패: {str(e)}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    async def search_fuels(self, search_term: str) -> List[Dict[str, Any]]:
        """연료명으로 검색 (부분 검색)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT id, fuel_name, fuel_engname, fuel_factor, net_calory
                    FROM fuel_master
                    WHERE fuel_name ILIKE %s OR fuel_engname ILIKE %s
                    ORDER BY fuel_name
                """
                
                search_pattern = f'%{search_term}%'
                cursor.execute(query, (search_pattern, search_pattern))
                results = cursor.fetchall()
                
                logger.info(f"✅ 연료 마스터 검색 성공: '{search_term}' → {len(results)}개 결과")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 연료 마스터 검색 실패: {str(e)}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    async def get_all_fuels(self) -> List[Dict[str, Any]]:
        """모든 연료 마스터 데이터 조회"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT id, fuel_name, fuel_engname, fuel_factor, net_calory
                    FROM fuel_master
                    ORDER BY fuel_name
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                logger.info(f"✅ 모든 연료 마스터 조회 성공: {len(results)}개")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 모든 연료 마스터 조회 실패: {str(e)}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    async def get_fuel_factor_by_name(self, fuel_name: str) -> Optional[Dict[str, Any]]:
        """연료명으로 배출계수만 조회 (간단한 응답)"""
        try:
            fuel = await self.get_fuel_by_name(fuel_name)
            if fuel:
                return {
                    'fuel_name': fuel['fuel_name'],
                    'fuel_factor': float(fuel['fuel_factor']),
                    'net_calory': float(fuel['net_calory']) if fuel['net_calory'] else None,
                    'found': True
                }
            else:
                return {
                    'fuel_name': fuel_name,
                    'fuel_factor': None,
                    'net_calory': None,
                    'found': False
                }
                
        except Exception as e:
            logger.error(f"❌ 배출계수 조회 실패: {str(e)}")
            return {
                'fuel_name': fuel_name,
                'fuel_factor': None,
                'net_calory': None,
                'found': False
            }

    # ============================================================================
    # 📋 기존 DB 작업 메서드들
    # ============================================================================

    async def _get_fueldirs_db(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 연료직접배출량 데이터 조회 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM fueldir 
                    ORDER BY created_at DESC 
                    LIMIT %s OFFSET %s
                """
                
                cursor.execute(query, (limit, skip))
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ FuelDir 목록 조회 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _get_fueldirs_by_process_db(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 연료직접배출량 데이터 조회 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM fueldir 
                    WHERE process_id = %s 
                    ORDER BY created_at DESC
                """
                
                cursor.execute(query, (process_id,))
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 공정별 FuelDir 조회 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _get_fueldir_db(self, fueldir_id: int) -> Optional[Dict[str, Any]]:
        """특정 연료직접배출량 데이터 조회 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM fueldir WHERE id = %s"
                cursor.execute(query, (fueldir_id,))
                result = cursor.fetchone()
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ FuelDir 조회 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _update_fueldir_db(self, fueldir_id: int, fueldir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """연료직접배출량 데이터 수정 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 업데이트할 필드들만 동적으로 생성
                set_clause = ", ".join([f"{key} = %s" for key in fueldir_data.keys()])
                values = list(fueldir_data.values()) + [fueldir_id]
                
                query = f"""
                    UPDATE fueldir 
                    SET {set_clause}, updated_at = NOW()
                    WHERE id = %s 
                    RETURNING *
                """
                
                cursor.execute(query, values)
                result = cursor.fetchone()
                conn.commit()
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ FuelDir 수정 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    async def _delete_fueldir_db(self, fueldir_id: int) -> bool:
        """연료직접배출량 데이터 삭제 (DB 작업)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                query = "DELETE FROM fueldir WHERE id = %s"
                cursor.execute(query, (fueldir_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"❌ FuelDir 삭제 실패: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

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
