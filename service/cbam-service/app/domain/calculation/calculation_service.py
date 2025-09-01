# ============================================================================
# 🎯 Calculation Service - CBAM 계산 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.calculation.calculation_repository import CalculationRepository
from app.domain.calculation.calculation_schema import (
    ProcessAttrdirEmissionCreateRequest, ProcessAttrdirEmissionResponse, ProcessAttrdirEmissionUpdateRequest,
    ProcessEmissionCalculationRequest, ProcessEmissionCalculationResponse,
    ProductEmissionCalculationRequest, ProductEmissionCalculationResponse,
    EmissionPropagationRequest, EmissionPropagationResponse,
    GraphRecalculationRequest, GraphRecalculationResponse,
    CircularReferenceError
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
            else:
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

    async def calculate_product_total_emission(self, product_id: int) -> ProductEmissionCalculationResponse:
        """제품별 총 배출량 계산"""
        try:
            result = await self.calc_repository.calculate_product_total_emission(product_id)
            if result:
                return ProductEmissionCalculationResponse(**result)
            else:
                raise Exception("제품별 총 배출량 계산에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error calculating product total emission for product {product_id}: {e}")
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
    # 🔄 공정 간 값 전파 관련 메서드들 (1단계 핵심 기능)
    # ============================================================================
    
    async def propagate_emissions(self, request: EmissionPropagationRequest) -> EmissionPropagationResponse:
        """공정 간 배출량 전파 계산 (핵심 메서드)"""
        try:
            logger.info(f"🔄 배출량 전파 시작: {request.source_process_id} → {request.target_process_id} ({request.edge_kind})")
            
            # 1. 순환 참조 검증
            if request.edge_kind == "continue":
                is_circular = await self._check_circular_reference(
                    request.source_process_id, request.target_process_id
                )
                if is_circular:
                    raise CircularReferenceError(
                        error_type="CIRCULAR_REFERENCE",
                        error_message="순환 참조가 감지되었습니다",
                        affected_processes=[request.source_process_id, request.target_process_id],
                        cycle_path=[request.source_process_id, request.target_process_id]
                    )
            
            # 2. 소스 공정 배출량 조회
            source_emission = await self.calc_repository.get_process_attrdir_emission(request.source_process_id)
            if not source_emission:
                raise Exception(f"소스 공정 {request.source_process_id}의 배출량을 찾을 수 없습니다.")
            
            source_em = float(source_emission['attrdir_em'])
            
            # 3. 타겟 공정 배출량 조회
            target_emission = await self.calc_repository.get_process_attrdir_emission(request.target_process_id)
            if not target_emission:
                raise Exception(f"타겟 공정 {request.target_process_id}의 배출량을 찾을 수 없습니다.")
            
            target_em = float(target_emission['attrdir_em'])
            
            # 4. 엣지 종류별 전파 계산
            propagated_amount, target_new_emission, propagation_formula = await self._calculate_propagation(
                request.edge_kind, source_em, target_em, request.propagation_amount
            )
            
            # 5. 타겟 공정 배출량 업데이트
            await self.calc_repository.update_process_attrdir_emission(
                request.target_process_id, 
                {"attrdir_em": target_new_emission}
            )
            
            # 6. 응답 생성
            response = EmissionPropagationResponse(
                source_process_id=request.source_process_id,
                target_process_id=request.target_process_id,
                edge_kind=request.edge_kind,
                source_original_emission=source_em,
                target_original_emission=target_em,
                propagated_amount=propagated_amount,
                target_new_emission=target_new_emission,
                propagation_formula=propagation_formula,
                calculation_date=datetime.utcnow()
            )
            
            logger.info(f"✅ 배출량 전파 완료: {propagated_amount} tCO2e 전파됨")
            return response
            
        except Exception as e:
            logger.error(f"❌ 배출량 전파 실패: {str(e)}")
            raise e
    
    async def recalculate_entire_graph(self, request: GraphRecalculationRequest) -> GraphRecalculationResponse:
        """전체 그래프 재계산 (엣지 변경 시 호출)"""
        try:
            logger.info(f"🚀 전체 그래프 재계산 시작: trigger_edge_id={request.trigger_edge_id}")
            
            # 1. 순환 참조 검증 (옵션)
            validation_errors = []
            if request.include_validation:
                validation_errors = await self._validate_graph_structure()
            
            # 2. 모든 continue 엣지 찾기
            continue_edges = await self.calc_repository.get_continue_edges()
            
            # 3. 각 continue 엣지에 대해 배출량 전파 실행
            propagation_chains = []
            total_emission_propagated = 0.0
            total_processes_calculated = 0
            
            for edge in continue_edges:
                try:
                    propagation_request = EmissionPropagationRequest(
                        source_process_id=edge['source_id'],
                        target_process_id=edge['target_id'],
                        edge_kind="continue"
                    )
                    
                    propagation_result = await self.propagate_emissions(propagation_request)
                    propagation_chains.append(propagation_result)
                    total_emission_propagated += propagation_result.propagated_amount
                    total_processes_calculated += 1
                    
                except Exception as e:
                    logger.warning(f"⚠️ 엣지 {edge['id']} 전파 실패: {str(e)}")
                    validation_errors.append(f"엣지 {edge['id']}: {str(e)}")
            
            # 4. 응답 생성
            response = GraphRecalculationResponse(
                total_processes_calculated=total_processes_calculated,
                total_emission_propagated=total_emission_propagated,
                propagation_chains=propagation_chains,
                validation_errors=validation_errors,
                calculation_date=datetime.utcnow(),
                status="success" if not validation_errors else "partial_success"
            )
            
            logger.info(f"✅ 전체 그래프 재계산 완료: {total_processes_calculated}개 공정, {total_emission_propagated} tCO2e 전파")
            return response
            
        except Exception as e:
            logger.error(f"❌ 전체 그래프 재계산 실패: {str(e)}")
            raise e
    
    # ============================================================================
    # 🔍 내부 헬퍼 메서드들
    # ============================================================================
    
    async def _calculate_propagation(self, edge_kind: str, source_em: float, target_em: float, 
                                   propagation_amount: Optional[float] = None) -> tuple[float, float, str]:
        """엣지 종류별 전파 계산 로직"""
        if edge_kind == "continue":
            # 공정→공정: source.attr_em이 target으로 누적 전달
            propagated = source_em
            new_target_em = target_em + source_em
            formula = f"타겟새배출량 = 기존배출량({target_em}) + 소스배출량({source_em}) = {new_target_em}"
            
        elif edge_kind == "produce":
            # 공정→제품: product.attr_em = sum(connected_processes.attr_em)
            propagated = source_em
            new_target_em = source_em  # 제품은 연결된 공정들의 합
            formula = f"제품배출량 = 연결된공정배출량({source_em})"
            
        elif edge_kind == "consume":
            # 제품→공정: to_next_process = product_amount - product_sell - product_eusell
            if propagation_amount is None:
                # 자동 계산 시 기본값 사용
                propagated = source_em * 0.1  # 예시: 10% 전파
            else:
                propagated = propagation_amount
            new_target_em = target_em + propagated
            formula = f"타겟새배출량 = 기존배출량({target_em}) + 소비전파량({propagated}) = {new_target_em}"
            
        else:
            raise ValueError(f"지원하지 않는 엣지 종류: {edge_kind}")
        
        return propagated, new_target_em, formula
    
    async def _check_circular_reference(self, source_id: int, target_id: int) -> bool:
        """순환 참조 검증 (DFS 기반)"""
        try:
            visited = set()
            path = []
            
            async def dfs(current_id: int, target: int) -> bool:
                if current_id == target:
                    return True
                if current_id in visited:
                    return False
                
                visited.add(current_id)
                path.append(current_id)
                
                # 현재 공정에서 나가는 continue 엣지들 찾기
                outgoing_edges = await self.calc_repository.get_outgoing_continue_edges(current_id)
                
                for edge in outgoing_edges:
                    if await dfs(edge['target_id'], target):
                        return True
                
                path.pop()
                return False
            
            return await dfs(target_id, source_id)
            
        except Exception as e:
            logger.warning(f"⚠️ 순환 참조 검증 중 오류: {str(e)}")
            return False  # 오류 발생 시 안전하게 False 반환
    
    async def _validate_graph_structure(self) -> List[str]:
        """전체 그래프 구조 검증"""
        errors = []
        try:
            # 1. 고립된 공정 확인
            isolated_processes = await self.calc_repository.get_isolated_processes()
            if isolated_processes:
                errors.append(f"고립된 공정 발견: {len(isolated_processes)}개")
            
            # 2. 무한 루프 가능성 확인
            long_chains = await self.calc_repository.get_very_long_chains(max_length=20)
            if long_chains:
                errors.append(f"매우 긴 체인 발견: {len(long_chains)}개 (20단계 이상)")
            
        except Exception as e:
            logger.warning(f"⚠️ 그래프 구조 검증 중 오류: {str(e)}")
            errors.append(f"검증 오류: {str(e)}")
        
        return errors

