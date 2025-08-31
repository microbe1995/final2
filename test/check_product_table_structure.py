#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product 테이블 구조 확인 스크립트
Railway DB에서 product 테이블의 현재 구조를 확인
"""

import asyncio
import asyncpg
import os
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_product_table_structure():
    """Product 테이블 구조 확인"""
    
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
        
        # 1단계: product 테이블 존재 여부 확인
        logger.info("🔍 1단계: product 테이블 존재 여부 확인")
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'product'
            );
        """)
        
        if table_exists:
            logger.info("✅ product 테이블이 존재합니다")
        else:
            logger.error("❌ product 테이블이 존재하지 않습니다")
            return
        
        # 2단계: product 테이블 구조 확인
        logger.info("🔍 2단계: product 테이블 구조 확인")
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
        
        # 3단계: 제약조건 확인
        logger.info("🔍 3단계: 제약조건 확인")
        constraints = await conn.fetch("""
            SELECT 
                constraint_name,
                constraint_type,
                table_name,
                column_name
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
        
        # 4단계: 인덱스 확인
        logger.info("🔍 4단계: 인덱스 확인")
        indexes = await conn.fetch("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE tablename = 'product'
            ORDER BY indexname
        """)
        
        if indexes:
            logger.info("📋 product 테이블 인덱스:")
            for index in indexes:
                logger.info(f"  - {index['indexname']}: {index['indexdef']}")
        else:
            logger.info("📋 인덱스가 없습니다")
        
        # 5단계: 레코드 수 확인
        logger.info("🔍 5단계: 레코드 수 확인")
        record_count = await conn.fetchval("SELECT COUNT(*) FROM product")
        logger.info(f"📊 product 테이블 레코드 수: {record_count}개")
        
        # 6단계: 샘플 데이터 확인 (있는 경우)
        if record_count > 0:
            logger.info("🔍 6단계: 샘플 데이터 확인")
            sample_data = await conn.fetch("SELECT * FROM product LIMIT 3")
            logger.info("📋 샘플 데이터:")
            for i, row in enumerate(sample_data, 1):
                logger.info(f"  레코드 {i}: {dict(row)}")
        
        # 7단계: 의존 관계 확인
        logger.info("🔍 7단계: 의존 관계 확인")
        dependencies = await conn.fetch("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND ccu.table_name = 'product'
        """)
        
        if dependencies:
            logger.info("📋 product 테이블을 참조하는 테이블들:")
            for dep in dependencies:
                logger.info(f"  - {dep['table_name']}.{dep['column_name']} → {dep['foreign_table_name']}.{dep['foreign_column_name']}")
        else:
            logger.info("📋 product 테이블을 참조하는 테이블이 없습니다")
        
        # 연결 종료
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ 테이블 구조 확인 실패: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def main():
    """메인 함수"""
    logger.info("🚀 Product 테이블 구조 확인 시작")
    await check_product_table_structure()
    logger.info("🏁 확인 완료")

if __name__ == "__main__":
    asyncio.run(main())
