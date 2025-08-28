#!/usr/bin/env python3
"""
matdir 엔드포인트 수정 후 테스트
"""

import requests
import json

# 테스트 URL들
DIRECT_MATDIR_URL = "https://lcafinal-production.up.railway.app/matdir"
DIRECT_INSTALL_URL = "https://lcafinal-production.up.railway.app/install"
GATEWAY_MATDIR_URL = "https://gateway-production-da31.up.railway.app/api/v1/boundary/matdir"
GATEWAY_INSTALL_URL = "https://gateway-production-da31.up.railway.app/api/v1/boundary/install"

def test_direct_matdir():
    """직접 matdir 접근 테스트"""
    print("🔍 직접 matdir 접근 테스트")
    print("=" * 50)
    
    try:
        response = requests.get(DIRECT_MATDIR_URL, timeout=10)
        print(f"📡 URL: {DIRECT_MATDIR_URL}")
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"📥 응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_direct_install():
    """직접 install 접근 테스트"""
    print("\n🔍 직접 install 접근 테스트")
    print("=" * 50)
    
    try:
        response = requests.get(DIRECT_INSTALL_URL, timeout=10)
        print(f"📡 URL: {DIRECT_INSTALL_URL}")
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"📥 응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_gateway_matdir():
    """Gateway matdir 접근 테스트"""
    print("\n🌐 Gateway matdir 접근 테스트")
    print("=" * 50)
    
    try:
        response = requests.get(GATEWAY_MATDIR_URL, timeout=10)
        print(f"📡 URL: {GATEWAY_MATDIR_URL}")
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"📥 응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_gateway_install():
    """Gateway install 접근 테스트"""
    print("\n🌐 Gateway install 접근 테스트")
    print("=" * 50)
    
    try:
        response = requests.get(GATEWAY_INSTALL_URL, timeout=10)
        print(f"📡 URL: {GATEWAY_INSTALL_URL}")
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"📥 응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
        else:
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_matdir_create():
    """matdir 생성 테스트"""
    print("\n💾 matdir 생성 테스트")
    print("=" * 50)
    
    # 실제 존재하는 process_id 사용 (테스트 결과에서 확인된 값)
    payload = {
        "process_id": 101,  # 실제 존재하는 process_id
        "mat_name": "테스트 원료",
        "mat_factor": 1.5,
        "mat_amount": 100.0,
        "oxyfactor": 1.0
    }
    
    try:
        response = requests.post(DIRECT_MATDIR_URL, json=payload, timeout=10)
        print(f"📡 URL: {DIRECT_MATDIR_URL}")
        print(f"📤 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 생성 성공!")
            print(f"📥 응답 내용: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 생성 실패!")
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    print("🚀 matdir 엔드포인트 수정 후 테스트 시작")
    print()
    
    # 1. 직접 접근 테스트
    test_direct_install()
    test_direct_matdir()
    
    # 2. Gateway 접근 테스트
    test_gateway_install()
    test_gateway_matdir()
    
    # 3. matdir 생성 테스트
    test_matdir_create()
    
    print("\n✅ 테스트 완료")
