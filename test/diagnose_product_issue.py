#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
제품 저장 실패 문제 진단 스크립트
Railway DB와 API 상태를 종합적으로 확인
"""

import asyncio
import asyncpg
import os
import logging
import httpx
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def diagnose_product_issue():
    """제품 저장 실패 문제 진단"""
    
    # DATABASE_URL 환경변수에서 가져오기
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        # 데이터베이스 연결
        logger.info("🔌 Railway DB에 연결 중...")
        conn = await asyncpg.connect(database_url)
        logger.info("✅ Railway DB 연결 성공")
        
        # 1단계: product 테이블 구조 확인
        logger.info("🔍 1단계: product 테이블 구조 확인")
        structure = await conn.fetch("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default,
                ordinal_position
            FROM information_schema.columns 
            WHERE table_name = 'product' 
            ORDER BY ordinal_position
        """)
        
        logger.info("📋 product 테이블 구조:")
        for col in structure:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            logger.info(f"  {col['ordinal_position']:2d}. {col['column_name']:<20} {col['data_type']:<20} {nullable}{default}")
        
        # 2단계: product 테이블 제약조건 확인
        logger.info("🔍 2단계: product 테이블 제약조건 확인")
        constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'product'
            ORDER BY tc.constraint_type, tc.constraint_name
        """)
        
        if constraints:
            logger.info("📋 product 테이블 제약조건:")
            for constraint in constraints:
                logger.info(f"  - {constraint['constraint_type']}: {constraint['constraint_name']} ({constraint['column_name']})")
        else:
            logger.info("📋 제약조건이 없습니다")
        
        # 3단계: product 테이블 레코드 수 확인
        logger.info("🔍 3단계: product 테이블 레코드 수 확인")
        record_count = await conn.fetchval("SELECT COUNT(*) FROM product")
        logger.info(f"📊 product 테이블 레코드 수: {record_count}개")
        
        # 4단계: install 테이블 확인 (외래키 관계)
        logger.info("🔍 4단계: install 테이블 확인")
        install_count = await conn.fetchval("SELECT COUNT(*) FROM install")
        logger.info(f"📊 install 테이블 레코드 수: {install_count}개")
        
        if install_count > 0:
            install_sample = await conn.fetch("SELECT id, install_name FROM install LIMIT 3")
            logger.info("📋 install 테이블 샘플:")
            for install in install_sample:
                logger.info(f"  - ID: {install['id']}, 이름: {install['install_name']}")
        
        # 5단계: 테스트 데이터로 INSERT 시도
        logger.info("🔍 5단계: 테스트 데이터로 INSERT 시도")
        try:
            # 테스트 데이터 준비 (5개 핵심 필드만)
            test_data = {
                'install_id': 1,  # 첫 번째 install ID 사용
                'product_name': '테스트 제품',
                'product_category': '단순제품',
                'prostart_period': '2024-01-01',
                'proend_period': '2024-12-31'
            }
            
            # INSERT 쿼리 실행
            result = await conn.fetchrow("""
                INSERT INTO product (
                    install_id, product_name, product_category, 
                    prostart_period, proend_period
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING id, install_id, product_name
            """, 
            test_data['install_id'], 
            test_data['product_name'], 
            test_data['product_category'],
            test_data['prostart_period'], 
            test_data['proend_period']
            )
            
            logger.info(f"✅ 테스트 INSERT 성공: {result}")
            
            # 테스트 데이터 삭제
            await conn.execute("DELETE FROM product WHERE id = $1", result['id'])
            logger.info("✅ 테스트 데이터 삭제 완료")
            
        except Exception as e:
            logger.error(f"❌ 테스트 INSERT 실패: {str(e)}")
            logger.error(f"상세 오류: {e}")
        
        # 6단계: API 엔드포인트 테스트
        logger.info("🔍 6단계: API 엔드포인트 테스트")
        try:
            async with httpx.AsyncClient() as client:
                # Gateway 상태 확인
                gateway_url = "https://gateway-production-22ef.up.railway.app"
                response = await client.get(f"{gateway_url}/health", timeout=10.0)
                logger.info(f"🌐 Gateway 상태: {response.status_code}")
                
                # CBAM 서비스 상태 확인
                cbam_response = await client.get(f"{gateway_url}/api/v1/cbam/product", timeout=10.0)
                logger.info(f"📦 CBAM Product API 상태: {cbam_response.status_code}")
                
                if cbam_response.status_code == 200:
                    products = cbam_response.json()
                    logger.info(f"📊 현재 제품 수: {len(products)}개")
                else:
                    logger.error(f"❌ CBAM Product API 오류: {cbam_response.text}")
                    
        except Exception as e:
            logger.error(f"❌ API 테스트 실패: {str(e)}")
        
        # 연결 종료
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ 진단 실패: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def main():
    """메인 함수"""
    logger.info("🚀 제품 저장 실패 문제 진단 시작")
    await diagnose_product_issue()
    logger.info("🏁 진단 완료")

if __name__ == "__main__":
    asyncio.run(main())
