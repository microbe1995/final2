#!/usr/bin/env python3
"""
matdir 라우팅 테스트 스크립트
Gateway를 통한 라우팅이 올바르게 작동하는지 확인
"""

import requests
import json
import time

# 테스트 설정
GATEWAY_URL = "http://localhost:8080"
CBAM_SERVICE_URL = "http://localhost:8001"

def test_direct_cbam_service():
    """cbam-service에 직접 접근 테스트"""
    print("🔍 CBAM Service 직접 접근 테스트")
    print("=" * 50)
    
    test_paths = [
        "/matdir",
        "/install",
        "/product",
        "/process"
    ]
    
    for path in test_paths:
        try:
            url = f"{CBAM_SERVICE_URL}{path}"
            print(f"📡 테스트 경로: {path}")
            response = requests.get(url, timeout=5)
            print(f"📥 응답 상태: {response.status_code}")
            print(f"📥 응답 내용: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
        print("-" * 30)

def test_gateway_routing():
    """Gateway를 통한 라우팅 테스트"""
    print("\n🌐 Gateway 라우팅 테스트")
    print("=" * 50)
    
    test_paths = [
        "/api/v1/boundary/matdir",
        "/api/v1/boundary/install",
        "/api/v1/boundary/product",
        "/api/v1/boundary/process",
        "/api/v1/cal-boundary/matdir",
        "/api/v1/cal_boundary/matdir"
    ]
    
    for path in test_paths:
        try:
            url = f"{GATEWAY_URL}{path}"
            print(f"📡 테스트 경로: {path}")
            response = requests.get(url, timeout=5)
            print(f"📥 응답 상태: {response.status_code}")
            if response.status_code == 200:
                print(f"📥 응답 내용: {response.text[:200]}...")
            else:
                print(f"📥 응답 내용: {response.text}")
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
        print("-" * 30)

def test_matdir_endpoints():
    """matdir 관련 엔드포인트 상세 테스트"""
    print("\n🧪 MatDir 엔드포인트 상세 테스트")
    print("=" * 50)
    
    # 먼저 공정 데이터가 있는지 확인
    try:
        process_url = f"{GATEWAY_URL}/api/v1/boundary/process"
        print(f"📡 공정 목록 조회: {process_url}")
        response = requests.get(process_url, timeout=5)
        print(f"📥 응답 상태: {response.status_code}")
        if response.status_code == 200:
            processes = response.json()
            print(f"📥 공정 개수: {len(processes)}")
            if processes:
                process_id = processes[0]['id']
                print(f"📥 첫 번째 공정 ID: {process_id}")
                
                # 해당 공정의 matdir 조회
                matdir_url = f"{GATEWAY_URL}/api/v1/boundary/matdir/process/{process_id}"
                print(f"📡 공정별 matdir 조회: {matdir_url}")
                matdir_response = requests.get(matdir_url, timeout=5)
                print(f"📥 응답 상태: {matdir_response.status_code}")
                print(f"📥 응답 내용: {matdir_response.text[:200]}...")
        else:
            print(f"📥 응답 내용: {response.text}")
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    print("🚀 MatDir 라우팅 테스트 시작")
    print(f"Gateway URL: {GATEWAY_URL}")
    print(f"CBAM Service URL: {CBAM_SERVICE_URL}")
    print()
    
    # 1. 직접 접근 테스트
    test_direct_cbam_service()
    
    # 2. Gateway 라우팅 테스트
    test_gateway_routing()
    
    # 3. MatDir 상세 테스트
    test_matdir_endpoints()
    
    print("\n✅ 테스트 완료")
