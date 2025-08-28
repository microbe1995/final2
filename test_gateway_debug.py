#!/usr/bin/env python3
"""
Gateway 라우팅 디버깅 테스트
"""

import requests
import json

# 테스트 URL들
GATEWAY_URL = "https://gateway-production-da31.up.railway.app"
CBAM_URL = "https://lcafinal-production.up.railway.app"

def test_gateway_health():
    """Gateway 헬스 체크"""
    print("🔍 Gateway 헬스 체크")
    print("=" * 50)
    
    try:
        url = f"{GATEWAY_URL}/health"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gateway 정상 작동")
            print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Gateway 오류")
            print(f"📥 응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_gateway_routing():
    """Gateway 라우팅 테스트"""
    print("\n🔍 Gateway 라우팅 테스트")
    print("=" * 50)
    
    # 다양한 경로 패턴 테스트
    test_paths = [
        "/api/v1/boundary/matdir",
        "/api/v1/boundary/install", 
        "/api/v1/boundary/product",
        "/api/v1/boundary/process",
        "/v1/boundary/matdir",
        "/boundary/matdir",
        "/matdir"
    ]
    
    for path in test_paths:
        try:
            url = f"{GATEWAY_URL}{path}"
            print(f"📡 테스트 경로: {path}")
            
            response = requests.get(url, timeout=10)
            print(f"📥 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 성공!")
            elif response.status_code == 404:
                print(f"❌ 404 Not Found")
            else:
                print(f"⚠️ 기타 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
        
        print()

def test_direct_vs_gateway():
    """직접 접근 vs Gateway 접근 비교"""
    print("\n🔍 직접 접근 vs Gateway 접근 비교")
    print("=" * 50)
    
    # 직접 접근 테스트
    try:
        url = f"{CBAM_URL}/matdir"
        print(f"📡 직접 접근: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 직접 접근 성공: {len(data)}개 데이터")
        else:
            print(f"❌ 직접 접근 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 직접 접근 오류: {str(e)}")
    
    print()
    
    # Gateway 접근 테스트
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 Gateway 접근: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gateway 접근 성공: {len(data)}개 데이터")
        else:
            print(f"❌ Gateway 접근 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ Gateway 접근 오류: {str(e)}")

def test_gateway_post():
    """Gateway POST 요청 테스트"""
    print("\n🔍 Gateway POST 요청 테스트")
    print("=" * 50)
    
    payload = {
        "process_id": 101,
        "mat_name": "Gateway 테스트",
        "mat_factor": 2.0,
        "mat_amount": 50.0,
        "oxyfactor": 1.0
    }
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 URL: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ POST 성공!")
            print(f"📥 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ POST 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ POST 오류: {str(e)}")

if __name__ == "__main__":
    print("🚀 Gateway 라우팅 디버깅 테스트 시작")
    print()
    
    # 1. Gateway 헬스 체크
    test_gateway_health()
    
    # 2. Gateway 라우팅 테스트
    test_gateway_routing()
    
    # 3. 직접 접근 vs Gateway 접근 비교
    test_direct_vs_gateway()
    
    # 4. Gateway POST 요청 테스트
    test_gateway_post()
    
    print("\n✅ 모든 디버깅 테스트 완료")
