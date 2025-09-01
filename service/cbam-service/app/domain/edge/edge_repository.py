# ============================================================================
# 📦 Edge Repository - 엣지 데이터 접근
# ============================================================================

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, update, delete
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

class EdgeRepository:
    """엣지 데이터 접근 클래스 (SQLAlchemy 세션)"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.info("✅ Edge Repository 초기화 완료")
    
    # ============================================================================
    # 📋 기본 CRUD 작업
    # ============================================================================
    
    async def create_edge(self, edge_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 생성"""
        try:
            query = text("""
                INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind)
                VALUES (:source_node_type, :source_id, :target_node_type, :target_id, :edge_kind)
                RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
            """)
            
            result = await self.db.execute(query, edge_data)
            await self.db.commit()
            
            row = result.fetchone()
            if row:
                logger.info(f"✅ 엣지 생성 성공: ID {row.id}")
                return dict(row._mapping)
            return None
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ 엣지 생성 실패: {str(e)}")
            return None
    
    async def get_edges(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """모든 엣지 조회 (페이지네이션)"""
        try:
            query = text("""
                SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                FROM edge
                ORDER BY id
                LIMIT :limit OFFSET :skip
            """)
            
            result = await self.db.execute(query, {"skip": skip, "limit": limit})
            rows = result.fetchall()
            
            return [dict(row._mapping) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ 엣지 목록 조회 실패: {str(e)}")
            return []
    
    async def get_edge(self, edge_id: int) -> Optional[Dict[str, Any]]:
        """특정 엣지 조회"""
        try:
            query = text("""
                SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                FROM edge
                WHERE id = :edge_id
            """)
            
            result = await self.db.execute(query, {"edge_id": edge_id})
            row = result.fetchone()
            
            if row:
                return dict(row._mapping)
            return None
            
        except Exception as e:
            logger.error(f"❌ 엣지 {edge_id} 조회 실패: {str(e)}")
            return None
    
    async def update_edge(self, edge_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """엣지 수정"""
        try:
            # 업데이트할 필드들만 추출
            set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
            set_clause += ", updated_at = NOW()"
            
            query = text(f"""
                UPDATE edge
                SET {set_clause}
                WHERE id = :edge_id
                RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
            """)
            
            params = {**update_data, "edge_id": edge_id}
            result = await self.db.execute(query, params)
            await self.db.commit()
            
            row = result.fetchone()
            if row:
                logger.info(f"✅ 엣지 {edge_id} 수정 성공")
                return dict(row._mapping)
            return None
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ 엣지 {edge_id} 수정 실패: {str(e)}")
            return None
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제"""
        try:
            query = text("DELETE FROM edge WHERE id = :edge_id")
            result = await self.db.execute(query, {"edge_id": edge_id})
            await self.db.commit()
            
            if result.rowcount > 0:
                logger.info(f"✅ 엣지 {edge_id} 삭제 성공")
                return True
            return False
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ 엣지 {edge_id} 삭제 실패: {str(e)}")
            return False
    
    # ============================================================================
    # 🔍 검색 및 필터링
    # ============================================================================
    
    async def get_edges_by_type(self, edge_kind: str) -> List[Dict[str, Any]]:
        """타입별 엣지 조회"""
        try:
            query = text("""
                SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                FROM edge
                WHERE edge_kind = :edge_kind
                ORDER BY id
            """)
            
            result = await self.db.execute(query, {"edge_kind": edge_kind})
            rows = result.fetchall()
            
            return [dict(row._mapping) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ 타입별 엣지 조회 실패: {str(e)}")
            return []
    
    async def get_edges_by_node(self, node_id: int) -> List[Dict[str, Any]]:
        """노드와 연결된 엣지 조회"""
        try:
            query = text("""
                SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                FROM edge
                WHERE source_id = :node_id OR target_id = :node_id
                ORDER BY id
            """)
            
            result = await self.db.execute(query, {"node_id": node_id})
            rows = result.fetchall()
            
            return [dict(row._mapping) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ 노드별 엣지 조회 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 🔗 배출량 전파 관련 메서드들
    # ============================================================================
    
    async def get_process_emission_data(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정의 배출량 데이터를 조회합니다."""
        try:
            query = text("""
                SELECT p.id, p.process_name, pae.attrdir_em, pae.cumulative_emission, pae.calculation_date
                FROM process p
                LEFT JOIN process_attrdir_emission pae ON p.id = pae.process_id
                WHERE p.id = :process_id
            """)
            
            result = await self.db.execute(query, {"process_id": process_id})
            row = result.fetchone()
            
            if row:
                return {
                    'process_id': row.id,
                    'process_name': row.process_name,
                    'attrdir_em': float(row.attrdir_em) if row.attrdir_em else 0.0,
                    'cumulative_emission': float(row.cumulative_emission) if row.cumulative_emission else 0.0,
                    'calculation_date': row.calculation_date.isoformat() if row.calculation_date else None
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ 공정 {process_id} 배출량 데이터 조회 실패: {str(e)}")
            return None
    
    async def get_continue_edges(self, source_process_id: int) -> List[Dict[str, Any]]:
        """특정 공정에서 나가는 continue 엣지들을 조회합니다."""
        try:
            query = text("""
                SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind
                FROM edge
                WHERE source_id = :source_process_id AND edge_kind = 'continue'
                ORDER BY id
            """)
            
            result = await self.db.execute(query, {"source_process_id": source_process_id})
            rows = result.fetchall()
            
            return [dict(row._mapping) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ 공정 {source_process_id}의 continue 엣지 조회 실패: {str(e)}")
            return []
    
    async def update_process_cumulative_emission(self, process_id: int, cumulative_emission: float) -> bool:
        """공정의 누적 배출량을 업데이트합니다."""
        try:
            query = text("""
                UPDATE process_attrdir_emission
                SET cumulative_emission = :cumulative_emission, calculation_date = NOW()
                WHERE process_id = :process_id
            """)
            
            result = await self.db.execute(query, {
                "process_id": process_id,
                "cumulative_emission": cumulative_emission
            })
            await self.db.commit()
            
            if result.rowcount > 0:
                logger.info(f"✅ 공정 {process_id} 누적 배출량 업데이트 성공: {cumulative_emission}")
                return True
            else:
                logger.warning(f"⚠️ 공정 {process_id}의 배출량 데이터가 없어 새로 생성합니다")
                # 배출량 데이터가 없으면 새로 생성
                insert_query = text("""
                    INSERT INTO process_attrdir_emission (process_id, cumulative_emission, calculation_date)
                    VALUES (:process_id, :cumulative_emission, NOW())
                """)
                
                await self.db.execute(insert_query, {
                    "process_id": process_id,
                    "cumulative_emission": cumulative_emission
                })
                await self.db.commit()
                return True
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ 공정 {process_id} 누적 배출량 업데이트 실패: {str(e)}")
            return False
    
    async def get_processes_connected_to_product(self, product_id: int) -> List[Dict[str, Any]]:
        """제품에 연결된 모든 공정들을 조회합니다."""
        try:
            query = text("""
                SELECT e.source_id as process_id, e.edge_kind
                FROM edge e
                WHERE e.target_id = :product_id AND e.edge_kind = 'produce'
                ORDER BY e.source_id
            """)
            
            result = await self.db.execute(query, {"product_id": product_id})
            rows = result.fetchall()
            
            return [dict(row._mapping) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ 제품 {product_id}에 연결된 공정 조회 실패: {str(e)}")
            return []
    
    async def update_product_emission(self, product_id: int, total_emission: float) -> bool:
        """제품의 배출량을 업데이트합니다."""
        try:
            query = text("""
                UPDATE product
                SET attr_em = :total_emission, updated_at = NOW()
                WHERE id = :product_id
            """)
            
            result = await self.db.execute(query, {
                "product_id": product_id,
                "total_emission": total_emission
            })
            await self.db.commit()
            
            if result.rowcount > 0:
                logger.info(f"✅ 제품 {product_id} 배출량 업데이트 성공: {total_emission}")
                return True
            return False
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ 제품 {product_id} 배출량 업데이트 실패: {str(e)}")
            return False
    
    async def get_product_data(self, product_id: int) -> Optional[Dict[str, Any]]:
        """제품 데이터를 조회합니다."""
        try:
            query = text("""
                SELECT id, product_name, amount, sell_amount, eusell_amount, attr_em
                FROM product
                WHERE id = :product_id
            """)
            
            result = await self.db.execute(query, {"product_id": product_id})
            row = result.fetchone()
            
            if row:
                return {
                    'id': row.id,
                    'product_name': row.product_name,
                    'amount': float(row.amount) if row.amount else 0.0,
                    'sell_amount': float(row.sell_amount) if row.sell_amount else 0.0,
                    'eusell_amount': float(row.eusell_amount) if row.eusell_amount else 0.0,
                    'attr_em': float(row.attr_em) if row.attr_em else 0.0
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ 제품 {product_id} 데이터 조회 실패: {str(e)}")
            return None
    
    async def get_processes_consuming_product(self, product_id: int) -> List[Dict[str, Any]]:
        """제품을 소비하는 모든 공정들을 조회합니다."""
        try:
            query = text("""
                SELECT e.target_id as process_id, e.edge_kind, pp.consumption_amount
                FROM edge e
                LEFT JOIN product_process pp ON e.target_id = pp.process_id AND e.source_id = pp.product_id
                WHERE e.source_id = :product_id AND e.edge_kind = 'consume'
                ORDER BY e.target_id
            """)
            
            result = await self.db.execute(query, {"product_id": product_id})
            rows = result.fetchall()
            
            return [dict(row._mapping) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ 제품 {product_id}를 소비하는 공정 조회 실패: {str(e)}")
            return []
    
    async def update_process_material_amount(self, process_id: int, product_id: int, amount: float) -> bool:
        """공정의 원료 투입량을 업데이트합니다."""
        try:
            query = text("""
                UPDATE product_process
                SET consumption_amount = :amount, updated_at = NOW()
                WHERE process_id = :process_id AND product_id = :product_id
            """)
            
            result = await self.db.execute(query, {
                "process_id": process_id,
                "product_id": product_id,
                "amount": amount
            })
            await self.db.commit()
            
            if result.rowcount > 0:
                logger.info(f"✅ 공정 {process_id}의 제품 {product_id} 투입량 업데이트 성공: {amount}")
                return True
            else:
                logger.warning(f"⚠️ 공정 {process_id}의 제품 {product_id} 관계가 없어 새로 생성합니다")
                # 관계가 없으면 새로 생성
                insert_query = text("""
                    INSERT INTO product_process (process_id, product_id, consumption_amount)
                    VALUES (:process_id, :product_id, :amount)
                """)
                
                await self.db.execute(insert_query, {
                    "process_id": process_id,
                    "product_id": product_id,
                    "amount": amount
                })
                await self.db.commit()
                return True
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"❌ 공정 {process_id}의 제품 {product_id} 투입량 업데이트 실패: {str(e)}")
            return False
