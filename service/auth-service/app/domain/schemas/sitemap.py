from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SitemapItem(BaseModel):
    """사이트맵 항목 스키마"""
    id: str
    title: str
    url: str
    updated_at: Optional[datetime] = None

class SitemapResponse(BaseModel):
    """사이트맵 응답 스키마"""
    items: List[SitemapItem]
    total: int
    page: int
    limit: int
