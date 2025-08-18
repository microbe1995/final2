# ============================================================================
# 🎮 CBAM 산정경계 설정 컨트롤러
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from loguru import logger
from typing import List, Dict, Any
import uuid
from datetime import datetime

from ..schema.cbam_schema import (
    CompanyInfo, CBAMProduct, ProductionProcess, CalculationBoundary,
    EmissionSource, SourceStream, ReportingPeriod, DataAllocation,
    CBAMBoundaryRequest, CBAMBoundaryResponse
)
from ..service.cbam_service import CBAMBoundaryMainService

# ============================================================================
# 🚀 CBAM 라우터 생성
# ============================================================================

cbam_router = APIRouter(
    prefix="/cbam",
    tags=["CBAM 산정경계 설정"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# ============================================================================
# 🔧 서비스 인스턴스 생성
# ============================================================================

cbam_service = CBAMBoundaryMainService()

# ============================================================================
# 🏭 기업 정보 관리 API
# ============================================================================

@cbam_router.post("/company/validate", response_model=Dict[str, Any])
async def validate_company_info(company_info: CompanyInfo):
    """기업 정보 검증"""
    try:
        logger.info(f"기업 정보 검증 요청: {company_info.company_name}")
        
        from ..service.cbam_service import CompanyValidationService
        is_valid, errors = CompanyValidationService.validate_company_info(company_info)
        
        return {
            "success": is_valid,
            "errors": errors,
            "message": "검증이 완료되었습니다" if is_valid else "검증 오류가 발생했습니다"
        }
    except Exception as e:
        logger.error(f"기업 정보 검증 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"기업 정보 검증 중 오류가 발생했습니다: {str(e)}"
        )

# ============================================================================
# 📦 CBAM 제품 관리 API
# ============================================================================

@cbam_router.post("/products/validate", response_model=Dict[str, Any])
async def validate_cbam_products(products: List[CBAMProduct]):
    """CBAM 제품 정보 검증"""
    try:
        logger.info(f"CBAM 제품 검증 요청: {len(products)}개 제품")
        
        from ..service.cbam_service import CBAMProductValidationService
        all_errors = []
        
        for product in products:
            is_valid, errors = CBAMProductValidationService.validate_product_info(product)
            if not is_valid:
                all_errors.extend([f"{product.product_name}: {error}" for error in errors])
        
        is_valid = len(all_errors) == 0
        
        return {
            "success": is_valid,
            "errors": all_errors,
            "message": "검증이 완료되었습니다" if is_valid else "검증 오류가 발생했습니다"
        }
    except Exception as e:
        logger.error(f"CBAM 제품 검증 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CBAM 제품 검증 중 오류가 발생했습니다: {str(e)}"
        )

@cbam_router.get("/products/hs-codes", response_model=Dict[str, str])
async def get_cbam_hs_codes():
    """CBAM 대상 HS 코드 목록 조회"""
    try:
        from ..service.cbam_service import CBAMProductValidationService
        return CBAMProductValidationService.CBAM_HS_CODES
    except Exception as e:
        logger.error(f"HS 코드 조회 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HS 코드 조회 중 오류가 발생했습니다: {str(e)}"
        )

@cbam_router.post("/products/check-target", response_model=Dict[str, Any])
async def check_cbam_target(hs_code: str, cn_code: str):
    """CBAM 대상 여부 확인"""
    try:
        from ..service.cbam_service import CBAMProductValidationService
        is_target = CBAMProductValidationService.check_cbam_target(hs_code, cn_code)
        
        return {
            "hs_code": hs_code,
            "cn_code": cn_code,
            "is_cbam_target": is_target,
            "message": f"HS 코드 {hs_code}는 CBAM {'대상' if is_target else '비대상'}입니다"
        }
    except Exception as e:
        logger.error(f"CBAM 대상 확인 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CBAM 대상 확인 중 오류가 발생했습니다: {str(e)}"
        )

# ============================================================================
# ⚙️ 생산 공정 관리 API
# ============================================================================

@cbam_router.post("/processes/validate", response_model=Dict[str, Any])
async def validate_production_processes(processes: List[ProductionProcess]):
    """생산 공정 정보 검증"""
    try:
        logger.info(f"생산 공정 검증 요청: {len(processes)}개 공정")
        
        from ..service.cbam_service import ProductionProcessValidationService
        all_errors = []
        
        # 개별 공정 검증
        for process in processes:
            is_valid, errors = ProductionProcessValidationService.validate_process_info(process)
            if not is_valid:
                all_errors.extend([f"{process.process_name}: {error}" for error in errors])
        
        # 공정 흐름 검증
        is_valid, errors = ProductionProcessValidationService.validate_process_flow(processes)
        if not is_valid:
            all_errors.extend(errors)
        
        is_valid = len(all_errors) == 0
        
        return {
            "success": is_valid,
            "errors": all_errors,
            "message": "검증이 완료되었습니다" if is_valid else "검증 오류가 발생했습니다"
        }
    except Exception as e:
        logger.error(f"생산 공정 검증 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"생산 공정 검증 중 오류가 발생했습니다: {str(e)}"
        )

@cbam_router.post("/processes/flow-analysis", response_model=Dict[str, Any])
async def analyze_process_flow(processes: List[ProductionProcess]):
    """생산 공정 흐름 분석"""
    try:
        logger.info(f"공정 흐름 분석 요청: {len(processes)}개 공정")
        
        # 공정 순서별 정렬
        sorted_processes = sorted(processes, key=lambda x: x.process_order)
        
        # 공정 간 연결성 분석
        flow_analysis = []
        for i, process in enumerate(sorted_processes):
            flow_info = {
                "process_id": process.process_id,
                "process_name": process.process_name,
                "process_order": process.process_order,
                "main_products": process.main_products,
                "input_materials": process.input_materials,
                "input_fuels": process.input_fuels,
                "energy_flows": process.energy_flows,
                "has_shared_utility": process.has_shared_utility,
                "produces_cbam_target": process.produces_cbam_target
            }
            
            # 이전 공정과의 연결성
            if i > 0:
                prev_process = sorted_processes[i-1]
                flow_info["previous_process"] = {
                    "process_id": prev_process.process_id,
                    "process_name": prev_process.process_name,
                    "connection_type": "순차적"
                }
            
            # 다음 공정과의 연결성
            if i < len(sorted_processes) - 1:
                next_process = sorted_processes[i+1]
                flow_info["next_process"] = {
                    "process_id": next_process.process_id,
                    "process_name": next_process.process_name,
                    "connection_type": "순차적"
                }
            
            flow_analysis.append(flow_info)
        
        return {
            "success": True,
            "total_processes": len(processes),
            "flow_analysis": flow_analysis,
            "message": "공정 흐름 분석이 완료되었습니다"
        }
    except Exception as e:
        logger.error(f"공정 흐름 분석 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공정 흐름 분석 중 오류가 발생했습니다: {str(e)}"
        )

# ============================================================================
# 📅 보고 기간 관리 API
# ============================================================================

@cbam_router.post("/periods/validate", response_model=Dict[str, Any])
async def validate_reporting_period(period: ReportingPeriod):
    """보고 기간 검증"""
    try:
        logger.info(f"보고 기간 검증 요청: {period.period_name}")
        
        from ..service.cbam_service import ReportingPeriodValidationService
        is_valid, errors = ReportingPeriodValidationService.validate_period(period)
        
        return {
            "success": is_valid,
            "errors": errors,
            "message": "검증이 완료되었습니다" if is_valid else "검증 오류가 발생했습니다"
        }
    except Exception as e:
        logger.error(f"보고 기간 검증 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고 기간 검증 중 오류가 발생했습니다: {str(e)}"
        )

@cbam_router.get("/periods/templates", response_model=Dict[str, Any])
async def get_period_templates():
    """보고 기간 템플릿 제공"""
    try:
        current_year = datetime.now().year
        
        templates = {
            "역년": {
                "period_type": "역년",
                "start_date": f"{current_year}-01-01T00:00:00",
                "end_date": f"{current_year}-12-31T23:59:59",
                "duration_months": 12,
                "description": f"{current_year}년 1월 1일부터 12월 31일까지"
            },
            "회계연도": {
                "period_type": "회계연도",
                "start_date": f"{current_year}-04-01T00:00:00",
                "end_date": f"{current_year+1}-03-31T23:59:59",
                "duration_months": 12,
                "description": f"{current_year}년 4월 1일부터 {current_year+1}년 3월 31일까지"
            },
            "국내제도": {
                "period_type": "국내제도",
                "start_date": f"{current_year}-01-01T00:00:00",
                "end_date": f"{current_year}-12-31T23:59:59",
                "duration_months": 12,
                "description": f"{current_year}년 온실가스 목표관리제 보고 기간"
            }
        }
        
        return {
            "success": True,
            "templates": templates,
            "message": "보고 기간 템플릿을 제공합니다"
        }
    except Exception as e:
        logger.error(f"보고 기간 템플릿 제공 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고 기간 템플릿 제공 중 오류가 발생했습니다: {str(e)}"
        )

# ============================================================================
# 🌍 산정경계 설정 API
# ============================================================================

@cbam_router.post("/boundary/create", response_model=CBAMBoundaryResponse)
async def create_cbam_boundary(request: CBAMBoundaryRequest):
    """CBAM 산정경계 설정 생성"""
    try:
        logger.info(f"CBAM 산정경계 설정 생성 요청: {request.company_info.company_name}")
        
        # 메인 서비스를 통한 산정경계 설정 생성
        response = cbam_service.create_cbam_boundary(request)
        
        logger.info(f"CBAM 산정경계 설정 생성 완료: {response.boundary_id}")
        return response
        
    except Exception as e:
        logger.error(f"CBAM 산정경계 설정 생성 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CBAM 산정경계 설정 생성 중 오류가 발생했습니다: {str(e)}"
        )

@cbam_router.post("/boundary/emission-sources", response_model=List[EmissionSource])
async def identify_emission_sources(
    boundary: CalculationBoundary,
    processes: List[ProductionProcess]
):
    """배출원 식별"""
    try:
        logger.info(f"배출원 식별 요청: {boundary.boundary_id}")
        
        from ..service.cbam_service import CalculationBoundaryService
        emission_sources = CalculationBoundaryService.identify_emission_sources(
            boundary, processes
        )
        
        return emission_sources
        
    except Exception as e:
        logger.error(f"배출원 식별 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"배출원 식별 중 오류가 발생했습니다: {str(e)}"
        )

@cbam_router.post("/boundary/source-streams", response_model=List[SourceStream])
async def identify_source_streams(
    boundary: CalculationBoundary,
    processes: List[ProductionProcess]
):
    """소스 스트림 식별"""
    try:
        logger.info(f"소스 스트림 식별 요청: {boundary.boundary_id}")
        
        from ..service.cbam_service import CalculationBoundaryService
        source_streams = CalculationBoundaryService.identify_source_streams(
            boundary, processes
        )
        
        return source_streams
        
    except Exception as e:
        logger.error(f"소스 스트림 식별 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"소스 스트림 식별 중 오류가 발생했습니다: {str(e)}"
        )

# ============================================================================
# 🔄 데이터 할당 API
# ============================================================================

@cbam_router.post("/allocation/create-plan", response_model=List[DataAllocation])
async def create_allocation_plan(
    boundary: CalculationBoundary,
    processes: List[ProductionProcess],
    shared_resources: List[str]
):
    """데이터 할당 계획 생성"""
    try:
        logger.info(f"데이터 할당 계획 생성 요청: {boundary.boundary_id}")
        
        from ..service.cbam_service import DataAllocationService
        allocations = DataAllocationService.create_allocation_plan(
            boundary, processes, shared_resources
        )
        
        return allocations
        
    except Exception as e:
        logger.error(f"데이터 할당 계획 생성 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 할당 계획 생성 중 오류가 발생했습니다: {str(e)}"
        )

# ============================================================================
# 📊 종합 분석 API
# ============================================================================

@cbam_router.post("/analysis/comprehensive", response_model=Dict[str, Any])
async def comprehensive_analysis(request: CBAMBoundaryRequest):
    """CBAM 산정경계 종합 분석"""
    try:
        logger.info(f"종합 분석 요청: {request.company_info.company_name}")
        
        # 1. 기본 검증
        validation_results = {
            "company_info": {"valid": True, "errors": []},
            "products": {"valid": True, "errors": []},
            "processes": {"valid": True, "errors": []},
            "period": {"valid": True, "errors": []}
        }
        
        # 기업 정보 검증
        from ..service.cbam_service import CompanyValidationService
        is_valid, errors = CompanyValidationService.validate_company_info(request.company_info)
        validation_results["company_info"] = {"valid": is_valid, "errors": errors}
        
        # 제품 검증
        from ..service.cbam_service import CBAMProductValidationService
        product_errors = []
        for product in request.target_products:
            is_valid, errors = CBAMProductValidationService.validate_product_info(product)
            if not is_valid:
                product_errors.extend([f"{product.product_name}: {error}" for error in errors])
        validation_results["products"] = {"valid": len(product_errors) == 0, "errors": product_errors}
        
        # 공정 검증
        from ..service.cbam_service import ProductionProcessValidationService
        process_errors = []
        for process in request.production_processes:
            is_valid, errors = ProductionProcessValidationService.validate_process_info(process)
            if not is_valid:
                process_errors.extend([f"{process.process_name}: {error}" for error in errors])
        
        # 공정 흐름 검증
        is_valid, errors = ProductionProcessValidationService.validate_process_flow(request.production_processes)
        if not is_valid:
            process_errors.extend(errors)
        validation_results["processes"] = {"valid": len(process_errors) == 0, "errors": process_errors}
        
        # 기간 검증
        from ..service.cbam_service import ReportingPeriodValidationService
        is_valid, errors = ReportingPeriodValidationService.validate_period(request.reporting_period)
        validation_results["period"] = {"valid": is_valid, "errors": errors}
        
        # 2. 산정경계 설정 생성
        boundary_response = None
        if all(result["valid"] for result in validation_results.values()):
            boundary_response = cbam_service.create_cbam_boundary(request)
        
        # 3. 분석 결과 요약
        analysis_summary = {
            "total_validation_errors": sum(len(result["errors"]) for result in validation_results.values()),
            "cbam_target_products": len([p for p in request.target_products if p.is_cbam_target]),
            "total_processes": len(request.production_processes),
            "cbam_target_processes": len([p for p in request.production_processes if p.produces_cbam_target]),
            "shared_utilities": len([p for p in request.production_processes if p.has_shared_utility]),
            "processes_without_measurement": len([p for p in request.production_processes if not p.has_measurement])
        }
        
        return {
            "success": True,
            "validation_results": validation_results,
            "boundary_response": boundary_response,
            "analysis_summary": analysis_summary,
            "message": "종합 분석이 완료되었습니다"
        }
        
    except Exception as e:
        logger.error(f"종합 분석 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"종합 분석 중 오류가 발생했습니다: {str(e)}"
        )

# ============================================================================
# 📋 상태 확인 API
# ============================================================================

@cbam_router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "CBAM 산정경계 설정 서비스",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@cbam_router.get("/info", response_model=Dict[str, Any])
async def service_info():
    """서비스 정보 조회"""
    return {
        "service_name": "CBAM 산정경계 설정 서비스",
        "description": "EU CBAM 규정에 따른 철강 제품 배출량 산정을 위한 산정경계 설정 모듈",
        "version": "1.0.0",
        "features": [
            "기업 정보 검증",
            "CBAM 제품 검증",
            "생산 공정 검증",
            "보고 기간 검증",
            "산정경계 설정",
            "배출원 및 소스 스트림 식별",
            "데이터 할당 계획 수립",
            "종합 분석"
        ],
        "supported_industries": ["철강", "알루미늄", "복합비료"],
        "api_endpoints": [
            "/cbam/company/validate",
            "/cbam/products/validate",
            "/cbam/processes/validate",
            "/cbam/periods/validate",
            "/cbam/boundary/create",
            "/cbam/analysis/comprehensive"
        ]
    }
