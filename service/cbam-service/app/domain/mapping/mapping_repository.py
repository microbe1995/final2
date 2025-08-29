# ============================================================================
# 🗄️ Mapping Repository - HS-CN 매핑 데이터베이스 접근 계층
# ============================================================================

import logging
import os
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = logging.getLogger(__name__)

class HSCNMappingRepository:
    """HS-CN 매핑 데이터베이스 리포지토리 (psycopg2 직접 연결)"""
    
    def __init__(self, db_session=None):
        # Railway DB 연결 정보
        self.database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    # ============================================================================
    # 📋 기본 CRUD 작업
    # ============================================================================
    
    async def create_mapping(self, mapping_data: HSCNMappingCreateRequest) -> Optional[HSCNMapping]:
        """HS-CN 매핑 생성"""
        try:
            mapping = HSCNMapping(
                hscode=mapping_data.hscode,
                aggregoods_name=mapping_data.aggregoods_name,
                aggregoods_engname=mapping_data.aggregoods_engname,
                cncode_total=mapping_data.cncode_total,
                goods_name=mapping_data.goods_name,
                goods_engname=mapping_data.goods_engname
            )
            
            self.db.add(mapping)
            self.db.commit()
            self.db.refresh(mapping)
            
            logger.info(f"✅ HS-CN 매핑 생성 성공: ID {mapping.id}")
            return mapping
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"❌ HS-CN 매핑 생성 실패: {str(e)}")
            return None
    
    async def get_mapping_by_id(self, mapping_id: int) -> Optional[HSCNMapping]:
        """ID로 HS-CN 매핑 조회"""
        try:
            mapping = self.db.query(HSCNMapping).filter(HSCNMapping.id == mapping_id).first()
            return mapping
        except SQLAlchemyError as e:
            logger.error(f"❌ HS-CN 매핑 조회 실패: {str(e)}")
            return None
    
    async def get_all_mappings(self, skip: int = 0, limit: int = 100) -> List[HSCNMapping]:
        """모든 HS-CN 매핑 조회 (페이지네이션)"""
        try:
            mappings = self.db.query(HSCNMapping).offset(skip).limit(limit).all()
            return mappings
        except SQLAlchemyError as e:
            logger.error(f"❌ HS-CN 매핑 목록 조회 실패: {str(e)}")
            return []
    
    async def update_mapping(self, mapping_id: int, mapping_data: HSCNMappingUpdateRequest) -> Optional[HSCNMapping]:
        """HS-CN 매핑 수정"""
        try:
            mapping = await self.get_mapping_by_id(mapping_id)
            if not mapping:
                return None
            
            # 업데이트할 필드만 수정
            update_data = mapping_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(mapping, field, value)
            
            self.db.commit()
            self.db.refresh(mapping)
            
            logger.info(f"✅ HS-CN 매핑 수정 성공: ID {mapping_id}")
            return mapping
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"❌ HS-CN 매핑 수정 실패: {str(e)}")
            return None
    
    async def delete_mapping(self, mapping_id: int) -> bool:
        """HS-CN 매핑 삭제"""
        try:
            mapping = await self.get_mapping_by_id(mapping_id)
            if not mapping:
                return False
            
            self.db.delete(mapping)
            self.db.commit()
            
            logger.info(f"✅ HS-CN 매핑 삭제 성공: ID {mapping_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"❌ HS-CN 매핑 삭제 실패: {str(e)}")
            return False
    
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
    
    async def search_by_hs_code(self, hs_code: str) -> List[HSCNMapping]:
        """HS 코드로 검색 (부분 일치)"""
        try:
            mappings = self.db.query(HSCNMapping).filter(
                HSCNMapping.hscode.like(f"{hs_code}%")
            ).all()
            
            return mappings
            
        except SQLAlchemyError as e:
            logger.error(f"❌ HS 코드 검색 실패: {str(e)}")
            return []
    
    async def search_by_cn_code(self, cn_code: str) -> List[HSCNMapping]:
        """CN 코드로 검색 (부분 일치)"""
        try:
            mappings = self.db.query(HSCNMapping).filter(
                HSCNMapping.cncode_total.like(f"{cn_code}%")
            ).all()
            
            return mappings
            
        except SQLAlchemyError as e:
            logger.error(f"❌ CN 코드 검색 실패: {str(e)}")
            return []
    
    async def search_by_goods_name(self, goods_name: str) -> List[HSCNMapping]:
        """품목명으로 검색 (부분 일치)"""
        try:
            mappings = self.db.query(HSCNMapping).filter(
                or_(
                    HSCNMapping.goods_name.ilike(f"%{goods_name}%"),
                    HSCNMapping.goods_engname.ilike(f"%{goods_name}%")
                )
            ).all()
            
            return mappings
            
        except SQLAlchemyError as e:
            logger.error(f"❌ 품목명 검색 실패: {str(e)}")
            return []
    
    # ============================================================================
    # 📊 통계 및 분석
    # ============================================================================
    
    async def get_mapping_stats(self) -> Dict[str, Any]:
        """매핑 통계 조회"""
        try:
            total_mappings = self.db.query(func.count(HSCNMapping.id)).scalar()
            unique_hscodes = self.db.query(func.count(func.distinct(HSCNMapping.hscode))).scalar()
            unique_cncodes = self.db.query(func.count(func.distinct(HSCNMapping.cncode_total))).scalar()
            
            return {
                'total_mappings': total_mappings or 0,
                'unique_hscodes': unique_hscodes or 0,
                'unique_cncodes': unique_cncodes or 0,
                'last_updated': None
            }
            
        except SQLAlchemyError as e:
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
        try:
            created_count = 0
            failed_count = 0
            errors = []
            
            for mapping_data in mappings_data:
                try:
                    mapping = HSCNMapping(
                        hscode=mapping_data.hscode,
                        aggregoods_name=mapping_data.aggregoods_name,
                        aggregoods_engname=mapping_data.aggregoods_engname,
                        cncode_total=mapping_data.cncode_total,
                        goods_name=mapping_data.goods_name,
                        goods_engname=mapping_data.goods_engname
                    )
                    
                    self.db.add(mapping)
                    created_count += 1
                    
                except Exception as e:
                    failed_count += 1
                    errors.append(f"매핑 생성 실패: {str(e)}")
            
            self.db.commit()
            
            logger.info(f"✅ 일괄 매핑 생성 완료: 성공 {created_count}개, 실패 {failed_count}개")
            
            return {
                'created_count': created_count,
                'failed_count': failed_count,
                'errors': errors
            }
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"❌ 일괄 매핑 생성 실패: {str(e)}")
            return {
                'created_count': 0,
                'failed_count': len(mappings_data),
                'errors': [f"일괄 처리 실패: {str(e)}"]
            }
