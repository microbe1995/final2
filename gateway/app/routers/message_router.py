from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging

from ..schemas.message import MessageRequest, MessageResponse, MessageError
from ..services.message_service import MessageService

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/message-service", tags=["Message Service"])

# 서비스 인스턴스 생성
message_service = MessageService()

@router.post("/process", 
             response_model=MessageResponse,
             summary="메시지 처리",
             description="사용자가 입력한 메시지를 받아서 처리하고 로그를 출력합니다.")
async def process_message(message_request: MessageRequest):
    """
    메시지 처리 엔드포인트
    
    - **message**: 처리할 메시지 (필수)
    - **user_id**: 사용자 ID (선택사항)
    - **timestamp**: 메시지 생성 시간 (자동 생성)
    
    반환값:
    - **success**: 처리 성공 여부
    - **message**: 처리된 메시지
    - **processed_at**: 처리 완료 시간
    - **message_id**: 고유 메시지 ID
    - **service_response**: 서비스 응답 데이터
    """
    try:
        logger.info("🚀 GATEWAY: /message-service/process 엔드포인트 호출됨")
        
        # 메시지 처리
        response = await message_service.process_message(message_request)
        
        # 로그 요약 출력
        log_summary = message_service.generate_log_summary(message_request, response)
        print(log_summary)  # 터미널에 직접 출력
        
        return response
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
    except Exception as e:
        logger.error(f"❌ GATEWAY: 예상치 못한 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류가 발생했습니다: {str(e)}"
        )

@router.get("/health",
            summary="메시지 서비스 헬스 체크",
            description="메시지 서비스의 상태를 확인합니다.")
async def health_check():
    """메시지 서비스 헬스 체크"""
    try:
        logger.info("🏥 GATEWAY: 메시지 서비스 헬스 체크")
        
        # 간단한 헬스 체크 로직
        health_status = {
            "service": "message-service",
            "status": "healthy",
            "timestamp": "2024-01-01T12:00:00",
            "version": "1.0.0"
        }
        
        logger.info(f"✅ GATEWAY: 헬스 체크 성공 - {health_status}")
        return health_status
        
    except Exception as e:
        logger.error(f"❌ GATEWAY: 헬스 체크 실패 - {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"서비스 상태 확인 실패: {str(e)}"
        )

@router.get("/info",
            summary="메시지 서비스 정보",
            description="메시지 서비스의 상세 정보를 반환합니다.")
async def service_info():
    """메시지 서비스 정보"""
    info = {
        "service_name": "message-service",
        "description": "사용자 메시지 처리 서비스",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/message-service/process",
                "method": "POST",
                "description": "메시지 처리"
            },
            {
                "path": "/message-service/health",
                "method": "GET",
                "description": "헬스 체크"
            },
            {
                "path": "/message-service/info",
                "method": "GET",
                "description": "서비스 정보"
            }
        ],
        "features": [
            "메시지 검증",
            "JSON 스키마 바인딩",
            "터미널 로그 출력",
            "서비스 프록시",
            "에러 처리"
        ]
    }
    
    logger.info(f"ℹ️ GATEWAY: 서비스 정보 요청 - {info['service_name']}")
    return info 