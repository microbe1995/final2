from sqlalchemy.orm import Session
from app.domain.repositories.user_repo import UserRepository
from app.domain.repositories.company_repo import CompanyRepository
from app.domain.schemas.auth import UserCreate, CompanyCreate, UserLogin
from app.common.security import get_password_hash, verify_password, create_access_token
from app.common.logger import auth_logger

class AuthService:
    """인증 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.company_repo = CompanyRepository(db)
    
    def register_company(self, company_data: CompanyCreate):
        """기업 회원가입"""
        # 사업자번호 중복 확인
        existing_company = self.company_repo.get_by_biz_no(company_data.biz_no)
        if existing_company:
            raise ValueError("이미 등록된 사업자번호입니다.")
        
        # 기업 생성
        company = self.company_repo.create(company_data)
        auth_logger.info(f"Company registered: {company.name_ko} (ID: {company.id})")
        return company
    
    def register_user(self, user_data: UserCreate):
        """사용자 회원가입"""
        # 사용자명 중복 확인
        existing_user = self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("이미 사용 중인 사용자명입니다.")
        
        # 비밀번호 해시화
        user_data_dict = user_data.dict()
        user_data_dict["hashed_password"] = get_password_hash(user_data.password)
        del user_data_dict["password"]
        
        # 사용자 생성
        user = self.user_repo.create(UserCreate(**user_data_dict))
        auth_logger.info(f"User registered: {user.username} (ID: {user.id})")
        return user
    
    def authenticate_user(self, username: str, password: str):
        """사용자 인증"""
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def login_user(self, user_credentials: UserLogin):
        """사용자 로그인"""
        user = self.authenticate_user(user_credentials.username, user_credentials.password)
        if not user:
            raise ValueError("잘못된 사용자명 또는 비밀번호입니다.")
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": user.username})
        
        auth_logger.info(f"User logged in: {user.username}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    
    def get_current_user(self, username: str):
        """현재 사용자 정보 조회"""
        return self.user_repo.get_by_username(username)
