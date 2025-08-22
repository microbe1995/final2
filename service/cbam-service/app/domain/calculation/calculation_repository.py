# ============================================================================
# 🧮 Calculation Repository - CBAM 계산 데이터 접근
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import text
from app.common.database_base import create_database_engine, get_db_session

logger = logging.getLogger(__name__)

class CalculationRepository:
    """계산 데이터 접근 클래스"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory_fuels: Dict[str, Dict[str, Any]] = {}
        self._memory_materials: Dict[str, Dict[str, Any]] = {}
        self._memory_precursors: Dict[int, Dict[str, Any]] = {}
        self._memory_results: Dict[int, Dict[str, Any]] = {}
        self._memory_products: Dict[int, Dict[str, Any]] = {}
        
        if self.use_database:
            logger.info("✅ PostgreSQL 계산 저장소 사용")
            self._initialize_database()
        else:
            logger.info("✅ 메모리 계산 저장소 사용")
            self._initialize_memory_data()
    
    def _initialize_database(self):
        """데이터베이스 초기화"""
        try:
            self.engine = create_database_engine()
            self._create_tables()
            logger.info("✅ 계산 저장소 데이터베이스 엔진 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 실패: {str(e)}")
            logger.info("메모리 저장소로 폴백")
            self.use_database = False
            self._initialize_memory_data()
    
    def _create_tables(self):
        """필요한 테이블들을 생성합니다"""
        try:
            with self.engine.connect() as conn:
                # 연료 테이블 생성
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS fuels (
                        id SERIAL PRIMARY KEY,
                        fuel_name VARCHAR(255) NOT NULL,
                        fuel_eng VARCHAR(255),
                        fuel_emfactor DECIMAL(10,2),
                        net_calory DECIMAL(10,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # 원료 테이블 생성
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS materials (
                        id SERIAL PRIMARY KEY,
                        item_name VARCHAR(255) NOT NULL,
                        item_eng VARCHAR(255),
                        carbon_factor DECIMAL(10,2),
                        em_factor DECIMAL(10,2),
                        cn_code VARCHAR(50),
                        cn_code1 VARCHAR(50),
                        cn_code2 VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # 전구물질 테이블 생성
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS precursors (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        calculation_type VARCHAR(50) NOT NULL,
                        fuel_id INTEGER,
                        material_id INTEGER,
                        quantity DECIMAL(10,2) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (fuel_id) REFERENCES fuels(id),
                        FOREIGN KEY (material_id) REFERENCES materials(id)
                    )
                """))
                
                # 계산 결과 테이블 생성
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS calculation_results (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        calculation_type VARCHAR(50) NOT NULL,
                        fuel_id INTEGER,
                        material_id INTEGER,
                        quantity DECIMAL(10,2) NOT NULL,
                        result_data JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (fuel_id) REFERENCES fuels(id),
                        FOREIGN KEY (material_id) REFERENCES materials(id)
                    )
                """))
                
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
                
                # 샘플 데이터 삽입 (테이블이 비어있을 때만)
                self._insert_sample_data(conn)
                
                conn.commit()
                logger.info("✅ 데이터베이스 테이블 생성 완료")
                
        except Exception as e:
            logger.error(f"❌ 테이블 생성 실패: {str(e)}")
            raise
    
    def _insert_sample_data(self, conn):
        """샘플 데이터를 삽입합니다"""
        try:
            # 연료 샘플 데이터 확인 및 삽입
            result = conn.execute(text("SELECT COUNT(*) FROM fuels"))
            if result.scalar() == 0:
                conn.execute(text("""
                    INSERT INTO fuels (fuel_name, fuel_eng, fuel_emfactor, net_calory) VALUES
                    ('천연가스', 'Natural Gas', 56.1, 48.0),
                    ('석탄', 'Coal', 94.6, 25.8),
                    ('중유', 'Heavy Oil', 77.4, 40.4)
                """))
                logger.info("✅ 연료 샘플 데이터 삽입 완료")
            
            # 원료 샘플 데이터 확인 및 삽입
            result = conn.execute(text("SELECT COUNT(*) FROM materials"))
            if result.scalar() == 0:
                conn.execute(text("""
                    INSERT INTO materials (item_name, item_eng, carbon_factor, em_factor, cn_code, cn_code1, cn_code2) VALUES
                    ('철광석', 'Iron Ore', 0.5, 0.024, '2601', '260111', '26011100'),
                    ('석회석', 'Limestone', 12.0, 0.034, '2521', '252100', '25210000')
                """))
                logger.info("✅ 원료 샘플 데이터 삽입 완료")
                
        except Exception as e:
            logger.warning(f"샘플 데이터 삽입 중 경고: {str(e)}")
            # 샘플 데이터 삽입 실패는 치명적이지 않으므로 계속 진행
    
    # ============================================================================
    # 🔥 연료 관련 메서드
    # ============================================================================
    
    async def get_fuel_by_name(self, fuel_name: str) -> Optional[Dict[str, Any]]:
        """연료명으로 연료 정보 조회"""
        try:
            if self.use_database:
                return await self._get_fuel_by_name_db(fuel_name)
            else:
                return self._get_fuel_by_name_memory(fuel_name)
        except Exception as e:
            logger.error(f"❌ 연료 조회 실패: {str(e)}")
            return None
    
    async def search_fuels(self, search: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """연료 검색"""
        try:
            if self.use_database:
                return await self._search_fuels_db(search, limit)
            else:
                return self._search_fuels_memory(search, limit)
        except Exception as e:
            logger.error(f"❌ 연료 검색 실패: {str(e)}")
            return []
    
    async def _get_fuel_by_name_db(self, fuel_name: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 연료명으로 조회"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT id, fuel_name, fuel_eng, fuel_emfactor, net_calory
                    FROM fuels 
                    WHERE LOWER(fuel_name) LIKE LOWER(:fuel_name)
                    LIMIT 1
                """)
                result = conn.execute(query, {"fuel_name": f"%{fuel_name}%"})
                row = result.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "fuel_name": row[1],
                        "fuel_eng": row[2],
                        "fuel_emfactor": float(row[3]) if row[3] else 0.0,
                        "net_calory": float(row[4]) if row[4] else 0.0
                    }
                return None
        except Exception as e:
            logger.error(f"❌ PostgreSQL 연료 조회 실패: {str(e)}")
            return self._get_fuel_by_name_memory(fuel_name)
    
    async def _search_fuels_db(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """PostgreSQL에서 연료 검색"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT id, fuel_name, fuel_eng, fuel_emfactor, net_calory
                    FROM fuels 
                    WHERE LOWER(fuel_name) LIKE LOWER(:search)
                    ORDER BY fuel_name
                    LIMIT :limit
                """)
                result = conn.execute(query, {"search": f"%{search}%", "limit": limit})
                
                fuels = []
                for row in result:
                    fuels.append({
                        "id": row[0],
                        "fuel_name": row[1],
                        "fuel_eng": row[2],
                        "fuel_emfactor": float(row[3]) if row[3] else 0.0,
                        "net_calory": float(row[4]) if row[4] else 0.0
                    })
                return fuels
        except Exception as e:
            logger.error(f"❌ PostgreSQL 연료 검색 실패: {str(e)}")
            return self._search_fuels_memory(search, limit)
    
    def _get_fuel_by_name_memory(self, fuel_name: str) -> Optional[Dict[str, Any]]:
        """메모리에서 연료명으로 조회"""
        for fuel in self._memory_fuels.values():
            if fuel_name.lower() in fuel["fuel_name"].lower():
                return fuel
        return None
    
    def _search_fuels_memory(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """메모리에서 연료 검색"""
        results = []
        for fuel in self._memory_fuels.values():
            if not search or search.lower() in fuel["fuel_name"].lower():
                results.append(fuel)
                if len(results) >= limit:
                    break
        return results
    
    # ============================================================================
    # 🧱 원료 관련 메서드
    # ============================================================================
    
    async def get_material_by_name(self, material_name: str) -> Optional[Dict[str, Any]]:
        """원료명으로 원료 정보 조회"""
        try:
            if self.use_database:
                return await self._get_material_by_name_db(material_name)
            else:
                return self._get_material_by_name_memory(material_name)
        except Exception as e:
            logger.error(f"❌ 원료 조회 실패: {str(e)}")
            return None
    
    async def search_materials(self, search: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """원료 검색"""
        try:
            if self.use_database:
                return await self._search_materials_db(search, limit)
            else:
                return self._search_materials_memory(search, limit)
        except Exception as e:
            logger.error(f"❌ 원료 검색 실패: {str(e)}")
            return []
    
    async def _get_material_by_name_db(self, material_name: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 원료명으로 조회"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT id, item_name, item_eng, carbon_factor, em_factor, cn_code, cn_code1, cn_code2
                    FROM materials 
                    WHERE LOWER(item_name) LIKE LOWER(:material_name)
                    LIMIT 1
                """)
                result = conn.execute(query, {"material_name": f"%{material_name}%"})
                row = result.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "item_name": row[1],
                        "item_eng": row[2],
                        "carbon_factor": float(row[3]) if row[3] else 0.0,
                        "em_factor": float(row[4]) if row[4] else 0.0,
                        "cn_code": row[5],
                        "cn_code1": row[6],
                        "cn_code2": row[7]
                    }
                return None
        except Exception as e:
            logger.error(f"❌ PostgreSQL 원료 조회 실패: {str(e)}")
            return self._get_material_by_name_memory(material_name)
    
    async def _search_materials_db(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """PostgreSQL에서 원료 검색"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT id, item_name, item_eng, carbon_factor, em_factor, cn_code, cn_code1, cn_code2
                    FROM materials 
                    WHERE LOWER(item_name) LIKE LOWER(:search)
                    ORDER BY item_name
                    LIMIT :limit
                """)
                result = conn.execute(query, {"search": f"%{search}%", "limit": limit})
                
                materials = []
                for row in result:
                    materials.append({
                        "id": row[0],
                        "item_name": row[1],
                        "item_eng": row[2],
                        "carbon_factor": float(row[3]) if row[3] else 0.0,
                        "em_factor": float(row[4]) if row[4] else 0.0,
                        "cn_code": row[5],
                        "cn_code1": row[6],
                        "cn_code2": row[7]
                    })
                return materials
        except Exception as e:
            logger.error(f"❌ PostgreSQL 원료 검색 실패: {str(e)}")
            return self._search_materials_memory(search, limit)
    
    def _get_material_by_name_memory(self, material_name: str) -> Optional[Dict[str, Any]]:
        """메모리에서 원료명으로 조회"""
        for material in self._memory_materials.values():
            if material_name.lower() in material["item_name"].lower():
                return material
        return None
    
    def _search_materials_memory(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """메모리에서 원료 검색"""
        results = []
        for material in self._memory_materials.values():
            if not search or search.lower() in material["item_name"].lower():
                results.append(material)
                if len(results) >= limit:
                    break
        return results
    
    # ============================================================================
    # 🔗 전구물질 관련 메서드
    # ============================================================================
    
    async def create_precursor(self, precursor_data: Dict[str, Any]) -> Dict[str, Any]:
        """전구물질 생성"""
        try:
            if self.use_database:
                return await self._create_precursor_db(precursor_data)
            else:
                return self._create_precursor_memory(precursor_data)
        except Exception as e:
            logger.error(f"❌ 전구물질 생성 실패: {str(e)}")
            raise
    
    async def get_precursor_by_id(self, precursor_id: int) -> Optional[Dict[str, Any]]:
        """전구물질 ID로 조회"""
        try:
            if self.use_database:
                return await self._get_precursor_by_id_db(precursor_id)
            else:
                return self._memory_precursors.get(precursor_id)
        except Exception as e:
            logger.error(f"❌ 전구물질 조회 실패: {str(e)}")
            return None
    
    async def get_precursors_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자 ID로 전구물질 목록 조회"""
        try:
            if self.use_database:
                return await self._get_precursors_by_user_id_db(user_id)
            else:
                return [p for p in self._memory_precursors.values() if p.get("user_id") == user_id]
        except Exception as e:
            logger.error(f"❌ 사용자별 전구물질 조회 실패: {str(e)}")
            return []
    
    async def delete_precursor(self, precursor_id: int) -> bool:
        """전구물질 삭제"""
        try:
            if self.use_database:
                return await self._delete_precursor_db(precursor_id)
            else:
                return self._delete_precursor_memory(precursor_id)
        except Exception as e:
            logger.error(f"❌ 전구물질 삭제 실패: {str(e)}")
            return False
    
    async def _create_precursor_db(self, precursor_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 전구물질 생성"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO precursors (user_id, calculation_type, fuel_id, material_id, quantity, created_at)
                    VALUES (:user_id, :calculation_type, :fuel_id, :material_id, :quantity, NOW())
                    RETURNING id
                """)
                result = conn.execute(query, precursor_data)
                new_precursor_id = result.scalar()
                
                if new_precursor_id:
                    return {**precursor_data, "id": new_precursor_id}
                return None
        except Exception as e:
            logger.error(f"❌ PostgreSQL 전구물질 생성 실패: {str(e)}")
            raise
    
    async def _get_precursor_by_id_db(self, precursor_id: int) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 전구물질 ID로 조회"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT id, user_id, calculation_type, fuel_id, material_id, quantity, created_at
                    FROM precursors
                    WHERE id = :precursor_id
                """)
                result = conn.execute(query, {"precursor_id": precursor_id})
                row = result.fetchone()
                
                if row:
                    return {
                        "id": row[0],
                        "user_id": row[1],
                        "calculation_type": row[2],
                        "fuel_id": row[3],
                        "material_id": row[4],
                        "quantity": float(row[5]) if row[5] else 0.0,
                        "created_at": row[6]
                    }
                return None
        except Exception as e:
            logger.error(f"❌ PostgreSQL 전구물질 조회 실패: {str(e)}")
            return self._memory_precursors.get(precursor_id)
    
    async def _get_precursors_by_user_id_db(self, user_id: str) -> List[Dict[str, Any]]:
        """PostgreSQL에서 사용자별 전구물질 조회"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT id, user_id, calculation_type, fuel_id, material_id, quantity, created_at
                    FROM precursors
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                """)
                result = conn.execute(query, {"user_id": user_id})
                
                precursors = []
                for row in result:
                    precursors.append({
                        "id": row[0],
                        "user_id": row[1],
                        "calculation_type": row[2],
                        "fuel_id": row[3],
                        "material_id": row[4],
                        "quantity": float(row[5]) if row[5] else 0.0,
                        "created_at": row[6]
                    })
                return precursors
        except Exception as e:
            logger.error(f"❌ PostgreSQL 사용자별 전구물질 조회 실패: {str(e)}")
            return [p for p in self._memory_precursors.values() if p.get("user_id") == user_id]
    
    async def _delete_precursor_db(self, precursor_id: int) -> bool:
        """PostgreSQL에서 전구물질 삭제"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    DELETE FROM precursors WHERE id = :precursor_id
                """)
                result = conn.execute(query, {"precursor_id": precursor_id})
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"❌ PostgreSQL 전구물질 삭제 실패: {str(e)}")
            return self._delete_precursor_memory(precursor_id)
    
    def _create_precursor_memory(self, precursor_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 전구물질 생성"""
        precursor_id = len(self._memory_precursors) + 1
        precursor = {
            **precursor_data,
            "id": precursor_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self._memory_precursors[precursor_id] = precursor
        
        logger.info(f"✅ 메모리 전구물질 생성: {precursor_id}")
        return precursor
    
    def _delete_precursor_memory(self, precursor_id: int) -> bool:
        """메모리에서 전구물질 삭제"""
        if precursor_id in self._memory_precursors:
            del self._memory_precursors[precursor_id]
            logger.info(f"✅ 메모리 전구물질 삭제 성공: {precursor_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 전구물질 삭제 실패: 전구물질을 찾을 수 없음 {precursor_id}")
            return False
    
    # ============================================================================
    # 📊 계산 결과 및 통계 메서드
    # ============================================================================
    
    async def save_calculation_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """계산 결과 저장"""
        try:
            if self.use_database:
                return await self._save_calculation_result_db(result_data)
            else:
                return self._save_calculation_result_memory(result_data)
        except Exception as e:
            logger.error(f"❌ 계산 결과 저장 실패: {str(e)}")
            raise
    
    async def get_calculation_stats(self) -> Dict[str, Any]:
        """계산 통계 조회"""
        try:
            if self.use_database:
                return await self._get_calculation_stats_db()
            else:
                return self._get_calculation_stats_memory()
        except Exception as e:
            logger.error(f"❌ 계산 통계 조회 실패: {str(e)}")
            return {}
    
    async def _save_calculation_result_db(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 계산 결과 저장"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO calculation_results (user_id, calculation_type, fuel_id, material_id, quantity, created_at)
                    VALUES (:user_id, :calculation_type, :fuel_id, :material_id, :quantity, NOW())
                    RETURNING id
                """)
                result = conn.execute(query, result_data)
                new_result_id = result.scalar()
                
                if new_result_id:
                    return {**result_data, "id": new_result_id}
                return None
        except Exception as e:
            logger.error(f"❌ PostgreSQL 계산 결과 저장 실패: {str(e)}")
            raise
    
    async def _get_calculation_stats_db(self) -> Dict[str, Any]:
        """PostgreSQL에서 계산 통계 조회"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT 
                        COUNT(*) AS total_calculations,
                        COUNT(CASE WHEN calculation_type = 'fuel' THEN 1 END) AS fuel_calculations,
                        COUNT(CASE WHEN calculation_type = 'material' THEN 1 END) AS material_calculations,
                        COUNT(DISTINCT user_id) AS total_users,
                        COUNT(DISTINCT user_id) FILTER (WHERE user_id IS NOT NULL) AS active_users,
                        COUNT(DISTINCT calculation_type) AS unique_calculation_types
                    FROM calculation_results
                """)
                result = conn.execute(query)
                row = result.fetchone()
                
                if row:
                    return {
                        "total_calculations": row[0],
                        "fuel_calculations": row[1],
                        "material_calculations": row[2],
                        "total_users": row[3],
                        "active_users": row[4],
                        "unique_calculation_types": row[5]
                    }
                return {}
        except Exception as e:
            logger.error(f"❌ PostgreSQL 계산 통계 조회 실패: {str(e)}")
            return self._get_calculation_stats_memory()
    
    def _save_calculation_result_memory(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 계산 결과 저장"""
        result_id = len(self._memory_results) + 1
        result = {
            **result_data,
            "id": result_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self._memory_results[result_id] = result
        return result
    
    def _get_calculation_stats_memory(self) -> Dict[str, Any]:
        """메모리에서 계산 통계 조회"""
        total_calculations = len(self._memory_results)
        fuel_calculations = len([r for r in self._memory_results.values() if r.get("calculation_type") == "fuel"])
        material_calculations = len([r for r in self._memory_results.values() if r.get("calculation_type") == "material"])
        total_precursors = len(self._memory_precursors)
        
        user_ids = set(r.get("user_id") for r in self._memory_results.values())
        active_users = len(user_ids)
        
        calculations_by_type = {}
        for result in self._memory_results.values():
            calc_type = result.get("calculation_type", "unknown")
            calculations_by_type[calc_type] = calculations_by_type.get(calc_type, 0) + 1
        
        return {
            "total_calculations": total_calculations,
            "fuel_calculations": fuel_calculations,
            "material_calculations": material_calculations,
            "total_precursors": total_precursors,
            "active_users": active_users,
            "calculations_by_type": calculations_by_type
        }
    
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
                query = text("""
                    INSERT INTO product (name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id)
                    VALUES (:name, :cn_code, :period_start, :period_end, :production_qty, :sales_qty, :export_qty, :inventory_qty, :defect_rate, :node_id)
                    RETURNING product_id, name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id, created_at
                """)
                result = conn.execute(query, product_data)
                row = result.fetchone()
                conn.commit()
                
                if row:
                    return {
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
                        "created_at": row[11].isoformat() if row[11] else None
                    }
                return None
        except Exception as e:
            logger.error(f"❌ PostgreSQL 제품 저장 실패: {str(e)}")
            raise
    
    async def _get_products_db(self) -> List[Dict[str, Any]]:
        """PostgreSQL에서 제품 목록 조회"""
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT product_id, name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate, node_id, created_at
                    FROM product
                    ORDER BY created_at DESC
                """)
                result = conn.execute(query)
                products = []
                
                for row in result:
                    products.append({
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
                        "created_at": row[11].isoformat() if row[11] else None
                    })
                
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