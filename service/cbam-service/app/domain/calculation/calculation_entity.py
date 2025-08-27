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
    name = Column(Text, nullable=False, index=True)  # 사업장명
    reporting_year = Column(Integer, nullable=False, default=datetime.now().year)  # 보고기간 (년도)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    products = relationship("Product", back_populates="install")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
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
    product_cncode = Column(Text)  # 제품 CN 코드
    goods_name = Column(Text)  # 상품명
    aggrgoods_name = Column(Text)  # 집계 상품명
    product_sell = Column(Numeric(15, 6), default=0)  # 제품 판매량
    product_eusell = Column(Numeric(15, 6), default=0)  # 제품 EU 판매량
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    install = relationship("Install", back_populates="products")
    processes = relationship("Process", back_populates="product")
    
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
            "product_cncode": self.product_cncode,
            "goods_name": self.goods_name,
            "aggrgoods_name": self.aggrgoods_name,
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
            product_cncode=data.get("product_cncode"),
            goods_name=data.get("goods_name"),
            aggrgoods_name=data.get("aggrgoods_name"),
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
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False, index=True)  # 제품 ID
    process_name = Column(Text, nullable=False, index=True)  # 프로세스명
    start_period = Column(Date, nullable=False)  # 시작일
    end_period = Column(Date, nullable=False)  # 종료일
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    product = relationship("Product", back_populates="processes")
    process_inputs = relationship("ProcessInput", back_populates="process")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "process_name": self.process_name,
            "start_period": self.start_period.isoformat() if self.start_period else None,
            "end_period": self.end_period.isoformat() if self.end_period else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 📥 ProcessInput 엔티티 (프로세스 입력)
# ============================================================================

class ProcessInput(Base):
    """프로세스 입력 엔티티"""
    
    __tablename__ = "process_input"
    
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 프로세스 ID
    input_type = Column(Text, nullable=False)  # 입력 타입 (material, fuel, electricity)
    input_name = Column(Text, nullable=False)  # 입력명
    amount = Column(Numeric(15, 6), nullable=False, default=0)  # 수량
    factor = Column(Numeric(15, 6))  # 배출계수
    oxy_factor = Column(Numeric(15, 6))  # 산화계수
    direm_emission = Column(Numeric(15, 6))  # 직접배출량
    indirem_emission = Column(Numeric(15, 6))  # 간접배출량
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    process = relationship("Process", back_populates="process_inputs")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "process_id": self.process_id,
            "input_type": self.input_type,
            "input_name": self.input_name,
            "amount": float(self.amount) if self.amount else 0.0,
            "factor": float(self.factor) if self.factor else None,
            "oxy_factor": float(self.oxy_factor) if self.oxy_factor else None,
            "direm_emission": float(self.direm_emission) if self.direm_emission else None,
            "indirem_emission": float(self.indirem_emission) if self.indirem_emission else None,
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