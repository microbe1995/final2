"""
사용자 엔티티 - 사용자 정보를 담는 데이터 모델
인증 서비스에서 관리하는 사용자 정보를 표현

주요 기능:
- 사용자 기본 정보 모델 (User)
- 사용자 인증 정보 모델 (UserCredentials)
- Pydantic 기반 데이터 검증
- 자동 타입 변환 및 직렬화
- 비밀번호 보안 (해시값만 저장)
- 타임스탬프 자동 관리
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# ============================================================================
# 👥 사용자 기본 정보 엔티티
# ============================================================================

class User(BaseModel):
    """
    사용자 엔티티
    
    주요 속성:
    - id: 사용자 고유 ID (UUID, 자동 생성)
    - username: 사용자명 (3-50자, 한글/영문/숫자/언더스코어)
    - email: 이메일 주소 (고유, 자동 검증)
    - full_name: 전체 이름 (2-100자)
    - password_hash: 암호화된 비밀번호 (해시값)
    - is_active: 계정 활성화 상태 (기본값: True)
    - created_at: 계정 생성 시간 (자동 설정)
    - updated_at: 정보 수정 시간 (자동 업데이트)
    - last_login: 마지막 로그인 시간
    """
    id: Optional[str] = Field(default=None, description="사용자 고유 ID")
    username: str = Field(..., description="사용자명", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="이메일 주소")
    full_name: str = Field(..., description="전체 이름", min_length=2, max_length=100)
    password_hash: str = Field(..., description="암호화된 비밀번호")
    is_active: bool = Field(default=True, description="계정 활성화 상태")
    created_at: datetime = Field(default_factory=datetime.now, description="계정 생성 시간")
    updated_at: Optional[datetime] = Field(default=None, description="정보 수정 시간")
    last_login: Optional[datetime] = Field(default=None, description="마지막 로그인 시간")
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환 (비밀번호 제외)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    def update_last_login(self):
        """마지막 로그인 시간 업데이트"""
        self.last_login = datetime.now()
    
    def update_modified_time(self):
        """수정 시간 업데이트"""
        self.updated_at = datetime.now()

# ============================================================================
# 🔐 사용자 인증 정보 엔티티
# ============================================================================

class UserCredentials(BaseModel):
    """
    사용자 인증 정보 엔티티
    
    주요 속성:
    - email: 이메일 주소 (자동 검증)
    - password: 비밀번호 (최소 6자)
    """
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호", min_length=6)
