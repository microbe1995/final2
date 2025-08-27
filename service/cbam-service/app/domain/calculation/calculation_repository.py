# ============================================================================
# 📦 Calculation Repository - Product 데이터 접근
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os

logger = logging.getLogger(__name__)

class CalculationRepository:
    """Product 데이터 접근 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise Exception("DATABASE_URL 환경변수가 설정되지 않았습니다.")
        
        self._initialize_database()
    
    def _initialize_database(self):
        """데이터베이스 초기화"""
        try:
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            # 데이터베이스 연결 테스트
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            conn.close()
            
            logger.info("✅ 데이터베이스 연결 성공")
            self._create_tables()
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            raise
    
    def _create_tables(self):
        """필요한 테이블들을 생성합니다"""
        try:
            import psycopg2
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cursor:
                # product 테이블이 이미 존재하는지 확인
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'product'
                    );
                """)
                
                if not cursor.fetchone()[0]:
                    logger.info("⚠️ product 테이블이 존재하지 않습니다. 수동으로 생성해주세요.")
                
                conn.commit()
                logger.info("✅ 데이터베이스 테이블 확인 완료")
                
        except Exception as e:
            logger.error(f"❌ 테이블 생성 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 📦 Product 관련 메서드
    # ============================================================================
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """제품 생성"""
        try:
            return await self._create_product_db(product_data)
        except Exception as e:
            logger.error(f"❌ 제품 생성 실패: {str(e)}")
            raise
    
    async def get_products(self) -> List[Dict[str, Any]]:
        """제품 목록 조회"""
        try:
            return await self._get_products_db()
        except Exception as e:
            logger.error(f"❌ 제품 목록 조회 실패: {str(e)}")
            raise
    
    async def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """특정 제품 조회"""
        try:
            return await self._get_product_db(product_id)
        except Exception as e:
            logger.error(f"❌ 제품 조회 실패: {str(e)}")
            raise
    
    async def update_product(self, product_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """제품 수정"""
        try:
            return await self._update_product_db(product_id, update_data)
        except Exception as e:
            logger.error(f"❌ 제품 수정 실패: {str(e)}")
            raise
    
    async def delete_product(self, product_id: int) -> bool:
        """제품 삭제"""
        try:
            return await self._delete_product_db(product_id)
        except Exception as e:
            logger.error(f"❌ 제품 삭제 실패: {str(e)}")
            raise
    
    # ============================================================================
    # 🗄️ Database 메서드들
    # ============================================================================
    
    async def _create_product_db(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스에 제품 생성"""
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO product (
                        install_id, product_name, product_category, 
                        prostart_period, proend_period, product_amount,
                        product_cncode, goods_name, aggrgoods_name,
                        product_sell, product_eusell
                    ) VALUES (
                        %(install_id)s, %(product_name)s, %(product_category)s,
                        %(prostart_period)s, %(proend_period)s, %(product_amount)s,
                        %(product_cncode)s, %(goods_name)s, %(aggrgoods_name)s,
                        %(product_sell)s, %(product_eusell)s
                    ) RETURNING *
                """, product_data)
                
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    return dict(result)
                else:
                    raise Exception("제품 생성에 실패했습니다.")
                    
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    async def _get_products_db(self) -> List[Dict[str, Any]]:
        """데이터베이스에서 제품 목록 조회"""
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM product ORDER BY id
                """)
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    async def _get_product_db(self, product_id: int) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 특정 제품 조회"""
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM product WHERE id = %s
                """, (product_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    async def _update_product_db(self, product_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """데이터베이스에서 제품 수정"""
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
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
                
                return dict(result) if result else None
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    async def _delete_product_db(self, product_id: int) -> bool:
        """데이터베이스에서 제품 삭제"""
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        conn = psycopg2.connect(self.database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM product WHERE id = %s
                """, (product_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()