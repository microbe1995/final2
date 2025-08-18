# ============================================================================
# 🔧 CBAM 산정경계 설정 서비스
# ============================================================================

from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import uuid
from datetime import datetime, timedelta

from ..schema.cbam_schema import (
    CompanyInfo, CBAMProduct, ProductionProcess, CalculationBoundary,
    EmissionSource, SourceStream, ReportingPeriod, DataAllocation,
    CBAMBoundaryRequest, CBAMBoundaryResponse
)

# ============================================================================
# 🏭 기업 정보 검증 서비스
# ============================================================================

class CompanyValidationService:
    """기업 정보 검증 서비스"""
    
    @staticmethod
    def validate_company_info(company_info: CompanyInfo) -> Tuple[bool, List[str]]:
        """기업 정보 검증"""
        errors = []
        
        # 기업명 검증
        if not company_info.company_name or len(company_info.company_name.strip()) < 2:
            errors.append("기업명은 2자 이상이어야 합니다")
        
        # 사업자등록번호 검증 (10자리 숫자)
        if not company_info.business_number or not company_info.business_number.isdigit() or len(company_info.business_number) != 10:
            errors.append("사업자등록번호는 10자리 숫자여야 합니다")
        
        # 이메일 형식 검증
        if not company_info.contact_email or '@' not in company_info.contact_email:
            errors.append("올바른 이메일 형식이 아닙니다")
        
        # 전화번호 형식 검증
        if not company_info.contact_phone or len(company_info.contact_phone.replace('-', '')) < 10:
            errors.append("올바른 전화번호 형식이 아닙니다")
        
        return len(errors) == 0, errors

# ============================================================================
# 📦 CBAM 제품 검증 서비스
# ============================================================================

class CBAMProductValidationService:
    """CBAM 제품 검증 서비스"""
    
    # CBAM 대상 HS 코드 (철강 제품)
    CBAM_HS_CODES = {
        "7208": "열간압연 평판제품",
        "7209": "냉간압연 평판제품", 
        "7210": "도금 평판제품",
        "7211": "실린더 평판제품",
        "7212": "기타 평판제품",
        "7213": "선재",
        "7214": "형강",
        "7215": "기타 형강",
        "7216": "기타 제품"
    }
    
    @staticmethod
    def validate_hs_code(hs_code: str) -> bool:
        """HS 코드 유효성 검증"""
        return hs_code in CBAMProductValidationService.CBAM_HS_CODES
    
    @staticmethod
    def check_cbam_target(hs_code: str, cn_code: str) -> bool:
        """CBAM 대상 여부 확인"""
        # HS 코드 6자리가 CBAM 대상 코드에 포함되는지 확인
        return hs_code in CBAMProductValidationService.CBAM_HS_CODES
    
    @staticmethod
    def validate_product_info(product: CBAMProduct) -> Tuple[bool, List[str]]:
        """제품 정보 검증"""
        errors = []
        
        # HS 코드 검증
        if not product.hs_code or len(product.hs_code) != 4:
            errors.append("HS 코드는 4자리여야 합니다")
        elif not CBAMProductValidationService.validate_hs_code(product.hs_code):
            errors.append(f"HS 코드 {product.hs_code}는 유효하지 않습니다")
        
        # CN 코드 검증 (HS 코드 + 2자리)
        if not product.cn_code or len(product.cn_code) != 6:
            errors.append("CN 코드는 6자리여야 합니다")
        elif not product.cn_code.startswith(product.hs_code):
            errors.append("CN 코드는 HS 코드로 시작해야 합니다")
        
        # 제품명 검증
        if not product.product_name or len(product.product_name.strip()) < 2:
            errors.append("제품명은 2자 이상이어야 합니다")
        
        # 단위 검증
        valid_units = ["톤", "kg", "g", "리터", "m³"]
        if product.unit not in valid_units:
            errors.append(f"단위는 다음 중 하나여야 합니다: {', '.join(valid_units)}")
        
        return len(errors) == 0, errors

# ============================================================================
# ⚙️ 생산 공정 검증 서비스
# ============================================================================

