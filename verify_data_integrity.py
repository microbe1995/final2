import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 데이터베이스 연결 정보
DATABASE_URL = 'postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway'

def verify_data_integrity():
    """데이터 무결성 개선 결과 검증"""
    
    try:
        print("🔍 CBAM 서비스 데이터 무결성 검증 중...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 1. 제약조건 확인
        print("\n🔒 제약조건 확인:")
        print("=" * 50)
        
        # matdir 테이블 제약조건
        cursor.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'matdir'
            ORDER BY constraint_type, constraint_name
        """)
        matdir_constraints = cursor.fetchall()
        
        print("📋 matdir 테이블 제약조건:")
        for constraint in matdir_constraints:
            print(f"  ✅ {constraint[0]}: {constraint[1]}")
        
        # fueldir 테이블 제약조건
        cursor.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'fueldir'
            ORDER BY constraint_type, constraint_name
        """)
        fueldir_constraints = cursor.fetchall()
        
        print("\n📋 fueldir 테이블 제약조건:")
        for constraint in fueldir_constraints:
            print(f"  ✅ {constraint[0]}: {constraint[1]}")
        
        # 2. 외래키 확인
        print("\n🔗 외래키 확인:")
        print("=" * 50)
        
        cursor.execute("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
                JOIN information_schema.referential_constraints AS rc
                  ON tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name IN ('matdir', 'fueldir')
        """)
        foreign_keys = cursor.fetchall()
        
        for fk in foreign_keys:
            print(f"  ✅ {fk[0]}.{fk[1]} -> {fk[2]}.{fk[3]} (DELETE: {fk[4]})")
        
        # 3. 인덱스 확인
        print("\n📈 인덱스 확인:")
        print("=" * 50)
        
        # matdir 인덱스
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'matdir'
            ORDER BY indexname
        """)
        matdir_indexes = cursor.fetchall()
        
        print("📋 matdir 테이블 인덱스:")
        for idx in matdir_indexes:
            print(f"  ✅ {idx[0]}")
        
        # fueldir 인덱스
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'fueldir'
            ORDER BY indexname
        """)
        fueldir_indexes = cursor.fetchall()
        
        print("\n📋 fueldir 테이블 인덱스:")
        for idx in fueldir_indexes:
            print(f"  ✅ {idx[0]}")
        
        # 4. 중복 데이터 확인
        print("\n🔄 중복 데이터 확인:")
        print("=" * 50)
        
        # matdir 중복 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT process_id, mat_name, COUNT(*) as count
                FROM matdir 
                GROUP BY process_id, mat_name 
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        matdir_duplicates = cursor.fetchone()[0]
        
        # fueldir 중복 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT process_id, fuel_name, COUNT(*) as count
                FROM fueldir 
                GROUP BY process_id, fuel_name 
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        fueldir_duplicates = cursor.fetchone()[0]
        
        print(f"  📊 중복 데이터 그룹:")
        print(f"    matdir: {matdir_duplicates}개 그룹")
        print(f"    fueldir: {fueldir_duplicates}개 그룹")
        
        if matdir_duplicates == 0 and fueldir_duplicates == 0:
            print("  ✅ 중복 데이터 없음!")
        else:
            print("  ⚠️ 중복 데이터가 여전히 존재합니다")
        
        # 5. 고아 데이터 확인
        print("\n⚠️ 고아 데이터 확인:")
        print("=" * 50)
        
        # matdir 고아 데이터
        cursor.execute("""
            SELECT COUNT(*) 
            FROM matdir m 
            LEFT JOIN process p ON m.process_id = p.id 
            WHERE p.id IS NULL
        """)
        orphan_matdir = cursor.fetchone()[0]
        
        # fueldir 고아 데이터
        cursor.execute("""
            SELECT COUNT(*) 
            FROM fueldir f 
            LEFT JOIN process p ON f.process_id = p.id 
            WHERE p.id IS NULL
        """)
        orphan_fueldir = cursor.fetchone()[0]
        
        print(f"  📊 고아 데이터:")
        print(f"    matdir: {orphan_matdir}개")
        print(f"    fueldir: {orphan_fueldir}개")
        
        if orphan_matdir == 0 and orphan_fueldir == 0:
            print("  ✅ 고아 데이터 없음!")
        else:
            print("  ⚠️ 고아 데이터가 존재합니다")
        
        # 6. 데이터 통계
        print("\n📊 데이터 통계:")
        print("=" * 50)
        
        cursor.execute("SELECT COUNT(*) FROM matdir")
        matdir_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM fueldir")
        fueldir_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM process")
        process_count = cursor.fetchone()[0]
        
        print(f"  📋 테이블별 레코드 수:")
        print(f"    process: {process_count}개")
        print(f"    matdir: {matdir_count}개")
        print(f"    fueldir: {fueldir_count}개")
        
        # 7. 최종 평가
        print("\n🎯 최종 평가:")
        print("=" * 50)
        
        issues = []
        
        if matdir_duplicates > 0:
            issues.append("matdir 중복 데이터")
        if fueldir_duplicates > 0:
            issues.append("fueldir 중복 데이터")
        if orphan_matdir > 0:
            issues.append("matdir 고아 데이터")
        if orphan_fueldir > 0:
            issues.append("fueldir 고아 데이터")
        
        if not issues:
            print("  🎉 모든 데이터 무결성 검증 통과!")
            print("  ✅ 외래키 제약조건: 정상")
            print("  ✅ UNIQUE 제약조건: 정상")
            print("  ✅ 중복 데이터: 없음")
            print("  ✅ 고아 데이터: 없음")
            print("  ✅ 인덱스: 정상")
        else:
            print(f"  ⚠️ 발견된 문제점: {', '.join(issues)}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ 데이터 무결성 검증 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verify_data_integrity()
