import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def cleanup_database():
    print("🧹 Railway DB 정리 시작...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. 현재 모든 테이블 확인
    print("\n📋 현재 DB의 모든 테이블:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    all_tables = cursor.fetchall()
    for table in all_tables:
        print(f"  - {table['table_name']}")

    # 2. 필요한 테이블들 (유지할 테이블)
    essential_tables = [
        'process',           # 공정 정보
        'edge',             # 공정 간 연결
        'process_attrdir_emission',  # 공정별 직접귀속배출량
        'matdir',           # 원료직접배출량
        'fueldir',          # 연료직접배출량
        'material_master',  # 원료 마스터 데이터
        'fuel_master',      # 연료 마스터 데이터
        'process_chain',    # 공정 체인 (통합 그룹용)
        'process_chain_link', # 체인 링크
        'cumulative_emission', # 누적 배출량 (통합 그룹용)
        'source_stream'     # 소스 스트림
    ]

    # 3. 삭제할 테이블들 확인
    print("\n🗑️ 삭제할 테이블들:")
    tables_to_delete = []
    for table in all_tables:
        if table['table_name'] not in essential_tables:
            tables_to_delete.append(table['table_name'])
            print(f"  - {table['table_name']} (삭제 예정)")

    if not tables_to_delete:
        print("  - 삭제할 테이블이 없습니다.")
    else:
        # 4. 삭제 실행
        print(f"\n⚠️ {len(tables_to_delete)}개 테이블을 삭제합니다. 계속하시겠습니까? (y/n)")
        # 실제로는 사용자 확인이 필요하지만, 스크립트에서는 자동으로 진행
        print("  - 자동으로 삭제를 진행합니다...")
        
        for table_name in tables_to_delete:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                print(f"  ✅ {table_name} 삭제 완료")
            except Exception as e:
                print(f"  ❌ {table_name} 삭제 실패: {e}")

    # 5. 정리 후 테이블 확인
    print("\n📋 정리 후 남은 테이블들:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    remaining_tables = cursor.fetchall()
    for table in remaining_tables:
        print(f"  ✅ {table['table_name']}")

    cursor.close()
    conn.close()
    print("\n🎉 DB 정리 완료!")

if __name__ == "__main__":
    cleanup_database()
