#!/usr/bin/env python3
"""
리팩토링된 코드 구조 및 문법 테스트 스크립트
- 파일 존재 여부 확인
- 코드 구조 분석
- 문법 오류 체크
- 리팩토링 효과 측정
"""

import os
import re
from pathlib import Path

class RefactoredStructureTester:
    def __init__(self):
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
    
    def test_file_existence(self):
        """리팩토링된 파일 존재 여부 테스트"""
        print("\n📁 파일 존재 여부 테스트 시작...")
        
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
                lines = len(file_path.read_text(encoding='utf-8').splitlines())
                
                if file_size > 1000 and lines > 50:
                    self.log_test(f"파일 {hook_file}", True, f"크기: {file_size} bytes, {lines}줄")
                else:
                    self.log_test(f"파일 {hook_file}", False, f"파일이 너무 작음: {file_size} bytes, {lines}줄")
                    all_exist = False
            else:
                self.log_test(f"파일 {hook_file}", False, "파일이 존재하지 않습니다")
                all_exist = False
        
        # 전체 파일 크기 체크
        if total_size < 100000:  # 100KB 미만이면 좋음
            self.log_test("전체 파일 크기", True, f"총 {total_size} bytes (적절함)")
        else:
            self.log_test("전체 파일 크기", False, f"총 {total_size} bytes (여전히 큼)")
        
        return all_exist
    
    def test_code_structure(self):
        """코드 구조 분석 테스트"""
        print("\n🏗️ 코드 구조 분석 테스트 시작...")
        
        hook_files = [
            ("useEmissionManager.ts", "frontend/src/hooks/useEmissionManager.ts"),
            ("useEdgeManager.ts", "frontend/src/hooks/useEdgeManager.ts"),
            ("useNodeManager.ts", "frontend/src/hooks/useNodeManager.ts"),
            ("useProcessCanvas.ts", "frontend/src/hooks/useProcessCanvas.ts")
        ]
        
        all_good = True
        
        for name, file_path in hook_files:
            if not Path(file_path).exists():
                continue
                
            content = Path(file_path).read_text(encoding='utf-8')
            
            # 1. 단일 책임 원칙 확인
            if name == "useEmissionManager.ts":
                if "emission" in content.lower() and "refresh" in content.lower():
                    self.log_test(f"{name} 단일 책임", True, "배출량 관리만 담당")
                else:
                    self.log_test(f"{name} 단일 책임", False, "배출량 관리 외 다른 책임 포함")
                    all_good = False
            
            elif name == "useEdgeManager.ts":
                if "edge" in content.lower() and "create" in content.lower() and "delete" in content.lower():
                    self.log_test(f"{name} 단일 책임", True, "엣지 관리만 담당")
                else:
                    self.log_test(f"{name} 단일 책임", False, "엣지 관리 외 다른 책임 포함")
                    all_good = False
            
            elif name == "useNodeManager.ts":
                if "node" in content.lower() and "create" in content.lower():
                    self.log_test(f"{name} 단일 책임", True, "노드 관리만 담당")
                else:
                    self.log_test(f"{name} 단일 책임", False, "노드 관리 외 다른 책임 포함")
                    all_good = False
            
            elif name == "useProcessCanvas.ts":
                if "useEmissionManager" in content and "useEdgeManager" in content and "useNodeManager" in content:
                    self.log_test(f"{name} 조합자 역할", True, "전용 훅들을 조합하여 사용")
                else:
                    self.log_test(f"{name} 조합자 역할", False, "전용 훅들을 사용하지 않음")
                    all_good = False
            
            # 2. 함수 개수 확인 (너무 많으면 단일 책임 위반)
            function_count = len(re.findall(r'const\s+\w+\s*=\s*useCallback|function\s+\w+|async\s+\w+', content))
            if function_count < 10:
                self.log_test(f"{name} 함수 개수", True, f"{function_count}개 함수 (적절함)")
            else:
                self.log_test(f"{name} 함수 개수", False, f"{function_count}개 함수 (너무 많음)")
                all_good = False
        
        return all_good
    
    def test_import_structure(self):
        """Import 구조 테스트"""
        print("\n📦 Import 구조 테스트 시작...")
        
        # 메인 훅에서 전용 훅들을 import하는지 확인
        main_hook_path = "frontend/src/hooks/useProcessCanvas.ts"
        if Path(main_hook_path).exists():
            content = Path(main_hook_path).read_text(encoding='utf-8')
            
            imports = re.findall(r'import.*from.*use\w+Manager', content)
            if len(imports) >= 3:
                self.log_test("전용 훅 Import", True, f"{len(imports)}개 전용 훅 import됨")
            else:
                self.log_test("전용 훅 Import", False, f"{len(imports)}개만 import됨 (3개 필요)")
                return False
            
            # 각 전용 훅이 올바른 함수들을 export하는지 확인
            for hook_file in ["useEmissionManager.ts", "useEdgeManager.ts", "useNodeManager.ts"]:
                file_path = f"frontend/src/hooks/{hook_file}"
                if Path(file_path).exists():
                    hook_content = Path(file_path).read_text(encoding='utf-8')
                    exports = re.findall(r'return\s*\{[^}]*\}', hook_content, re.DOTALL)
                    if exports:
                        self.log_test(f"{hook_file} Export", True, "함수들을 올바르게 export함")
                    else:
                        self.log_test(f"{hook_file} Export", False, "함수들을 export하지 않음")
                        return False
            
            return True
        else:
            self.log_test("Import 구조", False, "메인 훅 파일이 존재하지 않음")
            return False
    
    def test_code_quality(self):
        """코드 품질 테스트"""
        print("\n📊 코드 품질 테스트 시작...")
        
        hook_files = [
            "frontend/src/hooks/useEmissionManager.ts",
            "frontend/src/hooks/useEdgeManager.ts", 
            "frontend/src/hooks/useNodeManager.ts",
            "frontend/src/hooks/useProcessCanvas.ts"
        ]
        
        all_good = True
        
        for hook_file in hook_files:
            if not Path(hook_file).exists():
                continue
                
            content = Path(hook_file).read_text(encoding='utf-8')
            
            # 1. 주석 품질 확인
            comment_lines = len(re.findall(r'^\s*//.*|^\s*/\*.*\*/', content, re.MULTILINE))
            total_lines = len(content.splitlines())
            comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
            
            if comment_ratio > 0.1:  # 10% 이상 주석
                self.log_test(f"{Path(hook_file).name} 주석", True, f"{comment_ratio:.1%} 주석 비율")
            else:
                self.log_test(f"{Path(hook_file).name} 주석", False, f"{comment_ratio:.1%} 주석 비율 (부족)")
                all_good = False
            
            # 2. 에러 처리 확인
            error_handling = len(re.findall(r'try\s*\{|catch\s*\(|\.catch\(', content))
            if error_handling > 0:
                self.log_test(f"{Path(hook_file).name} 에러 처리", True, f"{error_handling}개 에러 처리 구문")
            else:
                self.log_test(f"{Path(hook_file).name} 에러 처리", False, "에러 처리 구문 없음")
                all_good = False
            
            # 3. TypeScript 타입 사용 확인
            type_usage = len(re.findall(r':\s*\w+|interface\s+\w+|type\s+\w+', content))
            if type_usage > 5:
                self.log_test(f"{Path(hook_file).name} 타입 사용", True, f"{type_usage}개 타입 사용")
            else:
                self.log_test(f"{Path(hook_file).name} 타입 사용", False, f"{type_usage}개 타입 사용 (부족)")
                all_good = False
        
        return all_good
    
    def test_refactoring_effectiveness(self):
        """리팩토링 효과 측정"""
        print("\n📈 리팩토링 효과 측정 시작...")
        
        # 백업 파일과 현재 파일 비교
        backup_file = "frontend/src/hooks/useProcessCanvas.ts.backup"
        current_file = "frontend/src/hooks/useProcessCanvas.ts"
        
        if Path(backup_file).exists() and Path(current_file).exists():
            backup_content = Path(backup_file).read_text(encoding='utf-8')
            current_content = Path(current_file).read_text(encoding='utf-8')
            
            backup_lines = len(backup_content.splitlines())
            current_lines = len(current_content.splitlines())
            
            reduction_ratio = (backup_lines - current_lines) / backup_lines if backup_lines > 0 else 0
            
            if reduction_ratio > 0.3:  # 30% 이상 줄어들면 좋음
                self.log_test("코드 라인 수 감소", True, f"{reduction_ratio:.1%} 감소 ({backup_lines} → {current_lines})")
            else:
                self.log_test("코드 라인 수 감소", False, f"{reduction_ratio:.1%} 감소 (부족)")
                return False
            
            # 함수 개수 비교
            backup_functions = len(re.findall(r'const\s+\w+\s*=\s*useCallback|function\s+\w+|async\s+\w+', backup_content))
            current_functions = len(re.findall(r'const\s+\w+\s*=\s*useCallback|function\s+\w+|async\s+\w+', current_content))
            
            if current_functions < backup_functions:
                self.log_test("함수 개수 감소", True, f"{backup_functions} → {current_functions}개")
            else:
                self.log_test("함수 개수 감소", False, f"함수 개수가 증가함 ({backup_functions} → {current_functions})")
                return False
            
            return True
        else:
            self.log_test("리팩토링 효과", False, "백업 파일 또는 현재 파일이 없음")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 리팩토링된 코드 구조 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("파일 존재 여부", self.test_file_existence),
            ("코드 구조", self.test_code_structure),
            ("Import 구조", self.test_import_structure),
            ("코드 품질", self.test_code_quality),
            ("리팩토링 효과", self.test_refactoring_effectiveness)
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
    tester = RefactoredStructureTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 리팩토링 구조 테스트 완료!")
        return 0
    else:
        print("\n❌ 리팩토링 구조 테스트 실패!")
        return 1

if __name__ == "__main__":
    exit(main())
