# ============================================================================
# 📦 Product Entity - 제품 데이터베이스 모델
# ============================================================================

from sqlalchemy import Column, Integer, Text, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Dict, Any

# 공통 Base 클래스 사용
from app.common.database_base import Base

class Product(Base):
    """제품 엔티티"""
    
    __tablename__ = "product"
    
    id = Column(Integer, primary_key=True, index=True)
    install_id = Column(Integer, ForeignKey("install.id"), nullable=False, index=True)  # 사업장 ID
    product_name = Column(Text, nullable=False, index=True)  # 제품명
    product_category = Column(Text, nullable=False)  # 제품 카테고리 (단순제품/복합제품)
    prostart_period = Column(Date, nullable=False)  # 기간 시작일
    proend_period = Column(Date, nullable=False)  # 기간 종료일
    product_amount = Column(Numeric(15, 6), nullable=False, default=0)  # 제품 수량
    cncode_total = Column(Text)  # 제품 CN 코드
    goods_name = Column(Text)  # 품목명
    goods_engname = Column(Text)  # 품목영문명
    aggrgoods_name = Column(Text)  # 품목군명
    aggrgoods_engname = Column(Text)  # 품목군영문명
    product_sell = Column(Numeric(15, 6), default=0)  # 제품 판매량
    product_eusell = Column(Numeric(15, 6), default=0)  # 제품 EU 판매량
    attr_em = Column(Numeric(15, 6), default=0)  # 제품 배출량
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 관계 설정
    product_processes = relationship("ProductProcess", back_populates="product")
    
    # 다대다 관계를 위한 편의 메서드
    @property
    def processes(self):
        """이 제품과 연결된 모든 공정들"""
        return [pp.process for pp in self.product_processes]
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "install_id": self.install_id,
            "product_name": self.product_name,
            "product_category": self.product_category,
            "prostart_period": self.prostart_period.isoformat() if self.prostart_period else None,
            "proend_period": self.proend_period.isoformat() if self.proend_period else None,
            "product_amount": float(self.product_amount) if self.product_amount else 0.0,
            "cncode_total": self.cncode_total,
            "goods_name": self.goods_name,
            "goods_engname": self.goods_engname,
            "aggrgoods_name": self.aggrgoods_name,
            "aggrgoods_engname": self.aggrgoods_engname,
            "product_sell": float(self.product_sell) if self.product_sell else 0.0,
            "product_eusell": float(self.product_eusell) if self.product_eusell else 0.0,
            "attr_em": float(self.attr_em) if self.attr_em else 0.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        """딕셔너리에서 엔티티 생성"""
        from datetime import date
        
        return cls(
            install_id=data.get("install_id"),
            product_name=data.get("product_name"),
            product_category=data.get("product_category"),
            prostart_period=date.fromisoformat(data.get("prostart_period")) if data.get("prostart_period") else None,
            proend_period=date.fromisoformat(data.get("proend_period")) if data.get("proend_period") else None,
            product_amount=data.get("product_amount", 0.0),
            cncode_total=data.get("cncode_total"),
            goods_name=data.get("goods_name"),
            goods_engname=data.get("goods_engname"),
            aggrgoods_name=data.get("aggrgoods_name"),
            aggrgoods_engname=data.get("aggrgoods_engname"),
            product_sell=data.get("product_sell", 0.0),
            product_eusell=data.get("product_eusell", 0.0),
            attr_em=data.get("attr_em", 0.0),
            created_at=datetime.now(timezone.utc)
        )
    
    def __repr__(self):
        return f"<Product(id={self.id}, product_name='{self.product_name}', install_id={self.install_id})>"
