import requests
import json

# 테스트용 API 엔드포인트
BASE_URL = "http://localhost:8001"  # CBAM 서비스 직접 접근

def test_install_delete():
    """사업장 삭제 기능 테스트"""
    
    try:
        print("🧪 사업장 삭제 기능 테스트 중...")
        
        # 1. 먼저 사업장 목록 조회
        print("\n📋 사업장 목록 조회:")
        response = requests.get(f"{BASE_URL}/install")
        
        if response.status_code == 200:
            installs = response.json()
            print(f"  ✅ 사업장 목록 조회 성공: {len(installs)}개")
            
            for install in installs:
                print(f"    - ID: {install['id']}, 이름: {install['install_name']}")
        e
            print(f"  ❌ 사업장 목록 조회 실패: {response.status_code}")
            return
        
        # 2. 첫 번째 사업장 삭제 테스트
        if installs:
            test_install_id = installs[0]['id']
            print(f"\n🗑️ 사업장 삭제 테스트 (ID: {test_install_id}):")
            
            response = requests.delete(f"{BASE_URL}/install/{test_install_id}")
            
            if response.status_code == 200:
                print(f"  ✅ 사업장 삭제 성공!")
                result = response.json()
                print(f"    결과: {result}")
            else:
                print(f"  ❌ 사업장 삭제 실패: {response.status_code}")
                print(f"    오류: {response.text}")
        else:
            print("\n⚠️ 테스트할 사업장이 없습니다.")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_install_delete()
