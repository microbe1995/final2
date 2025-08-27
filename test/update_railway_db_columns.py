#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Railway DB 컬럼명 업데이트 스크립트
스키마 변경사항에 맞춰 DB 컬럼명을 수정합니다.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# 환경변수에서 DB URL 가져오기
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

def connect_db():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        sys.exit(1)

def check_table_exists(conn, table_name):
    """테이블 존재 여부 확인"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (table_name,))
        return cursor.fetchone()[0]

def check_column_exists(conn, table_name, column_name):
    """컬럼 존재 여부 확인"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s 
                AND column_name = %s
            );
        """, (table_name, column_name))
        return cursor.fetchone()[0]

def update_install_table(conn):
    """Install 테이블 컬럼명 업데이트"""
    print("🔄 Install 테이블 업데이트 중...")
    
    # name 컬럼을 install_name으로 변경
    if check_column_exists(conn, 'install', 'name') and not check_column_exists(conn, 'install', 'install_name'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE install RENAME COLUMN name TO install_name;")
            print("✅ install.name → install.install_name 변경 완료")
    else:
        print("ℹ️ install 테이블은 이미 업데이트되었거나 변경이 필요하지 않습니다.")

def update_process_input_table(conn):
    """ProcessInput 테이블 컬럼명 업데이트"""
    print("🔄 ProcessInput 테이블 업데이트 중...")
    
    # amount 컬럼을 input_amount로 변경
    if check_column_exists(conn, 'process_input', 'amount') and not check_column_exists(conn, 'process_input', 'input_amount'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE process_input RENAME COLUMN amount TO input_amount;")
            print("✅ process_input.amount → process_input.input_amount 변경 완료")
    else:
        print("ℹ️ amount 컬럼은 이미 업데이트되었거나 변경이 필요하지 않습니다.")
    
    # direm_emission 컬럼을 direm으로 변경
    if check_column_exists(conn, 'process_input', 'direm_emission') and not check_column_exists(conn, 'process_input', 'direm'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE process_input RENAME COLUMN direm_emission TO direm;")
            print("✅ process_input.direm_emission → process_input.direm 변경 완료")
    else:
        print("ℹ️ direm_emission 컬럼은 이미 업데이트되었거나 변경이 필요하지 않습니다.")
    
    # indirem_emission 컬럼을 indirem으로 변경
    if check_column_exists(conn, 'process_input', 'indirem_emission') and not check_column_exists(conn, 'process_input', 'indirem'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE process_input RENAME COLUMN indirem_emission TO indirem;")
            print("✅ process_input.indirem_emission → process_input.indirem 변경 완료")
    else:
        print("ℹ️ indirem_emission 컬럼은 이미 업데이트되었거나 변경이 필요하지 않습니다.")

def verify_changes(conn):
    """변경사항 검증"""
    print("\n🔍 변경사항 검증 중...")
    
    # Install 테이블 확인
    if check_table_exists(conn, 'install'):
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'install' ORDER BY ordinal_position;")
            columns = [row['column_name'] for row in cursor.fetchall()]
            print(f"📋 Install 테이블 컬럼: {columns}")
    
    # ProcessInput 테이블 확인
    if check_table_exists(conn, 'process_input'):
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'process_input' ORDER BY ordinal_position;")
            columns = [row['column_name'] for row in cursor.fetchall()]
            print(f"📋 ProcessInput 테이블 컬럼: {columns}")

def main():
    """메인 함수"""
    print("🚀 Railway DB 컬럼명 업데이트 시작")
    print("=" * 50)
    
    conn = connect_db()
    
    try:
        # Install 테이블 업데이트
        if check_table_exists(conn, 'install'):
            update_install_table(conn)
        else:
            print("⚠️ install 테이블이 존재하지 않습니다.")
        
        # ProcessInput 테이블 업데이트
        if check_table_exists(conn, 'process_input'):
            update_process_input_table(conn)
        else:
            print("⚠️ process_input 테이블이 존재하지 않습니다.")
        
        # 변경사항 커밋
        conn.commit()
        print("\n✅ 모든 변경사항이 성공적으로 커밋되었습니다.")
        
        # 변경사항 검증
        verify_changes(conn)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
    finally:
        conn.close()
    
    print("\n🎉 Railway DB 컬럼명 업데이트 완료!")

if __name__ == "__main__":
    main()
