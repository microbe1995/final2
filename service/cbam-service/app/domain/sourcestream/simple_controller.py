from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sourcestream", tags=["SourceStream"])

@router.get("/health")
async def health_check():
    """sourcestream 헬스 체크"""
    logger.info("🏥 sourcestream 헬스 체크 API 호출")
    return {
        "status": "healthy",
        "service": "sourcestream",
        "message": "통합 공정 그룹 서비스가 정상적으로 작동 중입니다."
    }

@router.get("/test")
async def test_endpoint():
    """테스트 엔드포인트"""
    logger.info("🧪 sourcestream 테스트 API 호출")
    return {
        "message": "sourcestream 라우터가 정상적으로 등록되었습니다!",
        "status": "success"
    }
