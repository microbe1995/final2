#!/usr/bin/env python3
"""
matdir 데이터 생성 테스트
"""

import requests
import json

# 테스트 URL
GATEWAY_URL = "https://gateway-production-22ef.up.railway.app"

def test_create_matdir():
    """matdir 데이터 생성 테스트"""
    print("🔍 matdir 데이터 생성 테스트")
    print("=" * 50)
    
    # 새로운 matdir 데이터
    payload = {
        "process_id": 101,
        "mat_name": "테스트 원료 (DB 저장 확인)",
        "mat_factor": 2.5,
        "mat_amount": 75.0,
        "oxyfactor": 1.2
    }
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 URL: {url}")
        print(f"📤 요청 데이터: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ matdir 데이터 생성 성공!")
            print(f"📊 생성된 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 생성된 데이터의 ID 확인
            if 'id' in data:
                print(f"🆔 생성된 ID: {data['id']}")
                print(f"💾 Railway PostgreSQL DB에 정상 저장됨")
            
        else:
            print(f"❌ matdir 데이터 생성 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_get_matdirs():
    """matdir 데이터 조회 테스트"""
    print("\n🔍 matdir 데이터 조회 테스트")
    print("=" * 50)
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ matdir 데이터 조회 성공!")
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
            print(f"❌ matdir 데이터 조회 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    print("🚀 matdir DB 저장 테스트 시작")
    print()
    
    # 1. matdir 데이터 생성
    test_create_matdir()
    
    # 2. matdir 데이터 조회
    test_get_matdirs()
    
    print("\n✅ DB 저장 테스트 완료")
