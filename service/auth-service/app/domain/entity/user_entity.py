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
# 👤 사용자 엔티티
# ============================================================================

class User(BaseModel):
    """사용자 엔티티"""
    id: str = Field(..., description="사용자 고유 ID")
    email: str = Field(..., description="사용자 이메일 (고유 식별자)")
    full_name: str = Field(..., description="사용자 실명")
    password_hash: str = Field(..., description="해시된 비밀번호")
    is_active: bool = Field(default=True, description="계정 활성화 상태")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="계정 생성 시간")
    updated_at: Optional[datetime] = Field(None, description="정보 수정 시간")
    last_login: Optional[datetime] = Field(None, description="마지막 로그인 시간")
    
    def update_last_login(self):
        """마지막 로그인 시간 업데이트"""
        self.last_login = datetime.utcnow()

# ============================================================================
# 🔐 사용자 인증 정보 엔티티
# ============================================================================

class UserCredentials(BaseModel):
    """사용자 인증 정보 엔티티"""
    email: str = Field(..., description="사용자 이메일")
    password: str = Field(..., description="사용자 비밀번호")
