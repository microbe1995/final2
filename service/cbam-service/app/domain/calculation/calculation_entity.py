# ============================================================================
# 🧮 Calculation Entity - CBAM 계산 데이터 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal

Base = declarative_base()

# ============================================================================
# 🔥 연료 엔티티
# ============================================================================

class Fuel(Base):
    """연료 엔티티"""
    
    __tablename__ = "fuels"
    
    id = Column(Integer, primary_key=True, index=True)
    fuel_name = Column(Text, nullable=False, index=True)  # 연료명 (한글)
    fuel_eng = Column(Text)  # 연료영문명
    fuel_emfactor = Column(Numeric(10, 6), nullable=False, default=0)  # 배출계수 (tCO2/TJ)
    net_calory = Column(Numeric(10, 6), nullable=False, default=0)  # 순발열량 (TJ/Gg)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "fuel_name": self.fuel_name,
            "fuel_eng": self.fuel_eng,
            "fuel_emfactor": float(self.fuel_emfactor) if self.fuel_emfactor else 0.0,
            "net_calory": float(self.net_calory) if self.net_calory else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 🧱 원료 엔티티
# ============================================================================

class Material(Base):
    """원료 엔티티"""
    
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(Text, nullable=False, index=True)  # 원료명 (한글)
    item_eng = Column(Text)  # 원료영문명
    carbon_factor = Column(Numeric(5, 2), default=0.0)  # 탄소함량 (%)
    em_factor = Column(Numeric(10, 6), default=0.0)  # 배출계수 (tCO2/톤)
    cn_code = Column(Text)
    cn_code1 = Column(Text)
    cn_code2 = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "item_name": self.item_name,
            "item_eng": self.item_eng,
            "carbon_factor": float(self.carbon_factor) if self.carbon_factor else 0.0,
            "em_factor": float(self.em_factor) if self.em_factor else 0.0,
            "cn_code": self.cn_code,
            "cn_code1": self.cn_code1,
            "cn_code2": self.cn_code2,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 🔗 전구물질 엔티티
# ============================================================================

class Precursor(Base):
    """전구물질 엔티티"""
    
    __tablename__ = "precursors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, nullable=False, index=True)
    precursor = Column(Text, nullable=False)  # 전구물질명 (한글)
    precursor_eng = Column(Text)  # 전구물질명 (영문)
    cn1 = Column(Text, default="")  # CN코드1
    cn2 = Column(Text, default="")  # CN코드2
    cn3 = Column(Text, default="")  # CN코드3
    direct = Column(Numeric(10, 6), default=0.0)  # 직접 배출계수 (tCO2/톤)
    indirect = Column(Numeric(10, 6), default=0.0)  # 간접 배출계수 (tCO2/톤)
    final_country_code = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "precursor": self.precursor,
            "precursor_eng": self.precursor_eng,
            "cn1": self.cn1,
            "cn2": self.cn2,
            "cn3": self.cn3,
            "direct": float(self.direct) if self.direct else 0.0,
            "indirect": float(self.indirect) if self.indirect else 0.0,
            "final_country_code": self.final_country_code,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Precursor":
        """딕셔너리에서 엔티티 생성"""
        return cls(
            user_id=data.get("user_id"),
            precursor=data.get("precursor"),
            precursor_eng=data.get("precursor_eng", ""),
            cn1=data.get("cn1", ""),
            cn2=data.get("cn2", ""),
            cn3=data.get("cn3", ""),
            direct=data.get("direct", 0.0),
            indirect=data.get("indirect", 0.0),
            final_country_code=data.get("final_country_code", ""),
            created_at=datetime.utcnow()
        )

# ============================================================================
# 📊 계산 결과 엔티티
# ============================================================================

class CalculationResult(Base):
    """계산 결과 엔티티"""
    
    __tablename__ = "calculation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, nullable=False, index=True)
    calculation_type = Column(Text, nullable=False)  # fuel, material, precursor, electricity, cbam
    input_data = Column(Text)  # JSON 형태의 입력 데이터
    result_data = Column(Text)  # JSON 형태의 결과 데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "calculation_type": self.calculation_type,
            "input_data": self.input_data,
            "result_data": self.result_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }