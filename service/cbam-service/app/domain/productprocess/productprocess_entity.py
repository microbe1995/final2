# ============================================================================
# 🔗 ProductProcess Entity - 제품-공정 중간 테이블 엔티티
# ============================================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

class ProductProcess(Base):
    """제품-공정 중간 테이블 엔티티 (다대다 관계 해소)"""
    
    __tablename__ = "product_process"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False, index=True)  # 제품 ID
    process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 공정 ID
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    product = relationship("Product", back_populates="product_processes")
    process = relationship("Process", back_populates="product_processes", foreign_keys=[process_id])
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "process_id": self.process_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<ProductProcess(id={self.id}, product_id={self.product_id}, process_id={self.process_id})>"
