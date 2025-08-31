#!/usr/bin/env python3
"""
🚀 빠른 CORS 테스트 스크립트
- 핵심 엔드포인트만 빠르게 테스트
- 간단한 결과 출력
"""

import requests
import time

def test_cors(gateway_url: str, endpoint: str, origin: str = None):
    """CORS 테스트 실행"""
    url = f"{gateway_url}{endpoint}"
    headers = {}
    
    if origin:
        headers["Origin"] = origin
    
    print(f"\n🔍 테스트: {endpoint}")
    print(f"   URL: {url}")
    print(f"   Origin: {origin or 'N/A'}")
    
    # OPTIONS 테스트
    try:
        print("   📡 OPTIONS 요청...")
        start_time = time.time()
        response = requests.options(url, headers=headers, timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ OPTIONS 성공: {response.status_code} ({response_time:.3f}초)")
            
            # CORS 헤더 확인
            cors_origin = response.headers.get("Access-Control-Allow-Origin")
            cors_methods = response.headers.get("Access-Control-Allow-Methods")
            print(f"   🌐 CORS Origin: {cors_origin}")
            print(f"   🌐 CORS Methods: {cors_methods}")
            
            # GET 테스트
            print("   📡 GET 요청...")
            get_response = requests.get(url, headers=headers, timeout=10)
            if get_response.status_code < 400:
                print(f"   ✅ GET 성공: {get_response.status_code}")
                if get_response.content:
                    print(f"   📊 응답 크기: {len(get_response.content)} bytes")
            else:
                print(f"   ❌ GET 실패: {get_response.status_code}")
                
        else:
            print(f"   ❌ OPTIONS 실패: {response.status_code} ({response_time:.3f}초)")
            if response.content:
                print(f"   📄 에러: {response.text[:100]}")
                
    except Exception as e:
        print(f"   💥 예외: {e}")

def main():
    """메인 실행"""
    print("🚀 빠른 CORS 테스트")
    print("=" * 40)
    
    # Gateway URL
    gateway_url = "https://gateway-production-22ef.up.railway.app"
    
    # 테스트할 엔드포인트들
    test_endpoints = [
        "/api/v1/boundary/install",
        "/health"
    ]
    
    # 테스트할 오리진들
    test_origins = [
        "https://lca-final.vercel.app",
        "http://localhost:3000",
        None
    ]
    
    print(f"🎯 Gateway: {gateway_url}")
    print(f"🔍 엔드포인트: {len(test_endpoints)}개")
    print(f"🌐 오리진: {len(test_origins)}개")
    
    # 각 엔드포인트와 오리진 조합으로 테스트
    for endpoint in test_endpoints:
        for origin in test_origins:
            test_cors(gateway_url, endpoint, origin)
    
    print("\n🎯 테스트 완료!")

if __name__ == "__main__":
    main()
