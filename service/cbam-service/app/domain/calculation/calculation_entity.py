# ============================================================================
# 🧮 Calculation Entity - CBAM 계산 데이터 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, JSON, ARRAY, Text
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
    fuel_type_description = Column(String(100), nullable=False, index=True)
    fuel_type_description_eng = Column(String(100))
    emission_factor = Column(Numeric(10, 6), nullable=False, default=0)
    net_calorific_value = Column(Numeric(10, 6), nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "fuel_type_description": self.fuel_type_description,
            "fuel_type_description_eng": self.fuel_type_description_eng,
            "emission_factor": float(self.emission_factor) if self.emission_factor else 0.0,
            "net_calorific_value": float(self.net_calorific_value) if self.net_calorific_value else 0.0,
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
    item_name = Column(String(100), nullable=False, index=True)
    item_name_eng = Column(String(100))
    direct_factor = Column(Numeric(10, 6))
    indirect_factor = Column(Numeric(10, 6))
    total_factor = Column(Numeric(10, 6))
    cn_code = Column(String(20))
    cn_code1 = Column(String(20))
    cn_code2 = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "item_name": self.item_name,
            "item_name_eng": self.item_name_eng,
            "direct_factor": float(self.direct_factor) if self.direct_factor else None,
            "indirect_factor": float(self.indirect_factor) if self.indirect_factor else None,
            "total_factor": float(self.total_factor) if self.total_factor else None,
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
    user_id = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), default="")
    cn_code = Column(String(20), default="")
    cn_code1 = Column(String(20), default="")
    cn_code2 = Column(String(20), default="")
    production_routes = Column(ARRAY(Text), default=[])
    final_country_code = Column(String(10), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "name_en": self.name_en,
            "cn_code": self.cn_code,
            "cn_code1": self.cn_code1,
            "cn_code2": self.cn_code2,
            "production_routes": self.production_routes or [],
            "final_country_code": self.final_country_code,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Precursor":
        """딕셔너리에서 엔티티 생성"""
        return cls(
            user_id=data.get("user_id"),
            name=data.get("name"),
            name_en=data.get("name_en", ""),
            cn_code=data.get("cn_code", ""),
            cn_code1=data.get("cn_code1", ""),
            cn_code2=data.get("cn_code2", ""),
            production_routes=data.get("production_routes", []),
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
    user_id = Column(String(20), nullable=False, index=True)
    calculation_type = Column(String(50), nullable=False)
    input_data = Column(JSON)
    result_data = Column(JSON)
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