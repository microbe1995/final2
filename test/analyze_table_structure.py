import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 데이터베이스 연결 정보
DATABASE_URL = 'postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway'

def analyze_table_structure():
    """현재 테이블 구조와 제약조건을 분석"""
    
    try:
        print("🔍 CBAM 서비스 테이블 구조 분석 중...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 1. matdir 테이블 구조 분석
        print("\n📋 matdir 테이블 구조:")
        print("=" * 50)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'matdir'
            ORDER BY ordinal_position
        """)
        matdir_columns = cursor.fetchall()
        for col in matdir_columns:
            print(f"  {col[0]}: {col[1]} (NULL: {col[2]}, DEFAULT: {col[3]})")
        
        # matdir 테이블 제약조건 확인
        print("\n🔒 matdir 테이블 제약조건:")
        cursor.execute("""
            SELECT constraint_name, constraint_type, table_name
            FROM information_schema.table_constraints 
            WHERE table_name = 'matdir'
        """)
        matdir_constraints = cursor.fetchall()
        for constraint in matdir_constraints:
            print(f"  {constraint[0]}: {constraint[1]}")
        
        # 2. fueldir 테이블 구조 분석
        print("\n📋 fueldir 테이블 구조:")
        print("=" * 50)
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'fueldir'
            ORDER BY ordinal_position
        """)
        fueldir_columns = cursor.fetchall()
        for col in fueldir_columns:
            print(f"  {col[0]}: {col[1]} (NULL: {col[2]}, DEFAULT: {col[3]})")
        
        # fueldir 테이블 제약조건 확인
        print("\n🔒 fueldir 테이블 제약조건:")
        cursor.execute("""
            SELECT constraint_name, constraint_type, table_name
            FROM information_schema.table_constraints 
            WHERE table_name = 'fueldir'
        """)
        fueldir_constraints = cursor.fetchall()
        for constraint in fueldir_constraints:
            print(f"  {constraint[0]}: {constraint[1]}")
        
        # 3. process 테이블 존재 확인
        print("\n📋 process 테이블 확인:")
        print("=" * 50)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'process'
            )
        """)
        process_exists = cursor.fetchone()[0]
        print(f"  process 테이블 존재: {process_exists}")
        
        if process_exists:
            cursor.execute("SELECT COUNT(*) FROM process")
            process_count = cursor.fetchone()[0]
            print(f"  process 테이블 레코드 수: {process_count}")
        
        # 4. 외래키 참조 확인
        print("\n🔗 외래키 참조 확인:")
        print("=" * 50)
        cursor.execute("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name IN ('matdir', 'fueldir')
        """)
        foreign_keys = cursor.fetchall()
        for fk in foreign_keys:
            print(f"  {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]}")
        
        # 5. 고아 데이터 확인
        print("\n⚠️ 고아 데이터 확인:")
        print("=" * 50)
        
        # matdir의 고아 데이터 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matdir m 
            LEFT JOIN process p ON m.process_id = p.id 
            WHERE p.id IS NULL
        """)
        orphan_matdir = cursor.fetchone()[0]
        print(f"  matdir 고아 데이터: {orphan_matdir}개")
        
        # fueldir의 고아 데이터 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM fueldir f 
            LEFT JOIN process p ON f.process_id = p.id 
            WHERE p.id IS NULL
        """)
        orphan_fueldir = cursor.fetchone()[0]
        print(f"  fueldir 고아 데이터: {orphan_fueldir}개")
        
        # 6. 중복 데이터 확인
        print("\n🔄 중복 데이터 확인:")
        print("=" * 50)
        
        # matdir 중복 확인
        cursor.execute("""
            SELECT process_id, mat_name, COUNT(*) as count
            FROM matdir 
            GROUP BY process_id, mat_name 
            HAVING COUNT(*) > 1
        """)
        duplicate_matdir = cursor.fetchall()
        print(f"  matdir 중복 데이터: {len(duplicate_matdir)}개 그룹")
        for dup in duplicate_matdir[:5]:  # 처음 5개만 표시
            print(f"    process_id={dup[0]}, mat_name='{dup[1]}': {dup[2]}개")
        
        # fueldir 중복 확인
        cursor.execute("""
            SELECT process_id, fuel_name, COUNT(*) as count
            FROM fueldir 
            GROUP BY process_id, fuel_name 
            HAVING COUNT(*) > 1
        """)
        duplicate_fueldir = cursor.fetchall()
        print(f"  fueldir 중복 데이터: {len(duplicate_fueldir)}개 그룹")
        for dup in duplicate_fueldir[:5]:  # 처음 5개만 표시
            print(f"    process_id={dup[0]}, fuel_name='{dup[1]}': {dup[2]}개")
        
        cursor.close()
        conn.close()
        
        print("\n✅ 테이블 구조 분석 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    analyze_table_structure()
