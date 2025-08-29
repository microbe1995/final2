import os
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
import json

# 환경변수 설정
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def create_integrated_process_group_table():
    """통합 공정 그룹 배출량 테이블 생성"""
    
    try:
        # DB 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔗 DB 연결 성공")
        
        # 기존 테이블 삭제 (있다면)
        cursor.execute("""
            DROP TABLE IF EXISTS integrated_process_group_emission CASCADE;
        """)
        print("🗑️ 기존 테이블 삭제 완료")
        
        # 통합 공정 그룹 배출량 테이블 생성
        cursor.execute("""
            CREATE TABLE integrated_process_group_emission (
                id SERIAL PRIMARY KEY,
                chain_id INTEGER NOT NULL,
                process_id INTEGER NOT NULL,
                integrated_matdir_emission NUMERIC(15, 6) NOT NULL DEFAULT 0,
                integrated_fueldir_emission NUMERIC(15, 6) NOT NULL DEFAULT 0,
                integrated_attrdir_em NUMERIC(15, 6) NOT NULL DEFAULT 0,
                group_processes TEXT,
                calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chain_id) REFERENCES process_chain(id) ON DELETE CASCADE,
                FOREIGN KEY (process_id) REFERENCES process(id) ON DELETE CASCADE
            );
        """)
        
        # 인덱스 생성
        cursor.execute("""
            CREATE INDEX idx_integrated_process_group_emission_chain_id 
            ON integrated_process_group_emission(chain_id);
        """)
        
        cursor.execute("""
            CREATE INDEX idx_integrated_process_group_emission_process_id 
            ON integrated_process_group_emission(process_id);
        """)
        
        cursor.execute("""
            CREATE INDEX idx_integrated_process_group_emission_calculation_date 
            ON integrated_process_group_emission(calculation_date);
        """)
        
        # 변경사항 커밋
        conn.commit()
        
        print("✅ 통합 공정 그룹 배출량 테이블 생성 완료")
        print("📊 테이블 구조:")
        print("   - id: 기본키")
        print("   - chain_id: 그룹 ID (process_chain 참조)")
        print("   - process_id: 공정 ID (process 참조)")
        print("   - integrated_matdir_emission: 그룹의 총 원료배출량")
        print("   - integrated_fueldir_emission: 그룹의 총 연료배출량")
        print("   - integrated_attrdir_em: 그룹의 총 직접귀속배출량")
        print("   - group_processes: 그룹에 속한 공정들 (JSON)")
        print("   - calculation_date: 계산 일시")
        print("   - created_at, updated_at: 생성/수정 일시")
        
        # 테이블 확인
        cursor.execute("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'integrated_process_group_emission'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 생성된 컬럼들:")
        for col in columns:
            print(f"   - {col[1]}: {col[2]} ({'NULL' if col[3] == 'YES' else 'NOT NULL'})")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("🔌 DB 연결 종료")

if __name__ == "__main__":
    create_integrated_process_group_table()
