"""
인증 스키마 - 데이터 검증 및 직렬화
인증 서비스에서 사용되는 요청/응답 데이터 모델 정의

주요 기능:
- 회원가입 요청/응답 스키마
- 로그인 요청/응답 스키마
- 에러 응답 스키마
- 데이터 검증 및 유효성 검사
- Pydantic 기반 자동 직렬화
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re

# ============================================================================
# 📝 회원가입 스키마
# ============================================================================

class UserRegistrationRequest(BaseModel):
    """회원가입 요청 스키마"""
    username: str = Field(..., min_length=2, max_length=50, description="사용자명")
    email: EmailStr = Field(..., description="이메일 주소")
    full_name: Optional[str] = Field(None, max_length=100, description="전체 이름")
    password: str = Field(..., min_length=6, description="비밀번호")
    confirm_password: str = Field(..., description="비밀번호 확인")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """사용자명 유효성 검증 (한글, 영문, 숫자, 언더스코어 허용)"""
        if not re.match(r'^[가-힣a-zA-Z0-9_]+$', v):
            raise ValueError('사용자명은 한글, 영문, 숫자, 언더스코어만 사용 가능합니다')
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, v, info):
        """비밀번호 확인 검증"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v

# ============================================================================
# 🔐 로그인 스키마
# ============================================================================

class UserLoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호")

# ============================================================================
# ✏️ 회원 정보 수정 스키마
# ============================================================================

class UserUpdateRequest(BaseModel):
    """회원 정보 수정 요청 스키마"""
    username: Optional[str] = Field(None, min_length=2, max_length=50, description="사용자명")
    full_name: Optional[str] = Field(None, max_length=100, description="전체 이름")
    current_password: str = Field(..., description="현재 비밀번호")
    new_password: Optional[str] = Field(None, min_length=6, description="새 비밀번호")
    confirm_new_password: Optional[str] = Field(None, description="새 비밀번호 확인")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """사용자명 유효성 검증 (한글, 영문, 숫자, 언더스코어 허용)"""
        if v is not None and not re.match(r'^[가-힣a-zA-Z0-9_]+$', v):
            raise ValueError('사용자명은 한글, 영문, 숫자, 언더스코어만 사용 가능합니다')
        return v
    
    @field_validator('confirm_new_password')
    @classmethod
    def validate_confirm_new_password(cls, v, info):
        """새 비밀번호 확인 검증"""
        if 'new_password' in info.data and info.data['new_password'] is not None:
            if v != info.data['new_password']:
                raise ValueError('새 비밀번호가 일치하지 않습니다')
        return v

class PasswordChangeRequest(BaseModel):
    """비밀번호 변경 요청 스키마"""
    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., min_length=6, description="새 비밀번호")
    confirm_new_password: str = Field(..., description="새 비밀번호 확인")
    
    @field_validator('confirm_new_password')
    @classmethod
    def validate_confirm_new_password(cls, v, info):
        """비밀번호 확인 검증"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('새 비밀번호가 일치하지 않습니다')
        return v

# ============================================================================
# 🗑️ 회원 탈퇴 스키마
# ============================================================================

class UserDeleteRequest(BaseModel):
    """회원 탈퇴 요청 스키마"""
    password: str = Field(..., description="계정 삭제를 위한 비밀번호 확인")

# ============================================================================
# 📤 응답 스키마
# ============================================================================

class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
    last_login: Optional[str]

class AuthResponse(BaseModel):
    """인증 응답 스키마"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    """메시지 응답 스키마"""
    message: str
    detail: Optional[str] = None

# ============================================================================
# ❌ 오류 응답 스키마
# ============================================================================

class ErrorResponse(BaseModel):
    """오류 응답 스키마"""
    detail: str
    error_code: Optional[str] = None
