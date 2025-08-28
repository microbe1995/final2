# ============================================================================
# 🏗️ Mapping Entity - HS-CN 매핑 데이터베이스 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Text, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class HSCNMapping(Base):
    """HS-CN 매핑 테이블 엔티티"""
    
    __tablename__ = "hs_cn_mapping"
    
    # 기본 컬럼
    id = Column(Integer, primary_key=True, autoincrement=True, comment="매핑 ID")
    hscode = Column(String(6), nullable=False, comment="HS 코드 (앞 6자리)")
    aggregoods_name = Column(Text, nullable=True, comment="제품 대분류(한글)")
    aggregoods_engname = Column(Text, nullable=True, comment="제품 대분류(영문)")
    cncode_total = Column(String(8), nullable=False, comment="CN 코드 (8자리)")
    goods_name = Column(Text, nullable=True, comment="상세 품명(한글)")
    goods_engname = Column(Text, nullable=True, comment="상세 품명(영문)")
    
    # 인덱스 정의
    __table_args__ = (
        Index('idx_hs_cn_mapping_hscode', 'hscode'),
        Index('idx_hs_cn_mapping_cncode', 'cncode_total'),
        {'comment': 'HS 코드와 CN 코드 매핑 테이블'}
    )
    
    def __repr__(self):
        return f"<HSCNMapping(id={self.id}, hscode='{self.hscode}', cncode_total='{self.cncode_total}')>"
    
    def to_dict(self):
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'hscode': self.hscode,
            'aggregoods_name': self.aggregoods_name,
            'aggregoods_engname': self.aggregoods_engname,
            'cncode_total': self.cncode_total,
            'goods_name': self.goods_name,
            'goods_engname': self.goods_engname
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """딕셔너리에서 엔티티 생성"""
        return cls(
            hscode=data.get('hscode'),
            aggregoods_name=data.get('aggregoods_name'),
            aggregoods_engname=data.get('aggregoods_engname'),
            cncode_total=data.get('cncode_total'),
            goods_name=data.get('goods_name'),
            goods_engname=data.get('goods_engname')
        )
