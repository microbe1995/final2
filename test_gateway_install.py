#!/usr/bin/env python3
"""
Gateway를 통한 install 엔드포인트 테스트
"""

import requests
import json

# 테스트 URL들
DIRECT_URL = "https://lcafinal-production.up.railway.app/install"
GATEWAY_URL = "https://gateway-production-da31.up.railway.app/api/v1/boundary/install"

def test_direct_access():
    """직접 접근 테스트"""
    print("🔍 직접 접근 테스트")
    print("=" * 50)
    
    try:
        response = requests.get(DIRECT_URL, timeout=10)
        print(f"📡 URL: {DIRECT_URL}")
        print(f"📥 상태 코드: {response.status_code}")
        print(f"📥 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"📥 응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_gateway_access():
    """Gateway 접근 테스트"""
    print("\n🌐 Gateway 접근 테스트")
    print("=" * 50)
    
    try:
        response = requests.get(GATEWAY_URL, timeout=10)
        print(f"📡 URL: {GATEWAY_URL}")
        print(f"📥 상태 코드: {response.status_code}")
        print(f"📥 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"📥 응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_gateway_health():
    """Gateway 헬스체크"""
    print("\n🏥 Gateway 헬스체크")
    print("=" * 50)
    
    try:
        health_url = "https://gateway-production-da31.up.railway.app/health"
        response = requests.get(health_url, timeout=10)
        print(f"📡 URL: {health_url}")
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 Gateway 상태: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_other_endpoints():
    """다른 엔드포인트 테스트"""
    print("\n🧪 다른 엔드포인트 테스트")
    print("=" * 50)
    
    test_endpoints = [
        "https://lcafinal-production.up.railway.app/product",
        "https://gateway-production-da31.up.railway.app/api/v1/boundary/product",
        "https://lcafinal-production.up.railway.app/process",
        "https://gateway-production-da31.up.railway.app/api/v1/boundary/process"
    ]
    
    for url in test_endpoints:
        try:
            print(f"\n📡 테스트 URL: {url}")
            response = requests.get(url, timeout=10)
            print(f"📥 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                print(f"📥 응답 내용: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ 오류: {str(e)}")

def test_gateway_routing_logic():
    """Gateway 라우팅 로직 테스트"""
    print("\n🔧 Gateway 라우팅 로직 테스트")
    print("=" * 50)
    
    # 라우팅 로직 시뮬레이션
    original_path = "install"
    normalized_path = original_path
    
    print(f"📝 원본 경로: {original_path}")
    
    # 경로 정규화 시뮬레이션
    if normalized_path.startswith("api/"):
        normalized_path = normalized_path[4:]
        print(f"📝 api/ 제거 후: {normalized_path}")
    
    if normalized_path.startswith("v1/"):
        normalized_path = normalized_path[3:]
        print(f"📝 v1/ 제거 후: {normalized_path}")
    
    if normalized_path.startswith("boundary/"):
        normalized_path = normalized_path[9:]
        print(f"📝 boundary/ 제거 후: {normalized_path}")
    
    print(f"📝 최종 정규화된 경로: {normalized_path}")
    print(f"📝 최종 URL: https://lcafinal-production.up.railway.app/{normalized_path}")

if __name__ == "__main__":
    print("🚀 Gateway Install 엔드포인트 테스트 시작")
    print()
    
    # 1. Gateway 헬스체크
    test_gateway_health()
    
    # 2. 라우팅 로직 테스트
    test_gateway_routing_logic()
    
    # 3. 직접 접근 테스트
    test_direct_access()
    
    # 4. Gateway 접근 테스트
    test_gateway_access()
    
    # 5. 다른 엔드포인트 테스트
    test_other_endpoints()
    
    print("\n✅ 테스트 완료")
