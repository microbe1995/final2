# ============================================================================
# 🎯 Calculation Service - CBAM 계산 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.calculation.calculation_repository import CalculationRepository
from app.domain.calculation.calculation_schema import (
    ProductProcessCreateRequest, ProductProcessResponse,
    ProcessAttrdirEmissionCreateRequest, ProcessAttrdirEmissionResponse, ProcessAttrdirEmissionUpdateRequest,
    ProcessEmissionCalculationRequest, ProcessEmissionCalculationResponse,
    ProductEmissionCalculationRequest, ProductEmissionCalculationResponse,
    EdgeCreateRequest, EdgeResponse
)

logger = logging.getLogger(__name__)

class CalculationService:
    """CBAM 계산 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.calc_repository = CalculationRepository()
        logger.info("✅ Calculation 서비스 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.calc_repository.initialize()
            logger.info("✅ CBAM 계산 서비스 데이터베이스 연결 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Calculation 서비스 데이터베이스 초기화 실패 (서비스는 계속 실행): {e}")
            logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    



    
    async def delete_process(self, process_id: int) -> bool:
        """프로세스 삭제"""
        try:
            success = await self.calc_repository.delete_process(process_id)
            if success:
                logger.info(f"✅ 프로세스 {process_id} 삭제 성공")
            else:
                logger.warning(f"⚠️ 프로세스 {process_id}를 찾을 수 없음")
            return success
        except Exception as e:
            logger.error(f"Error deleting process {process_id}: {e}")
            raise e

    # ============================================================================
    # 🔗 ProductProcess 관련 메서드 (다대다 관계)
    # ============================================================================
    
    async def create_product_process(self, request: ProductProcessCreateRequest) -> ProductProcessResponse:
        """제품-공정 관계 생성"""
        try:
            product_process_data = {
                "product_id": request.product_id,
                "process_id": request.process_id
            }
            
            saved_product_process = await self.calc_repository.create_product_process(product_process_data)
            if saved_product_process:
                return ProductProcessResponse(**saved_product_process)
            else:
                raise Exception("제품-공정 관계 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error creating product-process relationship: {e}")
            raise e
    
    async def delete_product_process(self, product_id: int, process_id: int) -> bool:
        """제품-공정 관계 삭제"""
        try:
            success = await self.calc_repository.delete_product_process(product_id, process_id)
            return success
        except Exception as e:
            logger.error(f"Error deleting product-process relationship: {e}")
            raise e

    # ============================================================================
    # 📊 배출량 계산 관련 메서드들
    # ============================================================================
    
    async def calculate_process_attrdir_emission(self, process_id: int) -> ProcessAttrdirEmissionResponse:
        """공정별 직접귀속배출량 계산 및 저장"""
        try:
            result = await self.calc_repository.calculate_process_attrdir_emission(process_id)
            if result:
                return ProcessAttrdirEmissionResponse(**result)
            else:
                raise Exception("공정별 직접귀속배출량 계산에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error calculating process attrdir emission for process {process_id}: {e}")
            raise e
    
    async def get_process_attrdir_emission(self, process_id: int) -> Optional[ProcessAttrdirEmissionResponse]:
        """공정별 직접귀속배출량 조회"""
        try:
            result = await self.calc_repository.get_process_attrdir_emission(process_id)
            if result:
                return ProcessAttrdirEmissionResponse(**result)
            return None
        except Exception as e:
            logger.error(f"Error getting process attrdir emission for process {process_id}: {e}")
            raise e
    
    async def get_all_process_attrdir_emissions(self) -> List[ProcessAttrdirEmissionResponse]:
        """모든 공정별 직접귀속배출량 조회"""
        try:
            results = await self.calc_repository.get_all_process_attrdir_emissions()
            return [ProcessAttrdirEmissionResponse(**result) for result in results]
        except Exception as e:
            logger.error(f"Error getting all process attrdir emissions: {e}")
            raise e
    
    async def calculate_process_emission(self, request: ProcessEmissionCalculationRequest) -> ProcessEmissionCalculationResponse:
        """공정별 배출량 계산 (공식 포함)"""
        try:
            from datetime import datetime
            
            # 1. 공정 정보 조회
            process = await self.calc_repository.get_process(request.process_id)
            if not process:
                raise Exception(f"공정 ID {request.process_id}를 찾을 수 없습니다.")
            
            # 2. 직접귀속배출량 계산 및 저장
            emission_summary = await self.calc_repository.calculate_process_attrdir_emission(request.process_id)
            if not emission_summary:
                raise Exception("직접귀속배출량 계산에 실패했습니다.")
            
            # 3. 계산 공식 생성
            calculation_formula = (
                f"직접귀속배출량 = 원료직접배출량({emission_summary['total_matdir_emission']}) + "
                f"연료직접배출량({emission_summary['total_fueldir_emission']}) = "
                f"{emission_summary['attrdir_em']} tCO2e"
            )
            
            logger.info(f"✅ 공정 {request.process_id} 직접귀속배출량 계산 완료: {emission_summary['attrdir_em']}")
            
            return ProcessEmissionCalculationResponse(
                process_id=request.process_id,
                process_name=process['process_name'],
                total_matdir_emission=float(emission_summary['total_matdir_emission']),
                total_fueldir_emission=float(emission_summary['total_fueldir_emission']),
                attrdir_em=float(emission_summary['attrdir_em']),
                calculation_formula=calculation_formula,
                calculation_date=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating process emission for process {request.process_id}: {e}")
            raise e
    
    async def calculate_product_emission(self, request: ProductEmissionCalculationRequest) -> ProductEmissionCalculationResponse:
        """제품별 배출량 계산 (공식 포함)"""
        try:
            from datetime import datetime
            
            # 1. 제품별 총 배출량 계산
            product_emission_data = await self.calc_repository.calculate_product_total_emission(request.product_id)
            if not product_emission_data:
                raise Exception(f"제품 ID {request.product_id}의 배출량 계산에 실패했습니다.")
            
            # 2. 각 공정별 배출량 계산 응답 생성
            process_emissions = []
            for pe in product_emission_data['process_emissions']:
                process_emission_response = ProcessEmissionCalculationResponse(
                    process_id=pe['process_id'],
                    process_name=pe['process_name'],
                    total_matdir_emission=float(pe['total_matdir_emission']),
                    total_fueldir_emission=float(pe['total_fueldir_emission']),
                    attrdir_em=float(pe['attrdir_em']),
                    calculation_formula=f"공정별 직접귀속배출량 = {pe['attrdir_em']} tCO2e",
                    calculation_date=datetime.utcnow()
                )
                process_emissions.append(process_emission_response)
            
            # 3. 제품별 계산 공식 생성
            calculation_formula = (
                f"제품 총 배출량 = Σ(공정별 배출량) = {product_emission_data['total_emission']} tCO2e "
                f"(연결된 공정 수: {product_emission_data['process_count']}개)"
            )
            
            logger.info(f"✅ 제품 {request.product_id} 배출량 계산 완료: {product_emission_data['total_emission']}")
            
            return ProductEmissionCalculationResponse(
                product_id=request.product_id,
                product_name=product_emission_data['product_name'],
                total_emission=product_emission_data['total_emission'],
                process_emissions=process_emissions,
                calculation_formula=calculation_formula,
                calculation_date=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating product emission for product {request.product_id}: {e}")
            raise e

    # ============================================================================
    # 🔗 Edge 관련 서비스 메서드
    # ============================================================================

    async def create_edge(self, edge_data: EdgeCreateRequest) -> EdgeResponse:
        """Edge 생성 및 자동 통합 그룹 탐지"""
        try:
            logger.info(f"🔗 Edge 생성 요청: {edge_data.source_id} -> {edge_data.target_id} ({edge_data.edge_kind})")
            
            # 1. Edge 생성
            edge = await self.calc_repository.create_edge(edge_data.dict())
            logger.info(f"✅ Edge 생성 완료: ID {edge['id']}")
            
            # 2. 자동 통합 그룹 탐지 및 생성
            try:
                await self._auto_detect_and_create_process_chain(edge_data.source_id, edge_data.target_id)
                logger.info(f"✅ 자동 통합 그룹 탐지 및 생성 완료")
            except Exception as e:
                logger.warning(f"⚠️ 자동 통합 그룹 생성 실패 (Edge 생성은 성공): {e}")
            
            return EdgeResponse(**edge)
            
        except Exception as e:
            logger.error(f"❌ Edge 생성 실패: {e}")
            raise e

    async def get_edges(self) -> List[EdgeResponse]:
        """모든 Edge 조회"""
        try:
            edges = await self.calc_repository.get_edges()
            return [EdgeResponse(**edge) for edge in edges]
        except Exception as e:
            logger.error(f"❌ Edge 목록 조회 실패: {e}")
            raise e

    async def delete_edge(self, edge_id: int) -> bool:
        """Edge 삭제"""
        try:
            success = await self.calc_repository.delete_edge(edge_id)
            if success:
                logger.info(f"✅ Edge {edge_id} 삭제 성공")
            else:
                logger.warning(f"⚠️ Edge {edge_id}를 찾을 수 없음")
            return success
        except Exception as e:
            logger.error(f"❌ Edge 삭제 실패: {e}")
            raise e

    async def _auto_detect_and_create_process_chain(self, source_process_id: int, target_process_id: int):
        """Edge 생성 시 자동으로 통합 공정 그룹 탐지 및 생성"""
        try:
            logger.info(f"🔍 통합 공정 그룹 자동 탐지: {source_process_id} -> {target_process_id}")
            
            # 1. 기존 통합 그룹에서 해당 공정들이 이미 포함되어 있는지 확인
            existing_chains = await self.calc_repository.get_process_chains_by_process_ids([source_process_id, target_process_id])
            
            if existing_chains:
                logger.info(f"📋 기존 통합 그룹 발견: {len(existing_chains)}개")
                # 기존 그룹에 새로운 공정 추가 또는 그룹 병합 로직
                await self._merge_processes_into_existing_chains(source_process_id, target_process_id, existing_chains)
            else:
                logger.info("🆕 새로운 통합 그룹 생성")
                # 새로운 통합 그룹 생성
                await self._create_new_process_chain([source_process_id, target_process_id])
                
        except Exception as e:
            logger.error(f"❌ 자동 통합 그룹 탐지 실패: {e}")
            raise e

    async def _merge_processes_into_existing_chains(self, source_id: int, target_id: int, existing_chains: List[Dict]):
        """기존 통합 그룹에 새로운 공정들을 병합"""
        try:
            # 가장 적합한 그룹을 찾아서 병합
            best_chain = self._find_best_chain_for_merge(source_id, target_id, existing_chains)
            
            if best_chain:
                # 기존 그룹에 새로운 공정들 추가
                await self.calc_repository.add_processes_to_chain(best_chain['id'], [source_id, target_id])
                logger.info(f"✅ 공정들을 기존 그룹 {best_chain['id']}에 병합 완료")
            else:
                # 새로운 그룹 생성
                await self._create_new_process_chain([source_id, target_id])
                
        except Exception as e:
            logger.error(f"❌ 기존 그룹 병합 실패: {e}")
            raise e

    async def _create_new_process_chain(self, process_ids: List[int]):
        """새로운 통합 공정 그룹 생성"""
        try:
            # 1. 통합 그룹 생성
            chain_name = f"통합공정그룹-{min(process_ids)}-{max(process_ids)}"
            chain_data = {
                'chain_name': chain_name,
                'start_process_id': min(process_ids),
                'end_process_id': max(process_ids),
                'chain_length': len(process_ids),
                'is_active': True
            }
            
            chain = await self.calc_repository.create_process_chain(chain_data)
            logger.info(f"✅ 새로운 통합 그룹 생성: ID {chain['id']}")
            
            # 2. 그룹에 공정들 연결
            for i, process_id in enumerate(process_ids, 1):
                link_data = {
                    'chain_id': chain['id'],
                    'process_id': process_id,
                    'sequence_order': i,
                    'is_continue_edge': True
                }
                await self.calc_repository.create_process_chain_link(link_data)
            
            logger.info(f"✅ {len(process_ids)}개 공정을 그룹에 연결 완료")
            
            # 3. 통합 그룹의 총 배출량 계산 및 업데이트
            await self._calculate_and_update_chain_emission(chain['id'])
            
        except Exception as e:
            logger.error(f"❌ 새로운 통합 그룹 생성 실패: {e}")
            raise e

    async def _calculate_and_update_chain_emission(self, chain_id: int):
        """통합 그룹의 총 배출량 계산 및 업데이트"""
        try:
            # 그룹 내 모든 공정의 배출량 합계 계산
            total_emission = await self.calc_repository.calculate_chain_integrated_emissions(chain_id)
            logger.info(f"🔥 통합 그룹 {chain_id} 총 배출량: {total_emission}")
            
            # 그룹 정보 업데이트 (총 배출량 포함)
            await self.calc_repository.update_process_chain_emission(chain_id, total_emission)
            
        except Exception as e:
            logger.error(f"❌ 통합 그룹 배출량 계산 실패: {e}")
            raise e

    def _find_best_chain_for_merge(self, source_id: int, target_id: int, existing_chains: List[Dict]) -> Optional[Dict]:
        """병합에 가장 적합한 기존 그룹 찾기"""
        try:
            best_chain = None
            best_score = 0
            
            for chain in existing_chains:
                score = 0
                chain_processes = chain.get('processes', [])
                
                # 공정 연결성 점수 계산
                if source_id in chain_processes or target_id in chain_processes:
                    score += 10  # 이미 포함된 공정이 있으면 높은 점수
                
                # 그룹 크기 점수 (너무 큰 그룹은 피하기)
                if len(chain_processes) < 10:  # 최대 10개 공정까지만 허용
                    score += 5
                
                # 활성 상태 점수
                if chain.get('is_active', False):
                    score += 3
                
                if score > best_score:
                    best_score = score
                    best_chain = chain
            
            return best_chain
            
        except Exception as e:
            logger.error(f"❌ 최적 그룹 찾기 실패: {e}")
            return None