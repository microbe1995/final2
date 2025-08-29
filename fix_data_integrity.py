import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 데이터베이스 연결 정보
DATABASE_URL = 'postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway'

def fix_data_integrity():
    """데이터 무결성 개선"""
    
    try:
        print("🔧 CBAM 서비스 데이터 무결성 개선 중...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 1. 중복 데이터 정리
        print("\n🔄 중복 데이터 정리 중...")
        
        # matdir 중복 데이터 확인 및 정리
        cursor.execute("""
            SELECT process_id, mat_name, COUNT(*) as count
            FROM matdir 
            GROUP BY process_id, mat_name 
            HAVING COUNT(*) > 1
        """)
        duplicate_matdir = cursor.fetchall()
        
        if duplicate_matdir:
            print(f"  📋 matdir 중복 데이터 {len(duplicate_matdir)}개 그룹 발견")
            
            for dup in duplicate_matdir:
                process_id, mat_name, count = dup
                print(f"    🔍 process_id={process_id}, mat_name='{mat_name}': {count}개")
                
                # 중복 데이터 중 가장 최근 것만 남기고 나머지 삭제
                cursor.execute("""
                    DELETE FROM matdir 
                    WHERE id NOT IN (
                        SELECT id FROM (
                            SELECT id, ROW_NUMBER() OVER (
                                PARTITION BY process_id, mat_name 
                                ORDER BY created_at DESC
                            ) as rn
                            FROM matdir 
                            WHERE process_id = %s AND mat_name = %s
                        ) ranked 
                        WHERE rn = 1
                    )
                    AND process_id = %s AND mat_name = %s
                """, (process_id, mat_name, process_id, mat_name))
                
                deleted_count = cursor.rowcount
                print(f"      ✅ {deleted_count}개 중복 데이터 삭제 완료")
        
        # fueldir 중복 데이터 확인 및 정리
        cursor.execute("""
            SELECT process_id, fuel_name, COUNT(*) as count
            FROM fueldir 
            GROUP BY process_id, fuel_name 
            HAVING COUNT(*) > 1
        """)
        duplicate_fueldir = cursor.fetchall()
        
        if duplicate_fueldir:
            print(f"  📋 fueldir 중복 데이터 {len(duplicate_fueldir)}개 그룹 발견")
            
            for dup in duplicate_fueldir:
                process_id, fuel_name, count = dup
                print(f"    🔍 process_id={process_id}, fuel_name='{fuel_name}': {count}개")
                
                # 중복 데이터 중 가장 최근 것만 남기고 나머지 삭제
                cursor.execute("""
                    DELETE FROM fueldir 
                    WHERE id NOT IN (
                        SELECT id FROM (
                            SELECT id, ROW_NUMBER() OVER (
                                PARTITION BY process_id, fuel_name 
                                ORDER BY created_at DESC
                            ) as rn
                            FROM fueldir 
                            WHERE process_id = %s AND fuel_name = %s
                        ) ranked 
                        WHERE rn = 1
                    )
                    AND process_id = %s AND fuel_name = %s
                """, (process_id, fuel_name, process_id, fuel_name))
                
                deleted_count = cursor.rowcount
                print(f"      ✅ {deleted_count}개 중복 데이터 삭제 완료")
        
        # 2. UNIQUE 제약조건 추가 (안전하게)
        print("\n🔒 UNIQUE 제약조건 추가 중...")
        
        # matdir 테이블에 UNIQUE 제약조건 추가
        try:
            cursor.execute("""
                ALTER TABLE matdir 
                ADD CONSTRAINT unique_matdir_process_material 
                UNIQUE(process_id, mat_name)
            """)
            print("  ✅ matdir UNIQUE(process_id, mat_name) 제약조건 추가 완료")
        except Exception as e:
            if "already exists" in str(e):
                print("  ℹ️ matdir UNIQUE 제약조건이 이미 존재합니다")
            else:
                print(f"  ⚠️ matdir UNIQUE 제약조건 추가 실패: {e}")
        
        # fueldir 테이블에 UNIQUE 제약조건 추가
        try:
            cursor.execute("""
                ALTER TABLE fueldir 
                ADD CONSTRAINT unique_fueldir_process_fuel 
                UNIQUE(process_id, fuel_name)
            """)
            print("  ✅ fueldir UNIQUE(process_id, fuel_name) 제약조건 추가 완료")
        except Exception as e:
            if "already exists" in str(e):
                print("  ℹ️ fueldir UNIQUE 제약조건이 이미 존재합니다")
            else:
                print(f"  ⚠️ fueldir UNIQUE 제약조건 추가 실패: {e}")
        
        # 3. 인덱스 추가 (성능 최적화)
        print("\n📈 인덱스 추가 중...")
        
        # matdir 테이블 인덱스
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_matdir_process_material 
                ON matdir(process_id, mat_name)
            """)
            print("  ✅ matdir (process_id, mat_name) 인덱스 추가 완료")
        except Exception as e:
            print(f"  ⚠️ matdir 인덱스 추가 실패: {e}")
        
        # fueldir 테이블 인덱스
        try:
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fueldir_process_fuel 
                ON fueldir(process_id, fuel_name)
            """)
            print("  ✅ fueldir (process_id, fuel_name) 인덱스 추가 완료")
        except Exception as e:
            print(f"  ⚠️ fueldir 인덱스 추가 실패: {e}")
        
        # 4. 최종 검증
        print("\n🔍 최종 검증 중...")
        
        # 중복 데이터 재확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT process_id, mat_name, COUNT(*) as count
                FROM matdir 
                GROUP BY process_id, mat_name 
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        remaining_matdir_duplicates = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT process_id, fuel_name, COUNT(*) as count
                FROM fueldir 
                GROUP BY process_id, fuel_name 
                HAVING COUNT(*) > 1
            ) duplicates
        """)
        remaining_fueldir_duplicates = cursor.fetchone()[0]
        
        print(f"  📊 남은 중복 데이터:")
        print(f"    matdir: {remaining_matdir_duplicates}개 그룹")
        print(f"    fueldir: {remaining_fueldir_duplicates}개 그룹")
        
        # 제약조건 확인
        cursor.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'matdir' 
            AND constraint_type = 'UNIQUE'
        """)
        matdir_unique_constraints = cursor.fetchall()
        
        cursor.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'fueldir' 
            AND constraint_type = 'UNIQUE'
        """)
        fueldir_unique_constraints = cursor.fetchall()
        
        print(f"  🔒 UNIQUE 제약조건:")
        print(f"    matdir: {len(matdir_unique_constraints)}개")
        print(f"    fueldir: {len(fueldir_unique_constraints)}개")
        
        cursor.close()
        conn.close()
        
        print("\n✅ 데이터 무결성 개선 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_data_integrity()
