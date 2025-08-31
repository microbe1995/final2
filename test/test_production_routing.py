#!/usr/bin/env python3
"""
프로덕션 환경 라우팅 테스트 스크립트
Gateway를 통한 라우팅과 직접 접근을 비교 테스트
"""

import requests
import json
import time

# 테스트용 API 엔드포인트 - Gateway를 통해 접근
BASE_URL = "http://localhost:8080"  # Gateway 서비스

def test_production_routing():
    """프로덕션 라우팅 기능 테스트"""
    
    try:
        print("🧪 프로덕션 라우팅 기능 테스트 중...")
        
        # 테스트할 엔드포인트들
        endpoints = [
            "/api/v1/boundary/install",
            "/api/v1/boundary/product",
            "/api/v1/boundary/process",
            "/api/v1/boundary/edge",
            "/api/v1/boundary/mapping",
            "/api/v1/boundary/matdir",
            "/api/v1/boundary/fueldir",
            "/api/v1/boundary/processchain",
            "/api/v1/boundary/productprocess",
        ]
        
        for endpoint in endpoints:
            print(f"\n🔍 테스트: {endpoint}")
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ 성공: {len(data) if isinstance(data, list) else '데이터 있음'}")
                else:
                    print(f"  ❌ 실패: {response.status_code}")
            except Exception as e:
                print(f"  ❌ 오류: {e}")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_production_routing()
