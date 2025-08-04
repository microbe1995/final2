import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import httpx
from fastapi import HTTPException

from ..schemas.message import MessageRequest, MessageResponse, MessageError

# 로깅 설정
logger = logging.getLogger(__name__)

class MessageService:
    """메시지 처리 서비스"""
    
    def __init__(self):
        self.service_url = "http://localhost:8001"  # 메시지 서비스 URL
        self.timeout = 30.0
    
    async def process_message(self, message_request: MessageRequest) -> MessageResponse:
        """메시지 처리 메인 로직"""
        try:
            # 1. 로그 출력 - 요청 데이터
            logger.info("=" * 60)
            logger.info("🔵 GATEWAY: 메시지 처리 시작")
            logger.info(f"📥 받은 메시지: {message_request.message}")
            logger.info(f"⏰ 요청 시간: {message_request.timestamp}")
            logger.info(f"👤 사용자 ID: {message_request.user_id or 'N/A'}")
            logger.info("=" * 60)
            
            # 2. 메시지 검증
            self._validate_message(message_request)
            
            # 3. 메시지 서비스로 전송
            service_response = await self._send_to_message_service(message_request)
            
            # 4. 응답 생성
            response = MessageResponse(
                success=True,
                message=message_request.message,
                processed_at=datetime.now(),
                message_id=f"msg_{uuid.uuid4().hex[:12]}",
                service_response=service_response
            )
            
            # 5. 성공 로그 출력
            logger.info("=" * 60)
            logger.info("🟢 GATEWAY: 메시지 처리 완료")
            logger.info(f"✅ 처리 결과: {response.success}")
            logger.info(f"🆔 메시지 ID: {response.message_id}")
            logger.info(f"⏰ 처리 시간: {response.processed_at}")
            logger.info(f"📤 서비스 응답: {service_response}")
            logger.info("=" * 60)
            
            return response
            
        except Exception as e:
            # 에러 로그 출력
            logger.error("=" * 60)
            logger.error("🔴 GATEWAY: 메시지 처리 실패")
            logger.error(f"❌ 에러 메시지: {str(e)}")
            logger.error(f"📥 원본 메시지: {message_request.message}")
            logger.error("=" * 60)
            
            raise HTTPException(
                status_code=500,
                detail=f"메시지 처리 중 오류가 발생했습니다: {str(e)}"
            )
    
    def _validate_message(self, message_request: MessageRequest) -> None:
        """메시지 검증"""
        logger.info("🔍 GATEWAY: 메시지 검증 중...")
        
        if not message_request.message.strip():
            raise ValueError("메시지가 비어있습니다.")
        
        if len(message_request.message) > 1000:
            raise ValueError("메시지가 너무 깁니다 (최대 1000자).")
        
        logger.info("✅ GATEWAY: 메시지 검증 완료")
    
    async def _send_to_message_service(self, message_request: MessageRequest) -> Dict[str, Any]:
        """메시지 서비스로 전송"""
        logger.info("🚀 GATEWAY: 메시지 서비스로 전송 중...")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.service_url}/process",
                    json={
                        "message": message_request.message,
                        "timestamp": message_request.timestamp.isoformat(),
                        "user_id": message_request.user_id
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    service_data = response.json()
                    logger.info(f"✅ GATEWAY: 메시지 서비스 응답 성공")
                    logger.info(f"📊 서비스 데이터: {service_data}")
                    return service_data
                else:
                    logger.error(f"❌ GATEWAY: 메시지 서비스 응답 실패 - {response.status_code}")
                    logger.error(f"📄 응답 내용: {response.text}")
                    return {
                        "status": "error",
                        "error_code": response.status_code,
                        "error_message": response.text
                    }
                    
        except httpx.TimeoutException:
            logger.error("⏰ GATEWAY: 메시지 서비스 타임아웃")
            return {
                "status": "timeout",
                "error_message": "서비스 응답 시간 초과"
            }
        except httpx.ConnectError:
            logger.error("🔌 GATEWAY: 메시지 서비스 연결 실패")
            return {
                "status": "connection_error",
                "error_message": "서비스에 연결할 수 없습니다"
            }
        except Exception as e:
            logger.error(f"❌ GATEWAY: 메시지 서비스 전송 중 예외 발생: {str(e)}")
            return {
                "status": "exception",
                "error_message": str(e)
            }
    
    def generate_log_summary(self, message_request: MessageRequest, response: MessageResponse) -> str:
        """로그 요약 생성"""
        return f"""
{'='*80}
📋 GATEWAY 메시지 처리 요약
{'='*80}
📥 입력 메시지: {message_request.message}
⏰ 요청 시간: {message_request.timestamp}
👤 사용자 ID: {message_request.user_id or 'N/A'}
✅ 처리 성공: {response.success}
🆔 메시지 ID: {response.message_id}
⏰ 처리 완료: {response.processed_at}
📊 서비스 응답: {response.service_response}
{'='*80}
        """.strip() 