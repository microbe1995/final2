import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Message Service",
    description="사용자 메시지 처리 마이크로서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델
class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    timestamp: str = Field(..., description="ISO 형식의 타임스탬프")
    user_id: str = Field(default="anonymous", description="사용자 ID")

class MessageResponse(BaseModel):
    status: str = Field(..., description="처리 상태")
    message_id: str = Field(..., description="메시지 ID")
    processed_message: str = Field(..., description="처리된 메시지")
    processed_at: str = Field(..., description="처리 시간")
    log_entry: str = Field(..., description="로그 항목")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "message-service",
        "version": "1.0.0",
        "status": "running",
        "description": "사용자 메시지 처리 서비스"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "service": "message-service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/process", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """
    메시지 처리 엔드포인트
    
    사용자가 입력한 메시지를 받아서 처리하고 로그를 출력합니다.
    """
    try:
        # 1. 요청 로그 출력
        logger.info("=" * 60)
        logger.info("🟡 MESSAGE-SERVICE: 메시지 처리 시작")
        logger.info(f"📥 받은 메시지: {request.message}")
        logger.info(f"⏰ 요청 시간: {request.timestamp}")
        logger.info(f"👤 사용자 ID: {request.user_id or 'N/A'}")
        logger.info("=" * 60)
        
        # 2. 메시지 검증
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
        
        if len(request.message) > 1000:
            raise HTTPException(status_code=400, detail="메시지가 너무 깁니다 (최대 1000자).")
        
        # 3. 메시지 처리 (간단한 예시)
        processed_message = request.message.upper()  # 대문자로 변환
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        processed_at = datetime.now().isoformat()
        
        # 4. 처리 로그 출력
        logger.info("🔄 MESSAGE-SERVICE: 메시지 처리 중...")
        logger.info(f"📝 원본 메시지: {request.message}")
        logger.info(f"✨ 처리된 메시지: {processed_message}")
        logger.info(f"🆔 메시지 ID: {message_id}")
        
        # 5. 로그 항목 생성
        log_entry = f"메시지 '{request.message}'가 성공적으로 처리되었습니다. (ID: {message_id})"
        
        # 6. 성공 로그 출력
        logger.info("=" * 60)
        logger.info("🟢 MESSAGE-SERVICE: 메시지 처리 완료")
        logger.info(f"✅ 처리 상태: success")
        logger.info(f"🆔 메시지 ID: {message_id}")
        logger.info(f"⏰ 처리 시간: {processed_at}")
        logger.info(f"📝 로그 항목: {log_entry}")
        logger.info("=" * 60)
        
        # 7. 터미널에 직접 출력 (가시성을 위해)
        print("\n" + "="*80)
        print("🎯 MESSAGE SERVICE - 메시지 처리 완료")
        print("="*80)
        print(f"📥 입력 메시지: {request.message}")
        print(f"✨ 처리된 메시지: {processed_message}")
        print(f"🆔 메시지 ID: {message_id}")
        print(f"⏰ 처리 시간: {processed_at}")
        print(f"👤 사용자 ID: {request.user_id or 'N/A'}")
        print("="*80 + "\n")
        
        # 8. 응답 반환
        return MessageResponse(
            status="success",
            message_id=message_id,
            processed_message=processed_message,
            processed_at=processed_at,
            log_entry=log_entry
        )
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
    except Exception as e:
        # 예상치 못한 오류 처리
        logger.error("=" * 60)
        logger.error("🔴 MESSAGE-SERVICE: 메시지 처리 실패")
        logger.error(f"❌ 에러 메시지: {str(e)}")
        logger.error(f"📥 원본 메시지: {request.message}")
        logger.error("=" * 60)
        
        raise HTTPException(
            status_code=500,
            detail=f"메시지 처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/info")
async def service_info():
    """서비스 정보"""
    return {
        "service_name": "message-service",
        "description": "사용자 메시지 처리 마이크로서비스",
        "version": "1.0.0",
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "서비스 상태"
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "헬스 체크"
            },
            {
                "path": "/process",
                "method": "POST",
                "description": "메시지 처리"
            },
            {
                "path": "/info",
                "method": "GET",
                "description": "서비스 정보"
            }
        ],
        "features": [
            "메시지 검증",
            "메시지 처리 (대문자 변환)",
            "터미널 로그 출력",
            "고유 메시지 ID 생성",
            "에러 처리"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 MESSAGE-SERVICE: 서비스 시작 중...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info") 