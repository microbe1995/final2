from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from datetime import datetime

# ===== Company (기업) 스키마 =====

class CompanyRegisterIn(BaseModel):
    """기업 회원가입 입력 스키마"""
    company_id: str
    password: str
    Installation: str
    Installation_en: Optional[str] = None
    economic_activity: Optional[str] = None
    economic_activity_en: Optional[str] = None
    representative: Optional[str] = None
    representative_en: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    street: Optional[str] = None
    street_en: Optional[str] = None
    number: Optional[str] = None
    number_en: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    city_en: Optional[str] = None
    country: Optional[str] = None
    country_en: Optional[str] = None
    unlocode: Optional[str] = None
    sourcelatitude: Optional[float] = None
    sourcelongitude: Optional[float] = None

class CompanyRegisterOut(BaseModel):
    """기업 회원가입 출력 스키마"""
    id: int
    uuid: str
    company_id: str
    Installation: str
    Installation_en: Optional[str] = None
    economic_activity: Optional[str] = None
    economic_activity_en: Optional[str] = None
    representative: Optional[str] = None
    representative_en: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    street: Optional[str] = None
    street_en: Optional[str] = None
    number: Optional[str] = None
    number_en: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    city_en: Optional[str] = None
    country: Optional[str] = None
    country_en: Optional[str] = None
    unlocode: Optional[str] = None
    sourcelatitude: Optional[float] = None
    sourcelongitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CompanyOut(BaseModel):
    """기업 정보 출력 스키마"""
    id: int
    uuid: str
    company_id: str
    Installation: str
    Installation_en: Optional[str] = None
    economic_activity: Optional[str] = None
    economic_activity_en: Optional[str] = None
    representative: Optional[str] = None
    representative_en: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    street: Optional[str] = None
    street_en: Optional[str] = None
    number: Optional[str] = None
    number_en: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    city_en: Optional[str] = None
    country: Optional[str] = None
    country_en: Optional[str] = None
    unlocode: Optional[str] = None
    sourcelatitude: Optional[float] = None
    sourcelongitude: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== User (사용자) 스키마 =====

class UserRegisterIn(BaseModel):
    """사용자 회원가입 입력 스키마"""
    username: str
    password: str
    full_name: str
    company_id: int
    role: str = "user"
    is_company_admin: bool = False
    can_manage_users: bool = False
    can_view_reports: bool = True
    can_edit_data: bool = True
    can_export_data: bool = True

class UserRegisterOut(BaseModel):
    """사용자 회원가입 출력 스키마"""
    id: int
    uuid: str
    username: str
    full_name: str
    company_id: int
    role: str
    is_company_admin: bool
    can_manage_users: bool
    can_view_reports: bool
    can_edit_data: bool
    can_export_data: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    """사용자 정보 출력 스키마"""
    id: int
    uuid: str
    username: str
    full_name: str
    company_id: int
    role: str
    is_company_admin: bool
    can_manage_users: bool
    can_view_reports: bool
    can_edit_data: bool
    can_export_data: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== 로그인 스키마 =====

class LoginIn(BaseModel):
    """로그인 입력 스키마"""
    username: str  # company_id 또는 username
    password: str
    user_type: str = "company"  # "company" 또는 "user"

class LoginOut(BaseModel):
    """로그인 출력 스키마"""
    access_token: str
    token_type: str = "bearer"
    user_info: Union[CompanyOut, UserOut]

# ===== 토큰 스키마 =====

class TokenOut(BaseModel):
    """토큰 출력 스키마"""
    access_token: str
    token_type: str = "bearer"
    user_info: Union[CompanyOut, UserOut]

# ===== 국가 검색 스키마 =====

class CountrySearchIn(BaseModel):
    """국가 검색 입력 스키마"""
    search_term: str

class CountryOut(BaseModel):
    """국가 정보 출력 스키마"""
    id: int
    uuid: str
    code: str
    country_name: str
    korean_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CountrySearchOut(BaseModel):
    """국가 검색 결과 스키마"""
    countries: list[CountryOut]
    total_count: int
