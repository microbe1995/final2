from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ============================================================================
# 📝 기존 FuelDir 엔티티
# ============================================================================

class FuelDir(Base):
    __tablename__ = "fueldir"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("process.id", ondelete="CASCADE"), nullable=False)
    fuel_name = Column(String(255), nullable=False, comment="투입된 연료명")
    fuel_factor = Column(Numeric(10, 6), nullable=False, comment="배출계수")
    fuel_amount = Column(Numeric(15, 6), nullable=False, comment="투입된 연료량")
    fuel_oxyfactor = Column(Numeric(5, 4), nullable=True, default=1.0000, comment="산화계수 (기본값: 1)")
    fueldir_em = Column(Numeric(15, 6), nullable=True, default=0, comment="연료직접배출량 (계산 결과)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 관계 설정 (문자열로 참조하여 순환 임포트 방지)
    # process = relationship("Process", back_populates="fueldirs", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "process_id": self.process_id,
            "fuel_name": self.fuel_name,
            "fuel_factor": float(self.fuel_factor) if self.fuel_factor is not None else 0.0,
            "fuel_amount": float(self.fuel_amount) if self.fuel_amount is not None else 0.0,
            "fuel_oxyfactor": float(self.fuel_oxyfactor) if self.fuel_oxyfactor is not None else 1.0000,
            "fueldir_em": float(self.fueldir_em) if self.fueldir_em is not None else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            process_id=data.get("process_id"),
            fuel_name=data.get("fuel_name"),
            fuel_factor=data.get("fuel_factor"),
            fuel_amount=data.get("fuel_amount"),
            fuel_oxyfactor=data.get("fuel_oxyfactor", 1.0000),
            fueldir_em=data.get("fueldir_em", 0.0)
        )

    def __repr__(self):
        return f"<FuelDir(id={self.id}, fuel_name='{self.fuel_name}', fueldir_em={self.fueldir_em})>"

# ============================================================================
# 🏗️ Fuel Master 엔티티 (새로 추가)
# ============================================================================

class FuelMaster(Base):
    """연료 마스터 데이터 엔티티"""
    
    __tablename__ = "fuel_master"
    
    # 기본 컬럼
    id = Column(Integer, primary_key=True, autoincrement=True, comment="연료 마스터 ID")
    fuel_name = Column(String(255), nullable=False, comment="연료명")
    fuel_engname = Column(String(255), nullable=False, comment="연료 영문명")
    fuel_factor = Column(Numeric(10, 6), nullable=False, comment="연료 배출계수")
    net_calory = Column(Numeric(10, 6), nullable=True, comment="순발열량")
    
    # 인덱스 정의
    __table_args__ = (
        Index('idx_fuel_master_name', 'fuel_name'),
        Index('idx_fuel_master_engname', 'fuel_engname'),
        {'comment': '연료 마스터 데이터 테이블'}
    )
    
    def __repr__(self):
        return f"<FuelMaster(id={self.id}, fuel_name='{self.fuel_name}', fuel_factor={self.fuel_factor})>"
    
    def to_dict(self):
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'fuel_name': self.fuel_name,
            'fuel_engname': self.fuel_engname,
            'fuel_factor': float(self.fuel_factor),
            'net_calory': float(self.net_calory) if self.net_calory else None
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """딕셔너리에서 엔티티 생성"""
        return cls(
            fuel_name=data.get('fuel_name'),
            fuel_engname=data.get('fuel_engname'),
            fuel_factor=data.get('fuel_factor'),
            net_calory=data.get('net_calory')
        )
