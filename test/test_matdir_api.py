import requests
import json

# API 엔드포인트
BASE_URL = "https://lcafinal-production.up.railway.app"
MATDIR_CREATE_URL = f"{BASE_URL}/api/v1/boundary/matdir"
MATDIR_LIST_URL = f"{BASE_URL}/api/v1/boundary/matdir"
MATDIR_CALCULATE_URL = f"{BASE_URL}/api/v1/boundary/matdir/calculate"

def test_matdir_calculate():
    """원료직접배출량 계산 테스트"""
    print("🧮 원료직접배출량 계산 테스트")
    
    payload = {
        "mat_amount": 1.0,
        "mat_factor": 1.0,
        "oxyfactor": 1.0
    }
    
    try:
        response = requests.post(MATDIR_CALCULATE_URL, json=payload)
        print(f"📤 요청: {payload}")
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 내용: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 계산 성공!")
        else:
            print("❌ 계산 실패!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_matdir_create():
    """원료직접배출량 생성 테스트"""
    print("\n💾 원료직접배출량 생성 테스트")
    
    payload = {
        "process_id": 1,  # 실제 존재하는 process_id 사용
        "mat_name": "테스트 원료",
        "mat_factor": 1.0,
        "mat_amount": 1.0,
        "oxyfactor": 1.0
    }
    
    try:
        response = requests.post(MATDIR_CREATE_URL, json=payload)
        print(f"📤 요청: {payload}")
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 내용: {response.json()}")
        
        if response.status_code == 201:
            print("✅ 생성 성공!")
        else:
            print("❌ 생성 실패!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_matdir_list():
    """원료직접배출량 목록 조회 테스트"""
    print("\n📋 원료직접배출량 목록 조회 테스트")
    
    try:
        response = requests.get(MATDIR_LIST_URL)
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 내용: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 조회 성공!")
        else:
            print("❌ 조회 실패!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

def test_product_api():
    """제품 API 테스트 (참고용)"""
    print("\n🏭 제품 API 테스트 (참고용)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/product")
        print(f"📥 응답 상태: {response.status_code}")
        print(f"📥 응답 내용: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 제품 API 정상 작동!")
        else:
            print("❌ 제품 API 오류!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🚀 matdir API 테스트 시작")
    print("=" * 50)
    
    # 제품 API 테스트 (참고용)
    test_product_api()
    
    # matdir API 테스트
    test_matdir_calculate()
    test_matdir_create()
    test_matdir_list()
    
    print("\n" + "=" * 50)
    print("🏁 matdir API 테스트 완료")
