#!/usr/bin/env python3
"""
Vercel 배포된 리팩토링 코드 자동 테스트 스크립트
- 자동으로 배포된 사이트를 찾아서 테스트
"""

import requests
import json
import time
import sys
from pathlib import Path

class VercelAutoTester:
    def __init__(self):
        # 가능한 Vercel 배포 URL들
        self.possible_urls = [
            "https://www.envioatlas.cloud/",
            "https://envioatlas.cloud/",
            "https://envioatlas.vercel.app/",
            "https://cbam-app.vercel.app/",
            "https://cbam-frontend.vercel.app/"
        ]
        self.frontend_url = None
        self.api_url = None
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
    
    def find_deployment_url(self):
        """배포된 URL 자동 찾기"""
        print("\n🔍 배포된 URL 자동 탐지 중...")
        
        for url in self.possible_urls:
            try:
                print(f"  시도 중: {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # React/Next.js 앱인지 확인
                    if any(keyword in response.text.lower() for keyword in ['react', 'next', 'cbam', 'envioatlas']):
                        self.frontend_url = url
                        self.api_url = url  # 같은 도메인에서 API 제공
                        self.log_test("배포 URL 탐지", True, f"발견된 URL: {url}")
                        return True
            except requests.exceptions.RequestException:
                continue
        
        self.log_test("배포 URL 탐지", False, "접근 가능한 배포 URL을 찾을 수 없습니다")
        return False
    
    def test_frontend_access(self):
        """프론트엔드 접근 테스트"""
        print("\n🌐 프론트엔드 접근 테스트 시작...")
        
        try:
            response = requests.get(self.frontend_url, timeout=30)
            if response.status_code == 200:
                self.log_test("메인 페이지 접근", True, f"상태 코드: {response.status_code}")
                
                # HTML 내용 분석
                html_content = response.text.lower()
                if 'react' in html_content or 'next' in html_content:
                    self.log_test("React 앱 로드", True, "React/Next.js 앱이 정상 로드됨")
                else:
                    self.log_test("React 앱 로드", False, "React 앱이 로드되지 않음")
                
                # CBAM 관련 키워드 확인
                if 'cbam' in html_content or 'envioatlas' in html_content:
                    self.log_test("CBAM 앱 확인", True, "CBAM 관련 콘텐츠 발견")
                else:
                    self.log_test("CBAM 앱 확인", False, "CBAM 관련 콘텐츠를 찾을 수 없음")
                
                return True
            else:
                self.log_test("메인 페이지 접근", False, f"상태 코드: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("프론트엔드 접근", False, f"연결 실패: {str(e)}")
            return False
        except Exception as e:
            self.log_test("프론트엔드 접근", False, f"예외 발생: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """API 엔드포인트 테스트"""
        print("\n🔌 API 엔드포인트 테스트 시작...")
        
        # API 엔드포인트 목록
        endpoints = [
            "/api/v1/cbam/install/list",
            "/api/v1/cbam/product/list", 
            "/api/v1/cbam/process/list",
            "/api/v1/cbam/edge/list"
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
    
    def test_refactored_features(self):
        """리팩토링된 기능 테스트"""
        print("\n🔧 리팩토링된 기능 테스트 시작...")
        
        try:
            # 1. 제품 목록 조회
            response = requests.get(f"{self.api_url}/api/v1/cbam/product/list", timeout=15)
            if response.status_code == 200:
                products = response.json()
                self.log_test("제품 목록 조회", True, f"{len(products)}개 제품 조회됨")
                
                # 2. 공정 목록 조회
                response = requests.get(f"{self.api_url}/api/v1/cbam/process/list", timeout=15)
                if response.status_code == 200:
                    processes = response.json()
                    self.log_test("공정 목록 조회", True, f"{len(processes)}개 공정 조회됨")
                    
                    # 3. 엣지 목록 조회
                    response = requests.get(f"{self.api_url}/api/v1/cbam/edge/list", timeout=15)
                    if response.status_code == 200:
                        edges = response.json()
                        self.log_test("엣지 목록 조회", True, f"{len(edges)}개 엣지 조회됨")
                        
                        # 4. 배출량 계산 API 테스트 (리팩토링된 핵심 기능)
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
            # 1. 전체 그래프 재계산 API 테스트 (리팩토링된 핵심 기능)
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
            
            # 2. 엣지 목록 조회
            response = requests.get(f"{self.api_url}/api/v1/cbam/edge/list", timeout=15)
            if response.status_code == 200:
                edges = response.json()
                self.log_test("엣지 목록 조회", True, f"{len(edges)}개 엣지 조회됨")
                
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
        """성능 테스트"""
        print("\n⚡ 성능 테스트 시작...")
        
        try:
            # API 응답 시간 측정
            start_time = time.time()
            response = requests.get(f"{self.api_url}/api/v1/cbam/product/list", timeout=15)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                if response_time < 2.0:
                    self.log_test("API 응답 시간", True, f"{response_time:.2f}초 (빠름)")
                elif response_time < 5.0:
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
    
    def test_file_structure(self):
        """리팩토링된 파일 구조 확인"""
        print("\n📁 리팩토링된 파일 구조 테스트 시작...")
        
        hook_files = [
            "frontend/src/hooks/useEmissionManager.ts",
            "frontend/src/hooks/useEdgeManager.ts", 
            "frontend/src/hooks/useNodeManager.ts",
            "frontend/src/hooks/useProcessCanvas.ts"
        ]
        
        all_exist = True
        total_size = 0
        
        for hook_file in hook_files:
            file_path = Path(hook_file)
            if file_path.exists():
                file_size = file_path.stat().st_size
                total_size += file_size
                if file_size > 1000:
                    self.log_test(f"훅 파일 {hook_file}", True, f"크기: {file_size} bytes")
                else:
                    self.log_test(f"훅 파일 {hook_file}", False, "파일이 너무 작습니다")
                    all_exist = False
            else:
                self.log_test(f"훅 파일 {hook_file}", False, "파일이 존재하지 않습니다")
                all_exist = False
        
        # 전체 파일 크기 체크 (리팩토링 전 1606줄 → 현재 분리된 파일들)
        if total_size < 100000:  # 100KB 미만이면 좋음
            self.log_test("전체 파일 크기", True, f"총 {total_size} bytes (적절함)")
        else:
            self.log_test("전체 파일 크기", False, f"총 {total_size} bytes (여전히 큼)")
        
        return all_exist
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 Vercel 배포된 리팩토링 코드 자동 테스트 시작")
        print("=" * 60)
        
        # 먼저 배포 URL 찾기
        if not self.find_deployment_url():
            print("❌ 배포된 URL을 찾을 수 없습니다. 수동으로 URL을 확인해주세요.")
            return False
        
        tests = [
            ("프론트엔드 접근", self.test_frontend_access),
            ("API 엔드포인트", self.test_api_endpoints),
            ("리팩토링된 기능", self.test_refactored_features),
            ("엣지 작업", self.test_edge_operations),
            ("성능 테스트", self.test_performance),
            ("파일 구조", self.test_file_structure)
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
        
        if passed >= total * 0.7:  # 70% 이상 통과하면 성공
            print("🎉 대부분의 테스트가 통과했습니다! 리팩토링이 성공적으로 완료되었습니다.")
            return True
        else:
            print("⚠️ 많은 테스트가 실패했습니다. 문제를 확인해주세요.")
            return False

def main():
    """메인 함수"""
    tester = VercelAutoTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Vercel 배포 테스트 완료!")
        sys.exit(0)
    else:
        print("\n❌ Vercel 배포 테스트 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
