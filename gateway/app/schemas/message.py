from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MessageRequest(BaseModel):
    """메시지 요청 스키마"""
    message: str = Field(..., min_length=1, max_length=1000, description="전송할 메시지")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="메시지 생성 시간")
    user_id: Optional[str] = Field(None, description="사용자 ID (선택사항)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "안녕하세요! 이것은 테스트 메시지입니다.",
                "user_id": "user123"
            }
        }

class MessageResponse(BaseModel):
    """메시지 응답 스키마"""
    success: bool = Field(..., description="처리 성공 여부")
    message: str = Field(..., description="처리된 메시지")
    processed_at: datetime = Field(..., description="처리 시간")
    message_id: str = Field(..., description="메시지 ID")
    service_response: Optional[dict] = Field(None, description="서비스 응답 데이터")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "안녕하세요! 이것은 테스트 메시지입니다.",
                "processed_at": "2024-01-01T12:00:00",
                "message_id": "msg_123456789",
                "service_response": {
                    "status": "processed",
                    "log_entry": "메시지가 성공적으로 처리되었습니다."
                }
            }
        }

class MessageError(BaseModel):
    """메시지 에러 스키마"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    timestamp: datetime = Field(default_factory=datetime.now, description="에러 발생 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "메시지 처리 실패",
                "detail": "서비스 연결 오류",
                "timestamp": "2024-01-01T12:00:00"
            }
        } 