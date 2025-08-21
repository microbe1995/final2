from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..common.db import get_db
from ..domain.entities.country import Country
from ..domain.schemas.sitemap import SitemapItem, SitemapResponse

router = APIRouter(prefix="/api", tags=["sitemap"])

@router.get("/sitemap", response_model=SitemapResponse)
async def get_sitemap(
    q: Optional[str] = Query(None, description="검색어 (korean_name 기준)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db)
):
    """
    국가 검색 (korean_name 기준)
    
    Args:
        q: 검색어 (korean_name에서 부분 일치)
        page: 페이지 번호 (1부터 시작)
        limit: 페이지당 항목 수 (1-100)
    
    Returns:
        SitemapResponse: 검색 결과와 페이징 정보
    """
    try:
        # 검색 조건 구성
        query = db.query(Country)
        
        if q and q.strip():
            search_term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    Country.korean_name.ilike(search_term),
                    Country.country_name.ilike(search_term),
                    Country.code.ilike(search_term)
                )
            )
        
        # 전체 개수 계산
        total = query.count()
        
        # 페이징 적용
        offset = (page - 1) * limit
        countries = query.offset(offset).limit(limit).all()
        
        # 응답 데이터 구성
        items = [
            SitemapItem(
                id=str(country.id),
                title=country.korean_name,
                url=f"/country/{country.code}",
                updated_at=country.updated_at if hasattr(country, 'updated_at') else None
            )
            for country in countries
        ]
        
        return SitemapResponse(
            items=items,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        # 로깅은 미들웨어에서 처리
        # 검색 실패 시에도 빈 결과로 응답 (404 금지)
        return SitemapResponse(
            items=[],
            total=0,
            page=page,
            limit=limit
        )
