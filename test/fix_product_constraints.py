#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product 테이블 제약조건 수정 스크립트
Railway DB에서 잘못된 UNIQUE 제약조건을 복합 UNIQUE로 수정
"""

import asyncio
import asyncpg
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_product_constraints():
    """Product 테이블 제약조건 수정"""
    
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
        
        # 1단계: 현재 제약조건 확인
        logger.info("🔍 1단계: 현재 제약조건 확인")
        current_constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'product' AND tc.constraint_type = 'UNIQUE'
            ORDER BY tc.constraint_name
        """)
        
        logger.info("📋 현재 UNIQUE 제약조건:")
        for constraint in current_constraints:
            logger.info(f"  - {constraint['constraint_name']}: {constraint['column_name']}")
        
        # 2단계: 잘못된 제약조건 삭제
        logger.info("🔍 2단계: 잘못된 제약조건 삭제")
        for constraint in current_constraints:
            if constraint['constraint_name'] == 'unique_install_product':
                try:
                    await conn.execute(f"ALTER TABLE product DROP CONSTRAINT IF EXISTS {constraint['constraint_name']}")
                    logger.info(f"✅ 제약조건 삭제: {constraint['constraint_name']}")
                except Exception as e:
                    logger.warning(f"⚠️ 제약조건 삭제 실패: {constraint['constraint_name']} - {e}")
        
        # 3단계: 올바른 복합 UNIQUE 제약조건 생성
        logger.info("🔍 3단계: 올바른 복합 UNIQUE 제약조건 생성")
        try:
            await conn.execute("""
                ALTER TABLE product 
                ADD CONSTRAINT unique_install_product_name 
                UNIQUE (install_id, product_name)
            """)
            logger.info("✅ 복합 UNIQUE 제약조건 생성 완료: (install_id, product_name)")
        except Exception as e:
            logger.error(f"❌ 복합 UNIQUE 제약조건 생성 실패: {e}")
        
        # 4단계: 제약조건 확인
        logger.info("🔍 4단계: 수정된 제약조건 확인")
        new_constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'product' AND tc.constraint_type = 'UNIQUE'
            GROUP BY tc.constraint_name, tc.constraint_type
            ORDER BY tc.constraint_name
        """)
        
        logger.info("📋 수정된 UNIQUE 제약조건:")
        for constraint in new_constraints:
            logger.info(f"  - {constraint['constraint_name']}: {constraint['columns']}")
        
        # 5단계: 테스트 INSERT 시도
        logger.info("🔍 5단계: 테스트 INSERT 시도")
        try:
            # 테스트 데이터 준비 (5개 핵심 필드만)
            test_data = {
                'install_id': 9,  # 실제 존재하는 install ID
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
                ) VALUES ($1, $2, $3, $4::date, $5::date)
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
        
        # 연결 종료
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ 제약조건 수정 실패: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def main():
    """메인 함수"""
    logger.info("🚀 Product 테이블 제약조건 수정 시작")
    await fix_product_constraints()
    logger.info("🏁 수정 완료")

if __name__ == "__main__":
    asyncio.run(main())