class ProductionProcessValidationService:
    """생산 공정 검증 서비스"""
    
    @staticmethod
    def validate_process_info(process: ProductionProcess) -> Tuple[bool, List[str]]:
        """생산 공정 정보 검증"""
        errors = []
        
        # 공정 ID 검증
        if not process.process_id or len(process.process_id.strip()) < 3:
            errors.append("공정 ID는 3자 이상이어야 합니다")
        
        # 공정명 검증
        if not process.process_name or len(process.process_name.strip()) < 2:
            errors.append("공정명은 2자 이상이어야 합니다")
        
        # 주요 생산품 검증
        if not process.main_products or len(process.main_products) == 0:
            errors.append("주요 생산품을 최소 1개 이상 입력해야 합니다")
        
        # 투입 원료 검증
        if not process.input_materials or len(process.input_materials) == 0:
            errors.append("투입 원료를 최소 1개 이상 입력해야 합니다")
        
        # 투입 연료 검증
        if not process.input_fuels or len(process.input_fuels) == 0:
            errors.append("투입 연료를 최소 1개 이상 입력해야 합니다")
        
        # 공정 순서 검증
        if process.process_order < 1:
            errors.append("공정 순서는 1 이상이어야 합니다")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_process_flow(processes: List[ProductionProcess]) -> Tuple[bool, List[str]]:
        """공정 흐름 검증"""
        errors = []
        
        # 공정 순서 중복 검증
        process_orders = [p.process_order for p in processes]
        if len(process_orders) != len(set(process_orders)):
            errors.append("공정 순서가 중복됩니다")
        
        # 공정 순서 연속성 검증
        sorted_processes = sorted(processes, key=lambda x: x.process_order)
        for i, process in enumerate(sorted_processes):
            if process.process_order != i + 1:
                errors.append(f"공정 순서가 연속되지 않습니다: {process.process_name}")
        
        return len(errors) == 0, errors

# ============================================================================
# 📅 보고 기간 검증 서비스
# ============================================================================

class ReportingPeriodValidationService:
    """보고 기간 검증 서비스"""
    
    @staticmethod
    def validate_period(period: ReportingPeriod) -> Tuple[bool, List[str]]:
        """보고 기간 검증"""
        errors = []
        
        # 기간 유형 검증
        valid_period_types = ["역년", "회계연도", "국내제도"]
        if period.period_type not in valid_period_types:
            errors.append(f"기간 유형은 다음 중 하나여야 합니다: {', '.join(valid_period_types)}")
        
        # 시작일/종료일 검증
        if period.start_date >= period.end_date:
            errors.append("시작일은 종료일보다 이전이어야 합니다")
        
        # 기간 길이 검증
        if period.duration_months < 3 or period.duration_months > 12:
            errors.append("보고 기간은 3개월 이상 12개월 이하여야 합니다")
        
        # 실제 기간과 duration_months 일치 검증
        actual_months = (period.end_date.year - period.start_date.year) * 12 + (period.end_date.month - period.start_date.month)
        if abs(actual_months - period.duration_months) > 1:  # 1개월 오차 허용
            errors.append("실제 기간과 설정된 기간이 일치하지 않습니다")
        
        return len(errors) == 0, errors

# ============================================================================
# 🌍 산정경계 설정 서비스
# ============================================================================

