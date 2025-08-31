#!/usr/bin/env python3
"""
🌐 Gateway CORS 테스트 스크립트
- OPTIONS preflight 요청 테스트
- 실제 API 요청 테스트
- 다양한 오리진에서의 CORS 동작 확인
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# 테스트 설정
GATEWAY_URL = "https://gateway-production-22ef.up.railway.app"
TEST_ENDPOINTS = [
    "/api/v1/boundary/install",
    "/api/v1/boundary/install/",
    "/api/v1/boundary/install/names",
    "/health",
    "/api/v1/auth/health"
]

# 테스트할 오리진들
TEST_ORIGINS = [
    "https://lca-final.vercel.app",      # Vercel 프로덕션
    "http://localhost:3000",             # 로컬 개발
    "https://example.com",               # 허용되지 않은 도메인
    "https://malicious-site.com",        # 악의적 사이트
    None                                 # 오리진 헤더 없음
]

class CORSGatewayTester:
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
        self.session = requests.Session()
        self.results = []
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_options_request(self, endpoint: str, origin: str = None) -> Dict[str, Any]:
        """OPTIONS preflight 요청 테스트"""
        url = f"{self.gateway_url}{endpoint}"
        headers = {}
        
        if origin:
            headers["Origin"] = origin
            
        self.log(f"🔍 OPTIONS 테스트: {endpoint}")
        self.log(f"   URL: {url}")
        self.log(f"   Origin: {origin or 'N/A'}")
        
        try:
            start_time = time.time()
            response = self.session.options(url, headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            # CORS 헤더 확인
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Max-Age": response.headers.get("Access-Control-Max-Age")
            }
            
            result = {
                "test_type": "OPTIONS",
                "endpoint": endpoint,
                "origin": origin,
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "cors_headers": cors_headers,
                "success": response.status_code == 200,
                "error": None
            }
            
            if response.status_code == 200:
                self.log(f"   ✅ 성공: {response.status_code} ({response_time:.3f}초)")
                self.log(f"   🌐 CORS 헤더: {cors_headers}")
            else:
                self.log(f"   ❌ 실패: {response.status_code} ({response_time:.3f}초)")
                if response.content:
                    try:
                        error_content = response.json()
                        self.log(f"   📄 에러 내용: {error_content}")
                    except:
                        self.log(f"   📄 에러 내용: {response.text[:200]}")
                        
        except Exception as e:
            result = {
                "test_type": "OPTIONS",
                "endpoint": endpoint,
                "origin": origin,
                "status_code": None,
                "response_time": None,
                "cors_headers": {},
                "success": False,
                "error": str(e)
            }
            self.log(f"   💥 예외 발생: {e}", "ERROR")
            
        return result
    
    def test_get_request(self, endpoint: str, origin: str = None) -> Dict[str, Any]:
        """GET 요청 테스트 (CORS 헤더 포함)"""
        url = f"{self.gateway_url}{endpoint}"
        headers = {}
        
        if origin:
            headers["Origin"] = origin
            
        self.log(f"🔍 GET 테스트: {endpoint}")
        self.log(f"   URL: {url}")
        self.log(f"   Origin: {origin or 'N/A'}")
        
        try:
            start_time = time.time()
            response = self.session.get(url, headers=headers, timeout=10)
            response_time = time.time() - start_time
            
            # CORS 헤더 확인
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            result = {
                "test_type": "GET",
                "endpoint": endpoint,
                "origin": origin,
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "cors_headers": cors_headers,
                "success": response.status_code < 400,
                "error": None,
                "content_length": len(response.content)
            }
            
            if response.status_code < 400:
                self.log(f"   ✅ 성공: {response.status_code} ({response_time:.3f}초)")
                self.log(f"   📊 응답 크기: {len(response.content)} bytes")
                if response.status_code == 200 and response.content:
                    try:
                        content = response.json()
                        if isinstance(content, list):
                            self.log(f"   📋 응답 항목 수: {len(content)}개")
                        elif isinstance(content, dict):
                            self.log(f"   📋 응답 키: {list(content.keys())}")
                    except:
                        self.log(f"   📋 응답 타입: {type(response.content)}")
            else:
                self.log(f"   ❌ 실패: {response.status_code} ({response_time:.3f}초)")
                
        except Exception as e:
            result = {
                "test_type": "GET",
                "endpoint": endpoint,
                "origin": origin,
                "status_code": None,
                "response_time": None,
                "cors_headers": {},
                "success": False,
                "error": str(e),
                "content_length": 0
            }
            self.log(f"   💥 예외 발생: {e}", "ERROR")
            
        return result
    
    def test_endpoint(self, endpoint: str) -> List[Dict[str, Any]]:
        """특정 엔드포인트에 대한 모든 테스트 실행"""
        self.log(f"\n🚀 엔드포인트 테스트 시작: {endpoint}")
        self.log("=" * 60)
        
        results = []
        
        # 각 오리진에 대해 테스트
        for origin in TEST_ORIGINS:
            self.log(f"\n📍 오리진 테스트: {origin or 'N/A'}")
            
            # OPTIONS 테스트
            options_result = self.test_options_request(endpoint, origin)
            results.append(options_result)
            
            # GET 테스트 (OPTIONS가 성공한 경우에만)
            if options_result["success"]:
                get_result = self.test_get_request(endpoint, origin)
                results.append(get_result)
            else:
                self.log(f"   ⏭️ OPTIONS 실패로 인해 GET 테스트 건너뜀")
                
        return results
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """모든 엔드포인트에 대한 테스트 실행"""
        self.log("🚀 Gateway CORS 종합 테스트 시작")
        self.log("=" * 80)
        self.log(f"🎯 Gateway URL: {self.gateway_url}")
        self.log(f"🔍 테스트 엔드포인트: {len(TEST_ENDPOINTS)}개")
        self.log(f"🌐 테스트 오리진: {len(TEST_ORIGINS)}개")
        self.log("=" * 80)
        
        all_results = []
        
        for endpoint in TEST_ENDPOINTS:
            endpoint_results = self.test_endpoint(endpoint)
            all_results.extend(endpoint_results)
            
        return all_results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> None:
        """테스트 결과 리포트 생성"""
        self.log("\n" + "=" * 80)
        self.log("📊 CORS 테스트 결과 리포트")
        self.log("=" * 80)
        
        # 전체 통계
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        failed_tests = total_tests - successful_tests
        
        self.log(f"📈 전체 테스트: {total_tests}개")
        self.log(f"✅ 성공: {successful_tests}개")
        self.log(f"❌ 실패: {failed_tests}개")
        self.log(f"📊 성공률: {(successful_tests/total_tests*100):.1f}%")
        
        # 엔드포인트별 통계
        self.log(f"\n🔍 엔드포인트별 결과:")
        endpoint_stats = {}
        for result in results:
            endpoint = result["endpoint"]
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"total": 0, "success": 0, "failed": 0}
            
            endpoint_stats[endpoint]["total"] += 1
            if result["success"]:
                endpoint_stats[endpoint]["success"] += 1
            else:
                endpoint_stats[endpoint]["failed"] += 1
        
        for endpoint, stats in endpoint_stats.items():
            success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            self.log(f"   {endpoint}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # 오리진별 통계
        self.log(f"\n🌐 오리진별 결과:")
        origin_stats = {}
        for result in results:
            origin = result["origin"] or "N/A"
            if origin not in origin_stats:
                origin_stats[origin] = {"total": 0, "success": 0, "failed": 0}
            
            origin_stats[origin]["total"] += 1
            if result["success"]:
                origin_stats[origin]["success"] += 1
            else:
                origin_stats[origin]["failed"] += 1
        
        for origin, stats in origin_stats.items():
            success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            self.log(f"   {origin}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        # 실패한 테스트 상세 분석
        if failed_tests > 0:
            self.log(f"\n❌ 실패한 테스트 상세:")
            for result in results:
                if not result["success"]:
                    self.log(f"   {result['test_type']} {result['endpoint']} (Origin: {result['origin'] or 'N/A'})")
                    self.log(f"     상태코드: {result['status_code']}")
                    if result["error"]:
                        self.log(f"     에러: {result['error']}")
        
        # CORS 헤더 분석
        self.log(f"\n🌐 CORS 헤더 분석:")
        cors_headers_found = set()
        for result in results:
            if result["cors_headers"]:
                for header, value in result["cors_headers"].items():
                    if value:
                        cors_headers_found.add(f"{header}: {value}")
        
        if cors_headers_found:
            for header in sorted(cors_headers_found):
                self.log(f"   ✅ {header}")
        else:
            self.log(f"   ⚠️ CORS 헤더를 찾을 수 없음")
        
        self.log("\n" + "=" * 80)
        self.log("🎯 테스트 완료!")
        
        # 결과를 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cors_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "test_info": {
                    "gateway_url": self.gateway_url,
                    "timestamp": datetime.now().isoformat(),
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": failed_tests
                },
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        self.log(f"💾 결과가 {filename}에 저장되었습니다.")

def main():
    """메인 실행 함수"""
    print("🌐 Gateway CORS 테스트 스크립트")
    print("=" * 50)
    
    # Gateway URL 확인
    gateway_url = input(f"Gateway URL을 입력하세요 (기본값: {GATEWAY_URL}): ").strip()
    if not gateway_url:
        gateway_url = GATEWAY_URL
    
    print(f"\n🎯 테스트할 Gateway: {gateway_url}")
    
    # 테스트 실행
    tester = CORSGatewayTester(gateway_url)
    results = tester.run_all_tests()
    
    # 리포트 생성
    tester.generate_report(results)

if __name__ == "__main__":
    main()
