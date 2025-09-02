# ============================================================================
# 📋 Dummy Schema - Dummy 데이터 API 스키마
# ============================================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class DummyDataCreateRequest(BaseModel):
    """Dummy 데이터 생성 요청"""
    로트번호: str = Field(..., description="로트 번호")
    생산품명: str = Field(..., description="생산품명")
    생산수량: int = Field(..., description="생산수량")
    투입일: Optional[date] = Field(None, description="투입일")
    종료일: Optional[date] = Field(None, description="종료일")
    공정: str = Field(..., description="공정")
    투입물명: str = Field(..., description="투입물명")
    수량: int = Field(..., description="수량")
    단위: str = Field(..., description="단위")
    
    class Config:
        json_schema_extra = {
            "example": {
                "로트번호": "LOT001",
                "생산품명": "제품A",
                "생산수량": 100,
                "투입일": "2024-01-01",
                "종료일": "2024-01-31",
                "공정": "조립공정",
                "투입물명": "부품B",
                "수량": 50,
                "단위": "개"
            }
        }

class DummyDataResponse(BaseModel):
    """Dummy 데이터 응답"""
    id: int = Field(..., description="데이터 ID")
    로트번호: str = Field(..., description="로트 번호")
    생산품명: str = Field(..., description="생산품명")
    생산수량: int = Field(..., description="생산수량")
    투입일: Optional[date] = Field(None, description="투입일")
    종료일: Optional[date] = Field(None, description="종료일")
    공정: str = Field(..., description="공정")
    투입물명: str = Field(..., description="투입물명")
    수량: int = Field(..., description="수량")
    단위: str = Field(..., description="단위")
    created_at: Optional[datetime] = Field(None, description="생성일")
    updated_at: Optional[datetime] = Field(None, description="수정일")
    
    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }

class DummyDataUpdateRequest(BaseModel):
    """Dummy 데이터 수정 요청"""
    로트번호: Optional[str] = Field(None, description="로트 번호")
    생산품명: Optional[str] = Field(None, description="생산품명")
    생산수량: Optional[int] = Field(None, description="생산수량")
    투입일: Optional[date] = Field(None, description="투입일")
    종료일: Optional[date] = Field(None, description="종료일")
    공정: Optional[str] = Field(None, description="공정")
    투입물명: Optional[str] = Field(None, description="투입물명")
    수량: Optional[int] = Field(None, description="수량")
    단위: Optional[str] = Field(None, description="단위")

class DummyDataListResponse(BaseModel):
    """Dummy 데이터 목록 응답"""
    items: list[DummyDataResponse] = Field(..., description="데이터 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
