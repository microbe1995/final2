#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수정된 제품 생성 API 테스트 스크립트
언패킹 문제 해결 후 테스트
"""

import asyncio
import httpx
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_product_creation_fixed():
    """수정된 제품 생성 API 테스트"""
    
    try:
        async with httpx.AsyncClient() as client:
            # 1단계: 사업장 목록 조회
            logger.info("🔍 1단계: 사업장 목록 조회")
            response = await client.get("https://gateway-production-22ef.up.railway.app/api/v1/cbam/install")
            
            if response.status_code != 200:
                logger.error(f"❌ 사업장 목록 조회 실패: {response.status_code}")
                return
            
            installs = response.json()
            logger.info(f"✅ 사업장 {len(installs)}개 조회 성공")
            
            if not installs:
                logger.error("❌ 사업장이 없습니다")
                return
            
            # 첫 번째 사업장의 ID 사용
            install_id = installs[0]['id']
            logger.info(f"🔧 사용할 install_id: {install_id}")
            
            # 2단계: 제품 생성 테스트
            logger.info("🔍 2단계: 제품 생성 테스트")
            
            # 테스트 데이터 (5개 핵심 필드만)
            test_product = {
                "install_id": install_id,
                "product_name": f"테스트제품_{datetime.now().strftime('%H%M%S')}",
                "product_category": "단순제품",
                "prostart_period": "2024-01-01",
                "proend_period": "2024-12-31"
            }
            
            logger.info(f"📋 테스트 데이터: {test_product}")
            
            # 제품 생성 요청
            create_response = await client.post(
                "https://gateway-production-22ef.up.railway.app/api/v1/cbam/product",
                json=test_product
            )
            
            logger.info(f"📊 제품 생성 응답: {create_response.status_code}")
            
            if create_response.status_code == 201 or create_response.status_code == 200:
                created_product = create_response.json()
                logger.info(f"✅ 제품 생성 성공: {created_product}")
                
                # 3단계: 생성된 제품 조회
                logger.info("🔍 3단계: 생성된 제품 조회")
                product_id = created_product.get('id')
                
                if product_id:
                    get_response = await client.get(f"https://gateway-production-22ef.up.railway.app/api/v1/cbam/product/{product_id}")
                    
                    if get_response.status_code == 200:
                        retrieved_product = get_response.json()
                        logger.info(f"✅ 제품 조회 성공: {retrieved_product}")
                    else:
                        logger.error(f"❌ 제품 조회 실패: {get_response.status_code}")
                else:
                    logger.error("❌ 생성된 제품의 ID를 찾을 수 없습니다")
                    
            else:
                logger.error(f"❌ 제품 생성 실패: {create_response.status_code}")
                logger.error(f"응답 내용: {create_response.text}")
                
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def main():
    """메인 함수"""
    logger.info("🚀 수정된 제품 생성 API 테스트 시작")
    await test_product_creation_fixed()
    logger.info("🏁 테스트 완료")

if __name__ == "__main__":
    asyncio.run(main())
