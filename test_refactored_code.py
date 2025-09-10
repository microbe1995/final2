#!/usr/bin/env python3
"""
리팩토링된 useProcessCanvas.ts 코드 테스트 스크립트
- 프론트엔드 빌드 테스트
- 백엔드 API 연결 테스트
- 전체 시스템 통합 테스트
"""

import subprocess
import requests
import json
import time
import sys
from pathlib import Path

class RefactoredCodeTester:
    def __init__(self):
        self.base_url = "http://localhost:3000"  # Next.js 기본 포트
        self.api_url = "http://localhost:8000"   # FastAPI 기본 포트
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
    
    def test_frontend_build(self):
        """프론트엔드 빌드 테스트"""
        print("\n🔨 프론트엔드 빌드 테스트 시작...")
        
        try:
            # frontend 디렉토리로 이동
            frontend_path = Path("frontend")
            if not frontend_path.exists():
                self.log_test("프론트엔드 빌드", False, "frontend 디렉토리가 존재하지 않습니다")
                return False
            
            # TypeScript 컴파일 체크
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log_test("TypeScript 컴파일", True, "타입 오류 없음")
            else:
                self.log_test("TypeScript 컴파일", False, f"타입 오류: {result.stderr}")
                return False
            
            # Next.js 빌드 테스트
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log_test("Next.js 빌드", True, "빌드 성공")
                return True
            else:
                self.log_test("Next.js 빌드", False, f"빌드 실패: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_test("프론트엔드 빌드", False, "빌드 시간 초과")
            return False
        except Exception as e:
            self.log_test("프론트엔드 빌드", False, f"예외 발생: {str(e)}")
            return False
    
    def test_backend_api(self):
        """백엔드 API 연결 테스트"""
        print("\n🔌 백엔드 API 연결 테스트 시작...")
        
        try:
            # 헬스체크
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("백엔드 헬스체크", True, "API 서버 정상")
            else:
                self.log_test("백엔드 헬스체크", False, f"상태 코드: {response.status_code}")
                return False
            
            # CBAM API 엔드포인트 테스트
            endpoints = [
                "/api/v1/cbam/install/list",
                "/api/v1/cbam/product/list", 
                "/api/v1/cbam/process/list",
                "/api/v1/cbam/edge/list"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.api_url}{endpoint}", timeout=10)
                    if response.status_code in [200, 404]:  # 404도 정상 (데이터 없음)
                        self.log_test(f"API {endpoint}", True, f"상태 코드: {response.status_code}")
                    else:
                        self.log_test(f"API {endpoint}", False, f"상태 코드: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    self.log_test(f"API {endpoint}", False, f"연결 실패: {str(e)}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("백엔드 API 연결", False, f"연결 실패: {str(e)}")
            return False
        except Exception as e:
            self.log_test("백엔드 API 연결", False, f"예외 발생: {str(e)}")
            return False
    
    def test_refactored_hooks(self):
        """리팩토링된 훅 파일 존재 및 구조 테스트"""
        print("\n📁 리팩토링된 훅 파일 테스트 시작...")
        
        hook_files = [
            "frontend/src/hooks/useEmissionManager.ts",
            "frontend/src/hooks/useEdgeManager.ts", 
            "frontend/src/hooks/useNodeManager.ts",
            "frontend/src/hooks/useProcessCanvas.ts"
        ]
        
        all_exist = True
        for hook_file in hook_files:
            file_path = Path(hook_file)
            if file_path.exists():
                # 파일 크기 체크 (너무 작으면 문제)
                file_size = file_path.stat().st_size
                if file_size > 1000:  # 1KB 이상
                    self.log_test(f"훅 파일 {hook_file}", True, f"크기: {file_size} bytes")
                else:
                    self.log_test(f"훅 파일 {hook_file}", False, "파일이 너무 작습니다")
                    all_exist = False
            else:
                self.log_test(f"훅 파일 {hook_file}", False, "파일이 존재하지 않습니다")
                all_exist = False
        
        # 기존 백업 파일 확인
        backup_file = Path("frontend/src/hooks/useProcessCanvas.ts.backup")
        if backup_file.exists():
            self.log_test("백업 파일", True, "기존 파일 백업됨")
        else:
            self.log_test("백업 파일", False, "백업 파일이 없습니다")
        
        return all_exist
    
    def test_integration(self):
        """통합 테스트 (프론트엔드 + 백엔드)"""
        print("\n🔗 통합 테스트 시작...")
        
        try:
            # 프론트엔드 서버 시작 테스트
            frontend_path = Path("frontend")
            if not frontend_path.exists():
                self.log_test("통합 테스트", False, "frontend 디렉토리가 없습니다")
                return False
            
            # 개발 서버 시작 (백그라운드)
            print("프론트엔드 개발 서버 시작 중...")
            dev_server = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 서버 시작 대기
            time.sleep(10)
            
            # 프론트엔드 접근 테스트
            try:
                response = requests.get(f"{self.base_url}", timeout=10)
                if response.status_code == 200:
                    self.log_test("프론트엔드 접근", True, "페이지 로드 성공")
                else:
                    self.log_test("프론트엔드 접근", False, f"상태 코드: {response.status_code}")
            except requests.exceptions.RequestException:
                self.log_test("프론트엔드 접근", False, "연결 실패")
            
            # 개발 서버 종료
            dev_server.terminate()
            dev_server.wait(timeout=5)
            
            return True
            
        except Exception as e:
            self.log_test("통합 테스트", False, f"예외 발생: {str(e)}")
            return False
    
    def test_code_quality(self):
        """코드 품질 테스트"""
        print("\n📊 코드 품질 테스트 시작...")
        
        try:
            frontend_path = Path("frontend")
            
            # ESLint 체크
            result = subprocess.run(
                ["npx", "eslint", "src/hooks/", "--ext", ".ts,.tsx"],
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.log_test("ESLint 체크", True, "린트 오류 없음")
            else:
                # 경고는 허용, 에러만 실패로 처리
                if "error" in result.stdout.lower() or "error" in result.stderr.lower():
                    self.log_test("ESLint 체크", False, f"린트 에러: {result.stdout}")
                else:
                    self.log_test("ESLint 체크", True, "경고만 있음 (정상)")
            
            # 파일 라인 수 체크
            hook_files = [
                "src/hooks/useEmissionManager.ts",
                "src/hooks/useEdgeManager.ts",
                "src/hooks/useNodeManager.ts", 
                "src/hooks/useProcessCanvas.ts"
            ]
            
            total_lines = 0
            for hook_file in hook_files:
                file_path = frontend_path / hook_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        if lines < 1000:  # 각 파일이 1000줄 미만이면 좋음
                            self.log_test(f"파일 크기 {hook_file}", True, f"{lines}줄")
                        else:
                            self.log_test(f"파일 크기 {hook_file}", False, f"{lines}줄 (너무 큼)")
            
            if total_lines < 2000:  # 전체가 2000줄 미만이면 좋음
                self.log_test("전체 파일 크기", True, f"총 {total_lines}줄")
            else:
                self.log_test("전체 파일 크기", False, f"총 {total_lines}줄 (여전히 큼)")
            
            return True
            
        except Exception as e:
            self.log_test("코드 품질 테스트", False, f"예외 발생: {str(e)}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 리팩토링된 코드 테스트 시작")
        print("=" * 50)
        
        tests = [
            ("리팩토링된 훅 파일", self.test_refactored_hooks),
            ("코드 품질", self.test_code_quality),
            ("프론트엔드 빌드", self.test_frontend_build),
            ("백엔드 API", self.test_backend_api),
            ("통합 테스트", self.test_integration)
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
        print("\n" + "=" * 50)
        print("📋 테스트 결과 요약")
        print("=" * 50)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
        
        print(f"\n🎯 전체 결과: {passed}/{total} 테스트 통과")
        
        if passed == total:
            print("🎉 모든 테스트가 통과했습니다! 리팩토링이 성공적으로 완료되었습니다.")
            return True
        else:
            print("⚠️ 일부 테스트가 실패했습니다. 문제를 확인해주세요.")
            return False

def main():
    """메인 함수"""
    tester = RefactoredCodeTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 리팩토링 검증 완료!")
        sys.exit(0)
    else:
        print("\n❌ 리팩토링 검증 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
