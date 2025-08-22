# ============================================================================
# 🔍 DataSearch Entity - CBAM 데이터 검색 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, BigInteger
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
    category_cn = Column(Text)
    category_cn_eng = Column(Text)
    item_cn = Column(Text)
    item_cn_eng = Column(Text)
    item_hs = Column(Text)
    cn_code = Column(Text)
    em_factor = Column(Numeric(10, 6))  # 배출계수로 변경
    carbon_factor = Column(Numeric(5, 2))  # 탄소함량 추가
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
            "배출계수": float(self.em_factor) if self.em_factor else None,
            "탄소함량": float(self.carbon_factor) if self.carbon_factor else None
        }

# ============================================================================
# 🌍 국가 코드 엔티티
# ============================================================================

class CountryCode(Base):
    """국가 코드 엔티티"""
    
    __tablename__ = "country_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(Text, nullable=False)
    name_kr = Column(Text, nullable=False)
    code = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "country_name": self.country_name,
            "name_kr": self.name_kr,
            "code": self.code,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# ============================================================================
# 🔥 연료 검색용 엔티티
# ============================================================================

class FuelSearchData:
    """연료 검색 데이터 클래스"""
    
    def __init__(self, id: int, name: str, name_eng: str, fuel_emfactor: float, net_calory: float):
        self.id = id
        self.name = name
        self.name_eng = name_eng
        self.fuel_emfactor = fuel_emfactor
        self.net_calory = net_calory
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_eng": self.name_eng,
            "fuel_emfactor": self.fuel_emfactor,
            "net_calory": self.net_calory
        }

# ============================================================================
# 🧱 원료 검색용 엔티티
# ============================================================================

class MaterialSearchData:
    """원료 검색 데이터 클래스"""
    
    def __init__(self, id: int, name: str, name_eng: str, em_factor: float, carbon_factor: float, cn_code: str, cn_code1: str, cn_code2: str):
        self.id = id
        self.name = name
        self.name_eng = name_eng
        self.em_factor = em_factor
        self.carbon_factor = carbon_factor
        self.cn_code = cn_code
        self.cn_code1 = cn_code1
        self.cn_code2 = cn_code2
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_eng": self.name_eng,
            "em_factor": self.em_factor,
            "carbon_factor": self.carbon_factor,
            "cn_code": self.cn_code,
            "cn_code1": self.cn_code1,
            "cn_code2": self.cn_code2
        }

# ============================================================================
# 🔗 전구물질 검색용 엔티티
# ============================================================================

class PrecursorSearchData:
    """전구물질 검색 데이터 클래스"""
    
    def __init__(self, id: int, precursor: str, precursor_eng: str, direct: float, indirect: float, cn1: str):
        self.id = id
        self.precursor = precursor
        self.precursor_eng = precursor_eng
        self.direct = direct
        self.indirect = indirect
        self.cn1 = cn1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "precursor": self.precursor,
            "precursor_eng": self.precursor_eng,
            "direct": self.direct,
            "indirect": self.indirect,
            "cn1": self.cn1
        }