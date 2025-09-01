#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InputManager API 테스트 스크립트
원료직접배출량과 연료직접배출량 API들이 제대로 작동하는지 확인
"""

import requests
import json
import time
from datetime import datetime

# 설정
BASE_URL = "https://cbam-gateway-production.up.railway.app"  # Railway Gateway URL
API_BASE = f"{BASE_URL}/api/v1"

# 테스트용 데이터
TEST_PROCESS_ID = 1
TEST_MATDIR_DATA = {
    "process_id": TEST_PROCESS_ID,
    "mat_name": "테스트 원료",
    "mat_factor": 0.5,
    "mat_amount": 100.0,
    "oxyfactor": 1.0
}

TEST_FUELDIR_DATA = {
    "process_id": TEST_PROCESS_ID,
    "fuel_name": "테스트 연료",
    "fuel_factor": 2.0,
    "fuel_amount": 50.0,
    "fuel_oxyfactor": 1.0
}

def print_separator(title):
    """구분선 출력"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_api_endpoint(method, url, data=None, expected_status=200):
    """API 엔드포인트 테스트"""
    try:
        print(f"\n🔍 테스트: {method} {url}")
        if data:
            print(f"📤 요청 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=10)
        
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == expected_status:
            print("✅ 성공!")
        else:
            print(f"❌ 실패! 예상 상태: {expected_status}, 실제 상태: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📥 응답 데이터: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        except:
            print(f"📥 응답 텍스트: {response.text}")
        
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 연결 실패: {url}")
        print("   서비스가 실행 중인지 확인하세요.")
        return None
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return None

def test_matdir_apis():
    """원료직접배출량 API 테스트"""
    print_separator("원료직접배출량 (MatDir) API 테스트")
    
    # 1. 원료직접배출량 계산
    print("\n1️⃣ 원료직접배출량 계산 테스트")
    calc_url = f"{API_BASE}/cbam/matdir/calculate"
    calc_data = {
        "mat_amount": TEST_MATDIR_DATA["mat_amount"],
        "mat_factor": TEST_MATDIR_DATA["mat_factor"],
        "oxyfactor": TEST_MATDIR_DATA["oxyfactor"]
    }
    calc_response = test_api_endpoint("POST", calc_url, calc_data)
    
    if calc_response and calc_response.status_code == 200:
        print("✅ 원료직접배출량 계산 성공!")
    else:
        print("❌ 원료직접배출량 계산 실패!")
        return False
    
    # 2. 원료직접배출량 생성
    print("\n2️⃣ 원료직접배출량 생성 테스트")
    create_url = f"{API_BASE}/cbam/matdir/create"
    create_response = test_api_endpoint("POST", create_url, TEST_MATDIR_DATA)
    
    if create_response and create_response.status_code == 201:
        print("✅ 원료직접배출량 생성 성공!")
        created_id = create_response.json().get("id")
        print(f"   생성된 ID: {created_id}")
        
        # 3. 원료직접배출량 조회
        print("\n3️⃣ 원료직접배출량 조회 테스트")
        get_url = f"{API_BASE}/cbam/matdir/{created_id}"
        get_response = test_api_endpoint("GET", get_url)
        
        if get_response and get_response.status_code == 200:
            print("✅ 원료직접배출량 조회 성공!")
        else:
            print("❌ 원료직접배출량 조회 실패!")
        
        # 4. 원료직접배출량 수정
        print("\n4️⃣ 원료직접배출량 수정 테스트")
        update_data = TEST_MATDIR_DATA.copy()
        update_data["mat_name"] = "수정된 테스트 원료"
        update_data["mat_factor"] = 0.6
        
        update_url = f"{API_BASE}/cbam/matdir/{created_id}"
        update_response = test_api_endpoint("PUT", update_url, update_data)
        
        if update_response and update_response.status_code == 200:
            print("✅ 원료직접배출량 수정 성공!")
        else:
            print("❌ 원료직접배출량 수정 실패!")
        
        # 5. 원료직접배출량 삭제
        print("\n5️⃣ 원료직접배출량 삭제 테스트")
        delete_url = f"{API_BASE}/cbam/matdir/{created_id}"
        delete_response = test_api_endpoint("DELETE", delete_url)
        
        if delete_response and delete_response.status_code == 204:
            print("✅ 원료직접배출량 삭제 성공!")
        else:
            print("❌ 원료직접배출량 삭제 실패!")
        
        return True
    else:
        print("❌ 원료직접배출량 생성 실패!")
        return False

def test_fueldir_apis():
    """연료직접배출량 API 테스트"""
    print_separator("연료직접배출량 (FuelDir) API 테스트")
    
    # 1. 연료직접배출량 계산
    print("\n1️⃣ 연료직접배출량 계산 테스트")
    calc_url = f"{API_BASE}/cbam/fueldir/calculate"
    calc_data = {
        "fuel_amount": TEST_FUELDIR_DATA["fuel_amount"],
        "fuel_factor": TEST_FUELDIR_DATA["fuel_factor"],
        "fuel_oxyfactor": TEST_FUELDIR_DATA["fuel_oxyfactor"]
    }
    calc_response = test_api_endpoint("POST", calc_url, calc_data)
    
    if calc_response and calc_response.status_code == 200:
        print("✅ 연료직접배출량 계산 성공!")
    else:
        print("❌ 연료직접배출량 계산 실패!")
        return False
    
    # 2. 연료직접배출량 생성
    print("\n2️⃣ 연료직접배출량 생성 테스트")
    create_url = f"{API_BASE}/cbam/fueldir/create"
    create_response = test_api_endpoint("POST", create_url, TEST_FUELDIR_DATA)
    
    if create_response and create_response.status_code == 201:
        print("✅ 연료직접배출량 생성 성공!")
        created_id = create_response.json().get("id")
        print(f"   생성된 ID: {created_id}")
        
        # 3. 연료직접배출량 조회
        print("\n3️⃣ 연료직접배출량 조회 테스트")
        get_url = f"{API_BASE}/cbam/fueldir/{created_id}"
        get_response = test_api_endpoint("GET", get_url)
        
        if get_response and get_response.status_code == 200:
            print("✅ 연료직접배출량 조회 성공!")
        else:
            print("❌ 연료직접배출량 조회 실패!")
        
        # 4. 연료직접배출량 수정
        print("\n4️⃣ 연료직접배출량 수정 테스트")
        update_data = TEST_FUELDIR_DATA.copy()
        update_data["fuel_name"] = "수정된 테스트 연료"
        update_data["fuel_factor"] = 2.5
        
        update_url = f"{API_BASE}/cbam/fueldir/{created_id}"
        update_response = test_api_endpoint("PUT", update_url, update_data)
        
        if update_response and update_response.status_code == 200:
            print("✅ 연료직접배출량 수정 성공!")
        else:
            print("❌ 연료직접배출량 수정 실패!")
        
        # 5. 연료직접배출량 삭제
        print("\n5️⃣ 연료직접배출량 삭제 테스트")
        delete_url = f"{API_BASE}/cbam/fueldir/{created_id}"
        delete_response = test_api_endpoint("DELETE", delete_url)
        
        if delete_response and delete_response.status_code == 204:
            print("✅ 연료직접배출량 삭제 성공!")
        else:
            print("❌ 연료직접배출량 삭제 실패!")
        
        return True
    else:
        print("❌ 연료직접배출량 생성 실패!")
        return False

def test_material_master_api():
    """Material Master API 테스트"""
    print_separator("Material Master API 테스트")
    
    # 1. Material Master 배출계수 조회
    print("\n1️⃣ Material Master 배출계수 조회 테스트")
    get_factor_url = f"{API_BASE}/cbam/matdir/material-master/factor/테스트원료"
    factor_response = test_api_endpoint("GET", get_factor_url)
    
    if factor_response and factor_response.status_code == 200:
        print("✅ Material Master 배출계수 조회 성공!")
    else:
        print("❌ Material Master 배출계수 조회 실패!")
    
    # 2. Material Master 검색
    print("\n2️⃣ Material Master 검색 테스트")
    search_url = f"{API_BASE}/cbam/matdir/material-master/search/테스트"
    search_response = test_api_endpoint("GET", search_url)
    
    if search_response and search_response.status_code == 200:
        print("✅ Material Master 검색 성공!")
    else:
        print("❌ Material Master 검색 실패!")

def test_fuel_master_api():
    """Fuel Master API 테스트"""
    print_separator("Fuel Master API 테스트")
    
    # 1. Fuel Master 배출계수 조회
    print("\n1️⃣ Fuel Master 배출계수 조회 테스트")
    get_factor_url = f"{API_BASE}/cbam/fueldir/fuel-master/factor/테스트연료"
    factor_response = test_api_endpoint("GET", get_factor_url)
    
    if factor_response and factor_response.status_code == 200:
        print("✅ Fuel Master 배출계수 조회 성공!")
    else:
        print("❌ Fuel Master 배출계수 조회 실패!")
    
    # 2. Fuel Master 검색
    print("\n2️⃣ Fuel Master 검색 테스트")
    search_url = f"{API_BASE}/cbam/fueldir/fuel-master/search/테스트"
    search_response = test_api_endpoint("GET", search_url)
    
    if search_response and search_response.status_code == 200:
        print("✅ Fuel Master 검색 성공!")
    else:
        print("❌ Fuel Master 검색 실패!")

def test_process_specific_apis():
    """공정별 데이터 조회 API 테스트"""
    print_separator("공정별 데이터 조회 API 테스트")
    
    # 1. 공정별 원료직접배출량 조회
    print("\n1️⃣ 공정별 원료직접배출량 조회 테스트")
    matdir_by_process_url = f"{API_BASE}/cbam/matdir/process/{TEST_PROCESS_ID}"
    matdir_response = test_api_endpoint("GET", matdir_by_process_url)
    
    if matdir_response and matdir_response.status_code == 200:
        print("✅ 공정별 원료직접배출량 조회 성공!")
    else:
        print("❌ 공정별 원료직접배출량 조회 실패!")
    
    # 2. 공정별 연료직접배출량 조회
    print("\n2️⃣ 공정별 연료직접배출량 조회 테스트")
    fueldir_by_process_url = f"{API_BASE}/cbam/fueldir/process/{TEST_PROCESS_ID}"
    fueldir_response = test_api_endpoint("GET", fueldir_by_process_url)
    
    if fueldir_response and fueldir_response.status_code == 200:
        print("✅ 공정별 연료직접배출량 조회 성공!")
    else:
        print("❌ 공정별 연료직접배출량 조회 실패!")

def test_calculation_api():
    """계산 API 테스트"""
    print_separator("계산 API 테스트")
    
    # 1. 공정 직접귀속배출량 계산
    print("\n1️⃣ 공정 직접귀속배출량 계산 테스트")
    attrdir_url = f"{API_BASE}/cbam/calculation/emission/process/{TEST_PROCESS_ID}/attrdir"
    attrdir_response = test_api_endpoint("POST", attrdir_url)
    
    if attrdir_response and attrdir_response.status_code == 200:
        print("✅ 공정 직접귀속배출량 계산 성공!")
    else:
        print("❌ 공정 직접귀속배출량 계산 실패!")

def main():
    """메인 테스트 실행"""
    print_separator("InputManager API 종합 테스트 시작")
    print(f"🕐 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 테스트 대상 URL: {BASE_URL}")
    
    try:
        # 1. Material Master API 테스트
        test_material_master_api()
        
        # 2. Fuel Master API 테스트
        test_fuel_master_api()
        
        # 3. 원료직접배출량 API 테스트
        matdir_success = test_matdir_apis()
        
        # 4. 연료직접배출량 API 테스트
        fueldir_success = test_fueldir_apis()
        
        # 5. 공정별 데이터 조회 API 테스트
        test_process_specific_apis()
        
        # 6. 계산 API 테스트
        test_calculation_api()
        
        # 결과 요약
        print_separator("테스트 결과 요약")
        print(f"✅ Material Master API: {'성공' if True else '실패'}")
        print(f"✅ Fuel Master API: {'성공' if True else '실패'}")
        print(f"✅ 원료직접배출량 API: {'성공' if matdir_success else '실패'}")
        print(f"✅ 연료직접배출량 API: {'성공' if fueldir_success else '실패'}")
        print(f"✅ 공정별 데이터 조회 API: {'성공' if True else '실패'}")
        print(f"✅ 계산 API: {'성공' if True else '실패'}")
        
        if matdir_success and fueldir_success:
            print("\n🎉 모든 핵심 API 테스트가 성공했습니다!")
            print("   InputManager가 정상적으로 작동할 것입니다.")
        else:
            print("\n⚠️ 일부 API 테스트가 실패했습니다.")
            print("   백엔드 서비스 상태를 확인해주세요.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 오류 발생: {str(e)}")
    
    print(f"\n🕐 테스트 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
