"""
Message Service
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Message Service", version="1.0.0")

class MessageRequest(BaseModel):
    message: str
    timestamp: Optional[datetime] = None
    user_id: Optional[str] = "anonymous"

class MessageResponse(BaseModel):
    success: bool
    message_id: str
    processed_message: str
    processed_at: datetime

@app.get("/health")
async def health_check():
    return {"status": "Message Service Healthy"}

@app.post("/process")
async def process_message(request: MessageRequest):
    try:
        logger.info(f"📨 메시지 수신: {request.message}")
        logger.info(f"👤 사용자 ID: {request.user_id}")
        logger.info(f"⏰ 타임스탬프: {request.timestamp}")
        
        # 메시지 처리 (대문자 변환)
        processed_message = request.message.upper()
        
        # 응답 생성
        response = MessageResponse(
            success=True,
            message_id=f"msg_{datetime.now().timestamp()}",
            processed_message=processed_message,
            processed_at=datetime.now()
        )
        
        logger.info(f"✅ 메시지 처리 완료: {processed_message}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ 메시지 처리 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 