class CalculationBoundaryService:
    """산정경계 설정 서비스"""
    
    @staticmethod
    def create_boundary_configuration(
        company_info: CompanyInfo,
        products: List[CBAMProduct],
        processes: List[ProductionProcess],
        period: ReportingPeriod,
        preferences: Dict[str, Any]
    ) -> CalculationBoundary:
        """산정경계 설정 생성"""
        
        # CBAM 대상 제품 생산 공정 식별
        cbam_target_processes = [
            p.process_id for p in processes 
            if p.produces_cbam_target
        ]
        
        # CBAM 비대상 제품 생산 공정 식별
        non_cbam_processes = [
            p.process_id for p in processes 
            if not p.produces_cbam_target
        ]
        
        # 공동 사용 유틸리티 식별
        shared_utilities = []
        for process in processes:
            if process.has_shared_utility:
                # 공정별 주요 에너지/물질 흐름에서 유틸리티 추출
                for flow in process.energy_flows:
                    if any(utility in flow.lower() for utility in ["보일러", "발전", "스팀", "냉각수"]):
                        if flow not in shared_utilities:
                            shared_utilities.append(flow)
        
        # 경계 유형 결정
        boundary_type = preferences.get("boundary_type", "통합")
        if len(cbam_target_processes) == 1:
            boundary_type = "개별"
        
        # 데이터 할당 방법 결정
        allocation_method = preferences.get("allocation_method", "가동시간 기준")
        if shared_utilities:
            allocation_method = f"{allocation_method} + 공동유틸리티 가상분할"
        
        boundary = CalculationBoundary(
            boundary_id=f"BOUND_{uuid.uuid4().hex[:8].upper()}",
            boundary_name=f"{company_info.company_name} {period.period_name} 산정경계",
            boundary_type=boundary_type,
            included_processes=cbam_target_processes,
            excluded_processes=non_cbam_processes,
            shared_utilities=shared_utilities,
            allocation_method=allocation_method,
            description=f"{company_info.company_name}의 {period.period_name} CBAM 대상 제품 생산을 위한 산정경계"
        )
        
        return boundary
    
    @staticmethod
    def identify_emission_sources(
        boundary: CalculationBoundary,
        processes: List[ProductionProcess]
    ) -> List[EmissionSource]:
        """배출원 식별"""
        emission_sources = []
        
        for process in processes:
            if process.process_id in boundary.included_processes:
                # 연소 설비 배출원
                if any("연소" in fuel.lower() for fuel in process.input_fuels):
                    emission_sources.append(EmissionSource(
                        source_id=f"EMIT_{process.process_id}",
                        source_name=f"{process.process_name} 연소설비",
                        source_type="연소설비",
                        ghg_types=["CO2"],  # 철강은 CO2만
                        process_id=process.process_id,
                        measurement_method="연속측정" if process.has_measurement else "계산"
                    ))
                
                # 화학 반응 배출원
                if any("석회석" in material for material in process.input_materials):
                    emission_sources.append(EmissionSource(
                        source_id=f"EMIT_{process.process_id}_CHEM",
                        source_name=f"{process.process_name} 화학반응",
                        source_type="화학반응",
                        ghg_types=["CO2"],
                        process_id=process.process_id,
                        measurement_method="계산"
                    ))
        
        return emission_sources
    
    @staticmethod
    def identify_source_streams(
        boundary: CalculationBoundary,
        processes: List[ProductionProcess]
    ) -> List[SourceStream]:
        """소스 스트림 식별"""
        source_streams = []
        
        # 연료 스트림
        fuel_streams = set()
        for process in processes:
            if process.process_id in boundary.included_processes:
                for fuel in process.input_fuels:
                    if fuel not in fuel_streams:
                        fuel_streams.add(fuel)
                        source_streams.append(SourceStream(
                            stream_id=f"STREAM_{fuel}",
                            stream_name=fuel,
                            stream_type="연료",
                            carbon_content=CalculationBoundaryService._get_carbon_content(fuel),
                            is_precursor=False,
                            unit="톤"
                        ))
        
        # 원료 스트림 (전구물질 여부 확인)
        material_streams = set()
        for process in processes:
            if process.process_id in boundary.included_processes:
                for material in process.input_materials:
                    if material not in material_streams:
                        material_streams.add(material)
                        is_precursor = CalculationBoundaryService._is_precursor_material(material)
                        source_streams.append(SourceStream(
                            stream_id=f"STREAM_{material}",
                            stream_name=material,
                            stream_type="원료",
                            carbon_content=CalculationBoundaryService._get_carbon_content(material),
                            is_precursor=is_precursor,
                            precursor_process_id=process.process_id if is_precursor else None,
                            unit="톤"
                        ))
        
        return source_streams
    
    @staticmethod
    def _get_carbon_content(material_name: str) -> float:
        """물질별 탄소 함량 반환"""
        carbon_contents = {
            "코크스": 85.5,
            "석탄": 75.0,
            "천연가스": 75.0,
            "석회석": 12.0,
            "철광석": 2.0,
            "철스크랩": 0.5
        }
        return carbon_contents.get(material_name, 50.0)  # 기본값
    
    @staticmethod
    def _is_precursor_material(material_name: str) -> bool:
        """전구물질 여부 확인"""
        precursor_materials = ["소결광", "펠릿", "선철", "용강"]
        return material_name in precursor_materials

