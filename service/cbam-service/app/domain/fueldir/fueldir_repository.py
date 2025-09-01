# ============================================================================
# 📦 FuelDir Repository - 연료직접배출량 데이터 접근
# ============================================================================

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
from decimal import Decimal

logger = logging.getLogger(__name__)

class FuelDirRepository:
    """연료직접배출량 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
            return
        
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
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'application_name': 'cbam-service-fueldir'
                }
            )
            logger.info("✅ FuelDir 데이터베이스 연결 풀 생성 성공")
            
            # 테이블 생성은 선택적으로 실행
            try:
                await self._create_fueldir_table_async()
            except Exception as e:
                logger.warning(f"⚠️ FuelDir 테이블 생성 실패 (기본 기능은 정상): {e}")
            
        except Exception as e:
            logger.error(f"❌ FuelDir 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
    async def _create_fueldir_table_async(self):
        """fueldir 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # fueldir 테이블이 이미 존재하는지 확인
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'fueldir'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ fueldir 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    # fueldir 테이블 생성
                    await conn.execute("""
                        CREATE TABLE fueldir (
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
                    """)
                    
                    # 인덱스 생성
                    await conn.execute("""
                        CREATE INDEX idx_fueldir_process_id ON fueldir(process_id);
                        CREATE INDEX idx_fueldir_fuel_name ON fueldir(fuel_name);
                        CREATE INDEX idx_fueldir_process_fuel ON fueldir(process_id, fuel_name);
                        CREATE INDEX idx_fueldir_created_at ON fueldir(created_at);
                    """)
                    
                    logger.info("✅ fueldir 테이블 생성 완료")
                else:
                    logger.info("✅ fueldir 테이블이 이미 존재합니다.")
                    
        except Exception as e:
            logger.error(f"❌ fueldir 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")

    # ============================================================================
    # 📋 기존 FuelDir CRUD 메서드들
    # ============================================================================

    async def create_fueldir(self, fueldir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """연료직접배출량 데이터 생성 (중복 방지)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                # 중복 데이터 확인
                existing_record = await conn.fetchrow("""
                    SELECT id FROM fueldir 
                    WHERE process_id = $1 AND fuel_name = $2
                """, fueldir_data['process_id'], fueldir_data['fuel_name'])
                
                if existing_record:
                    # 중복 데이터가 있으면 업데이트
                    logger.info(f"🔄 중복 데이터 발견, 업데이트: process_id={fueldir_data['process_id']}, fuel_name={fueldir_data['fuel_name']}")
                    result = await conn.fetchrow("""
                        UPDATE fueldir 
                        SET fuel_factor = $1, fuel_amount = $2, fuel_oxyfactor = $3, fueldir_em = $4, updated_at = NOW()
                        WHERE process_id = $5 AND fuel_name = $6
                        RETURNING *
                    """, (
                        fueldir_data['fuel_factor'],
                        fueldir_data['fuel_amount'],
                        fueldir_data.get('fuel_oxyfactor', 1.0000),
                        fueldir_data.get('fueldir_em', 0),
                        fueldir_data['process_id'],
                        fueldir_data['fuel_name']
                    ))
                else:
                    # 새로운 데이터 삽입
                    result = await conn.fetchrow("""
                        INSERT INTO fueldir (process_id, fuel_name, fuel_factor, fuel_amount, fuel_oxyfactor, fueldir_em)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING *
                    """, (
                        fueldir_data['process_id'],
                        fueldir_data['fuel_name'],
                        fueldir_data['fuel_factor'],
                        fueldir_data['fuel_amount'],
                        fueldir_data.get('fuel_oxyfactor', 1.0000),
                        fueldir_data.get('fueldir_em', 0)
                    ))
                
                action = "업데이트" if existing_record else "생성"
                logger.info(f"✅ FuelDir {action} 성공: ID {result['id']}")
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ FuelDir 생성/업데이트 실패: {str(e)}")
            raise

    async def get_fueldirs(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 연료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_fueldirs_db(skip, limit)
        except Exception as e:
            logger.error(f"❌ FuelDir 목록 조회 실패: {str(e)}")
            return []

    async def get_fueldirs_by_process(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 연료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_fueldirs_by_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 공정별 FuelDir 조회 실패: {str(e)}")
            return []

    async def get_fueldir(self, fueldir_id: int) -> Optional[Dict[str, Any]]:
        """특정 연료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_fueldir_db(fueldir_id)
        except Exception as e:
            logger.error(f"❌ FuelDir 조회 실패: {str(e)}")
            return None

    async def update_fueldir(self, fueldir_id: int, fueldir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """연료직접배출량 데이터 수정"""
        await self._ensure_pool_initialized()
        try:
            return await self._update_fueldir_db(fueldir_id, fueldir_data)
        except Exception as e:
            logger.error(f"❌ FuelDir 수정 실패: {str(e)}")
            return None

    async def delete_fueldir(self, fueldir_id: int) -> bool:
        """연료직접배출량 데이터 삭제"""
        await self._ensure_pool_initialized()
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
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT id, fuel_name, fuel_engname, fuel_factor, net_calory
                    FROM fuel_master
                    WHERE fuel_name = $1
                """, fuel_name)
                
                if result:
                    logger.info(f"✅ 연료 마스터 조회 성공: {fuel_name}")
                    return dict(result)
                else:
                    logger.warning(f"⚠️ 연료 마스터 데이터를 찾을 수 없음: {fuel_name}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ 연료 마스터 조회 실패: {str(e)}")
            return None

    async def search_fuels(self, search_term: str) -> List[Dict[str, Any]]:
        """연료명으로 검색 (부분 검색)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, fuel_name, fuel_engname, fuel_factor, net_calory
                    FROM fuel_master
                    WHERE fuel_name ILIKE $1 OR fuel_engname ILIKE $1
                    ORDER BY fuel_name
                """, f'%{search_term}%')
                
                logger.info(f"✅ 연료 마스터 검색 성공: '{search_term}' → {len(results)}개 결과")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 연료 마스터 검색 실패: {str(e)}")
            return []

    async def get_all_fuels(self) -> List[Dict[str, Any]]:
        """모든 연료 마스터 데이터 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, fuel_name, fuel_engname, fuel_factor, net_calory
                    FROM fuel_master
                    ORDER BY fuel_name
                """)
                
                logger.info(f"✅ 모든 연료 마스터 조회 성공: {len(results)}개")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 모든 연료 마스터 조회 실패: {str(e)}")
            return []

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
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM fueldir 
                    ORDER BY created_at DESC 
                    LIMIT $1 OFFSET $2
                """, limit, skip)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ FuelDir 목록 조회 실패: {str(e)}")
            raise

    async def _get_fueldirs_by_process_db(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 연료직접배출량 데이터 조회 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM fueldir 
                    WHERE process_id = $1 
                    ORDER BY created_at DESC
                """, process_id)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 공정별 FuelDir 조회 실패: {str(e)}")
            raise

    async def _get_fueldir_db(self, fueldir_id: int) -> Optional[Dict[str, Any]]:
        """특정 연료직접배출량 데이터 조회 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM fueldir WHERE id = $1
                """, fueldir_id)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ FuelDir 조회 실패: {str(e)}")
            raise

    async def _update_fueldir_db(self, fueldir_id: int, fueldir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """연료직접배출량 데이터 수정 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # 업데이트할 필드들만 동적으로 생성
                set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(fueldir_data.keys())])
                values = list(fueldir_data.values()) + [fueldir_id]
                
                query = f"""
                    UPDATE fueldir 
                    SET {set_clause}, updated_at = NOW()
                    WHERE id = ${len(fueldir_data) + 1} 
                    RETURNING *
                """
                
                result = await conn.fetchrow(query, *values)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ FuelDir 수정 실패: {str(e)}")
            raise

    async def _delete_fueldir_db(self, fueldir_id: int) -> bool:
        """연료직접배출량 데이터 삭제 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM fueldir WHERE id = $1
                """, fueldir_id)
                
                return result != "DELETE 0"
                
        except Exception as e:
            logger.error(f"❌ FuelDir 삭제 실패: {str(e)}")
            raise

    async def get_total_fueldir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 연료직접배출량 계산"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT COALESCE(SUM(fueldir_em), 0) as total_emission
                    FROM fueldir 
                    WHERE process_id = $1
                """, process_id)
                
                total_emission = Decimal(str(result['total_emission'])) if result and result['total_emission'] else Decimal('0')
                logger.info(f"✅ 공정별 총 연료직접배출량 계산 성공: Process ID {process_id}, 총 배출량: {total_emission}")
                return total_emission
                
        except Exception as e:
            logger.error(f"❌ 공정별 총 연료직접배출량 계산 중 오류: {e}")
            return Decimal('0')

    async def get_fueldir_summary(self) -> Dict[str, Any]:
        """연료직접배출량 통계 요약"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_count,
                        COALESCE(SUM(fueldir_em), 0) as total_emission,
                        COALESCE(AVG(fueldir_em), 0) as average_emission,
                        COUNT(DISTINCT process_id) as process_count
                    FROM fueldir
                """)
                
                if result:
                    summary = {
                        "total_count": result['total_count'],
                        "total_emission": float(result['total_emission']) if result['total_emission'] else 0.0,
                        "average_emission": float(result['average_emission']) if result['average_emission'] else 0.0,
                        "process_count": result['process_count']
                    }
                    logger.info(f"✅ 연료직접배출량 통계 요약 생성 성공: {summary}")
                    return summary
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ 연료직접배출량 통계 요약 생성 중 오류: {e}")
            return {}
