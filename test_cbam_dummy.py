#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 CBAM Dummy 도메인 테스트 스크립트
Python 3.13.5 호환

이 스크립트는 CBAM 서비스의 Dummy 도메인 기능을 테스트합니다.
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

class CBAMDummyTester:
    """CBAM Dummy 도메인 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        초기화
        
        Args:
            base_url: CBAM 서비스 기본 URL
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_data: List[Dict[str, Any]] = []
        
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
    
    def generate_test_dummy_data(self, lot_number: str = None) -> Dict[str, Any]:
        """테스트용 Dummy 데이터 생성"""
        if not lot_number:
            lot_number = f"LOT{random.randint(1000, 9999)}"
            
        # 기간 설정 (현재 날짜 기준)
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=30)
        
        return {
            "로트번호": lot_number,
            "생산품명": f"테스트제품_{random.randint(100, 999)}",
            "생산수량": round(random.uniform(100.0, 10000.0), 2),
            "투입일": start_date.isoformat(),
            "종료일": end_date.isoformat(),
            "공정": random.choice(["압연", "용해", "주조", "단조", "열처리"]),
            "투입물명": f"테스트원료_{random.randint(100, 999)}",
            "수량": round(random.uniform(50.0, 5000.0), 2),
            "단위": random.choice(["kg", "ton", "개", "m"])
        }
    
    async def test_health_check(self) -> bool:
        """Dummy 도메인 상태 확인"""
        try:
            async with self.session.get(f"{self.base_url}/dummy/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Dummy 도메인 상태 확인 성공: {data}")
                    return True
                else:
                    logger.error(f"❌ Dummy 도메인 상태 확인 실패: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Dummy 도메인 상태 확인 중 오류: {str(e)}")
            return False
    
    async def test_get_all_dummy_data(self) -> bool:
        """모든 Dummy 데이터 조회 테스트"""
        try:
            logger.info("📋 모든 Dummy 데이터 조회 테스트 시작")
            
            # 기본 조회
            async with self.session.get(f"{self.base_url}/dummy/") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ 모든 Dummy 데이터 조회 성공: {data.get('total', 0)}개")
                else:
                    logger.error(f"❌ 모든 Dummy 데이터 조회 실패: {response.status}")
                    return False
            
            # 페이징 테스트
            async with self.session.get(f"{self.base_url}/dummy/?limit=5&offset=0") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ 페이징 테스트 성공: {len(data.get('data', []))}개")
                else:
                    logger.error(f"❌ 페이징 테스트 실패: {response.status}")
            
            # 검색 테스트
            search_term = "테스트"
            async with self.session.get(f"{self.base_url}/dummy/?search={search_term}") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ 검색 테스트 성공: '{search_term}' - {len(data.get('data', []))}개")
                else:
                    logger.error(f"❌ 검색 테스트 실패: {response.status}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 모든 Dummy 데이터 조회 테스트 중 오류: {str(e)}")
            return False
    
    async def test_create_dummy_data(self, dummy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Dummy 데이터 생성 테스트"""
        try:
            logger.info(f"📝 Dummy 데이터 생성 테스트 시작: {dummy_data['로트번호']}")
            
            async with self.session.post(
                f"{self.base_url}/dummy/",
                json=dummy_data
            ) as response:
                if response.status == 201 or response.status == 200:
                    created_data = await response.json()
                    logger.info(f"✅ Dummy 데이터 생성 성공: ID {created_data.get('id')}")
                    self.test_data.append(created_data)
                    return created_data
                else:
                    error_detail = await response.text()
                    logger.error(f"❌ Dummy 데이터 생성 실패: {response.status} - {error_detail}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 생성 테스트 중 오류: {str(e)}")
            return None
    
    async def test_get_single_dummy_data(self, data_id: int) -> bool:
        """단일 Dummy 데이터 조회 테스트"""
        try:
            logger.info(f"📋 단일 Dummy 데이터 조회 테스트 시작: ID {data_id}")
            
            async with self.session.get(f"{self.base_url}/dummy/{data_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ 단일 Dummy 데이터 조회 성공: {data['로트번호']}")
                    return True
                else:
                    logger.error(f"❌ 단일 Dummy 데이터 조회 실패: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 단일 Dummy 데이터 조회 테스트 중 오류: {str(e)}")
            return False
    
    async def test_update_dummy_data(self, data_id: int, update_data: Dict[str, Any]) -> bool:
        """Dummy 데이터 수정 테스트"""
        try:
            logger.info(f"📝 Dummy 데이터 수정 테스트 시작: ID {data_id}")
            
            async with self.session.put(
                f"{self.base_url}/dummy/{data_id}",
                json=update_data
            ) as response:
                if response.status == 200:
                    updated_data = await response.json()
                    logger.info(f"✅ Dummy 데이터 수정 성공: {updated_data['로트번호']}")
                    return True
                else:
                    error_detail = await response.text()
                    logger.error(f"❌ Dummy 데이터 수정 실패: {response.status} - {error_detail}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 수정 테스트 중 오류: {str(e)}")
            return False
    
    async def test_delete_dummy_data(self, data_id: int) -> bool:
        """Dummy 데이터 삭제 테스트"""
        try:
            logger.info(f"🗑️ Dummy 데이터 삭제 테스트 시작: ID {data_id}")
            
            async with self.session.delete(f"{self.base_url}/dummy/{data_id}") as response:
                if response.status == 200 or response.status == 204:
                    logger.info(f"✅ Dummy 데이터 삭제 성공: ID {data_id}")
                    return True
                else:
                    error_detail = await response.text()
                    logger.error(f"❌ Dummy 데이터 삭제 실패: {response.status} - {error_detail}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Dummy 데이터 삭제 테스트 중 오류: {str(e)}")
            return False
    
    async def test_bulk_operations(self) -> bool:
        """대량 작업 테스트"""
        try:
            logger.info("📦 대량 작업 테스트 시작")
            
            # 여러 Dummy 데이터 생성
            created_data = []
            for i in range(3):
                dummy_data = self.generate_test_dummy_data(f"대량테스트LOT_{i+1}")
                created_dummy = await self.test_create_dummy_data(dummy_data)
                if created_dummy:
                    created_data.append(created_dummy)
                    await asyncio.sleep(0.5)  # API 호출 간격 조절
            
            logger.info(f"✅ 대량 Dummy 데이터 생성 완료: {len(created_data)}개")
            
            # 생성된 데이터들 수정
            for data in created_data:
                update_data = {
                    "생산수량": round(random.uniform(200.0, 15000.0), 2),
                    "수량": round(random.uniform(100.0, 8000.0), 2)
                }
                await self.test_update_dummy_data(data['id'], update_data)
                await asyncio.sleep(0.3)
            
            logger.info("✅ 대량 Dummy 데이터 수정 완료")
            
            # 생성된 데이터들 삭제
            for data in created_data:
                await self.test_delete_dummy_data(data['id'])
                await asyncio.sleep(0.3)
            
            logger.info("✅ 대량 Dummy 데이터 삭제 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 대량 작업 테스트 중 오류: {str(e)}")
            return False
    
    async def test_error_handling(self) -> bool:
        """에러 처리 테스트"""
        try:
            logger.info("🚨 에러 처리 테스트 시작")
            
            # 존재하지 않는 데이터 조회
            async with self.session.get(f"{self.base_url}/dummy/99999") as response:
                if response.status == 404:
                    logger.info("✅ 404 에러 처리 정상")
                else:
                    logger.warning(f"⚠️ 예상과 다른 상태 코드: {response.status}")
            
            # 잘못된 데이터로 생성 시도
            invalid_data = {
                "로트번호": "",  # 빈 로트번호
                "생산품명": "테스트제품"
            }
            
            async with self.session.post(
                f"{self.base_url}/dummy/",
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
        logger.info("🚀 CBAM Dummy 도메인 종합 테스트 시작")
        logger.info(f"📍 테스트 대상: {self.base_url}/dummy")
        
        test_results = {}
        
        # 1. 도메인 상태 확인
        test_results['health_check'] = await self.test_health_check()
        
        if not test_results['health_check']:
            logger.error("❌ Dummy 도메인이 응답하지 않습니다. 테스트를 중단합니다.")
            return test_results
        
        # 2. 기본 CRUD 테스트
        test_results['get_all_dummy_data'] = await self.test_get_all_dummy_data()
        
        # 3. Dummy 데이터 생성 테스트
        test_dummy_data = self.generate_test_dummy_data("테스트LOT_기본")
        created_dummy = await self.test_create_dummy_data(test_dummy_data)
        test_results['create_dummy_data'] = created_dummy is not None
        
        if created_dummy:
            # 4. 단일 데이터 조회 테스트
            test_results['get_single_dummy_data'] = await self.test_get_single_dummy_data(created_dummy['id'])
            
            # 5. 데이터 수정 테스트
            update_data = {
                "생산수량": 9999.99,
                "수량": 8888.88
            }
            test_results['update_dummy_data'] = await self.test_update_dummy_data(created_dummy['id'], update_data)
            
            # 6. 데이터 삭제 테스트
            test_results['delete_dummy_data'] = await self.test_delete_dummy_data(created_dummy['id'])
        
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
            logger.info(f"{test_name:25} : {status}")
        
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
        }
    ]
    
    for config in test_configs:
        logger.info(f"\n🔧 {config['name']} 테스트 시작")
        logger.info(f"📍 URL: {config['url']}")
        
        try:
            async with CBAMDummyTester(config['url']) as tester:
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
