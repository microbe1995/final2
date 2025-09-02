"""
Dummy 데이터 엔티티
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class DummyData(BaseModel):
    """Dummy 데이터 엔티티"""
    id: Optional[int] = None
    로트번호: str
    생산품명: str
    생산수량: Decimal
    투입일: Optional[date] = None
    종료일: Optional[date] = None
    공정: str
    투입물명: str
    수량: Decimal
    단위: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }
