#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
제품 생성 API 테스트 스크립트
"""

import asyncio
import httpx
import json
from datetime import date, datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 테스트 환경 설정
GATEWAY_URL = "https://gateway-production-22ef.up.railway.app"
API_BASE = f"{GATEWAY_URL}/api/v1/cbam"

async def test_product_creation():
    """제품 생성 API 테스트"""
    
    # 테스트용 제품 데이터
    test_product = {
        "install_id": 1,  # 사업장 ID (실제 존재하는 ID 사용)
        "product_name": "테스트 제품",
        "product_category": "단순제품",
        "prostart_period": "2024-01-01",
        "proend_period": "2024-12-31",
        "product_amount": 100.0,
        "cncode_total": "TEST001",
        "goods_name": "테스트 품목",
        "goods_engname": "Test Item",
        "aggrgoods_name": "테스트 품목군",
        "aggrgoods_engname": "Test Item Group",
        "product_sell": 50.0,
        "product_eusell": 30.0
    }
    
    logger.info("🧪 제품 생성 API 테스트 시작")
    logger.info(f"📋 테스트 데이터: {json.dumps(test_product, indent=2, ensure_ascii=False)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # 1. 사업장 목록 조회 (install_id 확인용)
            logger.info("🔍 1단계: 사업장 목록 조회")
            response = await client.get(f"{API_BASE}/install")
            logger.info(f"📊 사업장 목록 응답: {response.status_code}")
            
            if response.status_code == 200:
                installs = response.json()
                logger.info(f"✅ 사업장 {len(installs)}개 조회 성공")
                if installs:
                    # 첫 번째 사업장 ID 사용
                    test_product["install_id"] = installs[0]["id"]
                    logger.info(f"🔧 install_id 업데이트: {test_product['install_id']}")
            else:
                logger.warning(f"⚠️ 사업장 목록 조회 실패: {response.status_code}")
                logger.warning(f"응답 내용: {response.text}")
            
            # 2. 제품 생성 테스트
            logger.info("🔍 2단계: 제품 생성")
            response = await client.post(
                f"{API_BASE}/product",
                json=test_product,
                headers={"Content-Type": "application/json"}
            )
            
            logger.info(f"📊 제품 생성 응답: {response.status_code}")
            
            if response.status_code == 200:
                created_product = response.json()
                logger.info("✅ 제품 생성 성공!")
                logger.info(f"생성된 제품: {json.dumps(created_product, indent=2, ensure_ascii=False)}")
                
                # 3. 생성된 제품 조회 테스트
                logger.info("🔍 3단계: 생성된 제품 조회")
                product_id = created_product["id"]
                response = await client.get(f"{API_BASE}/product/{product_id}")
                
                if response.status_code == 200:
                    retrieved_product = response.json()
                    logger.info("✅ 제품 조회 성공!")
                    logger.info(f"조회된 제품: {json.dumps(retrieved_product, indent=2, ensure_ascii=False)}")
                else:
                    logger.error(f"❌ 제품 조회 실패: {response.status_code}")
                    logger.error(f"응답 내용: {response.text}")
                
            elif response.status_code == 500:
                logger.error("❌ 500 Internal Server Error 발생")
                logger.error(f"응답 내용: {response.text}")
                
                # 에러 상세 분석
                try:
                    error_detail = response.json()
                    logger.error(f"에러 상세: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    logger.error(f"에러 응답 파싱 실패: {response.text}")
                    
            else:
                logger.error(f"❌ 제품 생성 실패: {response.status_code}")
                logger.error(f"응답 내용: {response.text}")
                
    except Exception as e:
        logger.error(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def test_product_list():
    """제품 목록 조회 테스트"""
    
    logger.info("🧪 제품 목록 조회 API 테스트")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{API_BASE}/product")
            
            logger.info(f"📊 제품 목록 응답: {response.status_code}")
            
            if response.status_code == 200:
                products = response.json()
                logger.info(f"✅ 제품 목록 조회 성공: {len(products)}개")
                if products:
                    logger.info(f"첫 번째 제품: {json.dumps(products[0], indent=2, ensure_ascii=False)}")
            else:
                logger.error(f"❌ 제품 목록 조회 실패: {response.status_code}")
                logger.error(f"응답 내용: {response.text}")
                
    except Exception as e:
        logger.error(f"❌ 제품 목록 조회 테스트 중 오류: {str(e)}")

async def main():
    """메인 테스트 함수"""
    logger.info("🚀 제품 API 종합 테스트 시작")
    
    # 1. 제품 목록 조회 테스트
    await test_product_list()
    
    # 2. 제품 생성 테스트
    await test_product_creation()
    
    logger.info("🏁 테스트 완료")

if __name__ == "__main__":
    asyncio.run(main())
