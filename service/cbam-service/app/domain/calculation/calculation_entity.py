# ============================================================================
# 🧮 Calculation Entity - CBAM 계산 데이터 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, BigInteger, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal

Base = declarative_base()

# ============================================================================
# 🏭 Install 엔티티 (사업장)
# ============================================================================

class Install(Base):
    """사업장 엔티티"""
    
    __tablename__ = "install"
    
    id = Column(Integer, primary_key=True, index=True)
    install_name = Column(Text, nullable=False, index=True)  # 사업장명
    reporting_year = Column(Integer, nullable=False, default=datetime.now().year)  # 보고기간 (년도)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    products = relationship("Product", back_populates="install")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "install_name": self.install_name,
            "reporting_year": self.reporting_year,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 📦 Product 엔티티 (제품)
# ============================================================================

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    install = relationship("Install", back_populates="products")
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
            created_at=datetime.utcnow()
        )

# ============================================================================
# 🔄 Process 엔티티 (프로세스)
# ============================================================================

class Process(Base):
    """프로세스 엔티티"""
    
    __tablename__ = "process"
    
    id = Column(Integer, primary_key=True, index=True)
    process_name = Column(Text, nullable=False, index=True)  # 프로세스명
    start_period = Column(Date, nullable=False)  # 시작일
    end_period = Column(Date, nullable=False)  # 종료일
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    product_processes = relationship("ProductProcess", back_populates="process")
    
    # 다대다 관계를 위한 편의 메서드
    @property
    def products(self):
        """이 공정과 연결된 모든 제품들"""
        return [pp.product for pp in self.product_processes]
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "process_name": self.process_name,
            "start_period": self.start_period.isoformat() if self.start_period else None,
            "end_period": self.end_period.isoformat() if self.end_period else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }



# ============================================================================
# 🔗 Edge 엔티티 (엣지)
# ============================================================================

class Edge(Base):
    """엣지 엔티티"""
    
    __tablename__ = "edge"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False, index=True)  # 소스 노드 ID
    target_id = Column(Integer, nullable=False, index=True)  # 타겟 노드 ID
    edge_kind = Column(Text, nullable=False)  # 엣지 종류 (consume/produce/continue)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_kind": self.edge_kind,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 🔗 ProductProcess 엔티티 (제품-공정 중간 테이블)
# ============================================================================

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
    process = relationship("Process", back_populates="product_processes")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "process_id": self.process_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }