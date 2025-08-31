#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gateway Boundary 서비스 테스트 스크립트
- Gateway를 통해 boundary/install API가 제대로 작동하는지 테스트
- 307 리다이렉트 문제가 해결되었는지 확인
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class GatewayBoundaryTester:
    def __init__(self, gateway_url: str = "https://gateway-production-22ef.up.railway.app"):
        self.gateway_url = gateway_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GatewayBoundaryTester/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
    def test_gateway_health(self) -> bool:
        """Gateway 헬스 체크 테스트"""
        try:
            print("🔍 Gateway 헬스 체크 테스트...")
            response = self.session.get(f"{self.gateway_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Gateway 헬스 체크 성공: {data.get('status', 'unknown')}")
                print(f"   서비스: {data.get('service', 'unknown')}")
                print(f"   버전: {data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ Gateway 헬스 체크 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Gateway 헬스 체크 오류: {e}")
            return False
    
    def test_boundary_install_list(self) -> bool:
        """Boundary 서비스의 install 목록 조회 테스트"""
        try:
            print("\n🔍 Boundary Install 목록 조회 테스트...")
            
            # 테스트할 엔드포인트들
            endpoints = [
                "/api/v1/boundary/install",
                "/api/v1/boundary/install/",
                "/api/v1/boundary/install/names"
            ]
            
            for endpoint in endpoints:
                print(f"   📡 테스트: {endpoint}")
                
                start_time = time.time()
                response = self.session.get(f"{self.gateway_url}{endpoint}", timeout=15)
                response_time = time.time() - start_time
                
                print(f"      상태코드: {response.status_code}")
                print(f"      응답시간: {response_time:.3f}초")
                
                # 응답 헤더 확인
                if 'location' in response.headers:
                    print(f"      ⚠️  리다이렉트 감지: {response.headers['location']}")
                
                # 응답 내용 확인
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"      ✅ 성공: {len(data)}개 항목 반환")
                            if data and len(data) > 0:
                                print(f"      📋 첫 번째 항목: {data[0]}")
                        else:
                            print(f"      ✅ 성공: {type(data)} 타입 반환")
                    except json.JSONDecodeError:
                        print(f"      ⚠️  JSON 파싱 실패: {response.text[:100]}...")
                elif response.status_code == 404:
                    print(f"      ❌ 404 Not Found")
                elif response.status_code == 307:
                    print(f"      ⚠️  307 Temporary Redirect - 여전히 리다이렉트 문제 존재")
                else:
                    print(f"      ❌ 예상치 못한 상태코드: {response.status_code}")
                    print(f"      📄 응답 내용: {response.text[:200]}...")
                
                print()
                
            return True
            
        except Exception as e:
            print(f"❌ Boundary Install 테스트 오류: {e}")
            return False
    
    def test_direct_cbam_service(self) -> bool:
        """직접 CBAM 서비스 연결 테스트 (비교용)"""
        try:
            print("\n🔍 직접 CBAM 서비스 연결 테스트...")
            
            cbam_url = "https://lcafinal-production.up.railway.app"
            endpoints = [
                "/install",
                "/install/",
                "/install/names"
            ]
            
            for endpoint in endpoints:
                print(f"   📡 테스트: {endpoint}")
                
                start_time = time.time()
                response = self.session.get(f"{cbam_url}{endpoint}", timeout=15)
                response_time = time.time() - start_time
                
                print(f"      상태코드: {response.status_code}")
                print(f"      응답시간: {response_time:.3f}초")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"      ✅ 성공: {len(data)}개 항목 반환")
                        else:
                            print(f"      ✅ 성공: {type(data)} 타입 반환")
                    except json.JSONDecodeError:
                        print(f"      ⚠️  JSON 파싱 실패")
                else:
                    print(f"      ❌ 실패: {response.status_code}")
                
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ 직접 CBAM 서비스 테스트 오류: {e}")
            return False
    
    def test_gateway_routing(self) -> bool:
        """Gateway 라우팅 구조 테스트"""
        try:
            print("\n🔍 Gateway 라우팅 구조 테스트...")
            
            # 존재하지 않는 서비스 테스트
            print("   📡 존재하지 않는 서비스 테스트: /api/v1/nonexistent")
            response = self.session.get(f"{self.gateway_url}/api/v1/nonexistent", timeout=10)
            print(f"      상태코드: {response.status_code}")
            
            if response.status_code == 404:
                print("      ✅ 올바르게 404 반환")
            else:
                print(f"      ⚠️  예상치 못한 응답: {response.status_code}")
            
            # 빈 경로 테스트
            print("   📡 빈 경로 테스트: /api/v1/boundary")
            response = self.session.get(f"{self.gateway_url}/api/v1/boundary", timeout=10)
            print(f"      상태코드: {response.status_code}")
            
            print()
            return True
            
        except Exception as e:
            print(f"❌ Gateway 라우팅 테스트 오류: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """모든 테스트 실행"""
        print("🚀 Gateway Boundary 서비스 종합 테스트 시작")
        print("=" * 60)
        
        results = {}
        
        # 1. Gateway 헬스 체크
        results['gateway_health'] = self.test_gateway_health()
        
        # 2. Boundary Install API 테스트
        results['boundary_install'] = self.test_boundary_install_list()
        
        # 3. 직접 CBAM 서비스 테스트
        results['direct_cbam'] = self.test_direct_cbam_service()
        
        # 4. Gateway 라우팅 테스트
        results['gateway_routing'] = self.test_gateway_routing()
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ 성공" if result else "❌ 실패"
            print(f"{test_name:20}: {status}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n전체 테스트: {success_count}/{total_count} 성공")
        
        if success_count == total_count:
            print("🎉 모든 테스트가 성공했습니다!")
        else:
            print("⚠️  일부 테스트가 실패했습니다. 로그를 확인하세요.")
        
        return results

def main():
    """메인 실행 함수"""
    print("Gateway Boundary 서비스 테스트 스크립트")
    print("이 스크립트는 Gateway를 통해 boundary/install API가 제대로 작동하는지 테스트합니다.")
    print()
    
    # 테스터 생성 및 실행
    tester = GatewayBoundaryTester()
    results = tester.run_all_tests()
    
    # 상세 결과 반환
    return results

if __name__ == "__main__":
    main()
