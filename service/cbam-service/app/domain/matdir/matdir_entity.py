from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ============================================================================
# 📝 기존 MatDir 엔티티
# ============================================================================

class MatDir(Base):
    __tablename__ = "matdir"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("process.id", ondelete="CASCADE"), nullable=False)
    mat_name = Column(String(255), nullable=False, comment="투입된 원료명")
    mat_factor = Column(Numeric(10, 6), nullable=False, comment="배출계수")
    mat_amount = Column(Numeric(15, 6), nullable=False, comment="투입된 원료량")
    oxyfactor = Column(Numeric(5, 4), nullable=True, default=1.0000, comment="산화계수 (기본값: 1)")
    matdir_em = Column(Numeric(15, 6), nullable=True, default=0, comment="원료직접배출량 (계산 결과)")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 관계 설정 (문자열로 참조하여 순환 임포트 방지)
    # process = relationship("Process", back_populates="matdirs", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "process_id": self.process_id,
            "mat_name": self.mat_name,
            "mat_factor": float(self.mat_factor) if self.mat_factor is not None else 0.0,
            "mat_amount": float(self.mat_amount) if self.mat_amount is not None else 0.0,
            "oxyfactor": float(self.oxyfactor) if self.oxyfactor is not None else 1.0000,
            "matdir_em": float(self.matdir_em) if self.matdir_em is not None else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            process_id=data.get("process_id"),
            mat_name=data.get("mat_name"),
            mat_factor=data.get("mat_factor"),
            mat_amount=data.get("mat_amount"),
            oxyfactor=data.get("oxyfactor", 1.0000),
            matdir_em=data.get("matdir_em", 0)
        )

# ============================================================================
# 🏗️ Material Master 엔티티 (새로 추가)
# ============================================================================

class MaterialMaster(Base):
    """원료 마스터 데이터 엔티티"""
    
    __tablename__ = "material_master"
    
    # 기본 컬럼
    id = Column(Integer, primary_key=True, autoincrement=True, comment="원료 마스터 ID")
    mat_name = Column(String(255), nullable=False, comment="원료명")
    mat_engname = Column(String(255), nullable=False, comment="원료 영문명")
    carbon_content = Column(Numeric(10, 6), nullable=True, comment="탄소 함량")
    mat_factor = Column(Numeric(10, 6), nullable=False, comment="원료 배출계수")
    
    # 인덱스 정의
    __table_args__ = (
        Index('idx_material_master_name', 'mat_name'),
        Index('idx_material_master_engname', 'mat_engname'),
        {'comment': '원료 마스터 데이터 테이블'}
    )
    
    def __repr__(self):
        return f"<MaterialMaster(id={self.id}, mat_name='{self.mat_name}', mat_factor={self.mat_factor})>"
    
    def to_dict(self):
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'mat_name': self.mat_name,
            'mat_engname': self.mat_engname,
            'carbon_content': float(self.carbon_content) if self.carbon_content else None,
            'mat_factor': float(self.mat_factor)
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """딕셔너리에서 엔티티 생성"""
        return cls(
            mat_name=data.get('mat_name'),
            mat_engname=data.get('mat_engname'),
            carbon_content=data.get('carbon_content'),
            mat_factor=data.get('mat_factor')
        )
