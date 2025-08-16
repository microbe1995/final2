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

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime

# ============================================================================
# 📝 회원가입 요청/응답 스키마
# ============================================================================

class UserRegistrationRequest(BaseModel):
    """
    사용자 회원가입 요청 스키마
    
    주요 속성:
    - username: 사용자명 (2-50자, 한글/영문/숫자/언더스코어)
    - email: 이메일 주소 (자동 검증)
    - password: 비밀번호 (6-100자)
    - confirm_password: 비밀번호 확인 (password와 일치해야 함)
    - full_name: 전체 이름 (2-100자)
    """
    username: str = Field(..., description="사용자명", min_length=2, max_length=50, pattern="^[가-힣a-zA-Z0-9_]+$")
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호", min_length=6, max_length=100)
    confirm_password: str = Field(..., description="비밀번호 확인")
    full_name: str = Field(..., description="전체 이름", min_length=2, max_length=100)
    
    @field_validator('confirm_password')
    @classmethod
    def validate_password_confirmation(cls, v, values):
        """비밀번호 확인 검증"""
        if 'password' in values.data and v != values.data['password']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """사용자명 검증 - 한글, 영문, 숫자, 언더스코어 허용"""
        if not v.replace('_', '').replace('-', '').replace(' ', '').isalnum() and not any(char in '가-힣' for char in v):
            raise ValueError('사용자명은 한글, 영문, 숫자, 언더스코어만 사용 가능합니다')
        return v

# ============================================================================
# 🔐 로그인 요청/응답 스키마
# ============================================================================

class UserLoginRequest(BaseModel):
    """
    사용자 로그인 요청 스키마
    
    주요 속성:
    - email: 이메일 주소 (자동 검증)
    - password: 비밀번호 (최소 1자)
    """
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호", min_length=1)

class UserRegistrationResponse(BaseModel):
    """
    사용자 회원가입 응답 스키마
    
    Attributes:
        message: 응답 메시지
        user: 생성된 사용자 정보
        status: 처리 상태
    """
    message: str = Field(..., description="응답 메시지")
    user: Dict[str, Any] = Field(..., description="생성된 사용자 정보")
    status: str = Field(..., description="처리 상태", pattern="^(success|error)$")

class UserLoginResponse(BaseModel):
    """
    사용자 로그인 응답 스키마
    
    Attributes:
        message: 응답 메시지
        user: 로그인된 사용자 정보
        token: 인증 토큰
        status: 처리 상태
    """
    message: str = Field(..., description="응답 메시지")
    user: Dict[str, Any] = Field(..., description="로그인된 사용자 정보")
    token: str = Field(..., description="인증 토큰")
    status: str = Field(..., description="처리 상태", pattern="^(success|error)$")

# ============================================================================
# 🚨 에러 응답 스키마
# ============================================================================

class ErrorResponse(BaseModel):
    """
    오류 응답 스키마
    
    주요 속성:
    - error: 오류 메시지
    - detail: 상세 오류 정보 (선택사항)
    - status_code: HTTP 상태 코드 (400-599)
    - timestamp: 오류 발생 시간 (자동 설정)
    """
    error: str = Field(..., description="오류 메시지")
    detail: Optional[str] = Field(default=None, description="상세 오류 정보")
    status_code: int = Field(..., description="HTTP 상태 코드", ge=400, le=599)
    timestamp: datetime = Field(default_factory=datetime.now, description="오류 발생 시간")
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class HealthResponse(BaseModel):
    """
    헬스 체크 응답 스키마
    
    Attributes:
        status: 서비스 상태
        service: 서비스명
        version: 서비스 버전
        timestamp: 체크 시간
    """
    status: str = Field(..., description="서비스 상태", pattern="^(healthy|unhealthy|error)$")
    service: str = Field(..., description="서비스명")
    version: str = Field(..., description="서비스 버전")
    timestamp: datetime = Field(default_factory=datetime.now, description="체크 시간")
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
