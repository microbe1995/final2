# ============================================================================
# 🔗 Edge Service - CBAM 배출량 전파 서비스
# ============================================================================

import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timezone

from app.domain.edge.edge_repository import EdgeRepository

logger = logging.getLogger(__name__)

class EdgeService:
    """엣지 기반 배출량 전파 서비스 (Repository 패턴)"""
    
    def __init__(self):
        self.edge_repository = EdgeRepository()
        logger.info("✅ Edge Service 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.edge_repository.initialize()
            logger.info("✅ Edge Service 데이터베이스 연결 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Edge Service 데이터베이스 초기화 실패 (서비스는 계속 실행): {e}")
            logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    async def get_process_emission_data(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정의 배출량 데이터를 조회합니다."""
        try:
            return await self.edge_repository.get_process_emission_data(process_id)
        except Exception as e:
            logger.error(f"공정 {process_id} 배출량 데이터 조회 실패: {e}")
            return None
    
    async def get_continue_edges(self, source_process_id: int) -> List[Dict[str, Any]]:
        """특정 공정에서 나가는 continue 엣지들을 조회합니다."""
        try:
            return await self.edge_repository.get_continue_edges(source_process_id)
        except Exception as e:
            logger.error(f"공정 {source_process_id}의 continue 엣지 조회 실패: {e}")
            return []
    
    async def update_process_cumulative_emission(self, process_id: int, cumulative_emission: float) -> bool:
        """공정의 누적 배출량을 업데이트합니다."""
        try:
            return await self.edge_repository.update_process_cumulative_emission(process_id, cumulative_emission)
        except Exception as e:
            logger.error(f"공정 {process_id} 누적 배출량 업데이트 실패: {e}")
            return False
    
    # ============================================================================
    # 🔗 룰 기반 배출량 전파 메서드들
    # ============================================================================
    
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
    
    async def propagate_emissions_produce(self, source_process_id: int, target_product_id: int) -> bool:
        """
        규칙 2: 공정→제품 배출량 전달 (edge_kind = "produce")
        product.attr_em = sum(connected_processes.attr_em)
        """
        try:
            logger.info(f"🔗 공정 {source_process_id} → 제품 {target_product_id} 배출량 전달 시작")
            
            # 1. 제품에 연결된 모든 공정들의 배출량 조회
            connected_processes = await self.edge_repository.get_processes_connected_to_product(target_product_id)
            
            if not connected_processes:
                logger.error(f"제품 {target_product_id}에 연결된 공정이 없습니다.")
                return False
            
            # 2. 연결된 공정들의 배출량 합계 계산
            total_emission = 0.0
            for process_data in connected_processes:
                process_emission = await self.get_process_emission_data(process_data['process_id'])
                if process_emission:
                    total_emission += process_emission['cumulative_emission']
                else:
                    logger.warning(f"공정 {process_data['process_id']}의 배출량 데이터를 찾을 수 없습니다.")
            
            # 3. 제품의 배출량 업데이트
            success = await self.edge_repository.update_product_emission(target_product_id, total_emission)
            
            if success:
                logger.info(f"✅ 제품 {target_product_id} 배출량 업데이트 완료: {total_emission}")
                return True
            else:
                logger.error(f"❌ 제품 {target_product_id} 배출량 업데이트 실패")
                return False
                
        except Exception as e:
            logger.error(f"공정 {source_process_id} → 제품 {target_product_id} 배출량 전달 실패: {e}")
            return False
    
    async def propagate_emissions_consume(self, source_product_id: int, target_process_id: int) -> bool:
        """
        규칙 3: 제품→공정 배출량 전달 (edge_kind = "consume")
        to_next_process = product_amount - product_sell - product_eusell
        여러 공정으로 소비될 경우 생산량 비율에 따라 분배
        product.attr_em이 전구물질 배출량으로 target.attr_em에 귀속
        """
        try:
            logger.info(f"🔗 제품 {source_product_id} → 공정 {target_process_id} 배출량 전달 시작")
            
            # 1. 제품 데이터 조회
            product_data = await self.edge_repository.get_product_data(source_product_id)
            if not product_data:
                logger.error(f"제품 {source_product_id} 데이터를 찾을 수 없습니다.")
                return False
            
            # 2. 제품 소비량 계산
            product_amount = product_data.get('amount', 0.0)
            product_sell = product_data.get('sell_amount', 0.0)
            product_eusell = product_data.get('eusell_amount', 0.0)
            
            to_next_process = product_amount - product_sell - product_eusell
            
            if to_next_process <= 0:
                logger.warning(f"제품 {source_product_id}의 다음 공정으로 전달할 수량이 없습니다: {to_next_process}")
                return True  # 에러가 아닌 정상 상황
            
            # 3. 해당 제품을 소비하는 모든 공정 조회
            consuming_processes = await self.edge_repository.get_processes_consuming_product(source_product_id)
            
            if not consuming_processes:
                logger.error(f"제품 {source_product_id}를 소비하는 공정이 없습니다.")
                return False
            
            # 4. 생산량 비율에 따른 분배 계산
            total_consumption = sum(proc.get('consumption_amount', 0.0) for proc in consuming_processes)
            
            if total_consumption <= 0:
                logger.error(f"제품 {source_product_id}의 총 소비량이 0입니다.")
                return False
            
            # 5. 타겟 공정의 분배 비율 계산
            target_consumption = next((proc.get('consumption_amount', 0.0) for proc in consuming_processes 
                                    if proc['process_id'] == target_process_id), 0.0)
            
            if target_consumption <= 0:
                logger.warning(f"공정 {target_process_id}의 제품 {source_product_id} 소비량이 0입니다.")
                return True
            
            # 6. 분배된 수량과 배출량 계산
            distribution_ratio = target_consumption / total_consumption
            distributed_amount = to_next_process * distribution_ratio
            product_emission = product_data.get('attr_em', 0.0)
            distributed_emission = product_emission * distribution_ratio
            
            # 7. 타겟 공정의 원료 투입량 업데이트
            success = await self.edge_repository.update_process_material_amount(
                target_process_id, source_product_id, distributed_amount
            )
            
            if not success:
                logger.error(f"공정 {target_process_id}의 원료 투입량 업데이트 실패")
                return False
            
            # 8. 타겟 공정의 전구물질 배출량 업데이트
            current_emission = await self.get_process_emission_data(target_process_id)
            if current_emission:
                new_attrdir_em = current_emission['attrdir_em'] + distributed_emission
                success = await self.update_process_cumulative_emission(target_process_id, new_attrdir_em)
                
                if success:
                    logger.info(f"✅ 공정 {target_process_id} 전구물질 배출량 업데이트 완료: +{distributed_emission}")
                    return True
                else:
                    logger.error(f"❌ 공정 {target_process_id} 전구물질 배출량 업데이트 실패")
                    return False
            else:
                logger.error(f"공정 {target_process_id}의 현재 배출량 데이터를 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            logger.error(f"제품 {source_product_id} → 공정 {target_process_id} 배출량 전달 실패: {e}")
            return False
    
    async def propagate_emissions_full_graph(self) -> Dict[str, Any]:
        """
        전체 그래프에 대해 배출량 전파를 실행합니다.
        엣지 변경이 발생할 때마다 전체 그래프를 재계산합니다.
        """
        try:
            logger.info("🔗 전체 그래프 배출량 전파 시작")
            
            # 1. 모든 엣지 조회
            all_edges = await self.get_edges()
            if not all_edges:
                logger.warning("전체 그래프에 엣지가 없습니다.")
                return {'success': True, 'message': '엣지가 없음'}
            
            # 2. 노드별로 분류
            process_nodes = set()
            product_nodes = set()
            
            for edge in all_edges:
                if edge['source_node_type'] == 'process':
                    process_nodes.add(edge['source_id'])
                if edge['target_node_type'] == 'process':
                    process_nodes.add(edge['target_id'])
                if edge['source_node_type'] == 'product':
                    product_nodes.add(edge['source_id'])
                if edge['target_node_type'] == 'product':
                    product_nodes.add(edge['target_id'])
            
            logger.info(f"📋 노드 분류 완료: 공정 {len(process_nodes)}개, 제품 {len(product_nodes)}개")
            
            # 3. 순환 참조 검사
            has_cycle = await self._detect_cycles(all_edges)
            if has_cycle:
                return {'success': False, 'error': '순환 참조가 발견되었습니다. DAG 위반'}
            
            # 4. 배출량 초기화 (누적 배출량을 자체 배출량으로 리셋)
            for process_id in process_nodes:
                emission_data = await self.get_process_emission_data(process_id)
                if emission_data:
                    await self.update_process_cumulative_emission(process_id, emission_data['attrdir_em'])
            
            # 5. 엣지 종류별로 배출량 전파 실행
            propagation_results = {
                'continue_edges': 0,
                'produce_edges': 0,
                'consume_edges': 0,
                'success_count': 0,
                'error_count': 0
            }
            
            # continue 엣지들 먼저 처리 (공정→공정)
            continue_edges = [edge for edge in all_edges if edge['edge_kind'] == 'continue']
            for edge in continue_edges:
                success = await self.propagate_emissions_continue(edge['source_id'], edge['target_id'])
                propagation_results['continue_edges'] += 1
                if success:
                    propagation_results['success_count'] += 1
                else:
                    propagation_results['error_count'] += 1
            
            # produce 엣지들 처리 (공정→제품)
            produce_edges = [edge for edge in all_edges if edge['edge_kind'] == 'produce']
            for edge in produce_edges:
                success = await self.propagate_emissions_produce(edge['source_id'], edge['target_id'])
                propagation_results['produce_edges'] += 1
                if success:
                    propagation_results['success_count'] += 1
                else:
                    propagation_results['error_count'] += 1
            
            # consume 엣지들 처리 (제품→공정)
            consume_edges = [edge for edge in all_edges if edge['edge_kind'] == 'consume']
            for edge in consume_edges:
                success = await self.propagate_emissions_consume(edge['source_id'], edge['target_id'])
                propagation_results['consume_edges'] += 1
                if success:
                    propagation_results['success_count'] += 1
                else:
                    propagation_results['error_count'] += 1
            
            # 6. 결과 요약
            total_edges = len(all_edges)
            success_rate = (propagation_results['success_count'] / total_edges * 100) if total_edges > 0 else 0
            
            result = {
                'success': propagation_results['error_count'] == 0,
                'total_edges': total_edges,
                'propagation_results': propagation_results,
                'success_rate': success_rate,
                'message': f"전체 그래프 배출량 전파 완료: {propagation_results['success_count']}/{total_edges} 성공 ({success_rate:.1f}%)"
            }
            
            logger.info(f"🎯 전체 그래프 배출량 전파 완료!")
            logger.info(f"  총 엣지: {total_edges}")
            logger.info(f"  성공: {propagation_results['success_count']}")
            logger.info(f"  실패: {propagation_results['error_count']}")
            logger.info(f"  성공률: {success_rate:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"전체 그래프 배출량 전파 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _detect_cycles(self, edges: List[Dict[str, Any]]) -> bool:
        """순환 참조(사이클)를 감지합니다."""
        try:
            # 그래프 구성
            graph = {}
            for edge in edges:
                source_key = f"{edge['source_node_type']}_{edge['source_id']}"
                target_key = f"{edge['target_node_type']}_{edge['target_id']}"
                
                if source_key not in graph:
                    graph[source_key] = []
                graph[source_key].append(target_key)
            
            # DFS로 사이클 감지
            visited = set()
            rec_stack = set()
            
            def has_cycle_util(node):
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        if has_cycle_util(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            for node in graph:
                if node not in visited:
                    if has_cycle_util(node):
                        logger.error(f"순환 참조 발견: 노드 {node}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"순환 참조 감지 실패: {e}")
            return False
    


    # ============================================================================
    # 🔗 기존 Edge CRUD 메서드들
    # ============================================================================
    
    async def create_edge(self, edge_data) -> Optional[Dict[str, Any]]:
        """엣지 생성 (Repository 패턴) - 엣지 생성 후 전체 그래프 재계산"""
        try:
            logger.info(f"엣지 생성 시작: {edge_data}")
            
            # Pydantic 모델을 딕셔너리로 변환
            edge_dict = {
                'source_node_type': edge_data.source_node_type,
                'source_id': edge_data.source_id,
                'target_node_type': edge_data.target_node_type,
                'target_id': edge_data.target_id,
                'edge_kind': edge_data.edge_kind
            }
            
            # Repository를 통해 엣지 생성
            result = await self.edge_repository.create_edge(edge_dict)
            
            if result:
                logger.info(f"✅ 엣지 생성 완료: ID {result['id']}")
                
                # 엣지 생성 후 전체 그래프 배출량 전파 실행
                logger.info("🔄 엣지 변경으로 인한 전체 그래프 배출량 전파 시작")
                propagation_result = await self.propagate_emissions_full_graph()
                
                if propagation_result['success']:
                    logger.info("✅ 전체 그래프 배출량 전파 완료")
                    result['propagation_result'] = propagation_result
                else:
                    logger.warning(f"⚠️ 전체 그래프 배출량 전파 실패: {propagation_result.get('error', 'Unknown error')}")
                    result['propagation_result'] = propagation_result
                
                return result
            else:
                logger.error("엣지 생성 실패: Repository에서 None을 반환했습니다.")
                return None
                
        except Exception as e:
            logger.error(f"엣지 생성 실패: {e}")
            import traceback
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise e
    
    async def get_edges(self) -> List[Dict[str, Any]]:
        """모든 엣지 조회 (Repository 패턴)"""
        try:
            return await self.edge_repository.get_edges()
        except Exception as e:
            logger.error(f"엣지 조회 실패: {e}")
            return []
    
    async def get_edge(self, edge_id: int) -> Optional[Dict[str, Any]]:
        """특정 엣지 조회 (Repository 패턴)"""
        try:
            return await self.edge_repository.get_edge(edge_id)
        except Exception as e:
            logger.error(f"엣지 {edge_id} 조회 실패: {e}")
            return None
    
    async def update_edge(self, edge_id: int, edge_data) -> Optional[Dict[str, Any]]:
        """엣지 수정 (Repository 패턴)"""
        try:
            logger.info(f"엣지 {edge_id} 수정: {edge_data}")
            
            # 업데이트할 데이터 준비
            update_data = {}
            if edge_data.source_node_type is not None:
                update_data['source_node_type'] = edge_data.source_node_type
            if edge_data.source_id is not None:
                update_data['source_id'] = edge_data.source_id
            if edge_data.target_node_type is not None:
                update_data['target_node_type'] = edge_data.target_node_type
            if edge_data.target_id is not None:
                update_data['target_id'] = edge_data.target_id
            if edge_data.edge_kind is not None:
                update_data['edge_kind'] = edge_data.edge_kind
            
            # Repository를 통해 엣지 수정
            result = await self.edge_repository.update_edge(edge_id, update_data)
            
            if result:
                logger.info(f"✅ 엣지 {edge_id} 수정 완료")
                return result
            else:
                logger.warning(f"엣지 {edge_id} 수정 실패: 해당 엣지를 찾을 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"엣지 {edge_id} 수정 실패: {e}")
            raise e
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제 (Repository 패턴)"""
        try:
            logger.info(f"엣지 {edge_id} 삭제")
            return await self.edge_repository.delete_edge(edge_id)
        except Exception as e:
            logger.error(f"엣지 {edge_id} 삭제 실패: {e}")
            raise e
