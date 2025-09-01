# ============================================================================
# 🏭 Edge Controller - 엣지 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List
import time

from app.domain.edge.edge_service import EdgeService
from app.domain.edge.edge_schema import (
    EdgeCreateRequest, EdgeResponse, EdgeUpdateRequest
)
from app.common.database_base import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Gateway를 통해 접근하므로 prefix 제거 (경로 중복 방지)
router = APIRouter(tags=["Edge"])

# 서비스 인스턴스 생성 (기존 CRUD용)
edge_service = EdgeService()

# ============================================================================
# 🔗 Edge 관련 엔드포인트
# ============================================================================

@router.post("/", response_model=EdgeResponse, status_code=201)
async def create_edge(edge_data: EdgeCreateRequest):
    """엣지 생성"""
    try:
        logger.info(f"🔗 엣지 생성 요청: {edge_data.source_id} -> {edge_data.target_id} ({edge_data.edge_kind})")
        result = await edge_service.create_edge(edge_data)
        logger.info(f"✅ 엣지 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 엣지 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/", response_model=List[EdgeResponse])
async def get_edges():
    """모든 엣지 목록 조회"""
    try:
        logger.info("📋 엣지 목록 조회 요청")
        edges = await edge_service.get_edges()
        logger.info(f"✅ 엣지 목록 조회 성공: {len(edges)}개")
        return edges
    except Exception as e:
        logger.error(f"❌ 엣지 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/{edge_id}", response_model=EdgeResponse)
async def get_edge(edge_id: int):
    """특정 엣지 조회"""
    try:
        logger.info(f"📋 엣지 조회 요청: ID {edge_id}")
        edge = await edge_service.get_edge(edge_id)
        if not edge:
            raise HTTPException(status_code=404, detail="엣지를 찾을 수 없습니다")
        
        logger.info(f"✅ 엣지 조회 성공: ID {edge_id}")
        return edge
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 엣지 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 조회 중 오류가 발생했습니다: {str(e)}")

@router.put("/{edge_id}", response_model=EdgeResponse)
async def update_edge(edge_id: int, edge_data: EdgeUpdateRequest):
    """엣지 수정"""
    try:
        logger.info(f"📝 엣지 수정 요청: ID {edge_id}")
        result = await edge_service.update_edge(edge_id, edge_data)
        if not result:
            raise HTTPException(status_code=404, detail="엣지를 찾을 수 없습니다")
        
        logger.info(f"✅ 엣지 수정 성공: ID {edge_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 엣지 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/{edge_id}")
async def delete_edge(edge_id: int):
    """엣지 삭제"""
    try:
        logger.info(f"🗑️ 엣지 삭제 요청: ID {edge_id}")
        success = await edge_service.delete_edge(edge_id)
        if not success:
            raise HTTPException(status_code=404, detail="엣지를 찾을 수 없습니다")
        
        logger.info(f"✅ 엣지 삭제 성공: ID {edge_id}")
        return {"message": "엣지가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 엣지 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🔗 CBAM 배출량 전파 엔드포인트
# ============================================================================

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
        
        logger.info(f"✅ 공정 체인 {chain_id} 배출량 누적 전달 완료")
        return {
            "success": True,
            "message": f"공정 체인 {chain_id} 배출량 누적 전달 완료",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 공정 체인 {chain_id} 배출량 전파 실패: {str(e)}")
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
        
        logger.info(f"✅ 공정 체인 {chain_id} 배출량 요약 조회 완료")
        return {
            "success": True,
            "message": f"공정 체인 {chain_id} 배출량 요약",
            "data": result.get('summary')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 공정 체인 {chain_id} 배출량 요약 조회 실패: {str(e)}")
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
        
        logger.info(f"✅ 공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 완료")
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
        logger.error(f"❌ 공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 실패: {str(e)}")
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
        
        logger.info(f"✅ 공정 {process_id} 배출량 정보 조회 완료")
        return {
            "success": True,
            "message": f"공정 {process_id} 배출량 정보",
            "data": emission_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 공정 {process_id} 배출량 정보 조회 실패: {str(e)}")
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
        
        logger.info(f"✅ 공정 {process_id}의 continue 엣지 조회 완료: {len(edges)}개")
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
        logger.error(f"❌ 공정 {process_id}의 continue 엣지 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류: {str(e)}"
        )

# ============================================================================
# 🔍 검색 및 필터링 엔드포인트
# ============================================================================

@router.get("/type/{edge_kind}", response_model=List[EdgeResponse])
async def get_edges_by_type(edge_kind: str):
    """타입별 엣지 조회"""
    try:
        logger.info(f"🔍 타입별 엣지 조회 요청: {edge_kind}")
        edges = await edge_service.get_edges_by_type(edge_kind)
        logger.info(f"✅ 타입별 엣지 조회 성공: {edge_kind} → {len(edges)}개")
        return edges
    except Exception as e:
        logger.error(f"❌ 타입별 엣지 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"타입별 엣지 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/node/{node_id}", response_model=List[EdgeResponse])
async def get_edges_by_node(node_id: int):
    """노드와 연결된 엣지 조회"""
    try:
        logger.info(f"🔍 노드별 엣지 조회 요청: 노드 ID {node_id}")
        edges = await edge_service.get_edges_by_node(node_id)
        logger.info(f"✅ 노드별 엣지 조회 성공: 노드 ID {node_id} → {len(edges)}개")
        return edges
    except Exception as e:
        logger.error(f"❌ 노드별 엣지 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"노드별 엣지 조회 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📊 통계 및 요약 엔드포인트
# ============================================================================

@router.get("/stats/summary")
async def get_edge_summary():
    """엣지 통계 요약"""
    try:
        logger.info("📊 엣지 통계 요약 요청")
        all_edges = await edge_service.get_edges()
        
        # 타입별 통계
        type_stats = {}
        for edge in all_edges:
            edge_type = edge.edge_kind
            if edge_type not in type_stats:
                type_stats[edge_type] = 0
            type_stats[edge_type] += 1
        
        summary = {
            "total_edges": len(all_edges),
            "edge_types": type_stats,
            "unique_nodes": len(set([edge.source_id for edge in all_edges] + [edge.target_id for edge in all_edges]))
        }
        
        logger.info(f"✅ 엣지 통계 요약 생성 성공: {summary}")
        return summary
    except Exception as e:
        logger.error(f"❌ 엣지 통계 요약 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 통계 요약 생성 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 일괄 처리 엔드포인트
# ============================================================================

@router.post("/bulk")
async def create_edges_bulk(edges_data: List[EdgeCreateRequest]):
    """여러 엣지 일괄 생성"""
    try:
        logger.info(f"📦 엣지 일괄 생성 요청: {len(edges_data)}개")
        results = []
        
        for edge_data in edges_data:
            try:
                result = await edge_service.create_edge(edge_data)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ 개별 엣지 생성 실패: {str(e)}")
                # 개별 실패는 전체 실패로 처리하지 않음
        
        logger.info(f"✅ 엣지 일괄 생성 완료: {len(results)}/{len(edges_data)}개 성공")
        return {
            "message": f"일괄 생성 완료: {len(results)}/{len(edges_data)}개 성공",
            "success_count": len(results),
            "total_count": len(edges_data),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ 엣지 일괄 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 일괄 생성 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 Router Export
# ============================================================================

# edge_router를 다른 모듈에서 import할 수 있도록 export
edge_router = router
__all__ = ["router", "edge_router"]
