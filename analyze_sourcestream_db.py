import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def analyze_sourcestream_db():
    """sourcestream 관련 DB 분석"""
    try:
        print("🔍 sourcestream 관련 DB 분석 중...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. 현재 테이블 구조 확인
        print("\n📋 현재 테이블 구조:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%sourcestream%'
            ORDER BY table_name
        """)
        sourcestream_tables = cursor.fetchall()
        
        if sourcestream_tables:
            print(f"  sourcestream 관련 테이블: {len(sourcestream_tables)}개")
            for table in sourcestream_tables:
                print(f"    - {table['table_name']}")
        else:
            print("  ⚠️ sourcestream 관련 테이블이 없습니다.")
        
        # 2. edge 테이블 구조 확인 (공정 간 연결)
        print("\n🔗 edge 테이블 구조:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'edge'
            ORDER BY ordinal_position
        """)
        edge_columns = cursor.fetchall()
        
        for col in edge_columns:
            print(f"    - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # 3. edge 데이터 확인
        print("\n🔗 edge 데이터 현황:")
        cursor.execute("SELECT COUNT(*) as count FROM edge")
        edge_count = cursor.fetchone()['count']
        print(f"  총 {edge_count}개 엣지")
        
        if edge_count > 0:
            cursor.execute("SELECT * FROM edge LIMIT 5")
            edges = cursor.fetchall()
            for edge in edges:
                print(f"    - ID: {edge['id']}, Source: {edge['source_id']}, Target: {edge['target_id']}, Kind: {edge['edge_kind']}")
        
        # 4. process 테이블 구조 확인
        print("\n⚙️ process 테이블 구조:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'process'
            ORDER BY ordinal_position
        """)
        process_columns = cursor.fetchall()
        
        for col in process_columns:
            print(f"    - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # 5. process_attrdir_emission 테이블 구조 확인
        print("\n📊 process_attrdir_emission 테이블 구조:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'process_attrdir_emission'
            ORDER BY ordinal_position
        """)
        emission_columns = cursor.fetchall()
        
        for col in emission_columns:
            print(f"    - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # 6. 공정 간 연결 패턴 분석
        print("\n🔍 공정 간 연결 패턴 분석:")
        cursor.execute("""
            SELECT 
                e.edge_kind,
                COUNT(*) as count,
                p1.process_name as source_process,
                p2.process_name as target_process
            FROM edge e
            LEFT JOIN process p1 ON e.source_id = p1.id
            LEFT JOIN process p2 ON e.target_id = p2.id
            WHERE e.edge_kind = 'continue'
            GROUP BY e.edge_kind, p1.process_name, p2.process_name
            ORDER BY count DESC
        """)
        continue_patterns = cursor.fetchall()
        
        if continue_patterns:
            print(f"  continue 엣지 패턴: {len(continue_patterns)}개")
            for pattern in continue_patterns:
                print(f"    - {pattern['source_process']} → {pattern['target_process']}: {pattern['count']}개")
        else:
            print("  ⚠️ continue 엣지가 없습니다.")
        
        cursor.close()
        conn.close()
        
        print("\n✅ sourcestream DB 분석 완료!")
        
    except Exception as e:
        print(f"❌ DB 분석 중 오류 발생: {e}")

if __name__ == "__main__":
    analyze_sourcestream_db()
