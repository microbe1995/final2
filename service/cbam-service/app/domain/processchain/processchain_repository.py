# ============================================================================
# 🔄 ProcessChain Repository - 통합 공정 그룹 데이터 레포지토리
# ============================================================================

import logging
import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func, create_engine
from sqlalchemy.orm import sessionmaker, Session

from .processchain_entity import (
    ProcessChain, ProcessChainLink, Base
)

logger = logging.getLogger(__name__)

class ProcessChainRepository:
    """통합 공정 그룹 레포지토리 클래스"""
    
    def __init__(self):
        """레포지토리 초기화"""
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다.")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # 테이블 생성
        self._create_tables()
    
    def _create_tables(self):
        """테이블 생성"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ processchain 테이블 생성 완료")
        except Exception as e:
            logger.error(f"❌ 테이블 생성 중 오류: {e}")
            raise e
    
    def get_db(self) -> Session:
        """데이터베이스 세션 반환"""
        return self.SessionLocal()
    
    # ============================================================================
    # 🔄 ProcessChain 관련 메서드 (통합 공정 그룹)
    # ============================================================================
    
    async def create_process_chain(self, chain_data: Dict[str, Any]) -> ProcessChain:
        """통합 공정 그룹 생성"""
        try:
            with self.get_db() as db:
                chain = ProcessChain(**chain_data)
                db.add(chain)
                db.commit()
                db.refresh(chain)
                logger.info(f"✅ 통합 공정 그룹 생성 성공: ID {chain.id}")
                return chain
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 생성 실패: {e}")
            raise e
    
    async def get_process_chain(self, chain_id: int) -> Optional[ProcessChain]:
        """통합 공정 그룹 조회"""
        try:
            with self.get_db() as db:
                chain = db.query(ProcessChain).filter(ProcessChain.id == chain_id).first()
                return chain
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 조회 실패: {e}")
            raise e
    
    async def get_all_process_chains(self) -> List[ProcessChain]:
        """모든 통합 공정 그룹 조회"""
        try:
            with self.get_db() as db:
                chains = db.query(ProcessChain).filter(ProcessChain.is_active == True).all()
                return chains
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 목록 조회 실패: {e}")
            raise e
    
    async def update_process_chain(self, chain_id: int, update_data: Dict[str, Any]) -> Optional[ProcessChain]:
        """통합 공정 그룹 수정"""
        try:
            with self.get_db() as db:
                chain = db.query(ProcessChain).filter(ProcessChain.id == chain_id).first()
                if not chain:
                    return None
                
                for key, value in update_data.items():
                    if hasattr(chain, key):
                        setattr(chain, key, value)
                
                chain.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(chain)
                logger.info(f"✅ 통합 공정 그룹 수정 성공: ID {chain_id}")
                return chain
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 수정 실패: {e}")
            raise e
    
    async def delete_process_chain(self, chain_id: int) -> bool:
        """통합 공정 그룹 삭제"""
        try:
            with self.get_db() as db:
                chain = db.query(ProcessChain).filter(ProcessChain.id == chain_id).first()
                if not chain:
                    return False
                
                db.delete(chain)
                db.commit()
                logger.info(f"✅ 통합 공정 그룹 삭제 성공: ID {chain_id}")
                return True
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 삭제 실패: {e}")
            raise e
    
    # ============================================================================
    # 🔗 ProcessChainLink 관련 메서드 (그룹 내 공정 멤버)
    # ============================================================================
    
    async def create_process_chain_link(self, link_data: Dict[str, Any]) -> ProcessChainLink:
        """통합 공정 그룹 링크 생성"""
        try:
            with self.get_db() as db:
                link = ProcessChainLink(**link_data)
                db.add(link)
                db.commit()
                db.refresh(link)
                logger.info(f"✅ 그룹 링크 생성 성공: ID {link.id}")
                return link
        except Exception as e:
            logger.error(f"❌ 그룹 링크 생성 실패: {e}")
            raise e
    
    async def get_chain_links(self, chain_id: int) -> List[ProcessChainLink]:
        """그룹에 속한 공정들 조회"""
        try:
            with self.get_db() as db:
                links = db.query(ProcessChainLink).filter(
                    ProcessChainLink.chain_id == chain_id
                ).order_by(ProcessChainLink.sequence_order).all()
                return links
        except Exception as e:
            logger.error(f"❌ 그룹 링크 조회 실패: {e}")
            raise e
    
    async def delete_chain_links(self, chain_id: int) -> bool:
        """그룹의 모든 링크 삭제"""
        try:
            with self.get_db() as db:
                db.query(ProcessChainLink).filter(
                    ProcessChainLink.chain_id == chain_id
                ).delete()
                db.commit()
                logger.info(f"✅ 그룹 링크 삭제 성공: chain_id {chain_id}")
                return True
        except Exception as e:
            logger.error(f"❌ 그룹 링크 삭제 실패: {e}")
            raise e
    
    # ============================================================================
    # 🔍 통합 공정 그룹 자동 탐지 메서드
    # ============================================================================
    
    async def detect_process_chains(self, max_chain_length: int = 10) -> List[Dict[str, Any]]:
        """연결된 공정들을 통합 공정 그룹으로 자동 탐지"""
        try:
            with self.get_db() as db:
                # Recursive CTE를 사용하여 연결된 공정 체인 탐지
                query = text("""
                    WITH RECURSIVE process_paths AS (
                        -- 시작점: continue 엣지가 있는 공정들
                        SELECT 
                            e.source_id as start_process,
                            e.target_id as current_process,
                            ARRAY[e.source_id, e.target_id] as path,
                            1 as depth
                        FROM edge e
                        WHERE e.edge_kind = 'continue'
                        
                        UNION ALL
                        
                        -- 재귀적으로 연결된 공정들 추가
                        SELECT 
                            pp.start_process,
                            e.target_id,
                            pp.path || e.target_id,
                            pp.depth + 1
                        FROM process_paths pp
                        JOIN edge e ON e.source_id = pp.current_process
                        WHERE e.edge_kind = 'continue'
                        AND pp.depth < :max_depth
                        AND e.target_id != ALL(pp.path)  -- 순환 방지
                    )
                    SELECT 
                        start_process,
                        current_process,
                        path,
                        depth,
                        array_length(path, 1) as chain_length
                    FROM process_paths
                    WHERE depth >= 2  -- 최소 2개 공정이 연결된 경우만
                    ORDER BY start_process, depth DESC
                """)
                
                result = db.execute(query, {"max_depth": max_chain_length})
                chains = []
                
                for row in result:
                    chain_info = {
                        "start_process_id": row.start_process,
                        "end_process_id": row.current_process,
                        "chain_length": row.chain_length,
                        "process_path": row.path,
                        "depth": row.depth
                    }
                    chains.append(chain_info)
                
                logger.info(f"✅ 통합 공정 그룹 탐지 완료: {len(chains)}개 발견")
                return chains
                
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 탐지 실패: {e}")
            raise e
    
    # ============================================================================
    # 📊 통합 공정 그룹 배출량 계산 메서드
    # ============================================================================
    
    async def calculate_chain_integrated_emissions(self, chain_id: int) -> Dict[str, Any]:
        """통합 공정 그룹의 총 배출량 계산"""
        try:
            with self.get_db() as db:
                # 그룹에 속한 공정들 조회
                links = await self.get_chain_links(chain_id)
                process_ids = [link.process_id for link in links]
                
                if not process_ids:
                    return {
                        "chain_id": chain_id,
                        "integrated_matdir_emission": 0,
                        "integrated_fueldir_emission": 0,
                        "integrated_attrdir_em": 0,
                        "process_count": 0
                    }
                
                # 각 공정의 배출량 조회
                query = text("""
                    SELECT 
                        process_id,
                        COALESCE(matdir_em, 0) as matdir_em,
                        COALESCE(fueldir_em, 0) as fueldir_em,
                        COALESCE(attrdir_em, 0) as attrdir_em
                    FROM process_attrdir_emission
                    WHERE process_id = ANY(:process_ids)
                """)
                
                result = db.execute(query, {"process_ids": process_ids})
                emissions = result.fetchall()
                
                # 그룹의 총 배출량 계산 (SUM)
                total_matdir = sum(Decimal(str(row.matdir_em)) for row in emissions)
                total_fueldir = sum(Decimal(str(row.fueldir_em)) for row in emissions)
                total_attrdir = sum(Decimal(str(row.attrdir_em)) for row in emissions)
                
                integrated_emission = {
                    "chain_id": chain_id,
                    "integrated_matdir_emission": float(total_matdir),
                    "integrated_fueldir_emission": float(total_fueldir),
                    "integrated_attrdir_em": float(total_attrdir),
                    "process_count": len(process_ids),
                    "process_ids": process_ids
                }
                
                logger.info(f"✅ 통합 공정 그룹 배출량 계산 완료: chain_id {chain_id}")
                return integrated_emission
                
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 배출량 계산 실패: {e}")
            raise e
    
    async def auto_detect_and_calculate_chains(self, max_chain_length: int = 10) -> Dict[str, Any]:
        """통합 공정 그룹 자동 탐지 및 배출량 계산"""
        try:
            # 1. 기존 그룹들 비활성화
            with self.get_db() as db:
                db.query(ProcessChain).update({"is_active": False})
                db.commit()
            
            # 2. 새로운 그룹들 탐지
            detected_chains = await self.detect_process_chains(max_chain_length)
            
            created_chains = []
            total_integrated_emission = Decimal('0')
            
            for chain_info in detected_chains:
                # 3. 그룹 생성
                chain_data = {
                    "chain_name": f"통합공정그룹-{chain_info['start_process_id']}-{chain_info['end_process_id']}",
                    "start_process_id": chain_info["start_process_id"],
                    "end_process_id": chain_info["end_process_id"],
                    "chain_length": chain_info["chain_length"],
                    "is_active": True
                }
                
                chain = await self.create_process_chain(chain_data)
                
                # 4. 그룹에 공정들 추가
                for i, process_id in enumerate(chain_info["process_path"]):
                    link_data = {
                        "chain_id": chain.id,
                        "process_id": process_id,
                        "sequence_order": i + 1,
                        "is_continue_edge": True
                    }
                    await self.create_process_chain_link(link_data)
                
                # 5. 그룹 배출량 계산
                emission_result = await self.calculate_chain_integrated_emissions(chain.id)
                total_integrated_emission += Decimal(str(emission_result["integrated_attrdir_em"]))
                
                created_chains.append({
                    "chain_id": chain.id,
                    "chain_name": chain.chain_name,
                    "process_count": emission_result["process_count"],
                    "integrated_emission": emission_result["integrated_attrdir_em"]
                })
            
            result = {
                "detected_chains": len(created_chains),
                "total_calculated_processes": sum(c["process_count"] for c in created_chains),
                "total_integrated_emission": float(total_integrated_emission),
                "created_chains": created_chains,
                "calculation_date": datetime.utcnow()
            }
            
            logger.info(f"✅ 통합 공정 그룹 자동 탐지 및 계산 완료: {len(created_chains)}개 그룹")
            return result
            
        except Exception as e:
            logger.error(f"❌ 통합 공정 그룹 자동 탐지 및 계산 실패: {e}")
            raise e
    
    # ============================================================================
    # 🔄 SourceStream 관련 메서드
    # ============================================================================
    
    async def create_source_stream(self, stream_data: Dict[str, Any]) -> SourceStream:
        """소스 스트림 생성"""
        try:
            with self.get_db() as db:
                stream = SourceStream(**stream_data)
                db.add(stream)
                db.commit()
                db.refresh(stream)
                logger.info(f"✅ 소스 스트림 생성 성공: ID {stream.id}")
                return stream
        except Exception as e:
            logger.error(f"❌ 소스 스트림 생성 실패: {e}")
            raise e
    
    async def get_source_streams(self, source_process_id: Optional[int] = None) -> List[SourceStream]:
        """소스 스트림 조회"""
        try:
            with self.get_db() as db:
                query = db.query(SourceStream)
                if source_process_id:
                    query = query.filter(SourceStream.source_process_id == source_process_id)
                streams = query.all()
                return streams
        except Exception as e:
            logger.error(f"❌ 소스 스트림 조회 실패: {e}")
            raise e
