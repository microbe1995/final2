from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegisterRequest(BaseModel):
    """회원가입 요청 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., min_length=8, description="사용자 비밀번호")
    username: str = Field(..., min_length=2, max_length=50, description="사용자 이름")
    full_name: Optional[str] = Field(None, max_length=100, description="전체 이름")
    
class UserRegisterResponse(BaseModel):
    """회원가입 응답 모델"""
    id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    username: str = Field(..., description="사용자 이름")
    full_name: Optional[str] = Field(None, description="전체 이름")
    created_at: datetime = Field(..., description="생성 시간")
    message: str = Field(..., description="응답 메시지")

class UserLoginRequest(BaseModel):
    """로그인 요청 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="사용자 비밀번호")

class UserLoginResponse(BaseModel):
    """로그인 응답 모델"""
    access_token: str = Field(..., description="액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    user: dict = Field(..., description="사용자 정보") 