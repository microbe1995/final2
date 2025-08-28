# ============================================================================
# 📋 Mapping Schema - HS-CN 매핑 데이터 모델
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ============================================================================
# 🏭 HS-CN 매핑 관련 스키마
# ============================================================================

class HSCNMappingResponse(BaseModel):
    """HS-CN 매핑 응답"""
    cncode_total: str = Field(..., description="CN 코드 (8자리)")
    goods_name: Optional[str] = Field(None, description="상세 품명(한글)")
    goods_engname: Optional[str] = Field(None, description="상세 품명(영문)")
    aggregoods_name: Optional[str] = Field(None, description="제품 대분류(한글)")
    aggregoods_engname: Optional[str] = Field(None, description="제품 대분류(영문)")

class HSCNMappingCreateRequest(BaseModel):
    """HS-CN 매핑 생성 요청"""
    hscode: str = Field(..., description="HS 코드 (앞 6자리)", min_length=6, max_length=6)
    aggregoods_name: Optional[str] = Field(None, description="제품 대분류(한글)")
    aggregoods_engname: Optional[str] = Field(None, description="제품 대분류(영문)")
    cncode_total: str = Field(..., description="CN 코드 (8자리)", min_length=8, max_length=8)
    goods_name: Optional[str] = Field(None, description="상세 품명(한글)")
    goods_engname: Optional[str] = Field(None, description="상세 품명(영문)")

class HSCNMappingUpdateRequest(BaseModel):
    """HS-CN 매핑 수정 요청"""
    hscode: Optional[str] = Field(None, description="HS 코드 (앞 6자리)", min_length=6, max_length=6)
    aggregoods_name: Optional[str] = Field(None, description="제품 대분류(한글)")
    aggregoods_engname: Optional[str] = Field(None, description="제품 대분류(영문)")
    cncode_total: Optional[str] = Field(None, description="CN 코드 (8자리)", min_length=8, max_length=8)
    goods_name: Optional[str] = Field(None, description="상세 품명(한글)")
    goods_engname: Optional[str] = Field(None, description="상세 품명(영문)")

class HSCNMappingFullResponse(BaseModel):
    """HS-CN 매핑 전체 응답 (ID 포함)"""
    id: int = Field(..., description="매핑 ID")
    hscode: str = Field(..., description="HS 코드 (앞 6자리)")
    aggregoods_name: Optional[str] = Field(None, description="제품 대분류(한글)")
    aggregoods_engname: Optional[str] = Field(None, description="제품 대분류(영문)")
    cncode_total: str = Field(..., description="CN 코드 (8자리)")
    goods_name: Optional[str] = Field(None, description="상세 품명(한글)")
    goods_engname: Optional[str] = Field(None, description="상세 품명(영문)")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")

# ============================================================================
# 🔍 조회 관련 스키마
# ============================================================================

class HSCodeLookupRequest(BaseModel):
    """HS 코드 조회 요청"""
    hs_code_10: str = Field(..., description="HS 코드 (10자리)", min_length=10, max_length=10)

class HSCodeLookupResponse(BaseModel):
    """HS 코드 조회 응답"""
    success: bool = Field(..., description="조회 성공 여부")
    data: List[HSCNMappingResponse] = Field(..., description="매핑 결과 목록")
    count: int = Field(..., description="조회된 결과 수")
    message: Optional[str] = Field(None, description="응답 메시지")

# ============================================================================
# 📊 통계 관련 스키마
# ============================================================================

class MappingStatsResponse(BaseModel):
    """매핑 통계 응답"""
    total_mappings: int = Field(..., description="전체 매핑 수")
    unique_hscodes: int = Field(..., description="고유 HS 코드 수")
    unique_cncodes: int = Field(..., description="고유 CN 코드 수")
    last_updated: Optional[datetime] = Field(None, description="마지막 업데이트 시간")

# ============================================================================
# 📦 Batch 처리 관련 스키마
# ============================================================================

class HSCNMappingBatchCreateRequest(BaseModel):
    """HS-CN 매핑 일괄 생성 요청"""
    mappings: List[HSCNMappingCreateRequest] = Field(..., description="매핑 목록")

class HSCNMappingBatchResponse(BaseModel):
    """HS-CN 매핑 일괄 처리 응답"""
    success: bool = Field(..., description="처리 성공 여부")
    created_count: int = Field(..., description="생성된 매핑 수")
    failed_count: int = Field(..., description="실패한 매핑 수")
    errors: List[str] = Field(default=[], description="오류 메시지 목록")
