from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Chatbot Service",
    description="GreenSteel MSA 시스템의 챗봇 서비스",
    version="1.0.0"
)

@app.post("/chatbot/generate/")
async def generate_chatbot_response(request: Request):
    data = await request.json()
    prompt = data.get("prompt")
    # 실제 챗봇 로직은 여기에 구현 (예시: echo)
    result = f"챗봇 응답: {prompt}"
    return JSONResponse(content={"result": result})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002) 