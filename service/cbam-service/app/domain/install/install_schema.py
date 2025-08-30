# ============================================================================
# 🏭 Install Schema - 사업장 API 스키마
# ============================================================================

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class InstallNameResponse(BaseModel):
    """사업장명 응답 (드롭다운용)"""
    id: int = Field(..., description="사업장 ID")
    install_name: str = Field(..., description="사업장명")

class InstallCreateRequest(BaseModel):
    """사업장 생성 요청"""
    install_name: str = Field(..., description="사업장명")
    reporting_year: int = Field(default=datetime.now().year, description="보고기간 (년도)")

class InstallResponse(BaseModel):
    """사업장 응답"""
    id: int = Field(..., description="사업장 ID")
    install_name: str = Field(..., description="사업장명")
    reporting_year: int = Field(..., description="보고기간 (년도)")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")

class InstallUpdateRequest(BaseModel):
    """사업장 수정 요청"""
    install_name: Optional[str] = Field(None, description="사업장명")
    reporting_year: Optional[int] = Field(None, description="보고기간 (년도)")

    class Config:
        from_attributes = True
