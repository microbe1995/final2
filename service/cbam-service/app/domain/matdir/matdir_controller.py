from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.common.database_base import get_database_session
from .matdir_service import MatDirService
from .matdir_schema import (
    MatDirCreateRequest, 
    MatDirUpdateRequest, 
    MatDirResponse,
    MatDirCalculationRequest,
    MatDirCalculationResponse
)

router = APIRouter(prefix="", tags=["원료직접배출량"])

def get_matdir_service(db: Session = Depends(get_database_session)) -> MatDirService:
    return MatDirService(db)

@router.post("/matdir", response_model=MatDirResponse, status_code=status.HTTP_201_CREATED)
async def create_matdir(
    matdir_data: MatDirCreateRequest,
    service: MatDirService = Depends(get_matdir_service)
):
    """원료직접배출량 데이터 생성"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"📝 원료직접배출량 생성 요청: {matdir_data.dict()}")
        
        result = service.create_matdir(matdir_data)
        logger.info(f"✅ 원료직접배출량 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"❌ 원료직접배출량 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"원료직접배출량 생성 실패: {str(e)}"
        )

@router.get("/matdir", response_model=List[MatDirResponse])
async def get_matdirs(
    skip: int = 0,
    limit: int = 100,
    service: MatDirService = Depends(get_matdir_service)
):
    """모든 원료직접배출량 데이터 조회"""
    try:
        return service.get_matdirs(skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"원료직접배출량 조회 실패: {str(e)}"
        )

@router.get("/matdir/process/{process_id}", response_model=List[MatDirResponse])
async def get_matdirs_by_process(
    process_id: int,
    service: MatDirService = Depends(get_matdir_service)
):
    """특정 공정의 원료직접배출량 데이터 조회"""
    try:
        return service.get_matdirs_by_process(process_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공정별 원료직접배출량 조회 실패: {str(e)}"
        )

@router.get("/matdir/{matdir_id}", response_model=MatDirResponse)
async def get_matdir(
    matdir_id: int,
    service: MatDirService = Depends(get_matdir_service)
):
    """특정 원료직접배출량 데이터 조회"""
    try:
        result = service.get_matdir(matdir_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="원료직접배출량 데이터를 찾을 수 없습니다."
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"원료직접배출량 조회 실패: {str(e)}"
        )

@router.put("/matdir/{matdir_id}", response_model=MatDirResponse)
async def update_matdir(
    matdir_id: int,
    matdir_data: MatDirUpdateRequest,
    service: MatDirService = Depends(get_matdir_service)
):
    """원료직접배출량 데이터 수정"""
    try:
        result = service.update_matdir(matdir_id, matdir_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="원료직접배출량 데이터를 찾을 수 없습니다."
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"원료직접배출량 수정 실패: {str(e)}"
        )

@router.delete("/matdir/{matdir_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_matdir(
    matdir_id: int,
    service: MatDirService = Depends(get_matdir_service)
):
    """원료직접배출량 데이터 삭제"""
    try:
        success = service.delete_matdir(matdir_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="원료직접배출량 데이터를 찾을 수 없습니다."
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"원료직접배출량 삭제 실패: {str(e)}"
        )

@router.post("/matdir/calculate", response_model=MatDirCalculationResponse)
async def calculate_matdir_emission(
    calculation_data: MatDirCalculationRequest,
    service: MatDirService = Depends(get_matdir_service)
):
    """원료직접배출량 계산"""
    try:
        return service.calculate_matdir_emission_with_formula(calculation_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"원료직접배출량 계산 실패: {str(e)}"
        )

@router.get("/matdir/process/{process_id}/total")
async def get_total_matdir_emission_by_process(
    process_id: int,
    service: MatDirService = Depends(get_matdir_service)
):
    """특정 공정의 총 원료직접배출량 조회"""
    try:
        total_emission = service.get_total_matdir_emission_by_process(process_id)
        return {
            "process_id": process_id,
            "total_matdir_emission": float(total_emission),
            "unit": "tCO2e"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"총 원료직접배출량 조회 실패: {str(e)}"
        )
