# ============================================================================
# 🔍 DataSearch Entity - CBAM 데이터 검색 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any
from decimal import Decimal

Base = declarative_base()

# ============================================================================
# 📊 HS코드 엔티티
# ============================================================================

class HSCode(Base):
    """HS코드 엔티티"""
    
    __tablename__ = "hs_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    hs_code = Column(BigInteger, index=True)
    cn_verification = Column(BigInteger, index=True)
    category_cn = Column(String(100))
    category_cn_eng = Column(String(100))
    item_cn = Column(String(100))
    item_cn_eng = Column(String(100))
    item_hs = Column(String(100))
    cn_code = Column(String(20))
    direct_factor = Column(Numeric(10, 6))
    indirect_factor = Column(Numeric(10, 6))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "hs_코드": self.hs_code,
            "cn_검증용": self.cn_verification,
            "품목군__(cn기준)": self.category_cn,
            "품목군_(cn기준)": self.category_cn_eng,
            "품목_(cn기준)": self.item_cn,
            "품목_(cn기준_영문)": self.item_cn_eng,
            "품목_(hs기준)": self.item_hs,
            "cn_코드": self.cn_code,
            "직접": float(self.direct_factor) if self.direct_factor else None,
            "간접": float(self.indirect_factor) if self.indirect_factor else None
        }

# ============================================================================
# 🌍 국가 코드 엔티티
# ============================================================================

class CountryCode(Base):
    """국가 코드 엔티티"""
    
    __tablename__ = "country_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(100), nullable=False)
    korean_name = Column(String(100), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "country_name": self.country_name,
            "korean_name": self.korean_name,
            "code": self.code
        }

# ============================================================================
# 🔥 연료 검색용 엔티티
# ============================================================================

class FuelSearchData:
    """연료 검색 데이터 클래스"""
    
    def __init__(self, id: int, name: str, name_eng: str, emission_factor: float, net_calorific_value: float):
        self.id = id
        self.name = name
        self.name_eng = name_eng
        self.emission_factor = emission_factor
        self.net_calorific_value = net_calorific_value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_eng": self.name_eng,
            "emission_factor": self.emission_factor,
            "net_calorific_value": self.net_calorific_value
        }

# ============================================================================
# 🧱 원료 검색용 엔티티
# ============================================================================

class MaterialSearchData:
    """원료 검색 데이터 클래스"""
    
    def __init__(self, id: int, name: str, name_eng: str, direct_factor: float, cn_code: str, cn_code1: str, cn_code2: str):
        self.id = id
        self.name = name
        self.name_eng = name_eng
        self.direct_factor = direct_factor
        self.cn_code = cn_code
        self.cn_code1 = cn_code1
        self.cn_code2 = cn_code2
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_eng": self.name_eng,
            "direct_factor": self.direct_factor,
            "cn_code": self.cn_code,
            "cn_code1": self.cn_code1,
            "cn_code2": self.cn_code2
        }

# ============================================================================
# 🔗 전구물질 검색용 엔티티
# ============================================================================

class PrecursorSearchData:
    """전구물질 검색 데이터 클래스"""
    
    def __init__(self, id: int, name: str, direct_factor: float, indirect_factor: float, cn_code: str):
        self.id = id
        self.name = name
        self.direct_factor = direct_factor
        self.indirect_factor = indirect_factor
        self.cn_code = cn_code
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "direct_factor": self.direct_factor,
            "indirect_factor": self.indirect_factor,
            "cn_code": self.cn_code
        }