# ============================================================================
# 📦 Dummy Repository - Dummy 데이터 접근
# ============================================================================

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import asyncpg
import asyncio

logger = logging.getLogger(__name__)

class DummyRepository:
    """Dummy 데이터 접근 클래스 (asyncpg 연결 풀)"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.pool: Optional[asyncpg.Pool] = None
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
        """dummy 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            # dummy 테이블이 이미 존재하는지 확인
            table_exists = await self.pool.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'dummy'
                );
            """)
            
            if not table_exists:
                logger.info("⚠️ dummy 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                
                # dummy 테이블 생성
                await self.pool.execute("""
                    CREATE TABLE dummy (
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
                await self.pool.execute("CREATE INDEX idx_dummy_로트번호 ON dummy(로트번호);")
                await self.pool.execute("CREATE INDEX idx_dummy_생산품명 ON dummy(생산품명);")
                await self.pool.execute("CREATE INDEX idx_dummy_공정 ON dummy(공정);")
                await self.pool.execute("CREATE INDEX idx_dummy_투입물명 ON dummy(투입물명);")
                
                logger.info("✅ dummy 테이블 생성 완료")
            else:
                logger.info("✅ dummy 테이블이 이미 존재합니다.")
                
        except Exception as e:
            logger.error(f"❌ dummy 테이블 생성 실패: {str(e)}")

    async def create_dummy_data(self, data: Dict[str, Any]) -> Optional[int]:
        """Dummy 데이터 생성"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return None
        
        try:
            # INSERT 쿼리 실행
            query = """
                INSERT INTO dummy (
                    로트번호, 생산품명, 생산수량, 투입일, 종료일, 공정, 투입물명, 수량, 단위
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id;
            """
            
            # 데이터 준비
            values = (
                data.get('로트번호'),
                data.get('생산품명'),
                data.get('생산수량'),
                data.get('투입일'),
                data.get('종료일'),
                data.get('공정'),
                data.get('투입물명'),
                data.get('수량'),
                data.get('단위')
            )
            
            # 쿼리 실행
            result = await self.pool.fetchval(query, *values)
            
            if result:
                logger.info(f"✅ Dummy 데이터 생성 성공: ID {result}")
                return result
            else:
                logger.error("❌ Dummy 데이터 생성 실패")
                return None
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 생성 실패: {e}")
            return None

    async def get_dummy_data_by_id(self, data_id: int) -> Optional[Dict[str, Any]]:
        """ID로 Dummy 데이터 조회"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return None
        
        try:
            query = "SELECT * FROM dummy WHERE id = $1;"
            row = await self.pool.fetchrow(query, data_id)
            
            if row:
                # Record를 딕셔너리로 변환
                data = dict(row)
                logger.info(f"✅ Dummy 데이터 조회 성공: ID {data_id}")
                return data
            else:
                logger.info(f"⚠️ Dummy 데이터를 찾을 수 없음: ID {data_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 조회 실패: {e}")
            return None

    async def get_all_dummy_data(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """모든 Dummy 데이터 조회 (페이징)"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return []
        
        try:
            query = "SELECT * FROM dummy ORDER BY id DESC LIMIT $1 OFFSET $2;"
            rows = await self.pool.fetch(query, limit, offset)
            
            # Record들을 딕셔너리로 변환
            data_list = [dict(row) for row in rows]
            
            logger.info(f"✅ Dummy 데이터 목록 조회 성공: {len(data_list)}개")
            return data_list
            
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 목록 조회 실패: {e}")
            return []

    async def update_dummy_data(self, data_id: int, data: Dict[str, Any]) -> bool:
        """Dummy 데이터 수정"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return False
        
        try:
            # 업데이트할 필드들만 추출
            update_fields = []
            values = []
            param_count = 1
            
            for key, value in data.items():
                if value is not None and key != 'id':
                    update_fields.append(f"{key} = ${param_count}")
                    values.append(value)
                    param_count += 1
            
            if not update_fields:
                logger.warning("⚠️ 업데이트할 필드가 없습니다.")
                return False
            
            # updated_at 필드 추가
            update_fields.append("updated_at = NOW()")
            
            # UPDATE 쿼리 실행
            query = f"""
                UPDATE dummy
                SET {', '.join(update_fields)}
                WHERE id = ${param_count};
            """
            values.append(data_id)
            
            result = await self.pool.execute(query, *values)
            
            if result:
                logger.info(f"✅ Dummy 데이터 수정 성공: ID {data_id}")
                return True
            else:
                logger.error(f"❌ Dummy 데이터 수정 실패: ID {data_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 수정 실패: {e}")
            return False

    async def delete_dummy_data(self, data_id: int) -> bool:
        """Dummy 데이터 삭제"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return False
        
        try:
            query = "DELETE FROM dummy WHERE id = $1;"
            result = await self.pool.execute(query, data_id)
            
            if result:
                logger.info(f"✅ Dummy 데이터 삭제 성공: ID {data_id}")
                return True
            else:
                logger.error(f"❌ Dummy 데이터 삭제 실패: ID {data_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 삭제 실패: {e}")
            return False

    async def search_dummy_data(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Dummy 데이터 검색"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return []
        
        try:
            # 여러 필드에서 검색
            query = """
                SELECT * FROM dummy
                WHERE 로트번호 ILIKE $1 
                   OR 생산품명 ILIKE $1 
                   OR 공정 ILIKE $1 
                   OR 투입물명 ILIKE $1
                ORDER BY id DESC
                LIMIT $2;
            """
            
            search_pattern = f"%{search_term}%"
            rows = await self.pool.fetch(query, search_pattern, limit)
            
            # Record들을 딕셔너리로 변환
            data_list = [dict(row) for row in rows]
            
            logger.info(f"✅ Dummy 데이터 검색 성공: '{search_term}' -> {len(data_list)}개")
            return data_list
            
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 검색 실패: {e}")
            return []

    async def get_dummy_data_count(self) -> int:
        """Dummy 데이터 총 개수"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return 0
        
        try:
            query = "SELECT COUNT(*) FROM dummy;"
            count = await self.pool.fetchval(query)
            
            logger.info(f"✅ Dummy 데이터 개수 조회 성공: {count}개")
            return count
            
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 개수 조회 실패: {e}")
            return 0
    
    async def get_all_dummy_data(self) -> List[dict]:
        """전체 더미 데이터 조회"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return []
        
        try:
            query = """
                SELECT 
                    id, 로트번호, 생산품명, 생산수량, 
                    투입일, 종료일, 공정, 투입물명, 수량, 단위,
                    created_at, updated_at
                FROM dummy 
                ORDER BY id DESC;
            """
            rows = await self.pool.fetch(query)
            
            # Record들을 딕셔너리로 변환
            data_list = [dict(row) for row in rows]
            
            logger.info(f"✅ 전체 더미 데이터 조회 성공: {len(data_list)}개")
            return data_list
            
        except Exception as e:
            logger.error(f"❌ 전체 더미 데이터 조회 실패: {e}")
            return []

    async def get_unique_product_names(self) -> List[str]:
        """고유한 제품명 목록 조회"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return []
        
        try:
            query = "SELECT DISTINCT 생산품명 FROM dummy WHERE 생산품명 IS NOT NULL ORDER BY 생산품명;"
            rows = await self.pool.fetch(query)
            
            # 제품명 추출
            product_names = [row['생산품명'] for row in rows if row['생산품명']]
            
            logger.info(f"✅ 고유 제품명 목록 조회 성공: {len(product_names)}개")
            return product_names
            
        except Exception as e:
            logger.error(f"❌ 고유 제품명 목록 조회 실패: {e}")
            return []

    async def get_unique_product_names_by_period(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[str]:
        """기간별 고유한 제품명 목록 조회"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return []
        
        try:
            # 기본 쿼리
            query = "SELECT DISTINCT 생산품명 FROM dummy WHERE 생산품명 IS NOT NULL"
            params = []
            
            # 기간 조건 추가 (기간이 겹치는 모든 제품 찾기)
            if start_date and end_date:
                # 날짜 형식 검증 및 변환
                try:
                    from datetime import datetime
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                    
                    # 날짜 순서 검증
                    if start_date_obj > end_date_obj:
                        logger.warning(f"⚠️ 시작일({start_date})이 종료일({end_date})보다 늦습니다.")
                        return []
                        
                except ValueError as e:
                    logger.error(f"❌ 날짜 형식 오류: {start_date} 또는 {end_date} - {e}")
                    return []
                
                # 기간 겹침 쿼리 (더 정확한 로직)
                query += """ AND (
                    (투입일 <= $2 AND 종료일 >= $1)  -- 기간이 겹치는 경우
                    OR (투입일 BETWEEN $1 AND $2)     -- 투입일이 기간 내에 있는 경우
                    OR (종료일 BETWEEN $1 AND $2)     -- 종료일이 기간 내에 있는 경우
                )"""
                params.extend([start_date_obj, end_date_obj])
                
            elif start_date:
                try:
                    from datetime import datetime
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    query += " AND 투입일 >= $1"
                    params.append(start_date_obj)
                except ValueError as e:
                    logger.error(f"❌ 시작일 형식 오류: {start_date} - {e}")
                    return []
                    
            elif end_date:
                try:
                    from datetime import datetime
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                    query += " AND 종료일 <= $1"
                    params.append(end_date_obj)
                except ValueError as e:
                    logger.error(f"❌ 종료일 형식 오류: {end_date} - {e}")
                    return []
            
            # 정렬 추가
            query += " ORDER BY 생산품명;"
            
            # 쿼리 실행
            rows = await self.pool.fetch(query, *params)
            
            # 제품명 추출
            product_names = [row['생산품명'] for row in rows if row['생산품명']]
            
            logger.info(f"✅ 기간별 제품명 목록 조회 성공: {start_date} ~ {end_date} - {len(product_names)}개")
            return product_names
            
        except Exception as e:
            logger.error(f"❌ 기간별 제품명 목록 조회 실패: {e}")
            return []

    async def get_unique_process_names(self) -> List[str]:
        """고유한 공정명 목록 조회"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return []
        
        try:
            query = """
                SELECT DISTINCT 공정 
                FROM dummy 
                WHERE 공정 IS NOT NULL 
                ORDER BY 공정;
            """
            rows = await self.pool.fetch(query)
            
            # 공정명 추출
            process_names = [row['공정'] for row in rows if row['공정']]
            
            logger.info(f"✅ 고유 공정명 목록 조회 성공: {len(process_names)}개")
            return process_names
            
        except Exception as e:
            logger.error(f"❌ 고유 공정명 목록 조회 실패: {e}")
            return []

    async def get_unique_process_names_by_period(self, start_period: str, end_period: str) -> List[str]:
        """기간별 고유한 공정명 목록 조회"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return []
        
        try:
            # 기본 쿼리
            query = "SELECT DISTINCT 공정 FROM dummy WHERE 공정 IS NOT NULL"
            params = []
            
            # 기간 조건 추가 (기간이 겹치는 모든 공정 찾기)
            if start_period and end_period:
                # 날짜 형식 검증 및 변환
                try:
                    from datetime import datetime
                    start_period_obj = datetime.strptime(start_period, "%Y-%m-%d").date()
                    end_period_obj = datetime.strptime(end_period, "%Y-%m-%d").date()
                    
                    # 날짜 순서 검증
                    if start_period_obj > end_period_obj:
                        logger.warning(f"⚠️ 시작일({start_period})이 종료일({end_period})보다 늦습니다.")
                        return []
                        
                except ValueError as e:
                    logger.error(f"❌ 날짜 형식 오류: {start_period} 또는 {end_period} - {e}")
                    return []
                
                # 기간 겹침 쿼리
                query += """ AND (
                    (투입일 <= $2 AND 종료일 >= $1)  -- 기간이 겹치는 경우
                    OR (투입일 BETWEEN $1 AND $2)     -- 투입일이 기간 내에 있는 경우
                    OR (종료일 BETWEEN $1 AND $2)     -- 종료일이 기간 내에 있는 경우
                )"""
                params.extend([start_period_obj, end_period_obj])
                
            elif start_period:
                try:
                    from datetime import datetime
                    start_period_obj = datetime.strptime(start_period, "%Y-%m-%d").date()
                    query += " AND 투입일 >= $1"
                    params.append(start_period_obj)
                except ValueError as e:
                    logger.error(f"❌ 시작일 형식 오류: {start_period} - {e}")
                    return []
                    
            elif end_period:
                try:
                    from datetime import datetime
                    end_period_obj = datetime.strptime(end_period, "%Y-%m-%d").date()
                    query += " AND 종료일 <= $1"
                    params.append(end_period_obj)
                except ValueError as e:
                    logger.error(f"❌ 종료일 형식 오류: {end_period} - {e}")
                    return []
            
            # 정렬 추가
            query += " ORDER BY 공정;"
            
            # 쿼리 실행
            rows = await self.pool.fetch(query, *params)
            
            # 공정명 추출
            process_names = [row['공정'] for row in rows if row['공정']]
            
            logger.info(f"✅ 기간별 공정명 목록 조회 성공: {start_period} ~ {end_period} - {len(process_names)}개")
            return process_names
            
        except Exception as e:
            logger.error(f"❌ 기간별 공정명 목록 조회 실패: {e}")
            return []

    async def get_unique_processes_by_product(self, product_name: str) -> List[str]:
        """특정 제품의 고유한 공정 목록 조회"""
        if not self.pool:
            logger.warning("⚠️ 연결 풀이 초기화되지 않았습니다.")
            return []
        
        try:
            query = """
                SELECT DISTINCT 공정 
                FROM dummy 
                WHERE 생산품명 = $1 AND 공정 IS NOT NULL 
                ORDER BY 공정;
            """
            rows = await self.pool.fetch(query, product_name)
            
            # 공정명 추출
            processes = [row['공정'] for row in rows if row['공정']]
            
            logger.info(f"✅ 제품 '{product_name}'의 공정 목록 조회 성공: {len(processes)}개")
            return processes
            
        except Exception as e:
            logger.error(f"❌ 제품 '{product_name}'의 공정 목록 조회 실패: {e}")
            return []

    async def close(self):
        """연결 풀 종료"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ Dummy 연결 풀 종료")
