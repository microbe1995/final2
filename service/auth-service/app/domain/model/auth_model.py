"""
인증 모델
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreateModel(BaseModel):
    """사용자 생성 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    username: str = Field(..., min_length=3, max_length=50, description="사용자명")
    password: str = Field(..., min_length=6, description="비밀번호")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "testuser",
                "password": "password123"
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
    is_active: bool = Field(..., description="활성 상태")
    created_at: datetime = Field(..., description="생성 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "testuser",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            }
        }


