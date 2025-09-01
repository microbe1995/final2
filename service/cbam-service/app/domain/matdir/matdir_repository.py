# ============================================================================
# 📦 MatDir Repository - 원료직접배출량 데이터 접근
# ============================================================================

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg
from decimal import Decimal

logger = logging.getLogger(__name__)

class MatDirRepository:
    """원료직접배출량 데이터 접근 클래스"""
    
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
                    'application_name': 'cbam-service-matdir'
                }
            )
            logger.info("✅ MatDir 데이터베이스 연결 풀 생성 성공")
            
            # 테이블 생성은 선택적으로 실행
            try:
                await self._create_matdir_table_async()
                await self._create_material_master_table_async()
            except Exception as e:
                logger.warning(f"⚠️ 테이블 생성 실패 (기본 기능은 정상): {e}")
            
        except Exception as e:
            logger.error(f"❌ MatDir 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        logger.info(f"🔍 연결 풀 상태 확인: pool={self.pool}, attempted={self._initialization_attempted}")
        
        if not self.pool and not self._initialization_attempted:
            logger.info("🔄 연결 풀 초기화 시작")
            await self.initialize()
        
        if not self.pool:
            logger.error("❌ 연결 풀이 초기화되지 않았습니다.")
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
        
        logger.info("✅ 연결 풀 정상 상태 확인")
    
    async def _create_matdir_table_async(self):
        """matdir 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # matdir 테이블이 이미 존재하는지 확인
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'matdir'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ matdir 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    # matdir 테이블 생성
                    await conn.execute("""
                        CREATE TABLE matdir (
                            id SERIAL PRIMARY KEY,
                            process_id INTEGER NOT NULL,
                            mat_name VARCHAR(255) NOT NULL,
                            mat_factor NUMERIC(10, 6) NOT NULL,
                            mat_amount NUMERIC(15, 6) NOT NULL,
                            oxyfactor NUMERIC(5, 4) DEFAULT 1.0000,
                            matdir_em NUMERIC(15, 6) DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            CONSTRAINT fk_matdir_process FOREIGN KEY (process_id) REFERENCES process(id) ON DELETE CASCADE,
                            CONSTRAINT unique_matdir_process_material UNIQUE(process_id, mat_name)
                        );
                    """)
                    
                    # 인덱스 생성
                    await conn.execute("""
                        CREATE INDEX idx_matdir_process_id ON matdir(process_id);
                        CREATE INDEX idx_matdir_mat_name ON matdir(mat_name);
                        CREATE INDEX idx_matdir_process_material ON matdir(process_id, mat_name);
                        CREATE INDEX idx_matdir_created_at ON matdir(created_at);
                    """)
                    
                    logger.info("✅ matdir 테이블 생성 완료")
                else:
                    logger.info("✅ matdir 테이블이 이미 존재합니다.")
                    
        except Exception as e:
            logger.error(f"❌ matdir 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")

    async def _create_material_master_table_async(self):
        """material_master 테이블 생성 (비동기)"""
        if not self.pool:
            logger.warning("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # material_master 테이블이 이미 존재하는지 확인
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'material_master'
                    );
                """)
                
                if not result:
                    logger.info("⚠️ material_master 테이블이 존재하지 않습니다. 자동으로 생성합니다.")
                    
                    # material_master 테이블 생성
                    await conn.execute("""
                        CREATE TABLE material_master (
                            id SERIAL PRIMARY KEY,
                            mat_name VARCHAR(255) NOT NULL UNIQUE,
                            mat_engname VARCHAR(255),
                            mat_factor NUMERIC(10, 6) NOT NULL DEFAULT 0,
                            carbon_content NUMERIC(10, 6),
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                        );
                    """)
                    
                    # 인덱스 생성
                    await conn.execute("""
                        CREATE INDEX idx_material_master_name ON material_master(mat_name);
                        CREATE INDEX idx_material_master_factor ON material_master(mat_factor);
                    """)
                    
                    # 기본 데이터 삽입 (예시)
                    await conn.execute("""
                        INSERT INTO material_master (mat_name, mat_engname, mat_factor, carbon_content) VALUES
                        ('직접환원철', 'Direct Reduced Iron', 0.123456, 0.045),
                        ('EAF 탄소 전극', 'EAF Carbon Electrode', 0.234567, 0.089),
                        ('석회석', 'Limestone', 0.345678, 0.120),
                        ('코크스', 'Coke', 0.456789, 0.156)
                        ON CONFLICT (mat_name) DO NOTHING;
                    """)
                    
                    logger.info("✅ material_master 테이블 생성 완료")
                else:
                    logger.info("✅ material_master 테이블이 이미 존재합니다.")
                    
        except Exception as e:
            logger.error(f"❌ material_master 테이블 생성 실패: {str(e)}")
            logger.warning("⚠️ 테이블 생성 실패로 인해 일부 기능이 제한될 수 있습니다.")

    async def test_connection(self) -> bool:
        """데이터베이스 연결 상태 테스트"""
        try:
            await self._ensure_pool_initialized()
            
            async with self.pool.acquire() as conn:
                # 간단한 쿼리로 연결 테스트
                result = await conn.fetchval("SELECT 1")
                logger.info(f"✅ 데이터베이스 연결 테스트 성공: {result}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 테스트 실패: {str(e)}")
            return False

    # ============================================================================
    # 📋 기존 MatDir CRUD 메서드들
    # ============================================================================

    async def create_matdir(self, matdir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """원료직접배출량 데이터 생성 (중복 방지)"""
        await self._ensure_pool_initialized()
        
        try:
            # 디버깅을 위한 데이터 로깅
            logger.info(f"🔍 create_matdir 입력 데이터: {matdir_data}")
            logger.info(f"🔍 oxyfactor 값: {matdir_data.get('oxyfactor')}")
            logger.info(f"🔍 matdir_em 값: {matdir_data.get('matdir_em')}")
            logger.info(f"🔍 process_id 타입: {type(matdir_data.get('process_id'))}, 값: {matdir_data.get('process_id')}")
            logger.info(f"🔍 mat_name 타입: {type(matdir_data.get('mat_name'))}, 값: {matdir_data.get('mat_name')}")
            logger.info(f"🔍 mat_factor 타입: {type(matdir_data.get('mat_factor'))}, 값: {matdir_data.get('mat_factor')}")
            logger.info(f"🔍 mat_amount 타입: {type(matdir_data.get('mat_amount'))}, 값: {matdir_data.get('mat_amount')}")
            
            async with self.pool.acquire() as conn:
                # 중복 데이터 확인
                logger.info("🔍 중복 데이터 확인 쿼리 실행 시작")
                existing_record = await conn.fetchrow("""
                    SELECT id FROM matdir 
                    WHERE process_id = $1 AND mat_name = $2
                """, matdir_data['process_id'], matdir_data['mat_name'])
                logger.info(f"🔍 중복 데이터 확인 결과: {existing_record}")
                
                if existing_record:
                    # 중복 데이터가 있으면 업데이트
                    logger.info(f"🔄 중복 데이터 발견, 업데이트: process_id={matdir_data['process_id']}, mat_name={matdir_data['mat_name']}")
                    
                    # oxyfactor 기본값 설정 (matdir_em은 계산된 값이므로 기본값 불필요)
                    oxyfactor = matdir_data.get('oxyfactor')
                    if oxyfactor is None:
                        oxyfactor = Decimal('1.0000')
                    
                    logger.info(f"🔍 UPDATE 쿼리 파라미터: oxyfactor={oxyfactor}, matdir_em={matdir_data['matdir_em']}")
                    logger.info("🔍 UPDATE 쿼리 실행 시작")
                    
                    # 파라미터 값을 개별적으로 로깅
                    logger.info(f"🔍 파라미터 1 (mat_factor): {matdir_data['mat_factor']} (타입: {type(matdir_data['mat_factor'])})")
                    logger.info(f"🔍 파라미터 2 (mat_amount): {matdir_data['mat_amount']} (타입: {type(matdir_data['mat_amount'])})")
                    logger.info(f"🔍 파라미터 3 (oxyfactor): {oxyfactor} (타입: {type(oxyfactor)})")
                    logger.info(f"🔍 파라미터 4 (matdir_em): {matdir_data['matdir_em']} (타입: {type(matdir_data['matdir_em'])})")
                    logger.info(f"🔍 파라미터 5 (process_id): {matdir_data['process_id']} (타입: {type(matdir_data['process_id'])})")
                    logger.info(f"🔍 파라미터 6 (mat_name): {matdir_data['mat_name']} (타입: {type(matdir_data['mat_name'])})")
                    
                    # 파라미터 튜플을 명시적으로 생성
                    params = (
                        matdir_data['mat_factor'],
                        matdir_data['mat_amount'],
                        oxyfactor,
                        matdir_data['matdir_em'],
                        matdir_data['process_id'],
                        matdir_data['mat_name']
                    )
                    
                    logger.info(f"🔍 최종 파라미터 튜플: {params}")
                    logger.info(f"🔍 파라미터 개수: {len(params)}")
                    
                    result = await conn.fetchrow("""
                        UPDATE matdir 
                        SET mat_factor = $1, mat_amount = $2, oxyfactor = $3, matdir_em = $4, updated_at = NOW()
                        WHERE process_id = $5 AND mat_name = $6
                        RETURNING *
                    """, *params)
                    logger.info(f"🔍 UPDATE 쿼리 실행 완료: {result}")
                else:
                    # 새로운 데이터 삽입
                    logger.info(f"🆕 새로운 데이터 삽입: process_id={matdir_data['process_id']}, mat_name={matdir_data['mat_name']}")
                    
                    # oxyfactor 기본값 설정 (matdir_em은 계산된 값이므로 기본값 불필요)
                    oxyfactor = matdir_data.get('oxyfactor')
                    if oxyfactor is None:
                        oxyfactor = Decimal('1.0000')
                    
                    logger.info(f"🔍 INSERT 쿼리 파라미터: oxyfactor={oxyfactor}, matdir_em={matdir_data['matdir_em']}")
                    logger.info("🔍 INSERT 쿼리 실행 시작")
                    
                    # 파라미터 값을 개별적으로 로깅
                    logger.info(f"🔍 파라미터 1 (process_id): {matdir_data['process_id']} (타입: {type(matdir_data['process_id'])})")
                    logger.info(f"🔍 파라미터 2 (mat_name): {matdir_data['mat_name']} (타입: {type(matdir_data['mat_name'])})")
                    logger.info(f"🔍 파라미터 3 (mat_factor): {matdir_data['mat_factor']} (타입: {type(matdir_data['mat_factor'])})")
                    logger.info(f"🔍 파라미터 4 (mat_amount): {matdir_data['mat_amount']} (타입: {type(matdir_data['mat_amount'])})")
                    logger.info(f"🔍 파라미터 5 (oxyfactor): {oxyfactor} (타입: {type(oxyfactor)})")
                    logger.info(f"🔍 파라미터 6 (matdir_em): {matdir_data['matdir_em']} (타입: {type(matdir_data['matdir_em'])})")
                    
                    # 파라미터 튜플을 명시적으로 생성
                    params = (
                        matdir_data['process_id'],
                        matdir_data['mat_name'],
                        matdir_data['mat_factor'],
                        matdir_data['mat_amount'],
                        oxyfactor,
                        matdir_data['matdir_em']
                    )
                    
                    logger.info(f"🔍 최종 파라미터 튜플: {params}")
                    logger.info(f"🔍 파라미터 개수: {len(params)}")
                    
                    result = await conn.fetchrow("""
                        INSERT INTO matdir (process_id, mat_name, mat_factor, mat_amount, oxyfactor, matdir_em)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING *
                    """, *params)
                    logger.info(f"🔍 INSERT 쿼리 실행 완료: {result}")
                
                action = "업데이트" if existing_record else "생성"
                logger.info(f"✅ MatDir {action} 성공: ID {result['id']}")
                return dict(result)
                
        except Exception as e:
            logger.error(f"❌ MatDir 생성/업데이트 실패: {str(e)}")
            logger.error(f"❌ 에러 타입: {type(e)}")
            logger.error(f"❌ 에러 상세: {e}")
            raise

    async def get_matdirs(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 원료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_matdirs_db(skip, limit)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 목록 조회 실패: {str(e)}")
            raise

    async def get_matdirs_by_process(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 원료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_matdirs_by_process_db(process_id)
        except Exception as e:
            logger.error(f"❌ 공정별 원료직접배출량 데이터 조회 실패: {str(e)}")
            raise

    async def get_matdir(self, matdir_id: int) -> Optional[Dict[str, Any]]:
        """특정 원료직접배출량 데이터 조회"""
        await self._ensure_pool_initialized()
        try:
            return await self._get_matdir_db(matdir_id)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 조회 실패: {str(e)}")
            raise

    async def update_matdir(self, matdir_id: int, matdir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """원료직접배출량 데이터 수정"""
        await self._ensure_pool_initialized()
        try:
            return await self._update_matdir_db(matdir_id, matdir_data)
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 데이터 수정 실패: {str(e)}")
            raise

    async def delete_matdir(self, matdir_id) -> bool:
        """원료직접배출량 데이터 삭제 - BIGINT ID 지원"""
        try:
            return await self._delete_matdir_db(matdir_id)
        except Exception as e:
            logger.error(f"❌ MatDir 삭제 실패: {str(e)}")
            return False

    def calculate_matdir_emission(self, mat_amount: Decimal, mat_factor: Decimal, oxyfactor: Decimal = Decimal('1.0000')) -> Decimal:
        """원료직접배출량 계산: matdir_em = mat_amount * mat_factor * oxyfactor"""
        return mat_amount * mat_factor * oxyfactor

    async def get_total_matdir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 원료직접배출량 계산"""
        matdirs = await self.get_matdirs_by_process(process_id)
        total_emission = sum(Decimal(str(matdir['matdir_em'])) for matdir in matdirs if matdir['matdir_em'])
        return total_emission

    # ============================================================================
    # 🏗️ Material Master 조회 메서드들 (새로 추가)
    # ============================================================================

    async def get_material_by_name(self, mat_name: str) -> Optional[Dict[str, Any]]:
        """원료명으로 마스터 데이터 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT id, mat_name, mat_engname, carbon_content, mat_factor
                    FROM material_master
                    WHERE mat_name = $1
                """, mat_name)
                
                if result:
                    logger.info(f"✅ 원료 마스터 조회 성공: {mat_name}")
                    return dict(result)
                else:
                    logger.warning(f"⚠️ 원료 마스터 데이터를 찾을 수 없음: {mat_name}")
                    return None
                
        except Exception as e:
            logger.error(f"❌ 원료 마스터 조회 실패: {str(e)}")
            return None
                
        except Exception as e:
            logger.error(f"❌ 원료 마스터 조회 실패: {str(e)}")
            return None

    async def search_materials(self, search_term: str) -> List[Dict[str, Any]]:
        """원료명으로 검색 (부분 검색)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, mat_name, mat_engname, carbon_content, mat_factor
                    FROM material_master
                    WHERE mat_name ILIKE $1 OR mat_engname ILIKE $1
                    ORDER BY mat_name
                """, f'%{search_term}%')
                
                logger.info(f"✅ 원료 마스터 검색 성공: '{search_term}' → {len(results)}개 결과")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 원료 마스터 검색 실패: {str(e)}")
            return []

    async def get_all_materials(self) -> List[Dict[str, Any]]:
        """모든 원료 마스터 데이터 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, mat_name, mat_engname, carbon_content, mat_factor
                    FROM material_master
                    ORDER BY mat_name
                """)
                
                logger.info(f"✅ 모든 원료 마스터 조회 성공: {len(results)}개")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 모든 원료 마스터 조회 실패: {str(e)}")
            return []

    async def get_material_factor_by_name(self, mat_name: str) -> Optional[Dict[str, Any]]:
        """원료명으로 배출계수만 조회 (간단한 응답)"""
        try:
            material = await self.get_material_by_name(mat_name)
            if material:
                return {
                    'mat_name': material['mat_name'],
                    'mat_factor': float(material['mat_factor']),
                    'carbon_content': float(material['carbon_content']) if material['carbon_content'] else None,
                    'found': True
                }
            else:
                return {
                    'mat_name': mat_name,
                    'mat_factor': None,
                    'carbon_content': None,
                    'found': False
                }
                
        except Exception as e:
            logger.error(f"❌ 배출계수 조회 실패: {str(e)}")
            return {
                'mat_name': mat_name,
                'mat_factor': None,
                'carbon_content': None,
                'found': False
            }

    # ============================================================================
    # 📋 기존 DB 작업 메서드들
    # ============================================================================

    async def _get_matdirs_db(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 원료직접배출량 데이터 조회 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM matdir 
                    ORDER BY created_at DESC 
                    OFFSET $1 LIMIT $2
                """, skip, limit)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ MatDir 목록 조회 실패: {str(e)}")
            raise

    async def _get_matdirs_by_process_db(self, process_id: int) -> List[Dict[str, Any]]:
        """특정 공정의 원료직접배출량 데이터 조회 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT * FROM matdir 
                    WHERE process_id = $1 
                    ORDER BY created_at DESC
                """, process_id)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ MatDir 조회 실패: {str(e)}")
            raise

    async def _get_matdir_db(self, matdir_id: int) -> Optional[Dict[str, Any]]:
        """특정 원료직접배출량 데이터 조회 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT * FROM matdir WHERE id = $1
                """, matdir_id)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ MatDir 조회 실패: {str(e)}")
            raise

    async def _update_matdir_db(self, matdir_id: int, matdir_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """원료직접배출량 데이터 수정 (DB 작업)"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # None 값과 잘못된 데이터 필터링
                filtered_data = {k: v for k, v in matdir_data.items() if v is not None}
                
                if not filtered_data:
                    raise Exception("업데이트할 데이터가 없습니다.")
                
                # 업데이트할 필드들만 동적으로 생성 (파라미터 수 정확하게 맞춤)
                set_fields = list(filtered_data.keys())
                set_clause = ", ".join([f"{field} = ${i+1}" for i, field in enumerate(set_fields)])
                values = list(filtered_data.values())
                
                # updated_at과 WHERE 절을 위한 추가 파라미터
                updated_at_param = len(values) + 1
                where_param = len(values) + 2
                
                query = f"""
                    UPDATE matdir 
                    SET {set_clause}, updated_at = ${updated_at_param}
                    WHERE id = ${where_param} 
                    RETURNING *
                """
                
                # updated_at과 matdir_id를 values에 추가
                final_values = values + [datetime.now(), matdir_id]
                
                logger.info(f"🔍 UPDATE 쿼리: {query}")
                logger.info(f"🔍 UPDATE 파라미터: {final_values}")
                
                result = await conn.fetchrow(query, *final_values)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ MatDir 수정 실패: {str(e)}")
            raise

    async def _delete_matdir_db(self, matdir_id) -> bool:
        """원료직접배출량 데이터 삭제 (DB 작업) - BIGINT ID 지원"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
            
        try:
            async with self.pool.acquire() as conn:
                # ID를 문자열로 변환하여 BIGINT 범위 지원
                matdir_id_str = str(matdir_id)
                result = await conn.execute("""
                    DELETE FROM matdir WHERE id = $1
                """, matdir_id_str)
                
                return result != "DELETE 0"
                
        except Exception as e:
            logger.error(f"❌ MatDir 삭제 실패: {str(e)}")
            raise

    # ============================================================================
    # 🔍 원료명 조회 관련 메서드들 (Railway DB의 materials 테이블 사용)
    # ============================================================================

    async def lookup_material_by_name(self, mat_name: str) -> List[Dict[str, Any]]:
        """원료명으로 배출계수 조회 (자동 매핑 기능) - Railway DB의 material_master 테이블 사용"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT id, mat_name, mat_engname, 
                           mat_factor, carbon_content
                    FROM material_master 
                    WHERE mat_name ILIKE $1 
                    ORDER BY mat_name
                """, f"%{mat_name}%")
                
                logger.info(f"✅ 원료명 조회 성공: '{mat_name}' → {len(results)}개 결과")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 원료명 조회 실패: {str(e)}")
            raise
