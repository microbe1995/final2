"""
Gateway Service Main Entry Point
Railway 배포를 위한 루트 레벨 main.py
"""
import sys
import os

# app 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# app.main에서 FastAPI 앱 import
from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
