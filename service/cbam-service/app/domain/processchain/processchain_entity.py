# ============================================================================
# 🔄 ProcessChain Entity - 통합 공정 그룹 데이터 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, BigInteger, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal

# 공통 Base 클래스만 import (Process는 문자열로 참조하여 순환 참조 방지)
from app.domain.calculation.calculation_entity import Base

# ============================================================================
# 🔄 ProcessChain 엔티티 (통합 공정 그룹)
# ============================================================================

class ProcessChain(Base):
    """통합 공정 그룹 엔티티 - 연결된 공정들을 하나의 그룹으로 관리"""
    
    __tablename__ = "process_chain"
    
    id = Column(Integer, primary_key=True, index=True)
    chain_name = Column(Text, nullable=False, index=True)  # 그룹명 (예: "압연1-용해 그룹")
    start_process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 시작 공정 ID
    end_process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 종료 공정 ID
    chain_length = Column(Integer, nullable=False, default=1)  # 그룹 내 공정 개수
    is_active = Column(Boolean, nullable=False, default=True)  # 활성 상태
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정 (문자열로 참조하여 순환 참조 방지)
    start_process = relationship("Process", foreign_keys=[start_process_id], lazy="select")
    end_process = relationship("Process", foreign_keys=[end_process_id], lazy="select")
    chain_links = relationship("ProcessChainLink", back_populates="chain", cascade="all, delete-orphan", lazy="select")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "chain_name": self.chain_name,
            "start_process_id": self.start_process_id,
            "end_process_id": self.end_process_id,
            "chain_length": self.chain_length,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 🔗 ProcessChainLink 엔티티 (그룹 내 공정 멤버)
# ============================================================================

class ProcessChainLink(Base):
    """통합 공정 그룹 링크 엔티티 - 그룹에 속한 각 공정의 순서와 연결 정보"""
    
    __tablename__ = "process_chain_link"
    
    id = Column(Integer, primary_key=True, index=True)
    chain_id = Column(Integer, ForeignKey("process_chain.id"), nullable=False, index=True)  # 그룹 ID
    process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 공정 ID
    sequence_order = Column(Integer, nullable=False)  # 그룹 내 순서 (1, 2, 3, ...)
    is_continue_edge = Column(Boolean, nullable=False, default=True)  # continue 엣지 여부
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정 (문자열로 참조하여 순환 참조 방지)
    chain = relationship("ProcessChain", back_populates="chain_links", lazy="select")
    process = relationship("Process", lazy="select")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "chain_id": self.chain_id,
            "process_id": self.process_id,
            "sequence_order": self.sequence_order,
            "is_continue_edge": self.is_continue_edge,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# ✅ SourceStream 엔티티 제거됨 - Edge가 이미 공정 간 연결을 관리
# ============================================================================
