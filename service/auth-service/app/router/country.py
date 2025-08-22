from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.common.db import get_db
from app.domain.services.country_service import CountryService
from app.domain.schemas.country import (
    CountryResponse, 
    CountrySearchRequest, 
    CountrySearchResponse,
    CountryCreate,
    CountryUpdate
)
from app.common.logger import auth_logger

router = APIRouter(tags=["countries"])

@router.get("/test")
async def test_country_router():
    """Countries 라우터 테스트 엔드포인트"""
    return {"message": "Countries router is working", "status": "ok"}

@router.get("/search", response_model=CountrySearchResponse)
async def search_countries(
    query: str = Query(..., description="검색어 (국가 코드, 영문명, 한국어명, UNLOCODE)"),
    limit: int = Query(10, description="검색 결과 제한 수", ge=1, le=100),
    page: int = Query(1, description="페이지 번호", ge=1),
    db: Session = Depends(get_db)
):
    """국가 검색 API"""
    try:
        country_service = CountryService(db)
        search_request = CountrySearchRequest(query=query, limit=limit)
        countries = country_service.search_countries(search_request)
        
        # 검색 결과가 없어도 200 OK 반환 (404 금지)
        auth_logger.info(f"국가 검색 완료: '{query}' -> {len(countries)}개 결과")
        
        return CountrySearchResponse(
            countries=countries,
            total=len(countries),
            query=query,
            page=page,
            limit=limit
        )
    except Exception as e:
        auth_logger.error(f"국가 검색 API 오류: {str(e)}")
        # 오류 발생 시에도 빈 결과로 응답 (사용자 경험 보존)
        return CountrySearchResponse(
            countries=[],
            total=0,
            query=query,
            page=page,
            limit=limit
        )

@router.get("/", response_model=List[CountryResponse])
async def get_all_countries(
    limit: int = Query(100, description="조회할 국가 수", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """모든 국가 조회 API"""
    try:
        country_service = CountryService(db)
        countries = country_service.get_all_countries(limit=limit)
        return countries
    except Exception as e:
        auth_logger.error(f"전체 국가 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="국가 조회 중 오류가 발생했습니다.")

@router.get("/code/{code}", response_model=CountryResponse)
async def get_country_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    """코드로 국가 조회 API"""
    try:
        country_service = CountryService(db)
        country = country_service.get_country_by_code(code)
        if not country:
            raise HTTPException(status_code=404, detail=f"국가 코드 '{code}'를 찾을 수 없습니다.")
        return country
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"코드로 국가 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="국가 조회 중 오류가 발생했습니다.")

@router.get("/unlocode/{unlocode}", response_model=CountryResponse)
async def get_country_by_unlocode(
    unlocode: str,
    db: Session = Depends(get_db)
):
    """UNLOCODE로 국가 조회 API"""
    try:
        country_service = CountryService(db)
        country = country_service.get_country_by_unlocode(unlocode)
        if not country:
            raise HTTPException(status_code=404, detail=f"UNLOCODE '{unlocode}'를 찾을 수 없습니다.")
        return country
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"UNLOCODE로 국가 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="국가 조회 중 오류가 발생했습니다.")

@router.post("/", response_model=CountryResponse)
async def create_country(
    country_data: CountryCreate,
    db: Session = Depends(get_db)
):
    """새 국가 생성 API"""
    try:
        country_service = CountryService(db)
        country = country_service.create_country(country_data)
        if not country:
            raise HTTPException(status_code=400, detail="국가 생성에 실패했습니다.")
        return country
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"국가 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="국가 생성 중 오류가 발생했습니다.")

@router.put("/{country_id}", response_model=CountryResponse)
async def update_country(
    country_id: int,
    country_data: CountryUpdate,
    db: Session = Depends(get_db)
):
    """국가 정보 업데이트 API"""
    try:
        country_service = CountryService(db)
        country = country_service.update_country(country_id, country_data)
        if not country:
            raise HTTPException(status_code=404, detail=f"국가 ID '{country_id}'를 찾을 수 없습니다.")
        return country
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"국가 업데이트 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="국가 업데이트 중 오류가 발생했습니다.")

@router.delete("/{country_id}")
async def delete_country(
    country_id: int,
    db: Session = Depends(get_db)
):
    """국가 삭제 API"""
    try:
        country_service = CountryService(db)
        success = country_service.delete_country(country_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"국가 ID '{country_id}'를 찾을 수 없습니다.")
        return {"message": f"국가 ID '{country_id}'가 성공적으로 삭제되었습니다."}
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"국가 삭제 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="국가 삭제 중 오류가 발생했습니다.")
