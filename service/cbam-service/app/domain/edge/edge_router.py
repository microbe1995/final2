# ============================================================================
# 🔗 Edge Router - CBAM 배출량 전파 API
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.common.database_base import get_db
from app.domain.edge.edge_service import EdgeService

router = APIRouter(prefix="/edge", tags=["edge"])

@router.post("/propagate-emissions/{chain_id}")
async def propagate_emissions(
    chain_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    공정 체인에 대해 배출량 누적 전달을 실행합니다.
    
    규칙 1번: 공정→공정 배출량 누적 전달 (edge_kind = "continue")
    """
    try:
        edge_service = EdgeService(db)
        
        # 배출량 누적 전달 실행
        result = await edge_service.propagate_emissions_chain(chain_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', '배출량 전파 실패')
            )
        
        return {
            "success": True,
            "message": f"공정 체인 {chain_id} 배출량 누적 전달 완료",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류: {str(e)}"
        )

@router.get("/chain-emission-summary/{chain_id}")
async def get_chain_emission_summary(
    chain_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    공정 체인의 배출량 요약 정보를 조회합니다.
    """
    try:
        edge_service = EdgeService(db)
        
        # 배출량 요약 조회
        result = await edge_service.get_process_chain_emission_summary(chain_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', '공정 체인 정보를 찾을 수 없습니다')
            )
        
        return {
            "success": True,
            "message": f"공정 체인 {chain_id} 배출량 요약",
            "data": result.get('summary')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류: {str(e)}"
        )

@router.post("/propagate-emissions-continue")
async def propagate_emissions_continue(
    source_process_id: int,
    target_process_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    두 공정 간의 배출량 누적 전달을 실행합니다.
    
    규칙 1번: 공정→공정 배출량 누적 전달 (edge_kind = "continue")
    """
    try:
        edge_service = EdgeService(db)
        
        # 배출량 누적 전달 실행
        success = await edge_service.propagate_emissions_continue(source_process_id, target_process_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 실패"
            )
        
        return {
            "success": True,
            "message": f"공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 완료",
            "data": {
                "source_process_id": source_process_id,
                "target_process_id": target_process_id,
                "propagation_time": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류: {str(e)}"
        )

@router.get("/process-emission/{process_id}")
async def get_process_emission(
    process_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    특정 공정의 배출량 정보를 조회합니다.
    """
    try:
        edge_service = EdgeService(db)
        
        # 공정 배출량 데이터 조회
        emission_data = await edge_service.get_process_emission_data(process_id)
        
        if not emission_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"공정 {process_id}의 배출량 데이터를 찾을 수 없습니다"
            )
        
        return {
            "success": True,
            "message": f"공정 {process_id} 배출량 정보",
            "data": emission_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류: {str(e)}"
        )

@router.get("/continue-edges/{process_id}")
async def get_continue_edges(
    process_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    특정 공정에서 나가는 continue 엣지들을 조회합니다.
    """
    try:
        edge_service = EdgeService(db)
        
        # continue 엣지 조회
        edges = await edge_service.get_continue_edges(process_id)
        
        return {
            "success": True,
            "message": f"공정 {process_id}의 continue 엣지들",
            "data": {
                "process_id": process_id,
                "edges": edges,
                "total_edges": len(edges)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류: {str(e)}"
        )
