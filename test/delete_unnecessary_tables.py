import psycopg2
import os

# 데이터베이스 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def delete_unnecessary_tables():
    conn = None
    cursor = None
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 삭제할 테이블 목록
        delete_tables = [
            'emission_attribution',
            'emission_factors', 
            'process_backup',
            'process_input',
            'product_backup',
            'product_emissions'
        ]
        
        print("🗑️ 불필요한 테이블 삭제 시작...")
        print("=" * 50)
        
        for table in delete_tables:
            try:
                # 테이블 존재 여부 확인
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table,))
                
                exists = cursor.fetchone()[0]
                
                if exists:
                    # 테이블 삭제
                    cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                    conn.commit()
                    print(f"✅ {table} 테이블 삭제 완료")
                else:
                    print(f"⚠️ {table} 테이블이 존재하지 않음")
                    
            except Exception as e:
                print(f"❌ {table} 테이블 삭제 실패: {e}")
                conn.rollback()
        
        print("\n" + "=" * 50)
        print("🎉 불필요한 테이블 삭제 완료!")
        
        # 삭제 후 남은 테이블 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        remaining_tables = cursor.fetchall()
        
        print(f"\n📋 삭제 후 남은 테이블 ({len(remaining_tables)}개):")
        for table in remaining_tables:
            print(f"• {table[0]}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    delete_unnecessary_tables()
