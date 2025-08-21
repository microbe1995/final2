from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.common.logger import auth_logger

class StandardErrorResponse:
    """표준 에러 응답"""
    
    @staticmethod
    def create(status_code: int, message: str, error_code: str = None):
        return {
            "success": False,
            "error": {
                "code": error_code or f"HTTP_{status_code}",
                "message": message,
                "status_code": status_code
            }
        }

async def validation_exception_handler(request: Request, exc: ValidationError):
    """Pydantic 검증 에러 핸들러"""
    auth_logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content=StandardErrorResponse.create(
            status_code=422,
            message="입력 데이터 검증에 실패했습니다.",
            error_code="VALIDATION_ERROR"
        )
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 핸들러"""
    auth_logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardErrorResponse.create(
            status_code=exc.status_code,
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        )
    )

async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    auth_logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=StandardErrorResponse.create(
            status_code=500,
            message="서버 내부 오류가 발생했습니다.",
            error_code="INTERNAL_SERVER_ERROR"
        )
    )
