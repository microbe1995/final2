from sqlalchemy.orm import Session
from app.domain.entities.company import Company
from app.domain.schemas.auth import CompanyCreate, CompanyUpdate

class CompanyRepository:
    """기업 리포지토리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, company_id: int) -> Company:
        """ID로 기업 조회"""
        return self.db.query(Company).filter(Company.id == company_id).first()
    
    def get_by_biz_no(self, biz_no: str) -> Company:
        """사업자번호로 기업 조회"""
        return self.db.query(Company).filter(Company.biz_no == biz_no).first()
    
    def get_by_name_ko(self, name_ko: str) -> Company:
        """국문 이름으로 기업 조회"""
        return self.db.query(Company).filter(Company.name_ko == name_ko).first()
    
    def create(self, company_data: CompanyCreate) -> Company:
        """기업 생성"""
        db_company = Company(**company_data.dict())
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return db_company
    
    def update(self, company_id: int, company_data: CompanyUpdate) -> Company:
        """기업 정보 업데이트"""
        db_company = self.get_by_id(company_id)
        if db_company:
            for field, value in company_data.dict(exclude_unset=True).items():
                setattr(db_company, field, value)
            self.db.commit()
            self.db.refresh(db_company)
        return db_company
    
    def delete(self, company_id: int) -> bool:
        """기업 삭제"""
        db_company = self.get_by_id(company_id)
        if db_company:
            self.db.delete(db_company)
            self.db.commit()
            return True
        return False
    
    def list_companies(self, skip: int = 0, limit: int = 100):
        """기업 목록 조회"""
        return self.db.query(Company).offset(skip).limit(limit).all()
