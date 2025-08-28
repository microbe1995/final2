import requests
import json

# API 엔드포인트 (제품 API와 동일한 패턴으로 테스트)
BASE_URL = "https://lcafinal-production.up.railway.app"

def test_different_paths():
    """다양한 경로로 matdir API 테스트"""
    
    # 테스트할 경로들
    test_paths = [
        "/api/matdir",
        "/api/v1/boundary/matdir", 
        "/api/v1/matdir",
        "/api/boundary/matdir",
        "/matdir",
        "/api/calculation/matdir"
    ]
    
    print("🔍 matdir API 올바른 경로 찾기")
    print("=" * 50)
    
    for path in test_paths:
        print(f"\n📡 테스트 경로: {path}")
        try:
            response = requests.get(f"{BASE_URL}{path}")
            print(f"📥 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ 성공! 올바른 경로: {path}")
                print(f"📥 응답 내용: {response.json()}")
                break
            elif response.status_code == 404:
                print("❌ 404 Not Found")
            else:
                print(f"📥 응답 내용: {response.json()}")
                
        except Exception as e:
            print(f"❌ 오류: {str(e)}")

def test_calculation_endpoints():
    """calculation 관련 엔드포인트 테스트"""
    print("\n🧮 calculation 엔드포인트 테스트")
    print("=" * 50)
    
    calc_paths = [
        "/api/v1/boundary/calc/material/calculate",
        "/api/v1/boundary/calc/fuel/calculate",
        "/api/v1/boundary/calc/electricity/calculate"
    ]
    
    for path in calc_paths:
        print(f"\n📡 테스트 경로: {path}")
        try:
            response = requests.get(f"{BASE_URL}{path}")
            print(f"📥 응답 상태: {response.status_code}")
            
            if response.status_code != 404:
                print(f"📥 응답 내용: {response.json()}")
                
        except Exception as e:
            print(f"❌ 오류: {str(e)}")

def test_working_endpoints():
    """작동하는 엔드포인트 확인"""
    print("\n✅ 작동하는 엔드포인트 확인")
    print("=" * 50)
    
    working_paths = [
        "/api/product",
        "/api/v1/boundary/product",
        "/api/v1/boundary/install",
        "/api/v1/boundary/process"
    ]
    
    for path in working_paths:
        print(f"\n📡 테스트 경로: {path}")
        try:
            response = requests.get(f"{BASE_URL}{path}")
            print(f"📥 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 정상 작동")
            else:
                print(f"📥 응답 내용: {response.json()}")
                
        except Exception as e:
            print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    test_working_endpoints()
    test_calculation_endpoints()
    test_different_paths()