# ============================================================================
# 🔄 데이터 할당 서비스
# ============================================================================

class DataAllocationService:
    """데이터 할당 서비스"""
    
    @staticmethod
    def create_allocation_plan(
        boundary: CalculationBoundary,
        processes: List[ProductionProcess],
        shared_resources: List[str]
    ) -> List[DataAllocation]:
        """데이터 할당 계획 생성"""
        allocations = []
        
        for resource in shared_resources:
            # 공유 자원을 사용하는 공정 식별
            using_processes = [
                p.process_id for p in processes 
                if p.process_id in boundary.included_processes and p.has_shared_utility
            ]
            
            if len(using_processes) > 1:
                # 할당 방법 결정
                allocation_method = "가동시간 기준"
                if "전력" in resource:
                    allocation_method = "전력사용량 기준"
                elif "열" in resource:
                    allocation_method = "열사용량 기준"
                
                # 할당 비율 계산 (균등 분배)
                allocation_factors = {
                    process_id: 1.0 / len(using_processes) 
                    for process_id in using_processes
                }
                
                allocations.append(DataAllocation(
                    allocation_id=f"ALLOC_{resource}",
                    shared_resource=resource,
                    resource_type=DataAllocationService._get_resource_type(resource),
                    total_consumption=100.0,  # 예시 값
                    unit="톤",
                    allocation_method=allocation_method,
                    allocation_factors=allocation_factors,
                    measurement_reliability="법정계량기"
                ))
        
        return allocations
    
    @staticmethod
    def _get_resource_type(resource_name: str) -> str:
        """자원 유형 판별"""
        if any(keyword in resource_name.lower() for keyword in ["연료", "가스", "석탄"]):
            return "연료"
        elif any(keyword in resource_name.lower() for keyword in ["전력", "전기"]):
            return "전력"
        elif any(keyword in resource_name.lower() for keyword in ["열", "스팀", "냉각"]):
            return "열"
        else:
            return "원료"

# ============================================================================
# 📋 CBAM 산정경계 설정 메인 서비스
# ============================================================================

