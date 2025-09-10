from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any
import uuid

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(Text, unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    company_id = Column(Text, unique=True, index=True, nullable=False)
    hashed_password = Column(Text, nullable=False)
    Installation = Column(Text, nullable=False)
    Installation_en = Column(Text, nullable=True)
    economic_activity = Column(Text, nullable=True)
    economic_activity_en = Column(Text, nullable=True)
    representative = Column(Text, nullable=True)
    representative_en = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    telephone = Column(Text, nullable=True)
    street = Column(Text, nullable=True)
    street_en = Column(Text, nullable=True)
    number = Column(Text, nullable=True)
    number_en = Column(Text, nullable=True)
    postcode = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    city_en = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    country_en = Column(Text, nullable=True)
    unlocode = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "uuid": self.uuid,
            "company_id": self.company_id,
            "Installation": self.Installation,
            "Installation_en": self.Installation_en,
            "economic_activity": self.economic_activity,
            "economic_activity_en": self.economic_activity_en,
            "representative": self.representative,
            "representative_en": self.representative_en,
            "email": self.email,
            "telephone": self.telephone,
            "street": self.street,
            "street_en": self.street_en,
            "number": self.number,
            "number_en": self.number_en,
            "postcode": self.postcode,
            "city": self.city,
            "city_en": self.city_en,
            "country": self.country,
            "country_en": self.country_en,
            "unlocode": self.unlocode,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


