"""
사용자 모델 정의
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    """사용자 생성 요청 모델"""
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

class UserLogin(BaseModel):
    """사용자 로그인 요청 모델"""
    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }

class UserResponse(BaseModel):
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

class Token(BaseModel):
    """토큰 응답 모델"""
    access_token: str = Field(..., description="액세스 토큰")
    token_type: str = Field("bearer", description="토큰 타입")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class User(BaseModel):
    """사용자 데이터베이스 모델"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="사용자 ID")
    email: str = Field(..., description="사용자 이메일")
    username: str = Field(..., description="사용자명")
    hashed_password: str = Field(..., description="해시된 비밀번호")
    is_active: bool = Field(True, description="활성 상태")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="생성 시간")
    updated_at: Optional[datetime] = Field(None, description="수정 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "testuser",
                "hashed_password": "$2b$12$...",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": None
            }
        }
