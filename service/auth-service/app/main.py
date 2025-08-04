"""
Auth Service
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service",
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

@app.get("/")
async def root():
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    logger.info("🔍 Auth Service Health Check")
    return {"status": "Auth Service Healthy"}

@app.post("/login")
async def login():
    logger.info("🔐 Login request received")
    return {"message": "Login endpoint", "status": "success"}

@app.post("/register")
async def register():
    logger.info("📝 Register request received")
    return {"message": "Register endpoint", "status": "success"}

@app.get("/verify")
async def verify_token():
    logger.info("🔍 Token verification request received")
    return {"message": "Token verification endpoint", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
