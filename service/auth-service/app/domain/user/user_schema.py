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
from datetime import datetime

# ============================================================================
# 👤 도메인 사용자 모델 (저장용)
# ============================================================================

class User(BaseModel):
	"""저장/조회에 사용하는 내부 도메인 사용자 모델"""
	id: str = Field(..., description="사용자 고유 ID")
	email: EmailStr = Field(..., description="사용자 이메일")
	full_name: str = Field(..., description="사용자 실명")
	password_hash: str = Field(..., description="해시된 비밀번호")
	is_active: bool = Field(default=True, description="계정 활성화 상태")
	created_at: datetime = Field(default_factory=datetime.utcnow, description="계정 생성 시간")
	updated_at: Optional[datetime] = Field(None, description="정보 수정 시간")
	last_login: Optional[datetime] = Field(None, description="마지막 로그인 시간")

# ============================================================================
# 📋 회원가입 스키마
# ============================================================================

class UserRegistrationRequest(BaseModel):
	"""회원가입 요청 스키마"""
	email: EmailStr = Field(..., description="사용자 이메일 (고유 식별자)")
	full_name: str = Field(..., min_length=2, max_length=100, description="사용자 실명")
	password: str = Field(..., min_length=6, description="비밀번호 (최소 6자)")
	confirm_password: str = Field(..., description="비밀번호 확인")
	
	@field_validator('full_name')
	@classmethod
	def validate_full_name(cls, v):
		"""실명 유효성 검증"""
		if not re.match(r'^[가-힣a-zA-Z\s]+$', v):
			raise ValueError("실명은 한글, 영문, 공백만 사용 가능합니다")
		return v
	
	@field_validator('confirm_password')
	@classmethod
	def validate_confirm_password(cls, v, values):
		"""비밀번호 확인 검증"""
		if 'password' in values.data and v != values.data['password']:
			raise ValueError("비밀번호가 일치하지 않습니다")
		return v

# ============================================================================
# 🔐 로그인 스키마
# ============================================================================

class UserCredentials(BaseModel):
	"""사용자 인증 정보 스키마"""
	email: EmailStr = Field(..., description="사용자 이메일")
	password: str = Field(..., description="사용자 비밀번호")

class UserLoginRequest(BaseModel):
	"""로그인 요청 스키마"""
	email: EmailStr = Field(..., description="사용자 이메일")
	password: str = Field(..., description="사용자 비밀번호")

# ============================================================================
# 📝 사용자 정보 수정 스키마
# ============================================================================

class UserUpdateRequest(BaseModel):
	"""사용자 정보 수정 요청 스키마"""
	full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="사용자 실명")
	
	@field_validator('full_name')
	@classmethod
	def validate_full_name(cls, v):
		"""실명 유효성 검증"""
		if v is not None and not re.match(r'^[가-힣a-zA-Z\s]+$', v):
			raise ValueError("실명은 한글, 영문, 공백만 사용 가능합니다")
		return v

# ============================================================================
# 🔑 비밀번호 변경 스키마
# ============================================================================

class PasswordChangeRequest(BaseModel):
	"""비밀번호 변경 요청 스키마"""
	current_password: str = Field(..., description="현재 비밀번호")
	new_password: str = Field(..., min_length=6, description="새 비밀번호 (최소 6자)")
	confirm_new_password: str = Field(..., description="새 비밀번호 확인")
	
	@field_validator('confirm_new_password')
	@classmethod
	def validate_confirm_new_password(cls, v, values):
		"""새 비밀번호 확인 검증"""
		if 'new_password' in values.data and v != values.data['new_password']:
			raise ValueError("새 비밀번호가 일치하지 않습니다")
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
	id: str = Field(..., description="사용자 고유 ID")
	email: str = Field(..., description="사용자 이메일")
	full_name: str = Field(..., description="사용자 실명")
	created_at: datetime = Field(..., description="계정 생성 시간")
	updated_at: Optional[datetime] = Field(None, description="정보 수정 시간")
	last_login: Optional[datetime] = Field(None, description="마지막 로그인 시간")

class AuthResponse(BaseModel):
	"""인증 응답 스키마"""
	user: UserResponse = Field(..., description="사용자 정보")
	token: str = Field(..., description="인증 토큰")

class MessageResponse(BaseModel):
	"""메시지 응답 스키마"""
	message: str = Field(..., description="응답 메시지")

# ============================================================================
# ❌ 에러 응답 스키마
# ============================================================================

class ErrorResponse(BaseModel):
	"""에러 응답 스키마"""
	detail: str = Field(..., description="에러 상세 내용")
