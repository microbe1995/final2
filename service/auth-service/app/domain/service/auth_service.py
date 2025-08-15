"""
인증 서비스 - 인증 비즈니스 로직
인증 서비스의 핵심 비즈니스 로직을 담당
"""
import logging
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.domain.entity.user_entity import User, UserCredentials
from app.domain.repository.user_repository import UserRepository
from app.domain.schema.auth_schema import UserRegistrationRequest, UserLoginRequest

# 로거 설정
logger = logging.getLogger(__name__)

class AuthService:
    """
    인증 서비스 클래스
    - 사용자 회원가입
    - 사용자 로그인
    - 비밀번호 해싱
    - 토큰 생성 및 검증
    """
    
    def __init__(self):
        """인증 서비스 초기화"""
        self.user_repository = UserRepository()
        self.secret_key = "your-secret-key-here"  # 실제로는 환경변수에서 가져와야 함
        
        logger.info("✅ 인증 서비스 초기화 완료")
    
    def _hash_password(self, password: str) -> str:
        """
        비밀번호 해싱
        
        Args:
            password: 원본 비밀번호
            
        Returns:
            해시된 비밀번호
        """
        # 실제로는 bcrypt나 argon2 사용 권장
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_token(self, user_id: str) -> str:
        """
        사용자 토큰 생성
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            생성된 토큰
        """
        # 실제로는 JWT 토큰 사용 권장
        token_data = f"{user_id}:{datetime.now().isoformat()}:{self.secret_key}"
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    async def register_user(self, registration_data: UserRegistrationRequest) -> Dict[str, Any]:
        """
        사용자 회원가입
        
        Args:
            registration_data: 회원가입 요청 데이터
            
        Returns:
            회원가입 결과
        """
        try:
            logger.info(f"🔐 회원가입 시작: {registration_data.email}")
            
            # 비밀번호 해싱
            hashed_password = self._hash_password(registration_data.password)
            
            # 사용자 엔티티 생성
            user = User(
                username=registration_data.username,
                email=registration_data.email,
                full_name=registration_data.full_name,
                password_hash=hashed_password
            )
            
            # 사용자 저장
            created_user = await self.user_repository.create_user(user)
            if not created_user:
                logger.error(f"❌ 사용자 생성 실패: {registration_data.email}")
                return {
                    "message": "회원가입 실패",
                    "error": "사용자 생성 중 오류가 발생했습니다",
                    "status": "error"
                }
            
            logger.info(f"✅ 회원가입 성공: {created_user.email}")
            
            return {
                "message": "회원가입 성공",
                "user": created_user.to_dict(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ 회원가입 실패: {str(e)}")
            return {
                "message": "회원가입 실패",
                "error": str(e),
                "status": "error"
            }
    
    async def login_user(self, login_data: UserLoginRequest) -> Dict[str, Any]:
        """
        사용자 로그인
        
        Args:
            login_data: 로그인 요청 데이터
            
        Returns:
            로그인 결과
        """
        try:
            logger.info(f"🔐 로그인 시작: {login_data.email}")
            
            # 사용자 인증 정보 생성
            credentials = UserCredentials(
                email=login_data.email,
                password=login_data.password
            )
            
            # 사용자 인증
            user = await self.user_repository.authenticate_user(credentials)
            if not user:
                logger.warning(f"❌ 로그인 실패: {login_data.email}")
                return {
                    "message": "로그인 실패",
                    "error": "이메일 또는 비밀번호가 올바르지 않습니다",
                    "status": "error"
                }
            
            # 토큰 생성
            token = self._generate_token(user.id)
            
            logger.info(f"✅ 로그인 성공: {user.email}")
            
            return {
                "message": "로그인 성공",
                "user": user.to_dict(),
                "token": token,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ 로그인 실패: {str(e)}")
            return {
                "message": "로그인 실패",
                "error": str(e),
                "status": "error"
            }
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        사용자 ID로 사용자 정보 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 정보 (있으면), None (없으면)
        """
        return await self.user_repository.get_user_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        이메일로 사용자 정보 조회
        
        Args:
            email: 이메일 주소
            
        Returns:
            사용자 정보 (있으면), None (없으면)
        """
        return await self.user_repository.get_user_by_email(email)
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """
        사용자 정보 업데이트
        
        Args:
            user_id: 사용자 ID
            update_data: 업데이트할 데이터
            
        Returns:
            업데이트된 사용자 정보 (성공 시), None (실패 시)
        """
        return await self.user_repository.update_user(user_id, update_data)
    
    async def delete_user(self, user_id: str) -> bool:
        """
        사용자 삭제
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            삭제 성공 여부
        """
        return await self.user_repository.delete_user(user_id)
    
    async def get_users_count(self) -> int:
        """
        등록된 사용자 수 조회
        
        Returns:
            사용자 수
        """
        return await self.user_repository.get_users_count()
    
    async def search_users(self, query: str) -> list:
        """
        사용자 검색
        
        Args:
            query: 검색 쿼리
            
        Returns:
            검색 결과 사용자 목록
        """
        return await self.user_repository.search_users(query)
    
    def validate_token(self, token: str) -> Optional[str]:
        """
        토큰 검증 (간단한 구현)
        
        Args:
            token: 검증할 토큰
            
        Returns:
            사용자 ID (유효한 경우), None (유효하지 않은 경우)
        """
        # 실제로는 JWT 토큰 검증 로직 구현
        # 현재는 간단한 구현
        try:
            # 토큰에서 사용자 ID 추출 (실제로는 더 복잡한 로직)
            if len(token) == 64:  # SHA256 해시 길이
                return "valid_user_id"  # 임시 구현
            return None
        except Exception:
            return None
