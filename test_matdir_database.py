#!/usr/bin/env python3
"""
matdir 데이터베이스 연결 및 테이블 생성 테스트
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

# Railway PostgreSQL URL
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def test_database_connection():
    """데이터베이스 연결 테스트"""
    print("🔍 데이터베이스 연결 테스트")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ 데이터베이스 연결 성공")
            print(f"📊 PostgreSQL 버전: {version[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {str(e)}")
        return False

def check_matdir_table():
    """matdir 테이블 존재 확인"""
    print("\n🔍 matdir 테이블 확인")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # matdir 테이블 존재 확인
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'matdir'
                );
            """)
            
            exists = cursor.fetchone()[0]
            
            if exists:
                print("✅ matdir 테이블이 존재합니다")
                
                # 테이블 구조 확인
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'matdir'
                    ORDER BY ordinal_position;
                """)
                
                columns = cursor.fetchall()
                print("📋 테이블 구조:")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
                
                # 데이터 개수 확인
                cursor.execute("SELECT COUNT(*) FROM matdir;")
                count = cursor.fetchone()[0]
                print(f"📊 현재 데이터 개수: {count}개")
                
            else:
                print("❌ matdir 테이블이 존재하지 않습니다")
        
        conn.close()
        return exists
        
    except Exception as e:
        print(f"❌ 테이블 확인 실패: {str(e)}")
        return False

def create_matdir_table():
    """matdir 테이블 생성"""
    print("\n🔨 matdir 테이블 생성")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # matdir 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matdir (
                    id SERIAL PRIMARY KEY,
                    process_id INTEGER NOT NULL,
                    mat_name VARCHAR(255) NOT NULL,
                    mat_factor NUMERIC(10, 6) NOT NULL,
                    mat_amount NUMERIC(15, 6) NOT NULL,
                    oxyfactor NUMERIC(5, 4) DEFAULT 1.0000,
                    matdir_em NUMERIC(15, 6) DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            print("✅ matdir 테이블 생성 완료")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {str(e)}")
        return False

def test_insert_matdir():
    """matdir 데이터 삽입 테스트"""
    print("\n💾 matdir 데이터 삽입 테스트")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 테스트 데이터 삽입
            test_data = {
                "process_id": 101,  # 실제 존재하는 process_id
                "mat_name": "테스트 철광석",
                "mat_factor": 1.5,
                "mat_amount": 100.0,
                "oxyfactor": 1.0,
                "matdir_em": 150.0  # 1.5 * 100.0 * 1.0
            }
            
            query = """
                INSERT INTO matdir (
                    process_id, mat_name, mat_factor, mat_amount, 
                    oxyfactor, matdir_em, created_at, updated_at
                ) VALUES (
                    %(process_id)s, %(mat_name)s, %(mat_factor)s, %(mat_amount)s,
                    %(oxyfactor)s, %(matdir_em)s, NOW(), NOW()
                ) RETURNING *
            """
            
            cursor.execute(query, test_data)
            result = cursor.fetchone()
            
            print(f"✅ 데이터 삽입 성공: ID {result['id']}")
            print(f"📊 삽입된 데이터: {json.dumps(dict(result), indent=2, ensure_ascii=False)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터 삽입 실패: {str(e)}")
        return False

def test_select_matdir():
    """matdir 데이터 조회 테스트"""
    print("\n📋 matdir 데이터 조회 테스트")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM matdir ORDER BY created_at DESC LIMIT 5;")
            results = cursor.fetchall()
            
            print(f"✅ 데이터 조회 성공: {len(results)}개")
            for i, row in enumerate(results, 1):
                print(f"📊 데이터 {i}: {json.dumps(dict(row), indent=2, ensure_ascii=False)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터 조회 실패: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 matdir 데이터베이스 테스트 시작")
    print()
    
    # 1. 데이터베이스 연결 테스트
    if not test_database_connection():
        print("❌ 데이터베이스 연결 실패로 테스트를 중단합니다.")
        exit(1)
    
    # 2. matdir 테이블 확인
    if not check_matdir_table():
        print("⚠️ matdir 테이블이 없어서 생성합니다.")
        if not create_matdir_table():
            print("❌ 테이블 생성 실패로 테스트를 중단합니다.")
            exit(1)
        check_matdir_table()  # 다시 확인
    
    # 3. 데이터 삽입 테스트
    test_insert_matdir()
    
    # 4. 데이터 조회 테스트
    test_select_matdir()
    
    print("\n✅ 모든 테스트 완료")
