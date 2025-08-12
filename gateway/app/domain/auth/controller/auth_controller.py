import logging
import json
from typing import Dict, Any
from fastapi import HTTPException

from ..service.auth_service import AuthService
from ..model.auth_model import UserRegisterRequest, UserRegisterResponse

logger = logging.getLogger(__name__)

class AuthController:
    """인증 컨트롤러"""
    
    def __init__(self):
        self.auth_service = AuthService()
        logger.info("AuthController 초기화 완료")
    
    async def register_user(self, user_data: UserRegisterRequest) -> UserRegisterResponse:
        """사용자 회원가입 처리"""
        try:
            # 로깅: 컨트롤러에서 받은 요청 데이터
            logger.info(f"컨트롤러 회원가입 요청: {json.dumps(user_data.dict(), ensure_ascii=False)}")
            
            # 서비스 호출
            result = self.auth_service.register_user(user_data)
            
            # 로깅: 컨트롤러에서 반환하는 응답 데이터
            logger.info(f"컨트롤러 회원가입 응답: {json.dumps(result.dict(), ensure_ascii=False)}")
            
            return result
            
        except ValueError as ve:
            logger.error(f"컨트롤러 회원가입 검증 오류: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"컨트롤러 회원가입 처리 중 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="회원가입 처리 중 오류가 발생했습니다.")
    
    async def login_user(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 로그인 처리"""
        try:
            email = credentials.get('email')
            password = credentials.get('password')
            
            # 로깅: 로그인 요청 데이터 (비밀번호는 마스킹)
            masked_credentials = {**credentials, 'password': '***'}
            logger.info(f"컨트롤러 로그인 요청: {json.dumps(masked_credentials, ensure_ascii=False)}")
            
            if not email or not password:
                raise HTTPException(status_code=400, detail="이메일과 비밀번호를 입력해주세요.")
            
            # 서비스 호출
            result = self.auth_service.login_user(email, password)
            
            if not result:
                logger.warning(f"로그인 실패: {email}")
                raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
            
            # 로깅: 로그인 성공 응답 (민감한 정보는 마스킹)
            safe_result = {**result}
            if 'user' in safe_result and 'password_hash' in safe_result['user']:
                safe_result['user']['password_hash'] = '***'
            logger.info(f"컨트롤러 로그인 성공: {json.dumps(safe_result, ensure_ascii=False)}")
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"컨트롤러 로그인 처리 중 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="로그인 처리 중 오류가 발생했습니다.") 