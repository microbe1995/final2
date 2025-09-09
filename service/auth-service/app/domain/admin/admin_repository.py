from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Union
import json

from app.common.db import get_db
from app.common.security import get_current_user, create_access_token, verify_password, get_password_hash
from app.domain.entities.country import Country
from app.domain.schemas.auth import (
    CompanyRegisterIn, CompanyRegisterOut, CompanyOut,
    UserRegisterIn, UserRegisterOut, UserOut,
    LoginIn, LoginOut, TokenOut,
    CountrySearchIn, CountryOut, CountrySearchOut
)
from app.common.logger import auth_logger

router = APIRouter(prefix="/auth", tags=["인증"])

@router.post("/register/company", response_model=CompanyRegisterOut)
async def register_company(company_data: CompanyRegisterIn, db: Session = Depends(get_db)):
    from app.domain.company import Company
    try:
        existing_company = db.query(Company).filter(Company.company_id == company_data.company_id).first()
        if existing_company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 기업 ID입니다.")
        hashed_password = get_password_hash(company_data.password)
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
            sourcelongitude=company_data.sourcelongitude,
        )
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        auth_logger.info(f"기업 회원가입 완료: {new_company.company_id}")
        return new_company
    except Exception as e:
        db.rollback()
        auth_logger.error(f"기업 회원가입 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="기업 회원가입 중 오류가 발생했습니다.")

@router.post("/register/user", response_model=UserRegisterOut)
async def register_user(user_data: UserRegisterIn, db: Session = Depends(get_db)):
    from app.domain.user import User
    from app.domain.company import Company
    try:
        company = db.query(Company).filter(Company.id == user_data.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="존재하지 않는 기업입니다.")
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="이미 존재하는 사용자명입니다.")
        hashed_password = get_password_hash(user_data.password)
        permissions = {
            "can_manage_users": user_data.can_manage_users,
            "can_view_reports": user_data.can_view_reports,
            "can_edit_data": user_data.can_edit_data,
            "can_export_data": user_data.can_export_data,
        }
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
            can_export_data=user_data.can_export_data,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        auth_logger.info(f"사용자 회원가입 완료: {new_user.username}")
        return new_user
    except Exception as e:
        db.rollback()
        auth_logger.error(f"사용자 회원가입 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 회원가입 중 오류가 발생했습니다.")

@router.post("/login", response_model=LoginOut)
async def login(login_data: LoginIn, db: Session = Depends(get_db)):
    from app.domain.user import User
    from app.domain.company import Company
    try:
        user = None
        user_type = None
        if login_data.user_type == "company":
            company = db.query(Company).filter(Company.company_id == login_data.username).first()
            if company and verify_password(login_data.password, company.hashed_password):
                user = company
                user_type = "company"
        elif login_data.user_type == "user":
            user_obj = db.query(User).filter(User.username == login_data.username).first()
            if user_obj and verify_password(login_data.password, user_obj.hashed_password):
                user = user_obj
                user_type = "user"
        else:
            company = db.query(Company).filter(Company.company_id == login_data.username).first()
            if company and verify_password(login_data.password, company.hashed_password):
                user = company
                user_type = "company"
            else:
                user_obj = db.query(User).filter(User.username == login_data.username).first()
                if user_obj and verify_password(login_data.password, user_obj.hashed_password):
                    user = user_obj
                    user_type = "user"
        if not user:
            raise HTTPException(status_code=401, detail="잘못된 로그인 정보입니다.")
        token_data = {
            "sub": str(user.id),
            "type": user_type,
            "username": user.company_id if user_type == "company" else user.username,
        }
        access_token = create_access_token(data=token_data)
        auth_logger.info(f"로그인 성공: {login_data.username} ({user_type})")
        return LoginOut(access_token=access_token, token_type="bearer", user_info=user)
    except Exception as e:
        auth_logger.error(f"로그인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다.")

@router.get("/me", response_model=Union[CompanyOut, UserOut])
async def get_current_user_info(current_user = Depends(get_current_user)):
    return current_user

@router.post("/countries/search", response_model=CountrySearchOut)
async def search_countries(search_data: CountrySearchIn, db: Session = Depends(get_db)):
    try:
        search_term = f"%{search_data.search_term}%"
        countries = db.query(Country).filter(Country.korean_name.ilike(search_term)).limit(20).all()
        return CountrySearchOut(countries=countries, total_count=len(countries))
    except Exception as e:
        raise HTTPException(status_code=500, detail="국가 검색 중 오류가 발생했습니다.")

@router.get("/countries", response_model=list[CountryOut])
async def get_all_countries(db: Session = Depends(get_db)):
    try:
        countries = db.query(Country).order_by(Country.korean_name).all()
        return countries
    except Exception as e:
        raise HTTPException(status_code=500, detail="국가 목록 조회 중 오류가 발생했습니다.")


