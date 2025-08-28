#!/usr/bin/env python3
"""
프로덕션 환경 라우팅 테스트 스크립트
Gateway를 통한 라우팅과 직접 접근을 비교 테스트
"""

import requests
import json
import time

# 프로덕션 환경 설정
PRODUCTION_GATEWAY_URL = "https://gateway-production-da31.up.railway.app"
PRODUCTION_CBAM_URL = "https://lcafinal-production.up.railway.app"

def test_direct_cbam_access():
    """cbam-service에 직접 접근 테스트"""
    print("🔍 CBAM Service 직접 접근 테스트")
    print("=" * 50)
    
    test_paths = [
        "/product",
        "/install", 
        "/process",
        "/matdir"
    ]
    
    for path in test_paths:
        try:
            url = f"{PRODUCTION_CBAM_URL}{path}"
            print(f"📡 테스트 경로: {path}")
            response = requests.get(url, timeout=10)
            print(f"📥 응답 상태: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"📥 응답 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
                print(f"📥 응답 내용 미리보기: {str(data)[:200]}...")
            else:
                print(f"📥 응답 내용: {response.text}")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
        print("-" * 30)

def test_gateway_routing():
    """Gateway를 통한 라우팅 테스트"""
    print("\n🌐 Gateway 라우팅 테스트")
    print("=" * 50)
    
    test_paths = [
        "/api/v1/boundary/product",
        "/api/v1/boundary/install",
        "/api/v1/boundary/process", 
        "/api/v1/boundary/matdir",
        "/api/v1/cal-boundary/product",
        "/api/v1/cal_boundary/product"
    ]
    
    for path in test_paths:
        try:
            url = f"{PRODUCTION_GATEWAY_URL}{path}"
            print(f"📡 테스트 경로: {path}")
            response = requests.get(url, timeout=10)
            print(f"📥 응답 상태: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"📥 응답 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
                print(f"📥 응답 내용 미리보기: {str(data)[:200]}...")
            else:
                print(f"📥 응답 내용: {response.text}")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
        print("-" * 30)

def test_gateway_health():
    """Gateway 헬스체크"""
    print("\n🏥 Gateway 헬스체크")
    print("=" * 50)
    
    try:
        url = f"{PRODUCTION_GATEWAY_URL}/health"
        print(f"📡 헬스체크 URL: {url}")
        response = requests.get(url, timeout=10)
        print(f"📥 응답 상태: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📥 Gateway 상태: {data}")
        else:
            print(f"📥 응답 내용: {response.text}")
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def compare_responses():
    """직접 접근과 Gateway 접근 결과 비교"""
    print("\n🔄 응답 비교 테스트")
    print("=" * 50)
    
    # 제품 데이터 비교
    try:
        # 직접 접근
        direct_url = f"{PRODUCTION_CBAM_URL}/product"
        direct_response = requests.get(direct_url, timeout=10)
        direct_data = direct_response.json() if direct_response.status_code == 200 else None
        
        # Gateway 접근
        gateway_url = f"{PRODUCTION_GATEWAY_URL}/api/v1/boundary/product"
        gateway_response = requests.get(gateway_url, timeout=10)
        gateway_data = gateway_response.json() if gateway_response.status_code == 200 else None
        
        print(f"📡 직접 접근: {direct_url}")
        print(f"📥 상태: {direct_response.status_code}")
        print(f"📥 데이터 개수: {len(direct_data) if direct_data else 'N/A'}")
        
        print(f"\n📡 Gateway 접근: {gateway_url}")
        print(f"📥 상태: {gateway_response.status_code}")
        print(f"📥 데이터 개수: {len(gateway_data) if gateway_data else 'N/A'}")
        
        # 데이터 비교
        if direct_data and gateway_data:
            if len(direct_data) == len(gateway_data):
                print("\n✅ 데이터 개수 일치!")
                # 첫 번째 항목 비교
                if direct_data and gateway_data:
                    print(f"📊 직접 접근 첫 번째 항목: {direct_data[0]['id'] if direct_data else 'N/A'}")
                    print(f"📊 Gateway 접근 첫 번째 항목: {gateway_data[0]['id'] if gateway_data else 'N/A'}")
            else:
                print(f"\n❌ 데이터 개수 불일치: 직접={len(direct_data)}, Gateway={len(gateway_data)}")
        else:
            print("\n❌ 하나 이상의 응답이 실패했습니다.")
            
    except Exception as e:
        print(f"❌ 비교 테스트 오류: {str(e)}")

if __name__ == "__main__":
    print("🚀 프로덕션 환경 라우팅 테스트 시작")
    print(f"Gateway URL: {PRODUCTION_GATEWAY_URL}")
    print(f"CBAM Service URL: {PRODUCTION_CBAM_URL}")
    print()
    
    # 1. Gateway 헬스체크
    test_gateway_health()
    
    # 2. 직접 접근 테스트
    test_direct_cbam_access()
    
    # 3. Gateway 라우팅 테스트
    test_gateway_routing()
    
    # 4. 응답 비교
    compare_responses()
    
    print("\n✅ 테스트 완료")
