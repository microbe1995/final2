from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.domain.entities.country import Country
from app.domain.schemas.country import CountryCreate, CountryUpdate, CountrySearchRequest
from app.common.logger import auth_logger

class CountryService:
    """국가 관련 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_countries(self, search_request: CountrySearchRequest) -> List[Country]:
        """국가 검색 (코드, 영문명, 한국어명으로 검색)"""
        try:
            query = self.db.query(Country)
            
            if search_request.query:
                search_term = f"%{search_request.query}%"
                query = query.filter(
                    or_(
                        Country.code.ilike(search_term),
                        Country.country_name.ilike(search_term),
                        Country.korean_name.ilike(search_term),
                        Country.unlocode.ilike(search_term) if Country.unlocode else False
                    )
                )
            
            # 정렬 (코드 기준)
            query = query.order_by(Country.code)
            
            # 제한
            if search_request.limit:
                query = query.limit(search_request.limit)
            
            countries = query.all()
            auth_logger.info(f"국가 검색 완료: '{search_request.query}' -> {len(countries)}개 결과")
            
            return countries
            
        except Exception as e:
            auth_logger.error(f"국가 검색 중 오류: {str(e)}")
            return []
    
    def get_country_by_code(self, code: str) -> Optional[Country]:
        """코드로 국가 조회"""
        try:
            return self.db.query(Country).filter(Country.code == code).first()
        except Exception as e:
            auth_logger.error(f"코드로 국가 조회 중 오류: {str(e)}")
            return None
    
    def get_country_by_unlocode(self, unlocode: str) -> Optional[Country]:
        """UNLOCODE로 국가 조회"""
        try:
            return self.db.query(Country).filter(Country.unlocode == unlocode).first()
        except Exception as e:
            auth_logger.error(f"UNLOCODE로 국가 조회 중 오류: {str(e)}")
            return None
    
    def get_all_countries(self, limit: Optional[int] = None) -> List[Country]:
        """모든 국가 조회"""
        try:
            query = self.db.query(Country).order_by(Country.code)
            if limit:
                query = query.limit(limit)
            return query.all()
        except Exception as e:
            auth_logger.error(f"모든 국가 조회 중 오류: {str(e)}")
            return []
    
    def create_country(self, country_data: CountryCreate) -> Optional[Country]:
        """새 국가 생성"""
        try:
            country = Country(**country_data.dict())
            self.db.add(country)
            self.db.commit()
            self.db.refresh(country)
            auth_logger.info(f"새 국가 생성: {country.code}")
            return country
        except Exception as e:
            self.db.rollback()
            auth_logger.error(f"국가 생성 중 오류: {str(e)}")
            return None
    
    def update_country(self, country_id: int, country_data: CountryUpdate) -> Optional[Country]:
        """국가 정보 업데이트"""
        try:
            country = self.db.query(Country).filter(Country.id == country_id).first()
            if not country:
                return None
            
            update_data = country_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(country, field, value)
            
            self.db.commit()
            self.db.refresh(country)
            auth_logger.info(f"국가 정보 업데이트: {country.code}")
            return country
        except Exception as e:
            self.db.rollback()
            auth_logger.error(f"국가 업데이트 중 오류: {str(e)}")
            return None
    
    def delete_country(self, country_id: int) -> bool:
        """국가 삭제"""
        try:
            country = self.db.query(Country).filter(Country.id == country_id).first()
            if not country:
                return False
            
            self.db.delete(country)
            self.db.commit()
            auth_logger.info(f"국가 삭제: {country.code}")
            return True
        except Exception as e:
            self.db.rollback()
            auth_logger.error(f"국가 삭제 중 오류: {str(e)}")
            return False
