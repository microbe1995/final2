from typing import Any, Optional, Dict
from pydantic import BaseModel

class StandardResponse(BaseModel):
    """표준 응답 모델"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: Optional[str] = None

class SuccessResponse(StandardResponse):
    """성공 응답 모델"""
    success: bool = True
    
    @classmethod
    def create(cls, data: Any = None, message: str = None):
        from datetime import datetime
        return cls(
            success=True,
            data=data,
            message=message,
            timestamp=datetime.utcnow().isoformat()
        )

class ErrorResponse(StandardResponse):
    """에러 응답 모델"""
    success: bool = False
    error: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(cls, error_code: str, message: str, status_code: int = None):
        from datetime import datetime
        return cls(
            success=False,
            error={
                "code": error_code,
                "message": message,
                "status_code": status_code
            },
            timestamp=datetime.utcnow().isoformat()
        )

def create_success_response(data: Any = None, message: str = None) -> Dict[str, Any]:
    """성공 응답 생성 헬퍼"""
    return SuccessResponse.create(data=data, message=message).dict()

def create_error_response(error_code: str, message: str, status_code: int = None) -> Dict[str, Any]:
    """에러 응답 생성 헬퍼"""
    return ErrorResponse.create(error_code=error_code, message=message, status_code=status_code).dict()
