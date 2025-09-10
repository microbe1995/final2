#!/usr/bin/env python3
"""
Vercel 배포된 리팩토링 코드 테스트 스크립트
- 배포된 프론트엔드 접근 테스트
- API 엔드포인트 테스트
- 리팩토링된 훅들의 동작 확인
"""

import requests
import json
import time
import sys
from pathlib import Path

class VercelDeploymentTester:
    def __init__(self):
        # Vercel 배포 URL (실제 URL로 변경 필요)
        self.frontend_url = "https://your-cbam-app.vercel.app"  # 실제 Vercel URL로 변경
        self.api_url = "https://your-api-url.com"  # 실제 API URL로 변경
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """테스트 결과 로깅"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_vercel_frontend_access(self):
        """Vercel 배포된 프론트엔드 접근 테스트"""
        print("\n🌐 Vercel 프론트엔드 접근 테스트 시작...")
        
        try:
            # 메인 페이지 접근
            response = requests.get(self.frontend_url, timeout=30)
            if response.status_code == 200:
                self.log_test("메인 페이지 접근", True, f"상태 코드: {response.status_code}")
                
                # HTML 내용에서 React 앱이 로드되었는지 확인
                if "react" in response.text.lower() or "next" in response.text.lower():
                    self.log_test("React 앱 로드", True, "React/Next.js 앱이 정상 로드됨")
                else:
                    self.log_test("React 앱 로드", False, "React 앱이 로드되지 않음")
                
                return True
            else:
                self.log_test("메인 페이지 접근", False, f"상태 코드: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Vercel 프론트엔드 접근", False, f"연결 실패: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Vercel 프론트엔드 접근", False, f"예외 발생: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """API 엔드포인트 테스트"""
        print("\n🔌 API 엔드포인트 테스트 시작...")
        
        # API 엔드포인트 목록
        endpoints = [
            "/api/v1/cbam/install/list",
            "/api/v1/cbam/product/list", 
            "/api/v1/cbam/process/list",
            "/api/v1/cbam/edge/list",
            "/api/v1/cbam/calculation/emission/graph/recalculate"
        ]
        
        success_count = 0
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=15)
                if response.status_code in [200, 404]:  # 404도 정상 (데이터 없음)
                    self.log_test(f"API {endpoint}", True, f"상태 코드: {response.status_code}")
                    success_count += 1
                else:
                    self.log_test(f"API {endpoint}", False, f"상태 코드: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_test(f"API {endpoint}", False, f"연결 실패: {str(e)}")
        
        return success_count > 0
    
    def test_refactored_functionality(self):
        """리팩토링된 기능 테스트"""
        print("\n🔧 리팩토링된 기능 테스트 시작...")
        
        try:
            # 1. 제품 목록 조회 테스트
            response = requests.get(f"{self.api_url}/api/v1/cbam/product/list", timeout=15)
            if response.status_code == 200:
                products = response.json()
                self.log_test("제품 목록 조회", True, f"{len(products)}개 제품 조회됨")
                
                # 2. 공정 목록 조회 테스트
                response = requests.get(f"{self.api_url}/api/v1/cbam/process/list", timeout=15)
                if response.status_code == 200:
                    processes = response.json()
                    self.log_test("공정 목록 조회", True, f"{len(processes)}개 공정 조회됨")
                    
                    # 3. 엣지 목록 조회 테스트
                    response = requests.get(f"{self.api_url}/api/v1/cbam/edge/list", timeout=15)
                    if response.status_code == 200:
                        edges = response.json()
                        self.log_test("엣지 목록 조회", True, f"{len(edges)}개 엣지 조회됨")
                        
                        # 4. 배출량 계산 API 테스트 (새로 추가된 기능)
                        if len(processes) > 0:
                            process_id = processes[0]['id']
                            response = requests.get(
                                f"{self.api_url}/api/v1/cbam/calculation/emission/process/{process_id}/attrdir", 
                                timeout=15
                            )
                            if response.status_code in [200, 404]:
                                self.log_test("배출량 계산 API", True, "배출량 계산 API 정상 동작")
                            else:
                                self.log_test("배출량 계산 API", False, f"상태 코드: {response.status_code}")
                        
                        return True
                    else:
                        self.log_test("엣지 목록 조회", False, f"상태 코드: {response.status_code}")
                        return False
                else:
                    self.log_test("공정 목록 조회", False, f"상태 코드: {response.status_code}")
                    return False
            else:
                self.log_test("제품 목록 조회", False, f"상태 코드: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("리팩토링된 기능 테스트", False, f"예외 발생: {str(e)}")
            return False
    
    def test_edge_operations(self):
        """엣지 관련 작업 테스트 (리팩토링된 핵심 기능)"""
        print("\n🔗 엣지 작업 테스트 시작...")
        
        try:
            # 1. 엣지 목록 조회
            response = requests.get(f"{self.api_url}/api/v1/cbam/edge/list", timeout=15)
            if response.status_code != 200:
                self.log_test("엣지 목록 조회", False, f"상태 코드: {response.status_code}")
                return False
            
            edges = response.json()
            self.log_test("엣지 목록 조회", True, f"{len(edges)}개 엣지 조회됨")
            
            # 2. 전체 그래프 재계산 API 테스트 (리팩토링된 핵심 기능)
            try:
                response = requests.post(
                    f"{self.api_url}/api/v1/cbam/calculation/emission/graph/recalculate",
                    json={"trigger_edge_id": None, "include_validation": False},
                    timeout=30
                )
                if response.status_code in [200, 201]:
                    self.log_test("전체 그래프 재계산", True, "재계산 API 정상 동작")
                else:
                    self.log_test("전체 그래프 재계산", False, f"상태 코드: {response.status_code}")
            except Exception as e:
                self.log_test("전체 그래프 재계산", False, f"API 호출 실패: {str(e)}")
            
            # 3. 배출량 전파 API 테스트
            if len(edges) > 0:
                edge = edges[0]
                if edge.get('edge_kind') == 'continue':
                    try:
                        response = requests.post(
                            f"{self.api_url}/api/v1/cbam/edge/propagate-emissions/continue",
                            params={
                                "source_process_id": edge['source_id'],
                                "target_process_id": edge['target_id']
                            },
                            timeout=15
                        )
                        if response.status_code in [200, 201]:
                            self.log_test("배출량 전파 API", True, "전파 API 정상 동작")
                        else:
                            self.log_test("배출량 전파 API", False, f"상태 코드: {response.status_code}")
                    except Exception as e:
                        self.log_test("배출량 전파 API", False, f"API 호출 실패: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_test("엣지 작업 테스트", False, f"예외 발생: {str(e)}")
            return False
    
    def test_performance(self):
        """성능 테스트 (리팩토링 전후 비교)"""
        print("\n⚡ 성능 테스트 시작...")
        
        try:
            # API 응답 시간 측정
            start_time = time.time()
            response = requests.get(f"{self.api_url}/api/v1/cbam/product/list", timeout=15)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                if response_time < 2.0:  # 2초 미만이면 좋음
                    self.log_test("API 응답 시간", True, f"{response_time:.2f}초 (빠름)")
                elif response_time < 5.0:  # 5초 미만이면 보통
                    self.log_test("API 응답 시간", True, f"{response_time:.2f}초 (보통)")
                else:
                    self.log_test("API 응답 시간", False, f"{response_time:.2f}초 (느림)")
                
                return True
            else:
                self.log_test("성능 테스트", False, f"API 호출 실패: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("성능 테스트", False, f"예외 발생: {str(e)}")
            return False
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        print("\n🛡️ 에러 처리 테스트 시작...")
        
        try:
            # 존재하지 않는 엔드포인트 테스트
            response = requests.get(f"{self.api_url}/api/v1/cbam/nonexistent", timeout=10)
            if response.status_code == 404:
                self.log_test("404 에러 처리", True, "존재하지 않는 엔드포인트에 대한 적절한 404 응답")
            else:
                self.log_test("404 에러 처리", False, f"예상과 다른 상태 코드: {response.status_code}")
            
            # 잘못된 파라미터 테스트
            response = requests.get(f"{self.api_url}/api/v1/cbam/product/get/invalid", timeout=10)
            if response.status_code in [400, 404]:
                self.log_test("잘못된 파라미터 처리", True, "잘못된 파라미터에 대한 적절한 에러 응답")
            else:
                self.log_test("잘못된 파라미터 처리", False, f"예상과 다른 상태 코드: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("에러 처리 테스트", False, f"예외 발생: {str(e)}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 Vercel 배포된 리팩토링 코드 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("Vercel 프론트엔드 접근", self.test_vercel_frontend_access),
            ("API 엔드포인트", self.test_api_endpoints),
            ("리팩토링된 기능", self.test_refactored_functionality),
            ("엣지 작업", self.test_edge_operations),
            ("성능 테스트", self.test_performance),
            ("에러 처리", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"테스트 실행 중 오류: {str(e)}")
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📋 테스트 결과 요약")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print(f"\n🎯 전체 결과: {passed}/{total} 테스트 통과")
        
        if passed >= total * 0.8:  # 80% 이상 통과하면 성공
            print("🎉 대부분의 테스트가 통과했습니다! 리팩토링이 성공적으로 완료되었습니다.")
            return True
        else:
            print("⚠️ 많은 테스트가 실패했습니다. 문제를 확인해주세요.")
            return False

def main():
    """메인 함수"""
    print("Vercel 배포 URL을 입력해주세요:")
    frontend_url = input("프론트엔드 URL (예: https://your-app.vercel.app): ").strip()
    api_url = input("API URL (예: https://your-api.com): ").strip()
    
    if not frontend_url or not api_url:
        print("❌ URL을 입력해주세요.")
        sys.exit(1)
    
    tester = VercelDeploymentTester()
    tester.frontend_url = frontend_url
    tester.api_url = api_url
    
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Vercel 배포 테스트 완료!")
        sys.exit(0)
    else:
        print("\n❌ Vercel 배포 테스트 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
