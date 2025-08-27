# ============================================================================
# 🎮 Calculation Controller - Product API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from loguru import logger
import time

from .calculation_service import CalculationService
from .calculation_schema import ProductCreateRequest, ProductResponse, ProductUpdateRequest, ProcessCreateRequest, ProcessResponse, ProcessUpdateRequest, ProductNameResponse, InstallCreateRequest, InstallResponse, InstallUpdateRequest, InstallNameResponse, ProcessInputResponse, ProcessInputCreateRequest, ProcessInputUpdateRequest, EmissionCalculationResponse, ProductEmissionResponse

router = APIRouter(prefix="", tags=["Product"])

# 서비스 인스턴스 생성
calculation_service = CalculationService()

# ============================================================================
# 🏭 Install 관련 엔드포인트
# ============================================================================

@router.get("/install", response_model=List[InstallResponse])
async def get_installs():
    """사업장 목록 조회"""
    try:
        logger.info("📋 사업장 목록 조회 요청")
        installs = await calculation_service.get_installs()
        logger.info(f"✅ 사업장 목록 조회 성공: {len(installs)}개")
        return installs
    except Exception as e:
        logger.error(f"❌ 사업장 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/install/names", response_model=List[InstallNameResponse])
async def get_install_names():
    """사업장명 목록 조회 (드롭다운용)"""
    try:
        logger.info("📋 사업장명 목록 조회 요청")
        install_names = await calculation_service.get_install_names()
        logger.info(f"✅ 사업장명 목록 조회 성공: {len(install_names)}개")
        return install_names
    except Exception as e:
        logger.error(f"❌ 사업장명 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장명 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/install/{install_id}", response_model=InstallResponse)
async def get_install(install_id: int):
    """특정 사업장 조회"""
    try:
        logger.info(f"📋 사업장 조회 요청: ID {install_id}")
        install = await calculation_service.get_install(install_id)
        if not install:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 조회 성공: ID {install_id}")
        return install
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/install", response_model=InstallResponse)
async def create_install(request: InstallCreateRequest):
    """사업장 생성"""
    try:
        logger.info(f"🏭 사업장 생성 요청: {request.name}")
        result = await calculation_service.create_install(request)
        logger.info(f"✅ 사업장 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 사업장 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/install/{install_id}", response_model=InstallResponse)
