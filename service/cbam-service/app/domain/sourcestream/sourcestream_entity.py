# ============================================================================
# 🔄 SourceStream Entity - 통합 공정 그룹 데이터 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, BigInteger, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal

Base = declarative_base()

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
    
    # 관계 설정
    start_process = relationship("Process", foreign_keys=[start_process_id])
    end_process = relationship("Process", foreign_keys=[end_process_id])
    chain_links = relationship("ProcessChainLink", back_populates="chain", cascade="all, delete-orphan")
    
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
    
    # 관계 설정
    chain = relationship("ProcessChain", back_populates="chain_links")
    process = relationship("Process")
    
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
# 📊 IntegratedProcessGroupEmission 엔티티 (통합 그룹 배출량)
# ============================================================================

class IntegratedProcessGroupEmission(Base):
    """통합 공정 그룹 배출량 엔티티 - 그룹의 총 배출량을 관리 (누적이 아님!)"""
    
    __tablename__ = "integrated_process_group_emission"
    
    id = Column(Integer, primary_key=True, index=True)
    chain_id = Column(Integer, ForeignKey("process_chain.id"), nullable=False, index=True)  # 그룹 ID
    process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 공정 ID
    integrated_matdir_emission = Column(Numeric(15, 6), nullable=False, default=0)  # 그룹의 총 원료배출량
    integrated_fueldir_emission = Column(Numeric(15, 6), nullable=False, default=0)  # 그룹의 총 연료배출량
    integrated_attrdir_em = Column(Numeric(15, 6), nullable=False, default=0)  # 그룹의 총 직접귀속배출량
    group_processes = Column(Text)  # 그룹에 속한 공정들 (JSON 형태로 저장)
    calculation_date = Column(DateTime, default=datetime.utcnow)  # 계산 일시
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    chain = relationship("ProcessChain")
    process = relationship("Process")
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "chain_id": self.chain_id,
            "process_id": self.process_id,
            "integrated_matdir_emission": float(self.integrated_matdir_emission) if self.integrated_matdir_emission else 0.0,
            "integrated_fueldir_emission": float(self.integrated_fueldir_emission) if self.integrated_fueldir_emission else 0.0,
            "integrated_attrdir_em": float(self.integrated_attrdir_em) if self.integrated_attrdir_em else 0.0,
            "group_processes": self.group_processes,
            "calculation_date": self.calculation_date.isoformat() if self.calculation_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# 🔄 SourceStream 엔티티 (소스 스트림)
# ============================================================================

class SourceStream(Base):
    """소스 스트림 엔티티 - 공정 간 물질/에너지 흐름을 관리"""
    
    __tablename__ = "source_stream"
    
    id = Column(Integer, primary_key=True, index=True)
    source_process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 소스 공정 ID
    target_process_id = Column(Integer, ForeignKey("process.id"), nullable=False, index=True)  # 타겟 공정 ID
    stream_type = Column(Text, nullable=False)  # 스트림 타입 (material, energy, waste)
    stream_name = Column(Text, nullable=False)  # 스트림명
    stream_amount = Column(Numeric(15, 6), nullable=False, default=0)  # 스트림량
    unit = Column(Text, nullable=False)  # 단위
    emission_factor = Column(Numeric(10, 6), nullable=False, default=0)  # 배출계수
    calculated_emission = Column(Numeric(15, 6), nullable=False, default=0)  # 계산된 배출량
    is_continue_stream = Column(Boolean, nullable=False, default=True)  # continue 스트림 여부
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    source_process = relationship("Process", foreign_keys=[source_process_id])
    target_process = relationship("Process", foreign_keys=[target_process_id])
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "source_process_id": self.source_process_id,
            "target_process_id": self.target_process_id,
            "stream_type": self.stream_type,
            "stream_name": self.stream_name,
            "stream_amount": float(self.stream_amount) if self.stream_amount else 0.0,
            "unit": self.unit,
            "emission_factor": float(self.emission_factor) if self.emission_factor else 0.0,
            "calculated_emission": float(self.calculated_emission) if self.calculated_emission else 0.0,
            "is_continue_stream": self.is_continue_stream,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
