#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product_backup 테이블 삭제 스크립트
Railway DB에서 product_backup 테이블을 삭제
"""

import asyncio
import asyncpg
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def delete_product_backup():
    """Product_backup 테이블 삭제"""
    
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
        
        # 1단계: product_backup 테이블 존재 여부 확인
        logger.info("🔍 1단계: product_backup 테이블 존재 여부 확인")
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'product_backup'
            );
        """)
        
        if not table_exists:
            logger.info("ℹ️ product_backup 테이블이 이미 존재하지 않습니다")
            return
        
        # 2단계: product_backup 테이블 정보 확인
        logger.info("🔍 2단계: product_backup 테이블 정보 확인")
        backup_info = await conn.fetch("""
            SELECT 
                COUNT(*) as record_count,
                pg_size_pretty(pg_total_relation_size('product_backup')) as table_size
            FROM product_backup
        """)
        
        if backup_info:
            record_count = backup_info[0]['record_count']
            table_size = backup_info[0]['table_size']
            logger.info(f"📊 product_backup 테이블: {record_count}개 레코드, {table_size}")
        
        # 3단계: product_backup 테이블 삭제
        logger.info("🗑️ 3단계: product_backup 테이블 삭제")
        await conn.execute("DROP TABLE IF EXISTS product_backup CASCADE")
        logger.info("✅ product_backup 테이블 삭제 완료")
        
        # 4단계: 삭제 확인
        logger.info("🔍 4단계: 삭제 확인")
        table_still_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'product_backup'
            );
        """)
        
        if not table_still_exists:
            logger.info("✅ product_backup 테이블이 성공적으로 삭제되었습니다")
        else:
            logger.error("❌ product_backup 테이블 삭제 실패")
        
        # 5단계: 현재 product 테이블 상태 확인
        logger.info("🔍 5단계: 현재 product 테이블 상태 확인")
        product_count = await conn.fetchval("SELECT COUNT(*) FROM product")
        logger.info(f"📊 현재 product 테이블 레코드 수: {product_count}개")
        
        # 연결 종료
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ product_backup 테이블 삭제 실패: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def main():
    """메인 함수"""
    logger.info("🚀 Product_backup 테이블 삭제 시작")
    await delete_product_backup()
    logger.info("🏁 삭제 완료")

if __name__ == "__main__":
    asyncio.run(main())
