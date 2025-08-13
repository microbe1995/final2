"""
인증 모델
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreateModel(BaseModel):
    """사용자 생성 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    username: str = Field(..., min_length=2, max_length=50, description="사용자명")
    password: str = Field(..., min_length=8, description="비밀번호")
    full_name: Optional[str] = Field(None, max_length=100, description="전체 이름")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "testuser",
                "password": "password123",
                "full_name": "홍길동"
            }
        }

class UserLoginModel(BaseModel):
    """사용자 로그인 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }

class UserResponseModel(BaseModel):
    """사용자 응답 모델"""
    id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    username: str = Field(..., description="사용자명")
    full_name: Optional[str] = Field(None, description="전체 이름")
    is_active: bool = Field(..., description="활성 상태")
    created_at: datetime = Field(..., description="생성 시간")
    message: str = Field(..., description="응답 메시지")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "testuser",
                "full_name": "홍길동",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "message": "회원가입이 성공적으로 완료되었습니다."
            }
        }
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


