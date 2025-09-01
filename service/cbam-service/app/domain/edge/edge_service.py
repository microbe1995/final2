# ============================================================================
# 🔗 Edge Service - CBAM 배출량 전파 서비스
# ============================================================================

import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, update
from sqlalchemy.orm import selectinload

from app.domain.edge.edge_entity import Edge
from app.domain.process.process_entity import Process
from app.domain.product.product_entity import Product
from app.domain.calculation.calculation_entity import ProcessAttrdirEmission

logger = logging.getLogger(__name__)

class EdgeService:
    """엣지 기반 배출량 전파 서비스"""
    
    def __init__(self, db_session: AsyncSession = None):
        self.db_session = db_session
    
    async def get_process_emission_data(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정의 배출량 데이터를 조회합니다."""
        try:
            query = select(ProcessAttrdirEmission).where(
                ProcessAttrdirEmission.process_id == process_id
            )
            result = await self.db_session.execute(query)
            emission_data = result.scalar_one_or_none()
            
            if emission_data:
                return {
                    'process_id': emission_data.process_id,
                    'attrdir_em': float(emission_data.attrdir_em) if emission_data.attrdir_em else 0.0,
                    'cumulative_emission': float(emission_data.cumulative_emission) if emission_data.cumulative_emission else 0.0,
                    'total_matdir_emission': float(emission_data.total_matdir_emission) if emission_data.total_matdir_emission else 0.0,
                    'total_fueldir_emission': float(emission_data.total_fueldir_emission) if emission_data.total_fueldir_emission else 0.0
                }
            return None
            
        except Exception as e:
            logger.error(f"공정 {process_id} 배출량 데이터 조회 실패: {e}")
            return None
    
    async def get_continue_edges(self, source_process_id: int) -> List[Dict[str, Any]]:
        """특정 공정에서 나가는 continue 엣지들을 조회합니다."""
        try:
            query = select(Edge).where(
                Edge.source_node_type == 'process',
                Edge.source_id == source_process_id,
                Edge.edge_kind == 'continue'
            )
            result = await self.db_session.execute(query)
            edges = result.scalars().all()
            
            return [
                {
                    'id': edge.id,
                    'source_node_type': edge.source_node_type,
                    'source_id': edge.source_id,
                    'target_node_type': edge.target_node_type,
                    'target_id': edge.target_id,
                    'edge_kind': edge.edge_kind,
                    'qty': float(edge.qty) if edge.qty else None
                }
                for edge in edges
            ]
            
        except Exception as e:
            logger.error(f"공정 {source_process_id}의 continue 엣지 조회 실패: {e}")
            return []
    
    async def update_process_cumulative_emission(self, process_id: int, cumulative_emission: float) -> bool:
        """공정의 누적 배출량을 업데이트합니다."""
        try:
            update_query = update(ProcessAttrdirEmission).where(
                ProcessAttrdirEmission.process_id == process_id
            ).values(
                cumulative_emission=Decimal(str(cumulative_emission)),
                updated_at=text('NOW()')
            )
            
            result = await self.db_session.execute(update_query)
            await self.db_session.commit()
            
            logger.info(f"공정 {process_id} 누적 배출량 업데이트: {cumulative_emission}")
            return True
            
        except Exception as e:
            logger.error(f"공정 {process_id} 누적 배출량 업데이트 실패: {e}")
            await self.db_session.rollback()
            return False
    
    async def propagate_emissions_continue(self, source_process_id: int, target_process_id: int) -> bool:
        """
        규칙 1: 공정→공정 배출량 누적 전달 (edge_kind = "continue")
        source.attr_em이 target으로 누적 전달되어 target.cumulative_emission = source.cumulative_emission + target.attrdir_em
        """
        try:
            logger.info(f"🔗 공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 시작")
            
            # 1. 소스 공정의 누적 배출량 조회
            source_emission = await self.get_process_emission_data(source_process_id)
            if not source_emission:
                logger.error(f"소스 공정 {source_process_id}의 배출량 데이터를 찾을 수 없습니다.")
                return False
            
            # 2. 타겟 공정의 배출량 데이터 조회
            target_emission = await self.get_process_emission_data(target_process_id)
            if not target_emission:
                logger.error(f"타겟 공정 {target_process_id}의 배출량 데이터를 찾을 수 없습니다.")
                return False
            
            # 3. 배출량 누적 계산
            source_cumulative = source_emission['cumulative_emission']
            target_own = target_emission['attrdir_em']
            target_cumulative = source_cumulative + target_own
            
            logger.info(f"🧮 배출량 누적 계산:")
            logger.info(f"  소스 공정 {source_process_id} 누적 배출량: {source_cumulative}")
            logger.info(f"  타겟 공정 {target_process_id} 자체 배출량: {target_own}")
            logger.info(f"  타겟 공정 {target_process_id} 최종 누적 배출량: {target_cumulative}")
            
            # 4. 타겟 공정의 누적 배출량 업데이트
            success = await self.update_process_cumulative_emission(target_process_id, target_cumulative)
            
            if success:
                logger.info(f"✅ 공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 완료")
                return True
            else:
                logger.error(f"❌ 공정 {target_process_id} 누적 배출량 업데이트 실패")
                return False
                
        except Exception as e:
            logger.error(f"공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 실패: {e}")
            return False
    
    async def propagate_emissions_chain(self, process_chain_id: int) -> Dict[str, Any]:
        """
        공정 체인 전체에 대해 배출량 누적 전달을 실행합니다.
        """
        try:
            logger.info(f"🔗 공정 체인 {process_chain_id} 배출량 누적 전달 시작")
            
            # 1. 공정 체인의 순서 정보 조회
            chain_query = text("""
                SELECT pcl.process_id, pcl.sequence_order, pcl.is_continue_edge
                FROM process_chain_link pcl
                WHERE pcl.chain_id = :chain_id
                ORDER BY pcl.sequence_order
            """)
            
            result = await self.db_session.execute(chain_query, {'chain_id': process_chain_id})
            chain_processes = result.fetchall()
            
            if not chain_processes:
                logger.error(f"공정 체인 {process_chain_id}의 공정 정보를 찾을 수 없습니다.")
                return {'success': False, 'error': '공정 체인 정보 없음'}
            
            logger.info(f"📋 공정 체인 {process_chain_id} 공정 순서: {len(chain_processes)}개")
            
            # 2. 순서대로 배출량 누적 전달 실행
            propagation_results = []
            previous_process_id = None
            
            for i, (process_id, sequence_order, is_continue_edge) in enumerate(chain_processes):
                logger.info(f"🔍 공정 {process_id} (순서: {sequence_order}) 처리 중...")
                
                if i == 0:
                    # 첫 번째 공정: 누적 배출량 = 자체 배출량
                    emission_data = await self.get_process_emission_data(process_id)
                    if emission_data:
                        own_emission = emission_data['attrdir_em']
                        success = await self.update_process_cumulative_emission(process_id, own_emission)
                        
                        propagation_results.append({
                            'process_id': process_id,
                            'sequence_order': sequence_order,
                            'own_emission': own_emission,
                            'cumulative_emission': own_emission,
                            'propagation_type': 'first_process',
                            'success': success
                        })
                        
                        previous_process_id = process_id
                        logger.info(f"✅ 첫 번째 공정 {process_id} 누적 배출량 설정: {own_emission}")
                    else:
                        logger.error(f"첫 번째 공정 {process_id} 배출량 데이터 없음")
                        return {'success': False, 'error': f'공정 {process_id} 배출량 데이터 없음'}
                        
                elif is_continue_edge and previous_process_id:
                    # continue 엣지가 있는 경우: 이전 공정에서 배출량 누적 전달
                    success = await self.propagate_emissions_continue(previous_process_id, process_id)
                    
                    if success:
                        # 업데이트된 누적 배출량 조회
                        updated_emission = await self.get_process_emission_data(process_id)
                        if updated_emission:
                            propagation_results.append({
                                'process_id': process_id,
                                'sequence_order': sequence_order,
                                'own_emission': updated_emission['attrdir_em'],
                                'cumulative_emission': updated_emission['cumulative_emission'],
                                'propagation_type': 'continue_edge',
                                'source_process_id': previous_process_id,
                                'success': True
                            })
                            
                            previous_process_id = process_id
                            logger.info(f"✅ 공정 {process_id} 배출량 누적 전달 완료")
                        else:
                            logger.error(f"공정 {process_id} 업데이트된 배출량 데이터 조회 실패")
                            return {'success': False, 'error': f'공정 {process_id} 배출량 데이터 조회 실패'}
                    else:
                        logger.error(f"공정 {previous_process_id} → 공정 {process_id} 배출량 누적 전달 실패")
                        return {'success': False, 'error': f'공정 {process_id} 배출량 누적 전달 실패'}
                        
                else:
                    # continue 엣지가 없는 경우: 자체 배출량만 설정
                    emission_data = await self.get_process_emission_data(process_id)
                    if emission_data:
                        own_emission = emission_data['attrdir_em']
                        success = await self.update_process_cumulative_emission(process_id, own_emission)
                        
                        propagation_results.append({
                            'process_id': process_id,
                            'sequence_order': sequence_order,
                            'own_emission': own_emission,
                            'cumulative_emission': own_emission,
                            'propagation_type': 'no_continue_edge',
                            'success': success
                        })
                        
                        previous_process_id = process_id
                        logger.info(f"✅ 공정 {process_id} 자체 배출량만 설정: {own_emission}")
                    else:
                        logger.error(f"공정 {process_id} 배출량 데이터 없음")
                        return {'success': False, 'error': f'공정 {process_id} 배출량 데이터 없음'}
            
            # 3. 결과 요약
            total_processes = len(propagation_results)
            successful_propagations = len([r for r in propagation_results if r['success']])
            
            final_result = {
                'success': True,
                'chain_id': process_chain_id,
                'total_processes': total_processes,
                'successful_propagations': successful_propagations,
                'propagation_results': propagation_results,
                'final_emission_summary': {
                    'total_own_emissions': sum(r['own_emission'] for r in propagation_results),
                    'total_cumulative_emissions': sum(r['cumulative_emission'] for r in propagation_results),
                    'last_process_cumulative': propagation_results[-1]['cumulative_emission'] if propagation_results else 0
                }
            }
            
            logger.info(f"🎯 공정 체인 {process_chain_id} 배출량 누적 전달 완료!")
            logger.info(f"  총 공정 수: {total_processes}")
            logger.info(f"  성공한 전파: {successful_propagations}")
            logger.info(f"  최종 누적 배출량: {final_result['final_emission_summary']['last_process_cumulative']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"공정 체인 {process_chain_id} 배출량 누적 전달 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_process_chain_emission_summary(self, process_chain_id: int) -> Dict[str, Any]:
        """공정 체인의 배출량 요약 정보를 조회합니다."""
        try:
            summary_query = text("""
                SELECT 
                    pcl.sequence_order,
                    pcl.process_id,
                    p.process_name,
                    pae.attrdir_em,
                    pae.cumulative_emission,
                    pae.calculation_date
                FROM process_chain_link pcl
                JOIN process p ON pcl.process_id = p.id
                LEFT JOIN process_attrdir_emission pae ON pcl.process_id = pae.process_id
                WHERE pcl.chain_id = :chain_id
                ORDER BY pcl.sequence_order
            """)
            
            result = await self.db_session.execute(summary_query, {'chain_id': process_chain_id})
            processes = result.fetchall()
            
            if not processes:
                return {'success': False, 'error': '공정 체인 정보 없음'}
            
            summary = {
                'chain_id': process_chain_id,
                'total_processes': len(processes),
                'processes': [
                    {
                        'sequence_order': proc.sequence_order,
                        'process_id': proc.process_id,
                        'process_name': proc.process_name,
                        'own_emission': float(proc.attrdir_em) if proc.attrdir_em else 0.0,
                        'cumulative_emission': float(proc.cumulative_emission) if proc.cumulative_emission else 0.0,
                        'calculation_date': proc.calculation_date.isoformat() if proc.calculation_date else None
                    }
                    for proc in processes
                ],
                'total_own_emissions': sum(float(proc.attrdir_em) if proc.attrdir_em else 0.0 for proc in processes),
                'total_cumulative_emissions': sum(float(proc.cumulative_emission) if proc.cumulative_emission else 0.0 for proc in processes)
            }
            
            return {'success': True, 'summary': summary}
            
        except Exception as e:
            logger.error(f"공정 체인 {process_chain_id} 배출량 요약 조회 실패: {e}")
            return {'success': False, 'error': str(e)}

    # ============================================================================
    # 🔗 기존 Edge CRUD 메서드들
    # ============================================================================
    
    async def create_edge(self, edge_data) -> Optional[Edge]:
        """엣지 생성"""
        try:
            # 기존 엣지 생성 로직 구현
            logger.info(f"엣지 생성: {edge_data}")
            return None  # TODO: 실제 구현 필요
        except Exception as e:
            logger.error(f"엣지 생성 실패: {e}")
            return None
    
    async def get_edges(self) -> List[Edge]:
        """모든 엣지 조회"""
        try:
            query = select(Edge)
            result = await self.db_session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"엣지 조회 실패: {e}")
            return []
    
    async def get_edge(self, edge_id: int) -> Optional[Edge]:
        """특정 엣지 조회"""
        try:
            query = select(Edge).where(Edge.id == edge_id)
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"엣지 {edge_id} 조회 실패: {e}")
            return None
    
    async def update_edge(self, edge_id: int, edge_data) -> Optional[Edge]:
        """엣지 수정"""
        try:
            # 기존 엣지 수정 로직 구현
            logger.info(f"엣지 {edge_id} 수정: {edge_data}")
            return None  # TODO: 실제 구현 필요
        except Exception as e:
            logger.error(f"엣지 {edge_id} 수정 실패: {e}")
            return None
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제"""
        try:
            # 기존 엣지 삭제 로직 구현
            logger.info(f"엣지 {edge_id} 삭제")
            return True  # TODO: 실제 구현 필요
        except Exception as e:
            logger.error(f"엣지 {edge_id} 삭제 실패: {e}")
            return False
