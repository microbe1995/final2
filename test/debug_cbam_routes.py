#!/usr/bin/env python3
"""
CBAM 서비스 라우트 디버깅 스크립트
"""

import requests
import json

def debug_cbam_routes():
    """CBAM 서비스 라우트 디버깅"""
    print("🔍 CBAM 서비스 라우트 디버깅")
    print("=" * 50)
    
    base_url = "https://lcafinal-production.up.railway.app"
    
    # 1. 루트 경로 테스트
    print("\n1️⃣ 루트 경로 테스트")
    test_paths = ["/", "/health", "/docs", "/openapi.json"]
    
    for path in test_paths:
        try:
            response = requests.get(f"{base_url}{path}", timeout=10)
            print(f"   {path}: {response.status_code}")
            
            if response.status_code == 200:
                if path == "/":
                    try:
                        data = response.json()
                        print(f"     ✅ 루트 경로 응답: {data}")
                    except:
                        print(f"     ✅ 루트 경로 응답: {response.text[:100]}...")
                elif path == "/health":
                    try:
                        data = response.json()
                        print(f"     ✅ 헬스체크: {data.get('service', 'N/A')}")
                    except:
                        print(f"     ✅ 헬스체크 응답: {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"     ❌ 404 Not Found")
            else:
                print(f"     ⚠️ {response.status_code}")
                
        except Exception as e:
            print(f"   {path}: ❌ 오류 - {e}")
    
    # 2. Install 관련 경로 테스트
    print("\n2️⃣ Install 관련 경로 테스트")
    install_paths = ["/install", "/install/", "/install/names", "/install/debug/structure"]
    
    for path in install_paths:
        try:
            response = requests.get(f"{base_url}{path}", timeout=10)
            print(f"   {path}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"     ✅ 성공: {len(data)}개 항목")
                    else:
                        print(f"     ✅ 성공: {data}")
                except:
                    print(f"     ✅ 성공: {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"     ❌ 404 Not Found")
            else:
                print(f"     ⚠️ {response.status_code}")
                
        except Exception as e:
            print(f"   {path}: ❌ 오류 - {e}")
    
    # 3. 라우트 정보 확인
    print("\n3️⃣ 라우트 정보 확인")
    try:
        response = requests.get(f"{base_url}/debug/routes", timeout=10)
        print(f"   /debug/routes: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"     ✅ 총 {data.get('total_routes', 0)}개 라우트")
            
            # 루트 경로 확인
            root_routes = [r for r in data.get('all_routes', []) if r['path'] == '/']
            if root_routes:
                print(f"     ✅ 루트 경로 발견: {root_routes[0]}")
            else:
                print(f"     ❌ 루트 경로 없음")
            
            # Install 라우트 확인
            install_routes = data.get('install_routes', [])
            if install_routes:
                print(f"     ✅ Install 라우트: {len(install_routes)}개")
                for route in install_routes[:3]:
                    print(f"       - {route['path']} [{', '.join(route['methods'])}]")
            else:
                print(f"     ❌ Install 라우트 없음")
        else:
            print(f"     ❌ {response.status_code}")
            
    except Exception as e:
        print(f"   /debug/routes: ❌ 오류 - {e}")

if __name__ == "__main__":
    debug_cbam_routes()
    print("\n" + "=" * 50)
    print("🏁 디버깅 완료")
