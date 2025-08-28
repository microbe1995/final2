#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product 테이블의 product_cncode 컬럼을 cncode_total로 변경하는 스크립트
"""

import psycopg2
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def rename_product_cncode_column():
    """Product 테이블의 product_cncode 컬럼을 cncode_total로 변경"""
    
    conn = None
    cursor = None
    
    try:
        # 데이터베이스 연결
        print("🔗 데이터베이스 연결 중...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 현재 테이블 구조 확인
        print("📋 현재 Product 테이블 구조 확인...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'product' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("현재 컬럼들:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
        
        # 컬럼명 변경
        print("\n🔧 product_cncode 컬럼을 cncode_total로 변경 중...")
        
        try:
            cursor.execute("""
                ALTER TABLE product 
                RENAME COLUMN product_cncode TO cncode_total;
            """)
            print("✅ product_cncode 컬럼을 cncode_total로 변경 완료")
        except psycopg2.errors.UndefinedColumn:
            print("⚠️ product_cncode 컬럼이 존재하지 않습니다")
        except psycopg2.errors.DuplicateColumn:
            print("⚠️ cncode_total 컬럼이 이미 존재합니다")
        
        # 변경사항 커밋
        conn.commit()
        
        # 업데이트된 테이블 구조 확인
        print("\n📋 업데이트된 Product 테이블 구조 확인...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'product' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("업데이트된 컬럼들:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}, nullable: {col[2]})")
        
        # 샘플 데이터 확인
        print("\n📊 샘플 데이터 확인...")
        cursor.execute("""
            SELECT id, product_name, cncode_total, goods_name, goods_engname, 
                   aggrgoods_name, aggrgoods_engname
            FROM product 
            LIMIT 5;
        """)
        
        products = cursor.fetchall()
        if products:
            print("샘플 제품 데이터:")
            for product in products:
                print(f"  ID: {product[0]}, 제품명: {product[1]}")
                print(f"    CN 코드: {product[2]}")
                print(f"    품목명: {product[3]}")
                print(f"    품목영문명: {product[4]}")
                print(f"    품목군명: {product[5]}")
                print(f"    품목군영문명: {product[6]}")
                print()
        else:
            print("등록된 제품이 없습니다")
        
        print("🎉 Product 테이블 컬럼명 변경 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("🔌 데이터베이스 연결 종료")

if __name__ == "__main__":
    rename_product_cncode_column()
