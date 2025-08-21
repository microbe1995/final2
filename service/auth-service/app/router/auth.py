from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Union
import json

from app.common.db import get_db
from app.common.security import get_current_user, create_access_token, verify_password, get_password_hash
# 순환 import 방지를 위해 필요할 때 import
from app.domain.entities.country import Country
from app.domain.schemas.auth import (
    CompanyRegisterIn, CompanyRegisterOut, CompanyOut,
    UserRegisterIn, UserRegisterOut, UserOut,
    LoginIn, LoginOut, TokenOut,
    CountrySearchIn, CountryOut, CountrySearchOut
)
from app.common.logger import auth_logger

router = APIRouter(prefix="/auth", tags=["인증"])

# ===== 기업 회원가입 =====

@router.post("/register/company", response_model=CompanyRegisterOut)
async def register_company(
    company_data: CompanyRegisterIn,
    db: Session = Depends(get_db)
):
    """기업 회원가입"""
    # 순환 import 방지를 위해 여기서 import
    from app.domain.entities.company.company import Company
    
    try:
        # 기업 ID 중복 확인
        existing_company = db.query(Company).filter(Company.company_id == company_data.company_id).first()
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 기업 ID입니다."
            )
        
        # 비밀번호 해시화
        hashed_password = get_password_hash(company_data.password)
        
        # 새 기업 생성
        new_company = Company(
            company_id=company_data.company_id,
            hashed_password=hashed_password,
            Installation=company_data.Installation,
            Installation_en=company_data.Installation_en,
            economic_activity=company_data.economic_activity,
            economic_activity_en=company_data.economic_activity_en,
            representative=company_data.representative,
            representative_en=company_data.representative_en,
            email=company_data.email,
            telephone=company_data.telephone,
            street=company_data.street,
            street_en=company_data.street_en,
            number=company_data.number,
            number_en=company_data.number_en,
            postcode=company_data.postcode,
            city=company_data.city,
            city_en=company_data.city_en,
            country=company_data.country,
            country_en=company_data.country_en,
            unlocode=company_data.unlocode,
            sourcelatitude=company_data.sourcelatitude,
            sourcelongitude=company_data.sourcelongitude
        )
        
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        
        auth_logger.info(f"기업 회원가입 완료: {new_company.company_id}")
        
        return new_company
        
    except Exception as e:
        db.rollback()
        auth_logger.error(f"기업 회원가입 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="기업 회원가입 중 오류가 발생했습니다."
        )

# ===== 사용자 회원가입 =====

@router.post("/register/user", response_model=UserRegisterOut)
async def register_user(
    user_data: UserRegisterIn,
    db: Session = Depends(get_db)
):
    """사용자 회원가입"""
    # 순환 import 방지를 위해 여기서 import
    from app.domain.entities.user.user import User
    from app.domain.entities.company.company import Company
    
    try:
        # 기업 존재 확인
        company = db.query(Company).filter(Company.id == user_data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="존재하지 않는 기업입니다."
            )
        
        # 사용자명 중복 확인
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 사용자명입니다."
            )
        
        # 비밀번호 해시화
        hashed_password = get_password_hash(user_data.password)
        
        # 권한 정보 JSON 변환
        permissions = {
            "can_manage_users": user_data.can_manage_users,
            "can_view_reports": user_data.can_view_reports,
            "can_edit_data": user_data.can_edit_data,
            "can_export_data": user_data.can_export_data
        }
        
        # 새 사용자 생성
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            company_id=user_data.company_id,
            role=user_data.role,
            permissions=json.dumps(permissions),
            is_company_admin=user_data.is_company_admin,
            can_manage_users=user_data.can_manage_users,
            can_view_reports=user_data.can_view_reports,
            can_edit_data=user_data.can_edit_data,
            can_export_data=user_data.can_export_data
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        auth_logger.info(f"사용자 회원가입 완료: {new_user.username}")
        
        return new_user
        
    except Exception as e:
        db.rollback()
        auth_logger.error(f"사용자 회원가입 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 회원가입 중 오류가 발생했습니다."
        )

# ===== 로그인 =====

@router.post("/login", response_model=LoginOut)
async def login(
    login_data: LoginIn,
    db: Session = Depends(get_db)
):
    """통합 로그인 (기업/사용자)"""
    # 순환 import 방지를 위해 여기서 import
    from app.domain.entities.user.user import User
    from app.domain.entities.company.company import Company
    
    try:
        user = None
        user_type = None
        
        # 기업 로그인 시도
        if login_data.user_type == "company":
            company = db.query(Company).filter(Company.company_id == login_data.username).first()
            if company and verify_password(login_data.password, company.hashed_password):
                user = company
                user_type = "company"
        
        # 사용자 로그인 시도
        elif login_data.user_type == "user":
            user_obj = db.query(User).filter(User.username == login_data.username).first()
            if user_obj and verify_password(login_data.password, user_obj.hashed_password):
                user = user_obj
                user_type = "user"
        
        # 자동 감지 (기업 ID로 먼저 시도)
        else:
            # 기업 ID로 시도
            company = db.query(Company).filter(Company.company_id == login_data.username).first()
            if company and verify_password(login_data.password, company.hashed_password):
                user = company
                user_type = "company"
            else:
                # 사용자명으로 시도
                user_obj = db.query(User).filter(User.username == login_data.username).first()
                if user_obj and verify_password(login_data.password, user_obj.hashed_password):
                    user = user_obj
                    user_type = "user"
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 로그인 정보입니다."
            )
        
        # JWT 토큰 생성
        token_data = {
            "sub": str(user.id),
            "type": user_type,
            "username": user.company_id if user_type == "company" else user.username
        }
        
        access_token = create_access_token(data=token_data)
        
        auth_logger.info(f"로그인 성공: {login_data.username} ({user_type})")
        
        return LoginOut(
            access_token=access_token,
            token_type="bearer",
            user_info=user
        )
        
    except Exception as e:
        auth_logger.error(f"로그인 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 중 오류가 발생했습니다."
        )

# ===== 현재 사용자 정보 =====

@router.get("/me", response_model=Union[CompanyOut, UserOut])
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """현재 로그인한 사용자 정보 조회"""
    return current_user

# ===== 국가 검색 =====

@router.post("/countries/search", response_model=CountrySearchOut)
async def search_countries(
    search_data: CountrySearchIn,
    db: Session = Depends(get_db)
):
    """국가 검색 (korean_name 기준)"""
    try:
        # korean_name으로 검색 (부분 일치)
        search_term = f"%{search_data.search_term}%"
        countries = db.query(Country).filter(
            Country.korean_name.ilike(search_term)
        ).limit(20).all()
        
        total_count = len(countries)
        
        auth_logger.info(f"국가 검색: '{search_data.search_term}' -> {total_count}개 결과")
        
        return CountrySearchOut(
            countries=countries,
            total_count=total_count
        )
        
    except Exception as e:
        auth_logger.error(f"국가 검색 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="국가 검색 중 오류가 발생했습니다."
        )

@router.get("/countries", response_model=list[CountryOut])
async def get_all_countries(
    db: Session = Depends(get_db)
):
    """모든 국가 목록 조회"""
    try:
        countries = db.query(Country).order_by(Country.korean_name).all()
        return countries
        
    except Exception as e:
        auth_logger.error(f"국가 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="국가 목록 조회 중 오류가 발생했습니다."
        )
