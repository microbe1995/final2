#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product 테이블 재구성 스크립트 (최종)
Railway DB에 접속하여 product 테이블을 재구성
"""

import asyncio
import asyncpg
import os
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def restructure_product_table():
    """Product 테이블 재구성"""
    
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
        
        # 0단계: 기존 백업 테이블 정리
        logger.info("🧹 0단계: 기존 백업 테이블 정리")
        await conn.execute("DROP TABLE IF EXISTS product_backup CASCADE")
        logger.info("✅ 기존 백업 테이블 삭제 완료")
        
        # 1단계: 의존 관계 확인
        logger.info("🔍 1단계: 의존 관계 확인")
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
        
        # 2단계: 기존 테이블 백업
        logger.info("📋 2단계: 기존 product 테이블 백업")
        await conn.execute("CREATE TABLE product_backup AS SELECT * FROM product")
        backup_count = await conn.fetchval("SELECT COUNT(*) FROM product_backup")
        logger.info(f"✅ 백업 완료: {backup_count}개 레코드")
        
        # 3단계: 의존 관계 해제 (외래키 제약조건 삭제)
        logger.info("🔗 3단계: 의존 관계 해제")
        for dep in dependencies:
            constraint_name = f"{dep['table_name']}_{dep['column_name']}_fkey"
            try:
                await conn.execute(f"ALTER TABLE {dep['table_name']} DROP CONSTRAINT IF EXISTS {constraint_name}")
                logger.info(f"✅ {dep['table_name']} 테이블의 외래키 제약조건 삭제")
            except Exception as e:
                logger.warning(f"⚠️ {dep['table_name']} 테이블의 외래키 제약조건 삭제 실패: {e}")
        
        # 4단계: 기존 product 테이블 삭제
        logger.info("🗑️ 4단계: 기존 product 테이블 삭제")
        await conn.execute("DROP TABLE IF EXISTS product CASCADE")
        logger.info("✅ 기존 테이블 삭제 완료")
        
        # 5단계: 새로운 product 테이블 생성 (단순화된 구조)
        logger.info("🏗️ 5단계: 새로운 product 테이블 생성")
        await conn.execute("""
            CREATE TABLE product (
                id SERIAL PRIMARY KEY,
                install_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                product_category TEXT NOT NULL,
                prostart_period DATE NOT NULL,
                proend_period DATE NOT NULL,
                cncode_total TEXT,
                goods_name TEXT,
                goods_engname TEXT,
                aggrgoods_name TEXT,
                aggrgoods_engname TEXT,
                product_amount NUMERIC(15, 6) DEFAULT 0,
                product_sell NUMERIC(15, 6) DEFAULT 0,
                product_eusell NUMERIC(15, 6) DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                CONSTRAINT unique_install_product UNIQUE(install_id, product_name),
                CONSTRAINT valid_period CHECK(prostart_period <= proend_period)
            )
        """)
        logger.info("✅ 새로운 product 테이블 생성 완료")
        
        # 6단계: 기존 데이터 복원
        logger.info("📊 6단계: 기존 데이터 복원")
        await conn.execute("""
            INSERT INTO product (
                install_id, product_name, product_category, prostart_period, proend_period,
                cncode_total, goods_name, goods_engname, aggrgoods_name, aggrgoods_engname,
                product_amount, product_sell, product_eusell, created_at, updated_at
            )
            SELECT 
                install_id, product_name, product_category, prostart_period, proend_period,
                cncode_total, goods_name, goods_engname, aggrgoods_name, aggrgoods_engname,
                COALESCE(product_amount, 0), COALESCE(product_sell, 0), COALESCE(product_eusell, 0),
                created_at, updated_at
            FROM product_backup
        """)
        restored_count = await conn.fetchval("SELECT COUNT(*) FROM product")
        logger.info(f"✅ 데이터 복원 완료: {restored_count}개 레코드")
        
        # 7단계: 외래키 제약조건 복원
        logger.info("🔗 7단계: 외래키 제약조건 복원")
        for dep in dependencies:
            try:
                await conn.execute(f"""
                    ALTER TABLE {dep['table_name']} 
                    ADD CONSTRAINT {dep['table_name']}_{dep['column_name']}_fkey 
                    FOREIGN KEY ({dep['column_name']}) REFERENCES product(id)
                """)
                logger.info(f"✅ {dep['table_name']} 테이블의 외래키 제약조건 복원")
            except Exception as e:
                logger.warning(f"⚠️ {dep['table_name']} 테이블의 외래키 제약조건 복원 실패: {e}")
        
        # 8단계: 인덱스 생성
        logger.info("📈 8단계: 인덱스 생성")
        await conn.execute("CREATE INDEX idx_product_install_id ON product(install_id)")
        await conn.execute("CREATE INDEX idx_product_product_name ON product(product_name)")
        logger.info("✅ 인덱스 생성 완료")
        
        # 9단계: 결과 확인
        logger.info("🔍 9단계: 결과 확인")
        result = await conn.fetch("""
            SELECT 'product' as table_name, COUNT(*) as record_count FROM product
            UNION ALL
            SELECT 'product_backup' as table_name, COUNT(*) as record_count FROM product_backup
        """)
        
        for row in result:
            logger.info(f"📊 {row['table_name']}: {row['record_count']}개 레코드")
        
        # 10단계: 테이블 구조 확인
        logger.info("🔍 10단계: 테이블 구조 확인")
        structure = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'product' 
            ORDER BY ordinal_position
        """)
        
        logger.info("📋 새로운 product 테이블 구조:")
        for col in structure:
            logger.info(f"  - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
        
        logger.info("🎉 Product 테이블 재구성 완료!")
        
        # 연결 종료
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ 테이블 재구성 실패: {str(e)}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")

async def main():
    """메인 함수"""
    logger.info("🚀 Product 테이블 재구성 시작")
    await restructure_product_table()
    logger.info("🏁 작업 완료")

if __name__ == "__main__":
    asyncio.run(main())
