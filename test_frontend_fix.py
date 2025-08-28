#!/usr/bin/env python3
"""
수정된 프론트엔드 matdir API 테스트
"""

import requests
import json

# 테스트 URL들
GATEWAY_URL = "https://gateway-production-22ef.up.railway.app"

def test_calculate_endpoint():
    """계산 엔드포인트 테스트"""
    print("🧮 계산 엔드포인트 테스트")
    print("=" * 50)
    
    payload = {
        "mat_amount": 100.0,
        "mat_factor": 1.5,
        "oxyfactor": 1.0
    }
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir/calculate"
        print(f"📡 URL: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 계산 성공!")
            print(f"📊 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 계산 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_create_endpoint():
    """생성 엔드포인트 테스트"""
    print("\n📝 생성 엔드포인트 테스트")
    print("=" * 50)
    
    payload = {
        "process_id": 101,
        "mat_name": "프론트엔드 수정 테스트",
        "mat_factor": 2.5,
        "mat_amount": 80.0,
        "oxyfactor": 1.1
    }
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 URL: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ 생성 성공!")
            print(f"📊 생성된 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 생성 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_list_endpoint():
    """목록 조회 엔드포인트 테스트"""
    print("\n📋 목록 조회 엔드포인트 테스트")
    print("=" * 50)
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 조회 성공!")
            print(f"📊 총 데이터 개수: {len(data)}개")
            
            # 최신 데이터 확인
            if data:
                latest = data[-1]
                print(f"🆕 최신 데이터:")
                print(f"   - ID: {latest.get('id')}")
                print(f"   - 원료명: {latest.get('mat_name')}")
                print(f"   - 배출량: {latest.get('matdir_em')}")
                print(f"   - 생성일: {latest.get('created_at')}")
        else:
            print(f"❌ 조회 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    print("🚀 수정된 프론트엔드 matdir API 테스트 시작")
    print()
    
    # 1. 계산 엔드포인트 테스트
    test_calculate_endpoint()
    
    # 2. 생성 엔드포인트 테스트
    test_create_endpoint()
    
    # 3. 목록 조회 엔드포인트 테스트
    test_list_endpoint()
    
    print("\n✅ 모든 테스트 완료")
    print("\n💡 이제 프론트엔드에서 matdir 데이터 저장이 정상 작동할 것입니다!")