async def update_install(install_id: int, request: InstallUpdateRequest):
    """사업장 수정"""
    try:
        logger.info(f"📝 사업장 수정 요청: ID {install_id}")
        result = await calculation_service.update_install(install_id, request)
        if not result:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 수정 성공: ID {install_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/install/{install_id}")
async def delete_install(install_id: int):
    """사업장 삭제"""
    try:
        logger.info(f"🗑️ 사업장 삭제 요청: ID {install_id}")
        success = await calculation_service.delete_install(install_id)
        if not success:
            raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
        
        logger.info(f"✅ 사업장 삭제 성공: ID {install_id}")
        return {"message": "사업장이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 사업장 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"사업장 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 Product 관련 엔드포인트 (단수형으로 통일)
# ============================================================================

@router.get("/product", response_model=List[ProductResponse])
async def get_products():
    """제품 목록 조회"""
    try:
        logger.info("📋 제품 목록 조회 요청")
        products = await calculation_service.get_products()
        logger.info(f"✅ 제품 목록 조회 성공: {len(products)}개")
        return products
    except Exception as e:
        logger.error(f"❌ 제품 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/product/names", response_model=List[ProductNameResponse])
async def get_product_names():
    """제품명 목록 조회 (드롭다운용)"""
    try:
        logger.info("📋 제품명 목록 조회 요청")
        product_names = await calculation_service.get_product_names()
        logger.info(f"✅ 제품명 목록 조회 성공: {len(product_names)}개")
        return product_names
    except Exception as e:
        logger.error(f"❌ 제품명 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품명 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/product/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """특정 제품 조회"""
    try:
        logger.info(f"📋 제품 조회 요청: ID {product_id}")
        product = await calculation_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 조회 성공: ID {product_id}")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/product", response_model=ProductResponse)
async def create_product(request: ProductCreateRequest):
    """제품 생성"""
    try:
        logger.info(f"📦 제품 생성 요청: {request.product_name}")
        result = await calculation_service.create_product(request)
        logger.info(f"✅ 제품 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 제품 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/product/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, request: ProductUpdateRequest):
    """제품 수정"""
    try:
        logger.info(f"📝 제품 수정 요청: ID {product_id}")
        result = await calculation_service.update_product(product_id, request)
        if not result:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 수정 성공: ID {product_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/product/{product_id}")
async def delete_product(product_id: int):
    """제품 삭제"""
    try:
        logger.info(f"🗑️ 제품 삭제 요청: ID {product_id}")
        success = await calculation_service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="제품을 찾을 수 없습니다")
        
        logger.info(f"✅ 제품 삭제 성공: ID {product_id}")
        return {"message": "제품이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🔄 Process 관련 엔드포인트
# ============================================================================

@router.get("/process", response_model=List[ProcessResponse])
async def get_processes():
    """프로세스 목록 조회"""
    try:
        logger.info("📋 프로세스 목록 조회 요청")
        processes = await calculation_service.get_processes()
        logger.info(f"✅ 프로세스 목록 조회 성공: {len(processes)}개")
        return processes
    except Exception as e:
        logger.error(f"❌ 프로세스 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/process/{process_id}", response_model=ProcessResponse)
async def get_process(process_id: int):
    """특정 프로세스 조회"""
    try:
        logger.info(f"📋 프로세스 조회 요청: ID {process_id}")
        process = await calculation_service.get_process(process_id)
        if not process:
            raise HTTPException(status_code=404, detail="프로세스를 찾을 수 없습니다")
        logger.info(f"✅ 프로세스 조회 성공: ID {process_id}")
        return process
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/process", response_model=ProcessResponse)
async def create_process(request: ProcessCreateRequest):
    """프로세스 생성"""
    try:
        logger.info(f"🔄 프로세스 생성 요청: {request.process_name}")
        result = await calculation_service.create_process(request)
        logger.info(f"✅ 프로세스 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 프로세스 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/process/{process_id}", response_model=ProcessResponse)
async def update_process(process_id: int, request: ProcessUpdateRequest):
    """프로세스 수정"""
    try:
        logger.info(f"📝 프로세스 수정 요청: ID {process_id}")
        result = await calculation_service.update_process(process_id, request)
        if not result:
            raise HTTPException(status_code=404, detail="프로세스를 찾을 수 없습니다")
        logger.info(f"✅ 프로세스 수정 성공: ID {process_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/process/{process_id}")
async def delete_process(process_id: int):
    """프로세스 삭제"""
    try:
        logger.info(f"🗑️ 프로세스 삭제 요청: ID {process_id}")
        success = await calculation_service.delete_process(process_id)
        if not success:
            raise HTTPException(status_code=404, detail="프로세스를 찾을 수 없습니다")
        logger.info(f"✅ 프로세스 삭제 성공: ID {process_id}")
        return {"message": "프로세스가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📥 ProcessInput 관련 엔드포인트
# ============================================================================

@router.get("/process-input", response_model=List[ProcessInputResponse])
async def get_process_inputs():
    """프로세스 입력 목록 조회"""
    try:
        logger.info("📋 프로세스 입력 목록 조회 요청")
        process_inputs = await calculation_service.get_process_inputs()
        logger.info(f"✅ 프로세스 입력 목록 조회 성공: {len(process_inputs)}개")
        return process_inputs
    except Exception as e:
        logger.error(f"❌ 프로세스 입력 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 입력 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/process-input/process/{process_id}", response_model=List[ProcessInputResponse])
async def get_process_inputs_by_process(process_id: int):
    """특정 프로세스의 입력 목록 조회"""
    try:
        logger.info(f"📋 프로세스 입력 조회 요청: 프로세스 ID {process_id}")
        process_inputs = await calculation_service.get_process_inputs_by_process(process_id)
        logger.info(f"✅ 프로세스 입력 조회 성공: {len(process_inputs)}개")
        return process_inputs
    except Exception as e:
        logger.error(f"❌ 프로세스 입력 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 입력 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/process-input/{process_input_id}", response_model=ProcessInputResponse)
async def get_process_input(process_input_id: int):
    """특정 프로세스 입력 조회"""
    try:
        logger.info(f"📋 프로세스 입력 조회 요청: ID {process_input_id}")
        process_input = await calculation_service.get_process_input(process_input_id)
        if not process_input:
            raise HTTPException(status_code=404, detail="프로세스 입력을 찾을 수 없습니다")
        
        logger.info(f"✅ 프로세스 입력 조회 성공: ID {process_input_id}")
        return process_input
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 입력 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 입력 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/process-input", response_model=ProcessInputResponse)
async def create_process_input(request: ProcessInputCreateRequest):
    """프로세스 입력 생성"""
    try:
        logger.info(f"📥 프로세스 입력 생성 요청: {request.input_name}")
        result = await calculation_service.create_process_input(request)
        logger.info(f"✅ 프로세스 입력 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 프로세스 입력 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 입력 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/process-input/{process_input_id}", response_model=ProcessInputResponse)
async def update_process_input(process_input_id: int, request: ProcessInputUpdateRequest):
    """프로세스 입력 수정"""
    try:
        logger.info(f"📝 프로세스 입력 수정 요청: ID {process_input_id}")
        result = await calculation_service.update_process_input(process_input_id, request)
        if not result:
            raise HTTPException(status_code=404, detail="프로세스 입력을 찾을 수 없습니다")
        
        logger.info(f"✅ 프로세스 입력 수정 성공: ID {process_input_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 입력 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 입력 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/process-input/{process_input_id}")
async def delete_process_input(process_input_id: int):
    """프로세스 입력 삭제"""
    try:
        logger.info(f"🗑️ 프로세스 입력 삭제 요청: ID {process_input_id}")
        success = await calculation_service.delete_process_input(process_input_id)
        if not success:
            raise HTTPException(status_code=404, detail="프로세스 입력을 찾을 수 없습니다")
        
        logger.info(f"✅ 프로세스 입력 삭제 성공: ID {process_input_id}")
        return {"message": "프로세스 입력이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 프로세스 입력 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 입력 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🧮 배출량 계산 관련 엔드포인트
# ============================================================================

@router.post("/emission/process/{process_id}", response_model=EmissionCalculationResponse)
async def calculate_process_emission(process_id: int):
    """프로세스별 배출량 계산"""
    try:
        logger.info(f"🧮 프로세스 배출량 계산 요청: 프로세스 ID {process_id}")
        result = await calculation_service.calculate_process_emission(process_id)
        logger.info(f"✅ 프로세스 배출량 계산 성공: 프로세스 ID {process_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 프로세스 배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"프로세스 배출량 계산 중 오류가 발생했습니다: {str(e)}")

@router.post("/emission/product/{product_id}", response_model=ProductEmissionResponse)
async def calculate_product_emission(product_id: int):
    """제품별 배출량 계산"""
    try:
        logger.info(f"🧮 제품 배출량 계산 요청: 제품 ID {product_id}")
        result = await calculation_service.calculate_product_emission(product_id)
        logger.info(f"✅ 제품 배출량 계산 성공: 제품 ID {product_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 제품 배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품 배출량 계산 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 Router Export
# ============================================================================

# calculation_router를 다른 모듈에서 import할 수 있도록 export
__all__ = ["router"]