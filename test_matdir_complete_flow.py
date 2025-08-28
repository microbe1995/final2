#!/usr/bin/env python3
"""
matdir 전체 플로우 테스트 (Gateway → cbam-service → DB)
"""

import requests
import json

# 테스트 URL들
GATEWAY_URL = "https://gateway-production-22ef.up.railway.app"

def test_matdir_complete_flow():
    """matdir 전체 플로우 테스트"""
    print("🚀 matdir 전체 플로우 테스트 시작")
    print("=" * 60)
    
    # 1. 계산 API 테스트
    print("\n1️⃣ 계산 API 테스트")
    print("-" * 30)
    
    calculate_payload = {
        "mat_amount": 100.0,
        "mat_factor": 1.5,
        "oxyfactor": 1.0
    }
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir/calculate"
        print(f"📡 URL: {url}")
        print(f"📤 요청 데이터: {json.dumps(calculate_payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=calculate_payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 계산 성공!")
            print(f"📊 계산 결과: {json.dumps(data, indent=2, ensure_ascii=False)}")
            calculated_emission = data.get('matdir_em', 0)
        else:
            print(f"❌ 계산 실패: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 계산 오류: {str(e)}")
        return
    
    # 2. DB 저장 테스트
    print("\n2️⃣ DB 저장 테스트")
    print("-" * 30)
    
    create_payload = {
        "process_id": 101,
        "mat_name": "전체 플로우 테스트 원료",
        "mat_factor": 1.5,
        "mat_amount": 100.0,
        "oxyfactor": 1.0,
        "matdir_em": calculated_emission
    }
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 URL: {url}")
        print(f"📤 요청 데이터: {json.dumps(create_payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=create_payload, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ DB 저장 성공!")
            print(f"📊 저장된 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
            saved_id = data.get('id')
        else:
            print(f"❌ DB 저장 실패: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ DB 저장 오류: {str(e)}")
        return
    
    # 3. 저장된 데이터 조회 테스트
    print("\n3️⃣ 저장된 데이터 조회 테스트")
    print("-" * 30)
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 조회 성공!")
            print(f"📊 총 데이터 개수: {len(data)}개")
            
            # 방금 저장한 데이터 찾기
            saved_data = None
            for item in data:
                if item.get('mat_name') == "전체 플로우 테스트 원료":
                    saved_data = item
                    break
            
            if saved_data:
                print(f"🆕 방금 저장한 데이터:")
                print(f"   - ID: {saved_data.get('id')}")
                print(f"   - 원료명: {saved_data.get('mat_name')}")
                print(f"   - 배출량: {saved_data.get('matdir_em')}")
                print(f"   - 생성일: {saved_data.get('created_at')}")
                print(f"✅ 전체 플로우 성공!")
            else:
                print(f"⚠️ 방금 저장한 데이터를 찾을 수 없습니다.")
        else:
            print(f"❌ 조회 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 조회 오류: {str(e)}")
    
    # 4. 공정별 데이터 조회 테스트
    print("\n4️⃣ 공정별 데이터 조회 테스트")
    print("-" * 30)
    
    try:
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir/process/101"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 공정별 조회 성공!")
            print(f"📊 공정 101의 데이터 개수: {len(data)}개")
            
            if data:
                print(f"📋 공정 101의 원료 목록:")
                for item in data:
                    print(f"   - {item.get('mat_name')}: {item.get('matdir_em')} tCO2e")
        else:
            print(f"❌ 공정별 조회 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 공정별 조회 오류: {str(e)}")

if __name__ == "__main__":
    test_matdir_complete_flow()
    print("\n🎉 전체 플로우 테스트 완료!")
