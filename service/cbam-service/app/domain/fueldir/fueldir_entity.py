from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
