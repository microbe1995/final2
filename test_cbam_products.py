#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 CBAM 제품 관리 기능 테스트 스크립트
Python 3.13.5 호환

이 스크립트는 CBAM 서비스의 제품 관리 기능을 종합적으로 테스트합니다.
"""

import asyncio
import aiohttp
import json
import time
import random
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class CBAMProductTester:
    """CBAM 제품 관리 기능 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        초기화
        
        Args:
            base_url: CBAM 서비스 기본 URL
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_install_id = 1  # 테스트용 설치 ID
        self.test_products: List[Dict[str, Any]] = []
        
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'Content-Type': 'application/json'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    def generate_test_product_data(self, product_name: str = None) -> Dict[str, Any]:
        """테스트용 제품 데이터 생성"""
        if not product_name:
            product_name = f"테스트제품_{random.randint(1000, 9999)}"
            
        # 기간 설정 (현재 날짜 기준)
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=30)
        
        return {
            "install_id": self.test_install_id,
            "product_name": product_name,
            "product_category": random.choice(["단순제품", "복합제품"]),
            "prostart_period": start_date.isoformat(),
            "proend_period": end_date.isoformat(),
            "product_amount": round(random.uniform(100.0, 10000.0), 2),
            "cncode_total": f"CN{random.randint(10000000, 99999999)}",
            "goods_name": f"테스트품목_{random.randint(100, 999)}",
            "goods_engname": f"Test_Goods_{random.randint(100, 999)}",
            "aggrgoods_name": f"테스트품목군_{random.randint(10, 99)}",
            "aggrgoods_engname": f"Test_Goods_Group_{random.randint(10, 99)}",
            "product_sell": round(random.uniform(50.0, 5000.0), 2),
            "product_eusell": round(random.uniform(10.0, 1000.0), 2)
        }
    
    async def test_health_check(self) -> bool:
        """서비스 상태 확인"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ 서비스 상태 확인 성공: {data}")
                    return True
                else:
                    logger.error(f"❌ 서비스 상태 확인 실패: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ 서비스 상태 확인 중 오류: {str(e)}")
            return False
    
    async def test_get_products(self) -> bool:
        """제품 목록 조회 테스트"""
        try:
            logger.info("📋 제품 목록 조회 테스트 시작")
            
            # 전체 제품 조회
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    products = await response.json()
                    logger.info(f"✅ 전체 제품 조회 성공: {len(products)}개")
                else:
                    logger.error(f"❌ 전체 제품 조회 실패: {response.status}")
                    return False
            
            # 설치 ID별 필터링 테스트
            async with self.session.get(f"{self.base_url}/?install_id={self.test_install_id}") as response:
                if response.status == 200:
                    filtered_products = await response.json()
                    logger.info(f"✅ 설치 ID별 필터링 성공: {len(filtered_products)}개")
                else:
                    logger.error(f"❌ 설치 ID별 필터링 실패: {response.status}")
            
            # 제품명 검색 테스트
            search_term = "테스트"
            async with self.session.get(f"{self.base_url}/?product_name={search_term}") as response:
                if response.status == 200:
                    search_results = await response.json()
                    logger.info(f"✅ 제품명 검색 성공: '{search_term}' - {len(search_results)}개")
                else:
                    logger.error(f"❌ 제품명 검색 실패: {response.status}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 제품 목록 조회 테스트 중 오류: {str(e)}")
            return False
    
    async def test_get_product_names(self) -> bool:
        """제품명 목록 조회 테스트"""
        try:
            logger.info("📋 제품명 목록 조회 테스트 시작")
            
            async with self.session.get(f"{self.base_url}/names") as response:
                if response.status == 200:
                    product_names = await response.json()
                    logger.info(f"✅ 제품명 목록 조회 성공: {len(product_names)}개")
                    
                    # 첫 번째 제품명 출력
                    if product_names:
                        first_product = product_names[0]
                        logger.info(f"   첫 번째 제품: {first_product}")
                    
                    return True
                else:
                    logger.error(f"❌ 제품명 목록 조회 실패: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 제품명 목록 조회 테스트 중 오류: {str(e)}")
            return False
    
    async def test_create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """제품 생성 테스트"""
        try:
            logger.info(f"📝 제품 생성 테스트 시작: {product_data['product_name']}")
            
            async with self.session.post(
                f"{self.base_url}/",
                json=product_data
            ) as response:
                if response.status == 201 or response.status == 200:
                    created_product = await response.json()
                    logger.info(f"✅ 제품 생성 성공: ID {created_product.get('id')}")
                    self.test_products.append(created_product)
                    return created_product
                else:
                    error_detail = await response.text()
                    logger.error(f"❌ 제품 생성 실패: {response.status} - {error_detail}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 제품 생성 테스트 중 오류: {str(e)}")
            return None
    
    async def test_get_single_product(self, product_id: int) -> bool:
        """단일 제품 조회 테스트"""
        try:
            logger.info(f"📋 단일 제품 조회 테스트 시작: ID {product_id}")
            
            async with self.session.get(f"{self.base_url}/{product_id}") as response:
                if response.status == 200:
                    product = await response.json()
                    logger.info(f"✅ 단일 제품 조회 성공: {product['product_name']}")
                    return True
                else:
                    logger.error(f"❌ 단일 제품 조회 실패: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 단일 제품 조회 테스트 중 오류: {str(e)}")
            return False
    
    async def test_update_product(self, product_id: int, update_data: Dict[str, Any]) -> bool:
        """제품 수정 테스트"""
        try:
            logger.info(f"📝 제품 수정 테스트 시작: ID {product_id}")
            
            async with self.session.put(
                f"{self.base_url}/{product_id}",
                json=update_data
            ) as response:
                if response.status == 200:
                    updated_product = await response.json()
                    logger.info(f"✅ 제품 수정 성공: {updated_product['product_name']}")
                    return True
                else:
                    error_detail = await response.text()
                    logger.error(f"❌ 제품 수정 실패: {response.status} - {error_detail}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 제품 수정 테스트 중 오류: {str(e)}")
            return False
    
    async def test_delete_product(self, product_id: int) -> bool:
        """제품 삭제 테스트"""
        try:
            logger.info(f"🗑️ 제품 삭제 테스트 시작: ID {product_id}")
            
            async with self.session.delete(f"{self.base_url}/{product_id}") as response:
                if response.status == 200 or response.status == 204:
                    logger.info(f"✅ 제품 삭제 성공: ID {product_id}")
                    return True
                else:
                    error_detail = await response.text()
                    logger.error(f"❌ 제품 삭제 실패: {response.status} - {error_detail}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 제품 삭제 테스트 중 오류: {str(e)}")
            return False
    
    async def test_bulk_operations(self) -> bool:
        """대량 작업 테스트"""
        try:
            logger.info("📦 대량 작업 테스트 시작")
            
            # 여러 제품 생성
            created_products = []
            for i in range(3):
                product_data = self.generate_test_product_data(f"대량테스트제품_{i+1}")
                created_product = await self.test_create_product(product_data)
                if created_product:
                    created_products.append(created_product)
                    await asyncio.sleep(0.5)  # API 호출 간격 조절
            
            logger.info(f"✅ 대량 제품 생성 완료: {len(created_products)}개")
            
            # 생성된 제품들 수정
            for product in created_products:
                update_data = {
                    "product_amount": round(random.uniform(200.0, 15000.0), 2),
                    "product_sell": round(random.uniform(100.0, 8000.0), 2)
                }
                await self.test_update_product(product['id'], update_data)
                await asyncio.sleep(0.3)
            
            logger.info("✅ 대량 제품 수정 완료")
            
            # 생성된 제품들 삭제
            for product in created_products:
                await self.test_delete_product(product['id'])
                await asyncio.sleep(0.3)
            
            logger.info("✅ 대량 제품 삭제 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 대량 작업 테스트 중 오류: {str(e)}")
            return False
    
    async def test_error_handling(self) -> bool:
        """에러 처리 테스트"""
        try:
            logger.info("🚨 에러 처리 테스트 시작")
            
            # 존재하지 않는 제품 조회
            async with self.session.get(f"{self.base_url}/99999") as response:
                if response.status == 404:
                    logger.info("✅ 404 에러 처리 정상")
                else:
                    logger.warning(f"⚠️ 예상과 다른 상태 코드: {response.status}")
            
            # 잘못된 데이터로 제품 생성 시도
            invalid_data = {
                "install_id": self.test_install_id,
                "product_name": "",  # 빈 제품명
                "product_category": "잘못된카테고리"
            }
            
            async with self.session.post(
                f"{self.base_url}/",
                json=invalid_data
            ) as response:
                if response.status in [400, 422]:
                    logger.info("✅ 유효성 검사 에러 처리 정상")
                else:
                    logger.warning(f"⚠️ 예상과 다른 상태 코드: {response.status}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 에러 처리 테스트 중 오류: {str(e)}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """모든 테스트 실행"""
        logger.info("🚀 CBAM 제품 관리 기능 종합 테스트 시작")
        logger.info(f"📍 테스트 대상: {self.base_url}")
        
        test_results = {}
        
        # 1. 서비스 상태 확인
        test_results['health_check'] = await self.test_health_check()
        
        if not test_results['health_check']:
            logger.error("❌ 서비스가 응답하지 않습니다. 테스트를 중단합니다.")
            return test_results
        
        # 2. 기본 CRUD 테스트
        test_results['get_products'] = await self.test_get_products()
        test_results['get_product_names'] = await self.test_get_product_names()
        
        # 3. 제품 생성 테스트
        test_product_data = self.generate_test_product_data("테스트제품_기본")
        created_product = await self.test_create_product(test_product_data)
        test_results['create_product'] = created_product is not None
        
        if created_product:
            # 4. 단일 제품 조회 테스트
            test_results['get_single_product'] = await self.test_get_single_product(created_product['id'])
            
            # 5. 제품 수정 테스트
            update_data = {
                "product_amount": 9999.99,
                "product_sell": 8888.88
            }
            test_results['update_product'] = await self.test_update_product(created_product['id'], update_data)
            
            # 6. 제품 삭제 테스트
            test_results['delete_product'] = await self.test_delete_product(created_product['id'])
        
        # 7. 대량 작업 테스트
        test_results['bulk_operations'] = await self.test_bulk_operations()
        
        # 8. 에러 처리 테스트
        test_results['error_handling'] = await self.test_error_handling()
        
        # 결과 요약
        logger.info("\n" + "="*60)
        logger.info("📊 테스트 결과 요약")
        logger.info("="*60)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ 통과" if result else "❌ 실패"
            logger.info(f"{test_name:20} : {status}")
        
        logger.info("-"*60)
        logger.info(f"전체 테스트: {total_tests}개")
        logger.info(f"통과: {passed_tests}개")
        logger.info(f"실패: {total_tests - passed_tests}개")
        logger.info(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            logger.info("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            logger.warning("⚠️ 일부 테스트가 실패했습니다.")
        
        return test_results

async def main():
    """메인 함수"""
    # 테스트 설정
    test_configs = [
        {
            "name": "로컬 CBAM 서비스",
            "url": "http://localhost:8001"
        },
        {
            "name": "Docker CBAM 서비스", 
            "url": "http://localhost:8001"
        }
    ]
    
    for config in test_configs:
        logger.info(f"\n🔧 {config['name']} 테스트 시작")
        logger.info(f"📍 URL: {config['url']}")
        
        try:
            async with CBAMProductTester(config['url']) as tester:
                results = await tester.run_all_tests()
                
                # 테스트 결과에 따른 처리
                if all(results.values()):
                    logger.info(f"✅ {config['name']} 테스트 완료 - 모든 기능 정상")
                else:
                    logger.warning(f"⚠️ {config['name']} 테스트 완료 - 일부 기능 문제")
                    
        except Exception as e:
            logger.error(f"❌ {config['name']} 테스트 중 치명적 오류: {str(e)}")
        
        logger.info(f"\n{'='*60}")
        time.sleep(2)  # 테스트 간 간격

if __name__ == "__main__":
    try:
        # Windows 환경에서 asyncio 이벤트 루프 정책 설정
        if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # 비동기 메인 함수 실행
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {str(e)}")
        logger.error("스크립트 실행을 확인해주세요.")
