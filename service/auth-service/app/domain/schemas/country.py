from pydantic import BaseModel
from typing import Optional, List

class CountryBase(BaseModel):
    """국가 기본 정보"""
    code: str
    country_name: str
    korean_name: str
    unlocode: Optional[str] = None

class CountryCreate(CountryBase):
    """국가 생성 스키마"""
    pass

class CountryUpdate(BaseModel):
    """국가 업데이트 스키마"""
    code: Optional[str] = None
    country_name: Optional[str] = None
    korean_name: Optional[str] = None
    unlocode: Optional[str] = None

class CountryResponse(CountryBase):
    """국가 응답 스키마"""
    id: int
    uuid: str
    
    class Config:
        from_attributes = True

class CountrySearchRequest(BaseModel):
    """국가 검색 요청 스키마"""
    query: str
    limit: Optional[int] = 10

class CountrySearchResponse(BaseModel):
    """국가 검색 응답 스키마"""
    countries: List[CountryResponse]
    total: int
    query: str
    page: int = 1
    limit: int = 10
