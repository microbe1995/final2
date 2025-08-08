#!/usr/bin/env python3
"""
Railway deployment script for Gateway and Auth Service
"""
import os
import sys
import subprocess
import threading
import time

def start_gateway():
    """Start Gateway service"""
    print("🚀 Starting Gateway service...")
    os.chdir("gateway/app")
    subprocess.run([sys.executable, "main.py"])

def start_auth_service():
    """Start Auth service"""
    print("🔐 Starting Auth service...")
    os.chdir("service/auth-service/app")
    subprocess.run([sys.executable, "main.py"])

def main():
    """Main function to start both services"""
    print("🌟 LCA Final - Starting Multiple Services on Railway")
    
    # Start Gateway in main thread (primary service)
    gateway_thread = threading.Thread(target=start_gateway)
    gateway_thread.daemon = True
    gateway_thread.start()
    
    # Wait a bit for gateway to start
    time.sleep(2)
    
    # Start Auth service in background
    auth_thread = threading.Thread(target=start_auth_service)
    auth_thread.daemon = True
    auth_thread.start()
    
    print("✅ Both services are starting...")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Shutting down services...")

if __name__ == "__main__":
    main()
