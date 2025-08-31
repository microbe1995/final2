# ============================================================================
# 🗄️ Mapping Repository - HS-CN 매핑 데이터베이스 접근 계층
# ============================================================================

import os
import logging
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


from app.domain.mapping.mapping_schema import HSCNMappingCreateRequest, HSCNMappingUpdateRequest

logger = logging.getLogger(__name__)

class HSCNMappingRepository:
    """HS-CN 매핑 데이터베이스 리포지토리 (psycopg2 직접 연결)"""
    
    def __init__(self, db_session=None):
        # 설정에서 데이터베이스 URL 가져오기
        self.database_url = os.getenv('DATABASE_URL')
    
    # ============================================================================
    # 📋 기본 CRUD 작업
    # ============================================================================
    
    async def create_mapping(self, mapping_data: HSCNMappingCreateRequest) -> Optional[Dict[str, Any]]:
        """HS-CN 매핑 생성"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                insert_sql = """
                INSERT INTO hs_cn_mapping (hscode, aggregoods_name, aggregoods_engname, 
                                         cncode_total, goods_name, goods_engname)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, hscode, aggregoods_name, aggregoods_engname, 
                          cncode_total, goods_name, goods_engname
                """
                
                cursor.execute(insert_sql, (
                    mapping_data.hscode,
                    mapping_data.aggregoods_name,
                    mapping_data.aggregoods_engname,
                    mapping_data.cncode_total,
                    mapping_data.goods_name,
                    mapping_data.goods_engname
                ))
                
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    logger.info(f"✅ HS-CN 매핑 생성 성공: ID {result['id']}")
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 생성 실패: {str(e)}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def get_mapping_by_id(self, mapping_id: int) -> Optional[Dict[str, Any]]:
        """ID로 HS-CN 매핑 조회"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                WHERE id = %s
                """
                
                cursor.execute(query, (mapping_id,))
                result = cursor.fetchone()
                
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 조회 실패: {str(e)}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def get_all_mappings(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 HS-CN 매핑 조회 (페이지네이션)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                ORDER BY id
                OFFSET %s LIMIT %s
                """
                
                cursor.execute(query, (skip, limit))
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 목록 조회 실패: {str(e)}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def update_mapping(self, mapping_id: int, mapping_data: HSCNMappingUpdateRequest) -> Optional[Dict[str, Any]]:
        """HS-CN 매핑 수정"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 업데이트할 필드만 동적으로 생성
                update_data = mapping_data.dict(exclude_unset=True)
                if not update_data:
                    return await self.get_mapping_by_id(mapping_id)
                
                set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
                values = list(update_data.values()) + [mapping_id]
                
                query = f"""
                UPDATE hs_cn_mapping 
                SET {set_clause}
                WHERE id = %s 
                RETURNING id, hscode, aggregoods_name, aggregoods_engname, 
                          cncode_total, goods_name, goods_engname
                """
                
                cursor.execute(query, values)
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    logger.info(f"✅ HS-CN 매핑 수정 성공: ID {mapping_id}")
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 수정 실패: {str(e)}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def delete_mapping(self, mapping_id: int) -> bool:
        """HS-CN 매핑 삭제"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                query = "DELETE FROM hs_cn_mapping WHERE id = %s"
                cursor.execute(query, (mapping_id,))
                conn.commit()
                
                success = cursor.rowcount > 0
                if success:
                    logger.info(f"✅ HS-CN 매핑 삭제 성공: ID {mapping_id}")
                else:
                    logger.warning(f"⚠️ HS-CN 매핑 삭제 실패: ID {mapping_id} (존재하지 않음)")
                
                return success
                
        except Exception as e:
            logger.error(f"❌ HS-CN 매핑 삭제 실패: {str(e)}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()
    
    # ============================================================================
    # 🔍 HS 코드 조회 기능
    # ============================================================================
    
    async def lookup_by_hs_code(self, hs_code: str) -> List[Dict[str, Any]]:
        """HS 코드로 CN 코드 조회 (부분 검색 허용)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # 부분 검색을 위해 LIKE 연산자 사용
                query = """
                    SELECT hscode, cncode_total, goods_name, goods_engname, 
                           aggregoods_name, aggregoods_engname
                    FROM hs_cn_mapping 
                    WHERE hscode LIKE %s
                    ORDER BY hscode, cncode_total
                """
                
                cursor.execute(query, (f"{hs_code}%",))
                results = cursor.fetchall()
                
                logger.info(f"🔍 HS 코드 조회: {hs_code}, 결과: {len(results)}개")
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ HS 코드 조회 실패: {str(e)}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def search_by_hs_code(self, hs_code: str) -> List[Dict[str, Any]]:
        """HS 코드로 검색 (부분 일치)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                WHERE hscode LIKE %s
                ORDER BY hscode, cncode_total
                """
                
                cursor.execute(query, (f"{hs_code}%",))
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ HS 코드 검색 실패: {str(e)}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def search_by_cn_code(self, cn_code: str) -> List[Dict[str, Any]]:
        """CN 코드로 검색 (부분 일치)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                WHERE cncode_total LIKE %s
                ORDER BY cncode_total, hscode
                """
                
                cursor.execute(query, (f"{cn_code}%",))
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ CN 코드 검색 실패: {str(e)}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    async def search_by_goods_name(self, goods_name: str) -> List[Dict[str, Any]]:
        """품목명으로 검색 (부분 일치)"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                SELECT id, hscode, aggregoods_name, aggregoods_engname, 
                       cncode_total, goods_name, goods_engname
                FROM hs_cn_mapping 
                WHERE goods_name ILIKE %s OR goods_engname ILIKE %s
                ORDER BY goods_name, hscode
                """
                
                cursor.execute(query, (f"%{goods_name}%", f"%{goods_name}%"))
                results = cursor.fetchall()
                
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"❌ 품목명 검색 실패: {str(e)}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_mapping_stats(self) -> Dict[str, Any]:
        """매핑 통계 조회"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM hs_cn_mapping")
                total_mappings = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT hscode) FROM hs_cn_mapping")
                unique_hscodes = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT cncode_total) FROM hs_cn_mapping")
                unique_cncodes = cursor.fetchone()[0]
                
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
        finally:
            if 'conn' in locals():
                conn.close()
    
    # ============================================================================
    # 📦 일괄 처리
    # ============================================================================
    
    async def create_mappings_batch(self, mappings_data: List[HSCNMappingCreateRequest]) -> Dict[str, Any]:
        """HS-CN 매핑 일괄 생성"""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            created_count = 0
            failed_count = 0
            errors = []
            
            with conn.cursor() as cursor:
                for mapping_data in mappings_data:
                    try:
                        insert_sql = """
                        INSERT INTO hs_cn_mapping (hscode, aggregoods_name, aggregoods_engname, 
                                                 cncode_total, goods_name, goods_engname)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        
                        cursor.execute(insert_sql, (
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
                
                conn.commit()
            
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
        finally:
            if 'conn' in locals():
                conn.close()
