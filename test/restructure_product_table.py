#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product 테이블 재구성 스크립트
Railway DB에 접속하여 product 테이블을 product_core와 product_detail로 분리
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
    """Product 테이블을 product_core와 product_detail로 재구성"""
    
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
        
        # 1단계: 기존 테이블 백업
        logger.info("📋 1단계: 기존 product 테이블 백업")
        await conn.execute("CREATE TABLE product_backup AS SELECT * FROM product")
        backup_count = await conn.fetchval("SELECT COUNT(*) FROM product_backup")
        logger.info(f"✅ 백업 완료: {backup_count}개 레코드")
        
        # 2단계: 기존 product 테이블 삭제
        logger.info("🗑️ 2단계: 기존 product 테이블 삭제")
        await conn.execute("DROP TABLE IF EXISTS product")
        logger.info("✅ 기존 테이블 삭제 완료")
        
        # 3단계: product_core 테이블 생성
        logger.info("🏗️ 3단계: product_core 테이블 생성")
        await conn.execute("""
            CREATE TABLE product_core (
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
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                
                CONSTRAINT unique_install_product UNIQUE(install_id, product_name),
                CONSTRAINT valid_period CHECK(prostart_period <= proend_period)
            )
        """)
        logger.info("✅ product_core 테이블 생성 완료")
        
        # 4단계: product_detail 테이블 생성
        logger.info("🏗️ 4단계: product_detail 테이블 생성")
        await conn.execute("""
            CREATE TABLE product_detail (
                id SERIAL PRIMARY KEY,
                product_core_id INTEGER NOT NULL,
                product_amount NUMERIC(15, 6) DEFAULT 0,
                product_sell NUMERIC(15, 6) DEFAULT 0,
                product_eusell NUMERIC(15, 6) DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        logger.info("✅ product_detail 테이블 생성 완료")
        
        # 5단계: 기존 데이터 마이그레이션 (핵심 정보만)
        logger.info("📊 5단계: 핵심 정보 마이그레이션")
        await conn.execute("""
            INSERT INTO product_core (
                install_id, product_name, product_category, prostart_period, proend_period,
                cncode_total, goods_name, goods_engname, aggrgoods_name, aggrgoods_engname,
                created_at, updated_at
            )
            SELECT 
                install_id, product_name, product_category, prostart_period, proend_period,
                cncode_total, goods_name, goods_engname, aggrgoods_name, aggrgoods_engname,
                created_at, updated_at
            FROM product_backup
        """)
        core_count = await conn.fetchval("SELECT COUNT(*) FROM product_core")
        logger.info(f"✅ 핵심 정보 마이그레이션 완료: {core_count}개 레코드")
        
        # 6단계: 기존 데이터 마이그레이션 (상세 정보)
        logger.info("📊 6단계: 상세 정보 마이그레이션")
        await conn.execute("""
            INSERT INTO product_detail (
                product_core_id, product_amount, product_sell, product_eusell, created_at, updated_at
            )
            SELECT 
                pc.id, pb.product_amount, pb.product_sell, pb.product_eusell, pb.created_at, pb.updated_at
            FROM product_backup pb
            JOIN product_core pc ON pb.install_id = pc.install_id AND pb.product_name = pc.product_name
        """)
        detail_count = await conn.fetchval("SELECT COUNT(*) FROM product_detail")
        logger.info(f"✅ 상세 정보 마이그레이션 완료: {detail_count}개 레코드")
        
        # 7단계: 외래키 제약조건 추가
        logger.info("🔗 7단계: 외래키 제약조건 추가")
        await conn.execute("""
            ALTER TABLE product_detail 
            ADD CONSTRAINT fk_product_detail_core 
            FOREIGN KEY (product_core_id) REFERENCES product_core(id) ON DELETE CASCADE
        """)
        logger.info("✅ 외래키 제약조건 추가 완료")
        
        # 8단계: 인덱스 생성
        logger.info("📈 8단계: 인덱스 생성")
        await conn.execute("CREATE INDEX idx_product_core_install_id ON product_core(install_id)")
        await conn.execute("CREATE INDEX idx_product_core_product_name ON product_core(product_name)")
        await conn.execute("CREATE INDEX idx_product_detail_core_id ON product_detail(product_core_id)")
        logger.info("✅ 인덱스 생성 완료")
        
        # 9단계: 결과 확인
        logger.info("🔍 9단계: 결과 확인")
        result = await conn.fetch("""
            SELECT 'product_core' as table_name, COUNT(*) as record_count FROM product_core
            UNION ALL
            SELECT 'product_detail' as table_name, COUNT(*) as record_count FROM product_detail
            UNION ALL
            SELECT 'product_backup' as table_name, COUNT(*) as record_count FROM product_backup
        """)
        
        for row in result:
            logger.info(f"📊 {row['table_name']}: {row['record_count']}개 레코드")
        
        # 10단계: 테이블 구조 확인
        logger.info("🔍 10단계: 테이블 구조 확인")
        core_structure = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'product_core' 
            ORDER BY ordinal_position
        """)
        
        detail_structure = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'product_detail' 
            ORDER BY ordinal_position
        """)
        
        logger.info("📋 product_core 테이블 구조:")
        for col in core_structure:
            logger.info(f"  - {col['column_name']}: {col['data_type']} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}")
        
        logger.info("📋 product_detail 테이블 구조:")
        for col in detail_structure:
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
