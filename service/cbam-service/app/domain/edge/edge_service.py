# ============================================================================
# 🔗 Edge Service - CBAM 배출량 전파 서비스
# ============================================================================

import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.domain.edge.edge_repository import EdgeRepository
from app.domain.edge.edge_schema import EdgeResponse

logger = logging.getLogger(__name__)

class EdgeService:
    """엣지 기반 배출량 전파 서비스 (Repository 패턴)"""
    
    def __init__(self, db: Session):
        self.repository = EdgeRepository(db)
        logger.info("✅ Edge Service 초기화 완료")
    
    async def initialize(self):
        """서비스 초기화"""
        await self.repository.initialize()
        logger.info("✅ Edge Service 초기화 완료")
    
    async def get_process_emission_data(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정의 배출량 데이터를 조회합니다."""
        try:
            return await self.repository.get_process_emission_data(process_id)
        except Exception as e:
            logger.error(f"공정 {process_id} 배출량 데이터 조회 실패: {e}")
            return None
    
    async def get_continue_edges(self, source_process_id: int) -> List[Dict[str, Any]]:
        """특정 공정에서 나가는 continue 엣지들을 조회합니다."""
        try:
            return await self.repository.get_continue_edges(source_process_id)
        except Exception as e:
            logger.error(f"공정 {source_process_id}의 continue 엣지 조회 실패: {e}")
            return []
    
    async def update_process_cumulative_emission(self, process_id: int, cumulative_emission: float) -> bool:
        """공정의 누적 배출량을 업데이트합니다."""
        try:
            return await self.repository.update_process_cumulative_emission(process_id, cumulative_emission)
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
            #    소스 공정의 누적값이 없으면 자체 직접귀속배출량을 누적으로 간주(체인 시작점)
            source_cumulative = source_emission['cumulative_emission'] if source_emission['cumulative_emission'] else source_emission['attrdir_em']
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
        저장 없이 계산만 수행(표시용). 실제 저장은 별도 save API에서 처리.
        """
        try:
            logger.info(f"🔗 공정 {source_process_id} → 제품 {target_product_id} 배출량 전달 시작")
            
            # 1. 공정의 배출량 데이터 조회
            process_data = await self.repository.get_process_emission_data(source_process_id)
            if not process_data:
                logger.error(f"공정 {source_process_id}의 배출량 데이터를 찾을 수 없습니다.")
                return False
            
            # 2. 제품의 현재 데이터 조회 (정확한 판매량/수량 반영)
            product_data = await self.repository.get_product_data(target_product_id)
            if not product_data:
                logger.error(f"제품 {target_product_id}의 데이터를 찾을 수 없습니다.")
                return False
            
            # 3. 제품에 연결된 모든 공정들의 배출량 합계 계산(표시용)
            total_emission = await self.compute_product_emission(target_product_id)
            
            logger.info(f"🧮 공정→제품 배출량 계산:")
            logger.info(f"  공정 {source_process_id} 직접귀속배출량: {process_data['attrdir_em']}")
            logger.info(f"  공정 {source_process_id} 누적 배출량: {process_data['cumulative_emission']}")
            logger.info(f"  제품 {target_product_id} 기존 배출량: {product_data['attr_em']}")
            logger.info(f"  제품 {target_product_id} 최종 배출량: {total_emission}")
            
            # 4. 저장은 하지 않음
            logger.info(f"✅ 공정 {source_process_id} → 제품 {target_product_id} 배출량 계산 완료(표시용): {total_emission}")
            return True
                
        except Exception as e:
            logger.error(f"공정 {source_process_id} → 제품 {target_product_id} 배출량 전달 실패: {e}")
            return False

    async def compute_product_emission(self, product_id: int) -> float:
        """현재 연결 상태 기준 제품 배출량(표시용)을 합산해 반환.
        - 제품은 생산하는 공정의 누적 배출량(cumulative_emission)을 받음
        - 단, 순환 참조를 방지하기 위해 직접적인 produce 관계만 고려
        - 잔여(to_next) 비율은 consume 전파에서 적용한다.
        """
        try:
            # 🔧 수정: produce 관계만 고려하여 순환 참조 방지
            connected_processes = await self.repository.get_processes_connected_to_product(product_id)
            seen = set()
            total_emission = 0.0
            
            for proc_data in connected_processes:
                pid = proc_data['process_id']
                if pid in seen:
                    continue
                seen.add(pid)
                proc_emission = await self.repository.get_process_emission_data(pid)
                if proc_emission:
                    # 🔧 수정: 제품은 생산 공정의 누적 배출량을 받음
                    cumulative_em = proc_emission.get('cumulative_emission') or 0.0
                    if cumulative_em == 0.0:
                        cumulative_em = proc_emission.get('attrdir_em') or 0.0
                    total_emission += cumulative_em
                    logger.info(f"  공정 {pid} 누적 배출량: {cumulative_em} tCO2e")

            logger.info(f"제품 {product_id} 총 배출량 계산: {total_emission} tCO2e")
            return float(total_emission)
        except Exception as e:
            logger.error(f"제품 {product_id} 표시용 배출량 합산 실패: {e}")
            return 0.0
    
    async def update_product_emission_from_processes(self, product_id: int) -> bool:
        """제품의 배출량을 연결된 공정들의 누적 배출량으로 업데이트합니다.
        단일 책임 원칙: 제품 배출량 업데이트만 담당
        """
        try:
            logger.info(f"🔄 제품 {product_id} 배출량 업데이트 시작")
            
            # 1. 제품의 현재 배출량 계산
            new_emission = await self.compute_product_emission(product_id)
            
            # 2. 제품 배출량 업데이트
            success = await self.repository.update_product_emission(product_id, new_emission)
            
            if success:
                logger.info(f"✅ 제품 {product_id} 배출량 업데이트 완료: {new_emission} tCO2e")
                return True
            else:
                logger.error(f"❌ 제품 {product_id} 배출량 업데이트 실패")
                return False
                
        except Exception as e:
            logger.error(f"제품 {product_id} 배출량 업데이트 실패: {e}")
            return False
    
    async def propagate_emissions_consume(self, source_product_id: int, target_process_id: int) -> bool:
        """
        규칙 3: 제품→공정 배출량 전달 (edge_kind = "consume")
        to_next_process = product_amount - product_sell - product_eusell
        여러 공정으로 소비될 경우 생산량 비율에 따라 분배한다.
        이 값은 target.mat_amount에 반영된다.
        동시에 product.attr_em이 전구물질 배출량으로 target.attr_em에 귀속된다.
        """
        try:
            logger.info(f"🔗 제품 {source_product_id} → 공정 {target_process_id} 배출량 전달 시작")
            
            # 1. 제품의 배출량 조회
            product_data = await self.repository.get_product_data(source_product_id)
            if not product_data:
                logger.error(f"제품 {source_product_id}의 데이터를 찾을 수 없습니다.")
                return False
            
            # 2. 공정의 현재 배출량 데이터 조회
            process_data = await self.repository.get_process_emission_data(target_process_id)
            if not process_data:
                logger.error(f"공정 {target_process_id}의 배출량 데이터를 찾을 수 없습니다.")
                return False
            
            # 3. 제품 소비량 조회 (product_process 테이블에서)
            consumption_data = await self.repository.get_processes_consuming_product(source_product_id)
            consumption_amount = 0.0
            
            for consume_data in consumption_data:
                if consume_data['process_id'] == target_process_id:
                    consumption_amount = float(consume_data['consumption_amount']) if consume_data['consumption_amount'] else 0.0
                    break
            
            # 4. to_next_process 계산 (dataallocation.mdc 규칙 3번)
            product_amount = float(product_data['product_amount'] or 0.0)
            product_sell = float(product_data['product_sell'] or 0.0)
            product_eusell = float(product_data['product_eusell'] or 0.0)
            to_next_process = product_amount - product_sell - product_eusell
            if to_next_process < 0:
                to_next_process = 0.0
            
            # 5. 여러 공정으로 소비될 경우 생산량 비율에 따라 분배
            total_consumption = sum([
                float(data['consumption_amount']) if data['consumption_amount'] else 0.0 
                for data in consumption_data
            ])
            
            if total_consumption > 0:
                consumption_ratio = (consumption_amount / total_consumption) if total_consumption > 0 else 0.0
            else:
                consumers = len(consumption_data)
                consumption_ratio = (1.0 / consumers) if consumers > 0 else 0.0
            allocated_amount = to_next_process * consumption_ratio
            
            # 6. 배출량 계산 (제품 배출량 * 소비 비율)
            # 🔧 수정: 순환 참조 방지를 위해 저장된 attr_em 사용
            product_emission = product_data['attr_em'] or 0.0
            logger.info(f"  제품 {source_product_id} 배출량 (저장값): {product_emission} tCO2e")

            # 최종 가중치 = (실투입비율 to_next/product_amount) × (소비자 분배 비율)
            to_next_share = (to_next_process / product_amount) if product_amount > 0 else 0.0
            process_ratio = to_next_share * consumption_ratio
            process_emission = product_emission * process_ratio

            # 7. 공정 누적 배출량 계산 (직접 배출량 + 전파된 배출량)
            # 🔧 단일책임원칙: consume 전파는 직접 배출량에 전파 배출량을 더함
            direct_emission = process_data['attrdir_em']
            total_process_emission = direct_emission + process_emission

            logger.info(f"🧮 제품→공정 배출량 계산 (dataallocation.mdc 규칙 3번):")
            logger.info(f"  제품 {source_product_id} 총량: {product_amount}")
            logger.info(f"  제품 {source_product_id} 판매량: {product_sell}")
            logger.info(f"  제품 {source_product_id} EU판매량: {product_eusell}")
            logger.info(f"  제품 {source_product_id} to_next_process: {to_next_process}")
            logger.info(f"  공정 {target_process_id} 소비량: {consumption_amount}")
            logger.info(f"  전체 소비량: {total_consumption}")
            logger.info(f"  소비 비율(입력/기본): {consumption_ratio}")
            logger.info(f"  실투입비율(to_next/amount): {to_next_share}")
            logger.info(f"  최종 분배비율(process_ratio): {process_ratio}")
            logger.info(f"  할당량: {allocated_amount}")
            logger.info(f"  제품 {source_product_id} 배출량: {product_emission}")
            logger.info(f"  공정 {target_process_id} 직접 배출량: {direct_emission}")
            logger.info(f"  공정 {target_process_id} 전파 배출량: {process_emission} (분배비율 {process_ratio})")
            logger.info(f"  공정 {target_process_id} 최종 누적 배출량: {total_process_emission}")
            
            # 8. 공정의 배출량 업데이트
            success = await self.repository.update_process_cumulative_emission(target_process_id, total_process_emission)
            
            # 9. 공정의 원료 투입량 업데이트 (target.mat_amount에 반영)
            if success:
                mat_amount_success = await self.repository.update_process_material_amount(
                    target_process_id, source_product_id, allocated_amount
                )
                if not mat_amount_success:
                    logger.warning(f"⚠️ 공정 {target_process_id}의 원료 투입량 업데이트 실패")
            
            if success:
                logger.info(f"✅ 제품 {source_product_id} → 공정 {target_process_id} 배출량 전달 완료")
                return True
            else:
                logger.error(f"❌ 공정 {target_process_id} 배출량 업데이트 실패")
                return False
                
        except Exception as e:
            logger.error(f"제품 {source_product_id} → 공정 {target_process_id} 배출량 전달 실패: {e}")
            return False
    
    async def propagate_emissions_full_graph(self) -> Dict[str, Any]:
        """전체 그래프에 대해 배출량 전파를 실행합니다."""
        try:
            logger.info("🔄 전체 그래프 배출량 전파 시작")
            # 중요: 전파를 여러 번 호출해도 결과가 누적되지 않도록
            # 모든 공정의 누적값을 먼저 직접귀속배출량으로 초기화한다(직접 배출량 복원)
            try:
                await self.repository.reset_cumulative_to_direct_emission()
                logger.info("🧹 누적 배출량을 직접귀속배출량으로 초기화 완료 (전파 시작 전)")
            except Exception as e:
                logger.warning(f"⚠️ 누적 초기화 경고(무시 가능): {e}")
            
            # 모든 엣지를 조회 (페이지네이션 제한 없이)
            all_edges = await self.repository.get_all_edges()
            
            if not all_edges:
                logger.info("전체 그래프에 엣지가 없습니다.")
                return {'success': True, 'message': '전체 그래프에 엣지가 없습니다.'}
            
            # 엣지 종류별로 분류
            continue_edges = [edge for edge in all_edges if edge['edge_kind'] == 'continue']
            produce_edges = [edge for edge in all_edges if edge['edge_kind'] == 'produce']
            consume_edges = [edge for edge in all_edges if edge['edge_kind'] == 'consume']
            
            logger.info(f"전체 그래프 엣지 분류: continue={len(continue_edges)}, produce={len(produce_edges)}, consume={len(consume_edges)}")
            
            # 🔍 디버깅: 각 엣지 상세 정보 로깅
            for edge in all_edges:
                logger.debug(f"  엣지 ID: {edge['id']}, 소스: {edge['source_id']}({edge['source_node_type']}), 타겟: {edge['target_id']}({edge['target_node_type']}), 종류: {edge['edge_kind']}")
            
            # 1. continue 엣지들 처리 (공정→공정)
            for edge in continue_edges:
                success = await self.propagate_emissions_continue(edge['source_id'], edge['target_id'])
                if not success:
                    logger.warning(f"continue 엣지 {edge['id']} 처리 실패")
            
            # 2. produce 엣지들 처리 (공정→제품)
            for edge in produce_edges:
                success = await self.propagate_emissions_produce(edge['source_id'], edge['target_id'])
                if not success:
                    logger.warning(f"produce 엣지 {edge['id']} 처리 실패")
            
            # 3. consume 엣지들 처리 (제품→공정)
            for edge in consume_edges:
                success = await self.propagate_emissions_consume(edge['source_id'], edge['target_id'])
                if not success:
                    logger.warning(f"consume 엣지 {edge['id']} 처리 실패")
            
            # 4. 🔧 추가: produce 엣지에 연결된 제품들의 배출량을 업데이트
            logger.info("🔄 제품 배출량 업데이트 시작")
            updated_products = 0
            product_ids = set()
            
            # produce 엣지에서 제품 ID 추출
            for edge in produce_edges:
                product_ids.add(edge['target_id'])
            
            for product_id in product_ids:
                success = await self.update_product_emission_from_processes(product_id)
                if success:
                    updated_products += 1
            
            logger.info(f"✅ 제품 배출량 업데이트 완료: {updated_products}/{len(product_ids)}개 제품")
            logger.info("✅ 전체 그래프 배출량 전파 완료")
            return {
                'success': True,
                'message': '전체 그래프 배출량 전파 완료',
                'processed_edges': {
                    'continue': len(continue_edges),
                    'produce': len(produce_edges),
                    'consume': len(consume_edges)
                }
            }
            
        except Exception as e:
            logger.error(f"전체 그래프 배출량 전파 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': '전체 그래프 배출량 전파 실패'
            }
    
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
    
    async def _validate_edge(self, edge_data) -> Dict[str, Any]:
        """엣지 유효성 검증"""
        try:
            source_type = edge_data.source_node_type
            target_type = edge_data.target_node_type
            edge_kind = edge_data.edge_kind
            
            # 1. 기본 유효성 검증
            if not source_type or not target_type or not edge_kind:
                return {'valid': False, 'error': '필수 필드가 누락되었습니다.'}
            
            # 2. 노드 타입 유효성 검증
            valid_node_types = ['process', 'product']
            if source_type not in valid_node_types or target_type not in valid_node_types:
                return {'valid': False, 'error': f'유효하지 않은 노드 타입입니다. 허용된 타입: {valid_node_types}'}
            
            # 3. 엣지 종류 유효성 검증
            valid_edge_kinds = ['consume', 'produce', 'continue']
            if edge_kind not in valid_edge_kinds:
                return {'valid': False, 'error': f'유효하지 않은 엣지 종류입니다. 허용된 종류: {valid_edge_kinds}'}
            
            # 4. 엣지 종류별 연결 규칙 검증
            validation_rules = {
                'consume': {
                    'valid_combinations': [
                        ('product', 'process'),  # 제품 → 공정 (소비)
                    ],
                    'description': '제품이 공정에서 소비됨'
                },
                'produce': {
                    'valid_combinations': [
                        ('process', 'product'),  # 공정 → 제품 (생산)
                    ],
                    'description': '공정이 제품을 생산함'
                },
                'continue': {
                    'valid_combinations': [
                        ('process', 'process'),  # 공정 → 공정 (연속)
                    ],
                    'description': '공정이 공정으로 연결됨'
                }
            }
            
            rule = validation_rules.get(edge_kind)
            if not rule:
                return {'valid': False, 'error': f'알 수 없는 엣지 종류: {edge_kind}'}
            
            valid_combination = (source_type, target_type)
            if valid_combination not in rule['valid_combinations']:
                return {
                    'valid': False, 
                    'error': f'{edge_kind} 엣지는 {rule["description"]}만 허용됩니다. 현재: {source_type} → {target_type}'
                }
            
            # 5. 동일 노드 간 연결 방지
            if source_type == target_type and edge_data.source_id == edge_data.target_id:
                return {'valid': False, 'error': '동일한 노드 간 연결은 허용되지 않습니다.'}
            
            # 6. 제품-제품 연결 방지 (continue 엣지)
            if source_type == 'product' and target_type == 'product':
                return {'valid': False, 'error': '제품 간 직접 연결은 허용되지 않습니다.'}
            
            # 7. 공정-공정 연결 시 같은 제품에 귀속된 공정들끼리만 연결 가능
            if edge_kind == 'continue' and source_type == 'process' and target_type == 'process':
                same_product_check = await self._check_same_product_processes(
                    edge_data.source_id, edge_data.target_id
                )
                if not same_product_check['valid']:
                    return same_product_check
            
            logger.info(f"✅ 엣지 유효성 검증 통과: {source_type}({edge_data.source_id}) → {target_type}({edge_data.target_id}) ({edge_kind})")
            return {'valid': True, 'error': None}
            
        except Exception as e:
            logger.error(f"❌ 엣지 유효성 검증 중 오류: {str(e)}")
            return {'valid': False, 'error': f'유효성 검증 중 오류가 발생했습니다: {str(e)}'}
    
    async def _check_same_product_processes(self, source_process_id: int, target_process_id: int) -> Dict[str, Any]:
        """두 공정이 같은 제품에 귀속되어 있는지 확인"""
        try:
            # 두 공정이 모두 같은 제품에 귀속되어 있는지 확인
            source_products = await self.repository.get_products_by_process(source_process_id)
            target_products = await self.repository.get_products_by_process(target_process_id)
            
            # 공통 제품이 있는지 확인
            common_products = set(source_products) & set(target_products)
            
            if not common_products:
                return {
                    'valid': False, 
                    'error': f'공정 {source_process_id}와 {target_process_id}가 서로 다른 제품에 귀속되어 있습니다. 공정 간 연결은 같은 제품에 귀속된 공정들끼리만 가능합니다.'
                }
            
            return {'valid': True, 'error': None}
            
        except Exception as e:
            logger.error(f"❌ 공정 제품 귀속 확인 중 오류: {str(e)}")
            return {'valid': False, 'error': f'공정 제품 귀속 확인 중 오류가 발생했습니다: {str(e)}'}

    async def create_edge(self, edge_data) -> Optional[EdgeResponse]:
        """엣지 생성 (Repository 패턴) - 엣지 생성 후 전체 그래프 재계산"""
        try:
            logger.info(f"엣지 생성 시작: {edge_data}")
            
            # 1. 엣지 유효성 검증
            validation_result = await self._validate_edge(edge_data)
            if not validation_result['valid']:
                logger.error(f"❌ 엣지 유효성 검증 실패: {validation_result['error']}")
                raise ValueError(f"엣지 유효성 검증 실패: {validation_result['error']}")
            
            # Pydantic 모델을 딕셔너리로 변환
            edge_dict = {
                'source_node_type': edge_data.source_node_type,
                'source_id': edge_data.source_id,
                'target_node_type': edge_data.target_node_type,
                'target_id': edge_data.target_id,
                'edge_kind': edge_data.edge_kind
            }
            
            # Repository를 통해 엣지 생성
            result = await self.repository.create_edge(edge_dict)
            
            if result:
                logger.info(f"✅ 엣지 생성 완료: ID {result['id']}")
                
                try:
                    # 엣지 생성 후 전체 그래프 배출량 전파 실행
                    logger.info("🔄 엣지 변경으로 인한 전체 그래프 배출량 전파 시작")
                    propagation_result = await self.propagate_emissions_full_graph()
                    
                    if propagation_result['success']:
                        logger.info("✅ 전체 그래프 배출량 전파 완료")
                        result['propagation_result'] = propagation_result
                    else:
                        logger.warning(f"⚠️ 전체 그래프 배출량 전파 실패: {propagation_result.get('error', 'Unknown error')}")
                        result['propagation_result'] = propagation_result
                        # 배출량 전파 실패는 엣지 생성을 실패시키지 않음 (경고만)
                        
                except Exception as propagation_error:
                    logger.error(f"❌ 배출량 전파 중 오류 발생: {propagation_error}")
                    # 배출량 전파 실패는 엣지 생성을 실패시키지 않음
                    result['propagation_result'] = {
                        'success': False,
                        'error': str(propagation_error),
                        'message': '배출량 전파 실패 (엣지는 생성됨)'
                    }
                
                return EdgeResponse(**result)
            else:
                logger.error("엣지 생성 실패: Repository에서 None을 반환했습니다.")
                return None
                
        except Exception as e:
            logger.error(f"엣지 생성 실패: {e}")
            import traceback
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise e
    
    async def get_edges(self, skip: int = 0, limit: int = 100) -> List[EdgeResponse]:
        """모든 엣지 조회 (Repository 패턴)"""
        try:
            edges = await self.repository.get_edges(skip, limit)
            return [EdgeResponse(**edge) for edge in edges]
        except Exception as e:
            logger.error(f"엣지 조회 실패: {e}")
            return []
    
    async def get_edge(self, edge_id: int) -> Optional[EdgeResponse]:
        """특정 엣지 조회 (Repository 패턴)"""
        try:
            edge = await self.repository.get_edge(edge_id)
            if edge:
                return EdgeResponse(**edge)
            return None
        except Exception as e:
            logger.error(f"엣지 {edge_id} 조회 실패: {e}")
            return None
    
    async def update_edge(self, edge_id: int, edge_data) -> Optional[EdgeResponse]:
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
            result = await self.repository.update_edge(edge_id, update_data)
            
            if result:
                logger.info(f"✅ 엣지 {edge_id} 수정 완료")
                
                # 엣지 수정 후 전체 그래프 배출량 전파 실행
                logger.info("🔄 엣지 변경으로 인한 전체 그래프 배출량 전파 시작")
                propagation_result = await self.propagate_emissions_full_graph()
                
                if propagation_result['success']:
                    logger.info("✅ 전체 그래프 배출량 전파 완료")
                    result['propagation_result'] = propagation_result
                else:
                    logger.warning(f"⚠️ 전체 그래프 배출량 전파 실패: {propagation_result.get('error', 'Unknown error')}")
                    result['propagation_result'] = propagation_result
                
                return EdgeResponse(**result)
            else:
                logger.error(f"엣지 {edge_id} 수정 실패: Repository에서 None을 반환했습니다.")
                return None
                
        except Exception as e:
            logger.error(f"엣지 {edge_id} 수정 실패: {e}")
            import traceback
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise e
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제 (Repository 패턴)"""
        try:
            logger.info(f"엣지 {edge_id} 삭제 시작")
            
            # Repository를 통해 엣지 삭제
            success = await self.repository.delete_edge(edge_id)
            
            if success:
                logger.info(f"✅ 엣지 {edge_id} 삭제 완료")
                
                # 🔧 단일책임원칙: 엣지 삭제는 삭제만 담당, 배출량 전파는 별도 함수에서 처리
                # propagate_emissions_full_graph에서 자체적으로 초기화 및 전파 수행
                logger.info("🔄 엣지 삭제로 인한 전체 그래프 배출량 전파 시작")
                propagation_result = await self.propagate_emissions_full_graph()
                
                if propagation_result['success']:
                    logger.info("✅ 전체 그래프 배출량 전파 완료")
                else:
                    logger.warning(f"⚠️ 전체 그래프 배출량 전파 실패: {propagation_result.get('error', 'Unknown error')}")
                
                return True
            else:
                logger.error(f"엣지 {edge_id} 삭제 실패: Repository에서 False를 반환했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"엣지 {edge_id} 삭제 실패: {e}")
            import traceback
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise e
    
    # ============================================================================
    # 🔍 검색 및 필터링 메서드들
    # ============================================================================
    
    async def get_edges_by_type(self, edge_kind: str) -> List[EdgeResponse]:
        """타입별 엣지 조회"""
        try:
            edges = await self.repository.get_edges_by_type(edge_kind)
            return [EdgeResponse(**edge) for edge in edges]
        except Exception as e:
            logger.error(f"타입별 엣지 조회 실패: {e}")
            return []
    
    async def get_edges_by_node(self, node_id: int) -> List[EdgeResponse]:
        """노드와 연결된 엣지 조회"""
        try:
            edges = await self.repository.get_edges_by_node(node_id)
            return [EdgeResponse(**edge) for edge in edges]
        except Exception as e:
            logger.error(f"노드별 엣지 조회 실패: {e}")
            return []
    
    # ============================================================================
    # 🔄 전체 그래프 배출량 전파 메서드들
    # ============================================================================
    
    async def propagate_emissions_chain(self, chain_id: int) -> Dict[str, Any]:
        """공정 체인에 대해 배출량 누적 전달을 실행합니다."""
        try:
            logger.info(f"🔄 공정 체인 {chain_id} 배출량 전파 시작")
            
            # 체인에 포함된 엣지들을 조회 (실제로는 체인 ID로 조회해야 하지만, 임시로 모든 continue 엣지 사용)
            continue_edges = await self.repository.get_edges_by_type('continue')
            
            if not continue_edges:
                return {
                    'success': False,
                    'error': 'continue 엣지가 없습니다.'
                }
            
            # 체인 내의 엣지들을 순서대로 처리
            processed_count = 0
            for edge in continue_edges:
                success = await self.propagate_emissions_continue(edge['source_id'], edge['target_id'])
                if success:
                    processed_count += 1
                else:
                    logger.warning(f"체인 내 엣지 {edge['id']} 처리 실패")
            
            logger.info(f"✅ 공정 체인 {chain_id} 배출량 전파 완료: {processed_count}/{len(continue_edges)}개 엣지 처리")
            return {
                'success': True,
                'message': f'공정 체인 {chain_id} 배출량 전파 완료',
                'processed_edges': processed_count,
                'total_edges': len(continue_edges)
            }
            
        except Exception as e:
            logger.error(f"공정 체인 {chain_id} 배출량 전파 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'공정 체인 {chain_id} 배출량 전파 실패'
            }
