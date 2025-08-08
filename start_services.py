#!/usr/bin/env python3
"""
Railway deployment script for Gateway Service
"""
import os
import sys

def main():
    """Start Gateway service only"""
    print("🚀 Starting Gateway Service on Railway...")
    
    # Set environment variables
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["PYTHONPATH"] = "/app"
    
    gateway_port = int(os.getenv("PORT", "8080"))
    print(f"📡 Gateway will run on port {gateway_port}")
    
    # Change to gateway directory
    gateway_path = "gateway/app"
    if os.path.exists(gateway_path):
        os.chdir(gateway_path)
        print(f"✅ Changed to directory: {os.getcwd()}")
    else:
        print(f"❌ Gateway directory not found: {gateway_path}")
        sys.exit(1)
    
    # Start the FastAPI application directly using uvicorn
    try:
        import uvicorn
        print("🌟 Starting FastAPI Gateway with uvicorn...")
        uvicorn.run("main:app", host="0.0.0.0", port=gateway_port, log_level="info")
    except ImportError:
        print("❌ uvicorn not installed, trying python main.py...")
        os.system(f"python main.py")

if __name__ == "__main__":
    main()