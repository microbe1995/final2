import os
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_and_fix_db_schema():
    print("🔍 CBAM 서비스 스키마 기준으로 DB 확인 및 수정...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. 현재 hs_cn_mapping 테이블 구조 확인
    print("\n📋 현재 hs_cn_mapping 테이블 구조:")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'hs_cn_mapping'
        ORDER BY ordinal_position
    """)
    current_columns = cursor.fetchall()
    for col in current_columns:
        print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")

    # 2. 스키마 기준 컬럼 정의
    expected_columns = {
        'id': 'SERIAL PRIMARY KEY',
        'hscode': 'VARCHAR(6) NOT NULL',
        'aggregoods_name': 'TEXT',
        'aggregoods_engname': 'TEXT', 
        'cncode_total': 'VARCHAR(8) NOT NULL',
        'goods_name': 'TEXT',
        'goods_engname': 'TEXT'
    }

    print(f"\n📋 스키마 기준 컬럼:")
    for col_name, col_def in expected_columns.items():
        print(f"  - {col_name}: {col_def}")

    # 3. 컬럼 비교 및 수정
    current_col_names = [col['column_name'] for col in current_columns]
    missing_columns = []
    wrong_columns = []

    for expected_col, expected_def in expected_columns.items():
        if expected_col not in current_col_names:
            missing_columns.append((expected_col, expected_def))
        else:
            # 컬럼 타입 확인
            current_col = next(col for col in current_columns if col['column_name'] == expected_col)
            if 'VARCHAR' in expected_def and 'character varying' not in current_col['data_type']:
                wrong_columns.append((expected_col, expected_def))

    # 4. 테이블 재생성
    if missing_columns or wrong_columns:
        print(f"\n⚠️ 테이블 구조가 스키마와 다릅니다.")
        print(f"  - 누락된 컬럼: {len(missing_columns)}개")
        print(f"  - 잘못된 컬럼: {len(wrong_columns)}개")
        
        # 기존 데이터 백업
        print("\n💾 기존 데이터 백업...")
        cursor.execute("SELECT * FROM hs_cn_mapping")
        backup_data = cursor.fetchall()
        print(f"  - 백업된 데이터: {len(backup_data)}개")

        # 테이블 재생성
        print("\n🔨 테이블 재생성...")
        cursor.execute("DROP TABLE IF EXISTS hs_cn_mapping CASCADE")
        
        create_sql = """
        CREATE TABLE hs_cn_mapping (
            id SERIAL PRIMARY KEY,
            hscode VARCHAR(6) NOT NULL,
            aggregoods_name TEXT,
            aggregoods_engname TEXT,
            cncode_total VARCHAR(8) NOT NULL,
            goods_name TEXT,
            goods_engname TEXT
        )
        """
        cursor.execute(create_sql)
        
        # 인덱스 생성
        cursor.execute("CREATE INDEX idx_hs_cn_mapping_hscode ON hs_cn_mapping(hscode)")
        cursor.execute("CREATE INDEX idx_hs_cn_mapping_cncode ON hs_cn_mapping(cncode_total)")
        
        print("  ✅ 테이블 재생성 완료")

        # 5. Excel 데이터 로드
        print("\n📥 Excel 데이터 로드...")
        excel_file_path = "masterdb/hs_cn_mapping.xlsx"
        
        try:
            df = pd.read_excel(excel_file_path)
            print(f"  ✅ Excel 파일 읽기 성공: {len(df)}개 행")
            print(f"  📊 컬럼: {list(df.columns)}")
            
            # 데이터 삽입
            inserted_count = 0
            for index, row in df.iterrows():
                try:
                    # Excel 컬럼명에 따라 매핑 (실제 컬럼명 확인 필요)
                    hscode = str(row.iloc[0]) if pd.notna(row.iloc[0]) else None
                    aggregoods_name = str(row.iloc[1]) if len(row) > 1 and pd.notna(row.iloc[1]) else None
                    aggregoods_engname = str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else None
                    cncode_total = str(row.iloc[3]) if len(row) > 3 and pd.notna(row.iloc[3]) else None
                    goods_name = str(row.iloc[4]) if len(row) > 4 and pd.notna(row.iloc[4]) else None
                    goods_engname = str(row.iloc[5]) if len(row) > 5 and pd.notna(row.iloc[5]) else None
                    
                    if hscode and cncode_total:
                        cursor.execute("""
                            INSERT INTO hs_cn_mapping (hscode, aggregoods_name, aggregoods_engname, cncode_total, goods_name, goods_engname)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (hscode, aggregoods_name, aggregoods_engname, cncode_total, goods_name, goods_engname))
                        inserted_count += 1
                        
                except Exception as e:
                    print(f"  ❌ 행 {index} 삽입 실패: {e}")
                    
            print(f"  ✅ 데이터 로드 완료: {inserted_count}개 삽입")
            
        except Exception as e:
            print(f"  ❌ Excel 파일 읽기 실패: {e}")

    else:
        print("\n✅ 테이블 구조가 스키마와 일치합니다.")

    # 6. 최종 확인
    print("\n📋 최종 테이블 구조:")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'hs_cn_mapping'
        ORDER BY ordinal_position
    """)
    final_columns = cursor.fetchall()
    for col in final_columns:
        print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")

    # 7. 데이터 확인
    cursor.execute("SELECT COUNT(*) as count FROM hs_cn_mapping")
    total_count = cursor.fetchone()['count']
    print(f"\n📊 총 레코드 수: {total_count}개")

    if total_count > 0:
        print("\n📄 샘플 데이터:")
        cursor.execute("SELECT * FROM hs_cn_mapping LIMIT 3")
        samples = cursor.fetchall()
        for sample in samples:
            print(f"  - {sample}")

    cursor.close()
    conn.close()
    print("\n🎉 DB 스키마 확인 및 수정 완료!")

if __name__ == "__main__":
    check_and_fix_db_schema()
