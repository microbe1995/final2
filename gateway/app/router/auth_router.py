"""
Auth Router
"""
from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/health")
async def auth_health():
    return {"status": "auth service healthy"}
