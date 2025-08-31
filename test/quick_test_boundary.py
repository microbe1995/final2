#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 Boundary 서비스 테스트 스크립트
- Gateway를 통해 boundary/install API가 작동하는지 빠르게 확인
"""

import requests
import json

def quick_test():
    """빠른 테스트 실행"""
    gateway_url = "https://gateway-production-22ef.up.railway.app"
    
    print("🚀 빠른 Boundary 서비스 테스트")
    print("=" * 50)
    
    # 1. Gateway 헬스 체크
    print("1️⃣ Gateway 헬스 체크...")
    try:
        response = requests.get(f"{gateway_url}/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Gateway 정상")
        else:
            print(f"   ❌ Gateway 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Gateway 연결 실패: {e}")
        return False
    
    # 2. Boundary Install API 테스트
    print("\n2️⃣ Boundary Install API 테스트...")
    try:
        response = requests.get(f"{gateway_url}/api/v1/boundary/install", timeout=15)
        print(f"   📡 엔드포인트: /api/v1/boundary/install")
        print(f"   📊 상태코드: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ 성공: {len(data)}개 사업장 반환")
                    if data:
                        print(f"   📋 첫 번째 사업장: {data[0].get('install_name', 'N/A')}")
                else:
                    print(f"   ✅ 성공: {type(data)} 타입 반환")
            except json.JSONDecodeError:
                print("   ⚠️  JSON 파싱 실패")
        elif response.status_code == 307:
            print("   ⚠️  307 리다이렉트 - 여전히 문제 존재")
            return False
        elif response.status_code == 404:
            print("   ❌ 404 Not Found - boundary 서비스 매핑 문제")
            return False
        else:
            print(f"   ❌ 예상치 못한 응답: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ API 호출 실패: {e}")
        return False
    
    # 3. Install Names API 테스트
    print("\n3️⃣ Install Names API 테스트...")
    try:
        response = requests.get(f"{gateway_url}/api/v1/boundary/install/names", timeout=15)
        print(f"   📡 엔드포인트: /api/v1/boundary/install/names")
        print(f"   📊 상태코드: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ 성공: {len(data)}개 사업장명 반환")
                else:
                    print(f"   ✅ 성공: {type(data)} 타입 반환")
            except json.JSONDecodeError:
                print("   ⚠️  JSON 파싱 실패")
        else:
            print(f"   ❌ 실패: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API 호출 실패: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 테스트 완료!")
    print("✅ 307 리다이렉트 문제가 해결되었다면 boundary/install API가 정상 작동할 것입니다.")
    
    return True

if __name__ == "__main__":
    quick_test()
