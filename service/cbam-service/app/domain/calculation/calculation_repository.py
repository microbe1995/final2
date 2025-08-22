# ============================================================================
# 🧮 Calculation Repository - Product 데이터 접근
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import text
from app.common.database_base import create_database_engine, get_db_session

logger = logging.getLogger(__name__)

class CalculationRepository:
    """Product 데이터 접근 클래스"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory_products: Dict[int, Dict[str, Any]] = {}
        
        if self.use_database:
            logger.info("✅ PostgreSQL Product 저장소 사용")
            self._initialize_database()
        else:
            logger.info("✅ 메모리 Product 저장소 사용")
            self._initialize_memory_data()
    
    def _initialize_database(self):
        """데이터베이스 초기화"""
        try:
            self.engine = create_database_engine()
            self._create_tables()
            logger.info("✅ Product 저장소 데이터베이스 엔진 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 실패: {str(e)}")
            logger.info("메모리 저장소로 폴백")
            self.use_database = False
            self._initialize_memory_data()
    
    def _create_tables(self):
        """필요한 테이블들을 생성합니다"""
        try:
            with self.engine.connect() as conn:
                # 제품 테이블 생성
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS product (
                        product_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        cn_code VARCHAR(50),
                        period_start DATE,
                        period_end DATE,
                        production_qty DECIMAL(10,2) DEFAULT 0,
                        sales_qty DECIMAL(10,2) DEFAULT 0,
                        export_qty DECIMAL(10,2) DEFAULT 0,
                        inventory_qty DECIMAL(10,2) DEFAULT 0,
                        defect_rate DECIMAL(5,4) DEFAULT 0,
                        node_id VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                conn.commit()
                logger.info("✅ 데이터베이스 테이블 생성 완료")
                
        except Exception as e:
            logger.error(f"❌ 테이블 생성 실패: {str(e)}")
            raise
    
    def _initialize_memory_data(self):
        """메모리 데이터 초기화"""
        logger.info("✅ 메모리 Product 저장소 초기화 완료")
    
    # ============================================================================
    # 📦 Product 관련 메서드
    # ============================================================================
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """제품 생성"""
        try:
            if self.use_database:
                return await self._create_product_db(product_data)
            else:
                return self._create_product_memory(product_data)
        except Exception as e:
            logger.error(f"❌ 제품 생성 실패: {str(e)}")
            raise
    
    async def get_products(self) -> List[Dict[str, Any]]:
        """제품 목록 조회"""
        try:
            if self.use_database:
                return await self._get_products_db()
            else:
                return self._get_products_memory()
        except Exception as e:
            logger.error(f"❌ 제품 목록 조회 실패: {str(e)}")
            return []
    
    async def _create_product_db(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 제품 저장"""
        try:
            with self.engine.connect() as conn:
                # 날짜 검증 및 정리
                cleaned_data = self._clean_product_data(product_data)
                
                # 먼저 테이블 구조 확인
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'product'
                """))
                columns = [row[0] for row in result.fetchall()]
                
                # created_at 컬럼이 있는지 확인
                has_created_at = 'created_at' in columns
                
                if has_created_at:
                    query = text("""
                        INSERT INTO product (name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id)
                        VALUES (:name, :cn_code, :period_start, :period_end, :production_qty, :sales_qty, :export_qty, :inventory_qty, :defect_rate, :node_id)
                        RETURNING product_id, name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id, created_at
                    """)
                else:
                    query = text("""
                        INSERT INTO product (name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id)
                        VALUES (:name, :cn_code, :period_start, :period_end, :production_qty, :sales_qty, :export_qty, :inventory_qty, :defect_rate, :node_id)
                        RETURNING product_id, name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id
                    """)
                
                result = conn.execute(query, cleaned_data)
                row = result.fetchone()
                conn.commit()
                
                if row:
                    response_data = {
                        "product_id": row[0],
                        "name": row[1],
                        "cn_code": row[2],
                        "period_start": row[3].isoformat() if row[3] else None,
                        "period_end": row[4].isoformat() if row[4] else None,
                        "production_qty": float(row[5]) if row[5] else 0,
                        "sales_qty": float(row[6]) if row[6] else 0,
                        "export_qty": float(row[7]) if row[7] else 0,
                        "inventory_qty": float(row[8]) if row[8] else 0,
                        "defect_rate": float(row[9]) if row[9] else 0,
                        "node_id": row[10],
                    }
                    
                    # created_at 컬럼이 있으면 추가
                    if has_created_at and len(row) > 11:
                        response_data["created_at"] = row[11].isoformat() if row[11] else None
                    else:
                        response_data["created_at"] = datetime.utcnow().isoformat()
                    
                    return response_data
                return None
        except Exception as e:
            logger.error(f"❌ PostgreSQL 제품 저장 실패: {str(e)}")
            raise
    
    def _clean_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """제품 데이터 정리 및 검증"""
        cleaned_data = product_data.copy()
        
        # 날짜 검증 및 정리
        try:
            # period_start 검증
            if cleaned_data.get('period_start'):
                start_date = str(cleaned_data['period_start'])
                # 잘못된 날짜 형식 수정 (예: 200003-03-04 → 2000-03-04)
                if len(start_date) > 10:
                    start_date = start_date[:10]
                if start_date.count('-') == 2:
                    parts = start_date.split('-')
                    if len(parts[0]) > 4:  # 연도가 4자리보다 큰 경우
                        parts[0] = parts[0][:4]
                    cleaned_data['period_start'] = '-'.join(parts)
            
            # period_end 검증
            if cleaned_data.get('period_end'):
                end_date = str(cleaned_data['period_end'])
                # 잘못된 날짜 형식 수정
                if len(end_date) > 10:
                    end_date = end_date[:10]
                if end_date.count('-') == 2:
                    parts = end_date.split('-')
                    if len(parts[0]) > 4:  # 연도가 4자리보다 큰 경우
                        parts[0] = parts[0][:4]
                    cleaned_data['period_end'] = '-'.join(parts)
            
            # 숫자 필드 검증
            numeric_fields = ['production_qty', 'sales_qty', 'export_qty', 'inventory_qty', 'defect_rate']
            for field in numeric_fields:
                if field in cleaned_data and cleaned_data[field] is not None:
                    try:
                        cleaned_data[field] = float(cleaned_data[field])
                    except (ValueError, TypeError):
                        cleaned_data[field] = 0.0
            
            logger.info(f"✅ 제품 데이터 정리 완료: {cleaned_data}")
            
        except Exception as e:
            logger.warning(f"⚠️ 제품 데이터 정리 중 경고: {str(e)}")
        
        return cleaned_data
    
    async def _get_products_db(self) -> List[Dict[str, Any]]:
        """PostgreSQL에서 제품 목록 조회"""
        try:
            with self.engine.connect() as conn:
                # 먼저 테이블 구조 확인
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'product'
                """))
                columns = [row[0] for row in result.fetchall()]
                
                # created_at 컬럼이 있는지 확인
                has_created_at = 'created_at' in columns
                
                if has_created_at:
                    query = text("""
                        SELECT product_id, name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id, created_at
                        FROM product
                        ORDER BY created_at DESC
                    """)
                else:
                    query = text("""
                        SELECT product_id, name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id
                        FROM product
                        ORDER BY product_id DESC
                    """)
                
                result = conn.execute(query)
                products = []
                
                for row in result:
                    product_data = {
                        "product_id": row[0],
                        "name": row[1],
                        "cn_code": row[2],
                        "period_start": row[3].isoformat() if row[3] else None,
                        "period_end": row[4].isoformat() if row[4] else None,
                        "production_qty": float(row[5]) if row[5] else 0,
                        "sales_qty": float(row[6]) if row[6] else 0,
                        "export_qty": float(row[7]) if row[7] else 0,
                        "inventory_qty": float(row[8]) if row[8] else 0,
                        "defect_rate": float(row[9]) if row[9] else 0,
                        "node_id": row[10],
                    }
                    
                    # created_at 컬럼이 있으면 추가
                    if has_created_at and len(row) > 11:
                        product_data["created_at"] = row[11].isoformat() if row[11] else None
                    else:
                        product_data["created_at"] = datetime.utcnow().isoformat()
                    
                    products.append(product_data)
                
                return products
        except Exception as e:
            logger.error(f"❌ PostgreSQL 제품 목록 조회 실패: {str(e)}")
            return []
    
    def _create_product_memory(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 제품 저장"""
        product_id = len(self._memory_products) + 1
        product = {
            **product_data,
            "product_id": product_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self._memory_products[product_id] = product
        return product
    
    def _get_products_memory(self) -> List[Dict[str, Any]]:
        """메모리에서 제품 목록 조회"""
        return list(self._memory_products.values())