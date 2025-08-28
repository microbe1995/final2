#!/usr/bin/env python3
"""
matdir API 엔드포인트 테스트
"""

import requests
import json
from decimal import Decimal

# 테스트 URL들
DIRECT_URL = "https://lcafinal-production.up.railway.app"
GATEWAY_URL = "https://gateway-production-da31.up.railway.app"

def test_matdir_create():
    """matdir 생성 API 테스트"""
    print("💾 matdir 생성 API 테스트")
    print("=" * 50)
    
    # 테스트 데이터
    payload = {
        "process_id": 101,  # 실제 존재하는 process_id
        "mat_name": "테스트 철광석",
        "mat_factor": 1.5,
        "mat_amount": 100.0,
        "oxyfactor": 1.0
    }
    
    # 직접 접근 테스트
    try:
        url = f"{DIRECT_URL}/matdir"
        print(f"📡 직접 접근: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 생성 성공!")
            print(f"📥 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 생성 실패!")
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 직접 접근 오류: {str(e)}")
    
    print()
    
    # Gateway 접근 테스트
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 Gateway 접근: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 생성 성공!")
            print(f"📥 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 생성 실패!")
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ Gateway 접근 오류: {str(e)}")

def test_matdir_list():
    """matdir 목록 조회 API 테스트"""
    print("\n📋 matdir 목록 조회 API 테스트")
    print("=" * 50)
    
    # 직접 접근 테스트
    try:
        url = f"{DIRECT_URL}/matdir"
        print(f"📡 직접 접근: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 조회 성공! 데이터 개수: {len(data)}개")
            for i, item in enumerate(data, 1):
                print(f"📊 데이터 {i}: ID {item.get('id')}, {item.get('mat_name')}, 배출량 {item.get('matdir_em')}")
        else:
            print(f"❌ 조회 실패!")
            print(f"📥 응답 내용: {response.text}")
            
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
            print(f"✅ 조회 성공! 데이터 개수: {len(data)}개")
            for i, item in enumerate(data, 1):
                print(f"📊 데이터 {i}: ID {item.get('id')}, {item.get('mat_name')}, 배출량 {item.get('matdir_em')}")
        else:
            print(f"❌ 조회 실패!")
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ Gateway 접근 오류: {str(e)}")

def test_matdir_calculate():
    """matdir 계산 API 테스트"""
    print("\n🧮 matdir 계산 API 테스트")
    print("=" * 50)
    
    # 테스트 데이터
    payload = {
        "mat_factor": 1.5,
        "mat_amount": 100.0,
        "oxyfactor": 1.0
    }
    
    # 직접 접근 테스트
    try:
        url = f"{DIRECT_URL}/matdir/calculate"
        print(f"📡 직접 접근: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 계산 성공!")
            print(f"📥 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 계산 실패!")
            print(f"📥 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 직접 접근 오류: {str(e)}")

if __name__ == "__main__":
    print("🚀 matdir API 테스트 시작")
    print()
    
    # 1. matdir 생성 테스트
    test_matdir_create()
    
    # 2. matdir 목록 조회 테스트
    test_matdir_list()
    
    # 3. matdir 계산 테스트
    test_matdir_calculate()
    
    print("\n✅ 모든 API 테스트 완료")
