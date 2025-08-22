# ============================================================================
# 🔍 DataSearch Schema - CBAM 데이터 검색 스키마
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============================================================================
# 📊 HS코드 검색 스키마
# ============================================================================

class HSCodeSearchResponse(BaseModel):
    """HS코드 검색 응답"""
    results: List[Dict[str, Any]] = Field(..., description="검색 결과")
    total: int = Field(..., description="전체 결과 수")
    page: int = Field(..., description="현재 페이지")
    page_size: int = Field(..., description="페이지 크기")

# ============================================================================
# 🔥 연료 검색 스키마
# ============================================================================

class FuelData(BaseModel):
    """연료 데이터"""
    id: int = Field(..., description="연료 ID")
    name: str = Field(..., description="연료명")
    name_eng: str = Field(..., description="연료영문명")
    fuel_emfactor: float = Field(..., description="배출계수")
    net_calory: float = Field(..., description="순발열량")

class FuelSearchResponse(BaseModel):
    """연료 검색 응답"""
    fuels: List[FuelData] = Field(..., description="연료 목록")

# ============================================================================
# 🧱 원료 검색 스키마
# ============================================================================

class MaterialData(BaseModel):
    """원료 데이터"""
    id: int
    name: str = Field(..., description="품목명")
    name_eng: Optional[str] = Field(default="", description="품목명(영문)")
    direct_factor: Optional[float] = Field(default=None, description="직접배출계수")
    cn_code: Optional[str] = Field(default="", description="CN코드")
    cn_code1: Optional[str] = Field(default="", description="CN코드1")
    cn_code2: Optional[str] = Field(default="", description="CN코드2")

class MaterialSearchResponse(BaseModel):
    """원료 검색 응답"""
    id: int = Field(..., description="원료 ID")
    name: str = Field(..., description="원료명")
    name_eng: str = Field(..., description="원료영문명")
    em_factor: Optional[float] = Field(default=None, description="배출계수")
    carbon_factor: Optional[float] = Field(default=0.0, description="탄소함량 (%)")
    cn_code: str = Field(..., description="CN코드")
    cn_code1: str = Field(..., description="CN코드1")
    cn_code2: str = Field(..., description="CN코드2")

# ============================================================================
# 🔗 전구물질 검색 스키마
# ============================================================================

class PrecursorData(BaseModel):
    """전구물질 데이터"""
    id: int = Field(..., description="전구물질 ID")
    precursor: str = Field(..., description="전구물질명")
    precursor_eng: str = Field(..., description="전구물질영문명")
    direct: float = Field(..., description="직접 배출계수")
    indirect: float = Field(..., description="간접 배출계수")
    cn1: str = Field(..., description="CN코드1")

class PrecursorSearchResponse(BaseModel):
    """전구물질 검색 응답"""
    precursors: List[PrecursorData] = Field(..., description="전구물질 목록")

# ============================================================================
# 🌍 국가 검색 스키마
# ============================================================================

class CountrySearchRequest(BaseModel):
    """국가 검색 요청"""
    name_kr: str = Field(..., description="국가명(한글)")
    
    @validator('name_kr')
    def validate_name_kr(cls, v):
        if not v or not v.strip():
            raise ValueError("국가명은 필수입니다")
        return v.strip()

class CountryData(BaseModel):
    """국가 데이터"""
    name_en: str = Field(..., description="국가명(영문)")
    name_kr: str = Field(..., description="국가명(한글)")
    unlocode: str = Field(..., description="UNLOCODE")

class CountrySearchResponse(BaseModel):
    """국가 검색 응답"""
    result: List[CountryData] = Field(..., description="국가 검색 결과")

# ============================================================================
# 🔍 통합 검색 스키마
# ============================================================================

class SearchRequest(BaseModel):
    """검색 요청 기본 클래스"""
    search: Optional[str] = Field(default="", description="검색어")
    limit: Optional[int] = Field(default=50, ge=1, le=100, description="결과 제한")

class HSCodeSearchRequest(SearchRequest):
    """HS코드 검색 요청"""
    hs: str = Field(..., description="HS코드")
    page: Optional[int] = Field(default=1, ge=1, description="페이지 번호")
    page_size: Optional[int] = Field(default=5, ge=1, le=20, description="페이지 크기")

# ============================================================================
# 🏥 헬스체크 스키마
# ============================================================================

class HealthCheckResponse(BaseModel):
    """헬스체크 응답"""
    status: str = Field(..., description="서비스 상태")
    service: str = Field(..., description="서비스 이름")
    version: str = Field(..., description="버전")
    database: str = Field(..., description="데이터베이스 상태")
    timestamp: str = Field(..., description="체크 시간")

# ============================================================================
# 📊 통계 스키마
# ============================================================================

class SearchStatsResponse(BaseModel):
    """검색 통계 응답"""
    total_searches: int = Field(..., description="전체 검색 수")
    hscode_searches: int = Field(..., description="HS코드 검색 수")
    country_searches: int = Field(..., description="국가 검색 수")
    fuel_searches: int = Field(..., description="연료 검색 수")
    material_searches: int = Field(..., description="원료 검색 수")
    precursor_searches: int = Field(..., description="전구물질 검색 수")
    searches_by_type: Dict[str, int] = Field(..., description="타입별 검색 수")
    last_updated: str = Field(..., description="마지막 업데이트 시간")