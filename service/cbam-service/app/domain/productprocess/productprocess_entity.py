# ============================================================================
# 🔗 ProductProcess Entity - 제품-공정 중간 테이블 엔티티
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any

# 공통 Base 클래스 사용 (다른 엔티티들과 동일하게)
from app.domain.calculation.calculation_entity import Base

class ProductProcess(Base):
    """제품-공정 중간 테이블 엔티티 (다대다 관계 해소)"""
    
    __tablename__ = "product_process"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False, index=True)  # 제품 ID
    process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 공정 ID
    consumption_amount = Column(Numeric(15, 6), default=0)  # 제품 소비량 (consume 엣지용)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계 설정 (순환참조 방지를 위해 문자열로 참조)
    product = relationship("Product", back_populates="product_processes", lazy="selectin")
    process = relationship("Process", back_populates="product_processes", lazy="selectin")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "process_id": self.process_id,
            "consumption_amount": float(self.consumption_amount) if self.consumption_amount else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<ProductProcess(id={self.id}, product_id={self.product_id}, process_id={self.process_id}, consumption_amount={self.consumption_amount})>"
