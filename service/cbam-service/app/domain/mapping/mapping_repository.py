# ============================================================================
# 🗄️ Mapping Repository - HS-CN 매핑 데이터베이스 접근 계층
# ============================================================================

import os
import logging
from typing import List, Optional, Dict, Any
import asyncpg

from app.domain.mapping.mapping_schema import HSCNMappingCreateRequest, HSCNMappingUpdateRequest

logger = logging.getLogger(__name__)

class HSCNMappingRepository:
    """HS-CN 매핑 데이터베이스 리포지토리 (asyncpg 연결 풀)"""
    
    def __init__(self, db_session=None):
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
                    'application_name': 'cbam-service-mapping'
                }
            )
            logger.info("✅ Mapping 데이터베이스 연결 풀 생성 성공")
            
        except Exception as e:
            logger.error(f"❌ Mapping 데이터베이스 연결 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
    # ============================================================================
    # 📋 기본 CRUD 작업
    # ============================================================================
    
    async def create_mapping(self, mapping_data: HSCNMappingCreateRequest) -> Optional[Dict[str, Any]]:
        """HS-CN 매핑 생성"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                INSERT INTO hs_cn_mapping (hscode, aggregoods_name, aggregoods_engname, 
                                         cncode_total, goods_name, goods_engname)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, hscode, aggregoods_name, aggregoods_engname, 
                          cncode_total, goods_name, goods_engname
                """, (
                    mapping_data.hscode,
                    mapping_data.aggregoods_name,
                    mapping_data.aggregoods_engname,
                    mapping_data.cncode_total,
                    mapping_data.goods_name,
                    mapping_data.goods_engname
                ))
                
                if result:
                    logger.info(f"✅ HS-CN 매핑 생성 성공: ID {result['id']}")
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 생성 실패: {str(e)}")
            return None
    
    async def get_mapping_by_id(self, mapping_id: int) -> Optional[Dict[str, Any]]:
        """ID로 HS-CN 매핑 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow("""
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                WHERE id = $1
                """, mapping_id)
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 조회 실패: {str(e)}")
            return None
    
    async def get_all_mappings(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 HS-CN 매핑 조회 (페이지네이션)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                ORDER BY id
                OFFSET $1 LIMIT $2
                """, skip, limit)
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 목록 조회 실패: {str(e)}")
            return []
    
    async def update_mapping(self, mapping_id: int, mapping_data: HSCNMappingUpdateRequest) -> Optional[Dict[str, Any]]:
        """HS-CN 매핑 수정"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                # 업데이트할 필드만 동적으로 생성
                update_data = mapping_data.dict(exclude_unset=True)
                if not update_data:
                    return await self.get_mapping_by_id(mapping_id)
                
                set_clause = ", ".join([f"{key} = ${i+1}" for i, key in enumerate(update_data.keys())])
                values = list(update_data.values()) + [mapping_id]
                
                query = f"""
                UPDATE hs_cn_mapping 
                SET {set_clause}
                WHERE id = ${len(update_data) + 1} 
                RETURNING id, hscode, aggregoods_name, aggregoods_engname, 
                          cncode_total, goods_name, goods_engname
                """
                
                result = await conn.fetchrow(query, *values)
                
                if result:
                    logger.info(f"✅ HS-CN 매핑 수정 성공: ID {mapping_id}")
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 수정 실패: {str(e)}")
            return None
    
    async def delete_mapping(self, mapping_id: int) -> bool:
        """HS-CN 매핑 삭제"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("""
                    DELETE FROM hs_cn_mapping WHERE id = $1
                """, mapping_id)
                
                success = result != "DELETE 0"
                if success:
                    logger.info(f"✅ HS-CN 매핑 삭제 성공: ID {mapping_id}")
                else:
                    logger.warning(f"⚠️ HS-CN 매핑 삭제 실패: ID {mapping_id} (존재하지 않음)")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 삭제 실패: {str(e)}")
            return False
    
    # ============================================================================
    # 🔍 HS 코드 조회 기능
    # ============================================================================
    
    async def lookup_by_hs_code(self, hs_code: str) -> List[Dict[str, Any]]:
        """HS 코드로 CN 코드 조회 (부분 검색 허용)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                # 부분 검색을 위해 LIKE 연산자 사용
                results = await conn.fetch("""
                    SELECT hscode, cncode_total, goods_name, goods_engname, 
                           aggregoods_name, aggregoods_engname
                    FROM hs_cn_mapping 
                    WHERE hscode LIKE $1
                    ORDER BY hscode, cncode_total
                """, f"{hs_code}%")
                
                logger.info(f"🔍 HS 코드 조회: {hs_code}, 결과: {len(results)}개")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ HS 코드 조회 실패: {str(e)}")
            return []
    
    async def search_by_hs_code(self, hs_code: str) -> List[Dict[str, Any]]:
        """HS 코드로 검색 (부분 일치)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                WHERE hscode LIKE $1
                ORDER BY hscode, cncode_total
                """, f"{hs_code}%")
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ HS 코드 검색 실패: {str(e)}")
            return []
    
    async def search_by_cn_code(self, cn_code: str) -> List[Dict[str, Any]]:
        """CN 코드로 검색 (부분 일치)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                WHERE cncode_total LIKE $1
                ORDER BY cncode_total, hscode
                """, f"{cn_code}%")
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ CN 코드 검색 실패: {str(e)}")
            return []
    
    async def search_by_goods_name(self, goods_name: str) -> List[Dict[str, Any]]:
        """품목명으로 검색 (부분 일치)"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                results = await conn.fetch("""
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                WHERE goods_name ILIKE $1 OR goods_engname ILIKE $1
                ORDER BY goods_name, hscode
                """, f"%{goods_name}%")
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 품목명 검색 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_mapping_stats(self) -> Dict[str, Any]:
        """매핑 통계 조회"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                total_mappings = await conn.fetchval("SELECT COUNT(*) FROM hs_cn_mapping")
                unique_hscodes = await conn.fetchval("SELECT COUNT(DISTINCT hscode) FROM hs_cn_mapping")
                unique_cncodes = await conn.fetchval("SELECT COUNT(DISTINCT cncode_total) FROM hs_cn_mapping")
                
                return {
                    'total_mappings': total_mappings or 0,
                    'unique_hscodes': unique_hscodes or 0,
                    'unique_cncodes': unique_cncodes or 0,
                    'last_updated': None
                }
                
        except Exception as e:
            logger.error(f"❌ 매핑 통계 조회 실패: {str(e)}")
            return {
                'total_mappings': 0,
                'unique_hscodes': 0,
                'unique_cncodes': 0
            }
    
    # ============================================================================
    # 📦 일괄 처리
    # ============================================================================
    
    async def create_mappings_batch(self, mappings_data: List[HSCNMappingCreateRequest]) -> Dict[str, Any]:
        """HS-CN 매핑 일괄 생성"""
        await self._ensure_pool_initialized()
        
        try:
            async with self.pool.acquire() as conn:
                created_count = 0
                failed_count = 0
                errors = []
                
                for mapping_data in mappings_data:
                    try:
                        await conn.execute("""
                        INSERT INTO hs_cn_mapping (hscode, aggregoods_name, aggregoods_engname, 
                                                 cncode_total, goods_name, goods_engname)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        """, (
                            mapping_data.hscode,
                            mapping_data.aggregoods_name,
                            mapping_data.aggregoods_engname,
                            mapping_data.cncode_total,
                            mapping_data.goods_name,
                            mapping_data.goods_engname
                        ))
                        
                        created_count += 1
                        
                    except Exception as e:
                        failed_count += 1
                        errors.append(f"매핑 생성 실패: {str(e)}")
                
                logger.info(f"✅ 일괄 매핑 생성 완료: 성공 {created_count}개, 실패 {failed_count}개")
                
                return {
                    'created_count': created_count,
                    'failed_count': failed_count,
                    'errors': errors
                }
                
        except Exception as e:
            logger.error(f"❌ 일괄 매핑 생성 실패: {str(e)}")
            return {
                'created_count': 0,
                'failed_count': len(mappings_data),
                'errors': [f"일괄 처리 실패: {str(e)}"]
            }
