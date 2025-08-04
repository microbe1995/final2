"""
Chatbot Service
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot Service",
    description="AI Chatbot Service",
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
        "service": "Chatbot Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    logger.info("🔍 Chatbot Service Health Check")
    return {"status": "Chatbot Service Healthy"}

@app.post("/chat")
async def chat():
    logger.info("💬 Chat request received")
    return {"message": "Chat endpoint", "status": "success"}

@app.post("/process")
async def process_message():
    logger.info("🤖 Message processing request received")
    return {"message": "Message processing endpoint", "status": "success"}

@app.get("/models")
async def get_models():
    logger.info("📋 Models list request received")
    return {"message": "Models endpoint", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port) 