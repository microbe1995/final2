"""
인증 서비스 - 인증 비즈니스 로직
인증 서비스의 핵심 비즈니스 로직을 담당

주요 기능:
- 사용자 회원가입 및 검증
- 사용자 로그인 및 인증
- 비밀번호 해싱 및 검증
- 토큰 생성 및 관리
- 사용자 정보 관리
- 에러 처리 및 로깅
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

import hashlib
import secrets
import logging
from datetime import datetime
from typing import Optional, Tuple
from app.domain.entity.user_entity import User
from app.domain.repository.user_repository import UserRepository
from app.domain.schema.auth_schema import UserRegistrationRequest, UserLoginRequest, UserUpdateRequest, PasswordChangeRequest, UserDeleteRequest

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🔐 인증 서비스 클래스
# ============================================================================

class AuthService:
    """
    인증 서비스
    
    주요 기능:
    - 사용자 회원가입
    - 사용자 로그인
    - 회원 정보 수정
    - 비밀번호 변경
    - 회원 탈퇴
    - 토큰 생성
    - 비밀번호 해싱
    """
    
    def __init__(self, user_repository: UserRepository):
        """인증 서비스 초기화"""
        self.user_repository = user_repository
        logger.info("✅ AuthService 초기화 완료")
    
    # ============================================================================
    # 🔐 사용자 인증 관련 메서드
    # ============================================================================
    
    async def register_user(self, request: UserRegistrationRequest) -> Tuple[User, str]:
        """
        사용자 회원가입
        
        Args:
            request: 회원가입 요청 데이터
            
        Returns:
            Tuple[User, str]: 생성된 사용자 정보와 액세스 토큰
            
        Raises:
            ValueError: 사용자명 또는 이메일이 이미 존재하는 경우
        """
        try:
            logger.info(f"🔐 회원가입 시작: {request.email}")
            
            # 기존 사용자 확인
            existing_user = await self.user_repository.get_user_by_username(request.username)
            if existing_user:
                raise ValueError(f"사용자명 '{request.username}'이 이미 존재합니다")
            
            existing_email = await self.user_repository.get_user_by_email(request.email)
            if existing_email:
                raise ValueError(f"이메일 '{request.email}'이 이미 존재합니다")
            
            # 비밀번호 해싱
            password_hash = self._hash_password(request.password)
            
            # 사용자 생성
            user = User(
                username=request.username,
                email=request.email,
                full_name=request.full_name,
                password_hash=password_hash
            )
            
            # 저장소에 저장
            created_user = await self.user_repository.create_user(user)
            
            # 액세스 토큰 생성
            token = self._generate_token()
            
            logger.info(f"✅ 회원가입 성공: {request.email}")
            return created_user, token
            
        except Exception as e:
            logger.error(f"❌ 회원가입 실패: {request.email} - {str(e)}")
            raise
    
    async def login_user(self, request: UserLoginRequest) -> Tuple[User, str]:
        """
        사용자 로그인
        
        Args:
            request: 로그인 요청 데이터
            
        Returns:
            Tuple[User, str]: 인증된 사용자 정보와 액세스 토큰
            
        Raises:
            ValueError: 이메일 또는 비밀번호가 잘못된 경우
        """
        try:
            logger.info(f"🔐 로그인 시작: {request.email}")
            
            # 사용자 조회
            user = await self.user_repository.get_user_by_email(request.email)
            if not user:
                raise ValueError("이메일 또는 비밀번호가 잘못되었습니다")
            
            # 비밀번호 검증
            if not await self.user_repository.authenticate_user(request.email, request.password):
                raise ValueError("이메일 또는 비밀번호가 잘못되었습니다")
            
            # 마지막 로그인 시간 업데이트
            user.update_last_login()
            await self.user_repository.update_user(user)
            
            # 액세스 토큰 생성
            token = self._generate_token()
            
            logger.info(f"✅ 로그인 성공: {request.email}")
            return user, token
            
        except Exception as e:
            logger.error(f"❌ 로그인 실패: {request.email} - {str(e)}")
            raise
    
    # ============================================================================
    # ✏️ 회원 정보 관리 메서드
    # ============================================================================
    
    async def update_user_info(self, user_id: str, request: UserUpdateRequest) -> User:
        """
        회원 정보 수정
        
        Args:
            user_id: 수정할 사용자 ID
            request: 수정 요청 데이터
            
        Returns:
            User: 수정된 사용자 정보
            
        Raises:
            ValueError: 현재 비밀번호가 잘못되었거나 사용자명이 이미 존재하는 경우
        """
        try:
            logger.info(f"✏️ 회원 정보 수정 시작: {user_id}")
            
            # 사용자 조회
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다")
            
            # 현재 비밀번호 확인
            if not await self.user_repository.authenticate_user(user.email, request.current_password):
                raise ValueError("현재 비밀번호가 잘못되었습니다")
            
            # 사용자명 중복 확인 (변경하려는 경우)
            if request.username and request.username != user.username:
                existing_user = await self.user_repository.get_user_by_username(request.username)
                if existing_user:
                    raise ValueError(f"사용자명 '{request.username}'이 이미 존재합니다")
                user.username = request.username
            
            # 전체 이름 업데이트
            if request.full_name is not None:
                user.full_name = request.full_name
            
            # 새 비밀번호 설정 (제공된 경우)
            if request.new_password:
                user.password_hash = self._hash_password(request.new_password)
            
            # 사용자 정보 업데이트
            updated_user = await self.user_repository.update_user(user)
            
            logger.info(f"✅ 회원 정보 수정 성공: {user.email}")
            return updated_user
            
        except Exception as e:
            logger.error(f"❌ 회원 정보 수정 실패: {user_id} - {str(e)}")
            raise
    
    async def change_password(self, user_id: str, request: PasswordChangeRequest) -> User:
        """
        비밀번호 변경
        
        Args:
            user_id: 비밀번호를 변경할 사용자 ID
            request: 비밀번호 변경 요청 데이터
            
        Returns:
            User: 업데이트된 사용자 정보
            
        Raises:
            ValueError: 현재 비밀번호가 잘못된 경우
        """
        try:
            logger.info(f"🔑 비밀번호 변경 시작: {user_id}")
            
            # 사용자 조회
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다")
            
            # 현재 비밀번호 확인
            if not await self.user_repository.authenticate_user(user.email, request.current_password):
                raise ValueError("현재 비밀번호가 잘못되었습니다")
            
            # 새 비밀번호 설정
            user.password_hash = self._hash_password(request.new_password)
            
            # 사용자 정보 업데이트
            updated_user = await self.user_repository.update_user(user)
            
            logger.info(f"✅ 비밀번호 변경 성공: {user_id}")
            return updated_user
            
        except Exception as e:
            logger.error(f"❌ 비밀번호 변경 실패: {user_id} - {str(e)}")
            raise
    
    # ============================================================================
    # 🗑️ 회원 탈퇴 메서드
    # ============================================================================
    
    async def delete_user(self, user_id: str, request: UserDeleteRequest) -> bool:
        """
        회원 탈퇴
        
        Args:
            user_id: 탈퇴할 사용자 ID
            request: 탈퇴 요청 데이터
            
        Returns:
            bool: 탈퇴 성공 여부
            
        Raises:
            ValueError: 비밀번호가 잘못된 경우
        """
        try:
            logger.info(f"🗑️ 회원 탈퇴 시작: {user_id}")
            
            # 사용자 조회
            user = await self.user_repository.get_user_by_id(user_id)
            if not user:
                raise ValueError("사용자를 찾을 수 없습니다")
            
            # 비밀번호 확인
            if not await self.user_repository.authenticate_user(user.email, request.password):
                raise ValueError("비밀번호가 잘못되었습니다")
            
            # 사용자 삭제
            result = await self.user_repository.delete_user(user_id)
            
            logger.info(f"✅ 회원 탈퇴 성공: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 회원 탈퇴 실패: {user_id} - {str(e)}")
            raise
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    def _hash_password(self, password: str) -> str:
        """
        비밀번호 해싱 (SHA256)
        
        Args:
            password: 원본 비밀번호
            
        Returns:
            str: 해시된 비밀번호
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_token(self) -> str:
        """
        액세스 토큰 생성
        
        Returns:
            str: 생성된 토큰
        """
        return secrets.token_urlsafe(32)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        사용자 ID로 사용자 조회
        
        Args:
            user_id: 조회할 사용자 ID
            
        Returns:
            Optional[User]: 사용자 정보 또는 None
        """
        return await self.user_repository.get_user_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자 조회
        
        Args:
            email: 조회할 이메일
            
        Returns:
            Optional[User]: 사용자 정보 또는 None
        """
        return await self.user_repository.get_user_by_email(email)