class CBAMBoundaryMainService:
    """CBAM 산정경계 설정 메인 서비스"""
    
    def __init__(self):
        self.company_validator = CompanyValidationService()
        self.product_validator = CBAMProductValidationService()
        self.process_validator = ProductionProcessValidationService()
        self.period_validator = ReportingPeriodValidationService()
        self.boundary_service = CalculationBoundaryService()
        self.allocation_service = DataAllocationService()
    
    def create_cbam_boundary(
        self, 
        request: CBAMBoundaryRequest
    ) -> CBAMBoundaryResponse:
        """CBAM 산정경계 설정 생성"""
        
        validation_errors = []
        recommendations = []
        
        # 1단계: 기업 정보 검증
        is_valid, errors = self.company_validator.validate_company_info(request.company_info)
        if not is_valid:
            validation_errors.extend(errors)
        
        # 2단계: CBAM 제품 검증
        for product in request.target_products:
            is_valid, errors = self.product_validator.validate_product_info(product)
            if not is_valid:
                validation_errors.extend([f"{product.product_name}: {error}" for error in errors])
        
        # 3단계: 생산 공정 검증
        for process in request.production_processes:
            is_valid, errors = self.process_validator.validate_process_info(process)
            if not is_valid:
                validation_errors.extend([f"{process.process_name}: {error}" for error in errors])
        
        # 공정 흐름 검증
        is_valid, errors = self.process_validator.validate_process_flow(request.production_processes)
        if not is_valid:
            validation_errors.extend(errors)
        
        # 4단계: 보고 기간 검증
        is_valid, errors = self.period_validator.validate_period(request.reporting_period)
        if not is_valid:
            validation_errors.extend(errors)
        
        # 검증 오류가 있으면 응답 생성
        if validation_errors:
            return CBAMBoundaryResponse(
                boundary_id="",
                boundary_configuration=CalculationBoundary(
                    boundary_id="",
                    boundary_name="",
                    boundary_type="",
                    included_processes=[],
                    excluded_processes=[],
                    shared_utilities=[],
                    allocation_method="",
                    description=""
                ),
                emission_sources=[],
                source_streams=[],
                data_allocations=[],
                recommendations=[],
                validation_errors=validation_errors,
                next_steps=["입력 데이터를 수정하고 다시 시도하세요"]
            )
        
        # 5단계: 산정경계 설정 생성
        boundary = self.boundary_service.create_boundary_configuration(
            request.company_info,
            request.target_products,
            request.production_processes,
            request.reporting_period,
            request.boundary_preferences
        )
        
        # 6단계: 배출원 및 소스 스트림 식별
        emission_sources = self.boundary_service.identify_emission_sources(
            boundary, 
            request.production_processes
        )
        
        source_streams = self.boundary_service.identify_source_streams(
            boundary, 
            request.production_processes
        )
        
        # 7단계: 데이터 할당 계획 수립
        data_allocations = self.allocation_service.create_allocation_plan(
            boundary,
            request.production_processes,
            boundary.shared_utilities
        )
        
        # 8단계: 권장사항 및 다음 단계 생성
        recommendations = self._generate_recommendations(boundary, request)
        next_steps = self._generate_next_steps(boundary, request)
        
        return CBAMBoundaryResponse(
            boundary_id=boundary.boundary_id,
            boundary_configuration=boundary,
            emission_sources=emission_sources,
            source_streams=source_streams,
            data_allocations=data_allocations,
            recommendations=recommendations,
            validation_errors=validation_errors,
            next_steps=next_steps
        )
    
    def _generate_recommendations(
        self, 
        boundary: CalculationBoundary, 
        request: CBAMBoundaryRequest
    ) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # CBAM 대상 제품 중심 경계 설정 권장
        cbam_target_count = len([p for p in request.target_products if p.is_cbam_target])
        if cbam_target_count > 0:
            recommendations.append("CBAM 대상 제품 생산 공정을 중심으로 경계를 설정하세요")
        
        # 공동 사용 유틸리티 가상 분할 권장
        if boundary.shared_utilities:
            recommendations.append("공동 사용 유틸리티는 가상 분할을 통해 할당하세요")
        
        # 계측기 설치 권장
        processes_without_measurement = [
            p for p in request.production_processes 
            if not p.has_measurement and p.process_id in boundary.included_processes
        ]
        if processes_without_measurement:
            recommendations.append("계측기가 없는 공정에 계측기를 설치하여 데이터 정확성을 높이세요")
        
        # 전구물질 관리 권장
        precursor_materials = [
            s for s in request.target_products 
            if any("소결광" in p.main_products for p in request.production_processes)
        ]
        if precursor_materials:
            recommendations.append("전구물질의 내재 배출량을 정확히 계산하여 복합제품 배출량에 반영하세요")
        
        return recommendations
    
    def _generate_next_steps(
        self, 
        boundary: CalculationBoundary, 
        request: CBAMBoundaryRequest
    ) -> List[str]:
        """다음 단계 생성"""
        next_steps = []
        
        # 기본 단계
        next_steps.extend([
            "배출원 및 소스 스트림 식별 완료",
            "데이터 할당 계획 수립 완료"
        ])
        
        # 계측기 관련 단계
        if any(not p.has_measurement for p in request.production_processes):
            next_steps.append("계측기 설치 및 검증")
        
        # 데이터 수집 단계
        next_steps.extend([
            "연료 및 원료 사용량 데이터 수집",
            "전력 사용량 데이터 수집",
            "제품별 생산량 데이터 수집"
        ])
        
        # 배출량 계산 단계
        next_steps.extend([
            "직접 배출량 계산",
            "간접 배출량 계산",
            "전구물질 내재 배출량 계산"
        ])
        
        # 검증 및 보고 단계
        next_steps.extend([
            "배출량 계산 결과 검증",
            "CBAM 보고서 작성",
            "EU 수입업자와 데이터 공유"
        ])
        
        return next_steps
