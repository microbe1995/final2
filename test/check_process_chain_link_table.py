#!/usr/bin/env python3
"""
process_chain_link 테이블의 구조와 데이터를 확인하는 스크립트
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime

async def check_process_chain_link_table():
    """process_chain_link 테이블의 구조와 데이터를 확인합니다."""
    
    # DATABASE_URL 환경변수 확인
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        # 데이터베이스 연결
        print("🔗 Railway DB 연결 중...")
        conn = await asyncpg.connect(database_url)
        print("✅ DB 연결 성공")
        
        # 1. process_chain_link 테이블 구조 확인
        print("\n📋 process_chain_link 테이블 구조 확인...")
        columns_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'process_chain_link' 
        ORDER BY ordinal_position;
        """
        
        columns = await conn.fetch(columns_query)
        print("테이블 구조:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # 2. is_continue_edge 컬럼 존재 여부 확인
        print("\n🔍 is_continue_edge 컬럼 확인...")
        is_continue_edge_exists = any(col['column_name'] == 'is_continue_edge' for col in columns)
        
        if is_continue_edge_exists:
            print("✅ is_continue_edge 컬럼이 존재합니다.")
        else:
            print("❌ is_continue_edge 컬럼이 존재하지 않습니다.")
            print("💡 이 컬럼이 필요합니다. 추가해야 합니다.")
        
        # 3. 데이터 개수 확인
        print("\n📊 데이터 개수 확인...")
        count_query = "SELECT COUNT(*) FROM process_chain_link;"
        count = await conn.fetchrow(count_query)
        print(f"총 데이터 개수: {count[0]}개")
        
        # 4. 샘플 데이터 확인
        print("\n📋 샘플 데이터 확인...")
        if count[0] > 0:
            sample_query = "SELECT * FROM process_chain_link LIMIT 5;"
            samples = await conn.fetch(sample_query)
            
            print("샘플 데이터:")
            for i, sample in enumerate(samples, 1):
                print(f"  {i}. {dict(sample)}")
        else:
            print("ℹ️ 데이터가 없습니다.")
        
        # 5. process_chain 테이블과의 관계 확인
        print("\n🔗 process_chain 테이블과의 관계 확인...")
        try:
            chain_query = """
            SELECT pc.id, pc.chain_name, pc.is_active, COUNT(pcl.id) as link_count
            FROM process_chain pc
            LEFT JOIN process_chain_link pcl ON pc.id = pcl.chain_id
            GROUP BY pc.id, pc.chain_name, pc.is_active
            ORDER BY pc.id;
            """
            
            chains = await conn.fetch(chain_query)
            print("공정 체인 정보:")
            for chain in chains:
                print(f"  - ID {chain['id']}: {chain['chain_name']} (활성: {chain['is_active']}, 링크: {chain['link_count']}개)")
                
        except Exception as e:
            print(f"⚠️ process_chain 테이블 조회 실패: {e}")
        
        # 6. 결과 저장
        check_result = {
            "check_date": datetime.now().isoformat(),
            "table": "process_chain_link",
            "columns": [{"name": col['column_name'], "type": col['data_type'], "nullable": col['is_nullable']} for col in columns],
            "is_continue_edge_exists": is_continue_edge_exists,
            "total_records": count[0],
            "sample_data": [dict(sample) for sample in samples] if count[0] > 0 else [],
            "status": "success"
        }
        
        with open("process_chain_link_check.json", "w", encoding="utf-8") as f:
            json.dump(check_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 결과가 process_chain_link_check.json에 저장되었습니다.")
        
        # 7. 문제 해결 방안 제시
        if not is_continue_edge_exists:
            print("\n💡 문제 해결 방안:")
            print("1. is_continue_edge 컬럼을 process_chain_link 테이블에 추가")
            print("2. 또는 기존 컬럼을 사용하도록 코드 수정")
            print("3. 또는 process_chain_link 테이블을 사용하지 않는 방식으로 로직 변경")
        
        print("🎯 process_chain_link 테이블 확인 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
        # 오류 결과 저장
        error_result = {
            "check_date": datetime.now().isoformat(),
            "table": "process_chain_link",
            "status": "error",
            "error_message": str(e)
        }
        
        with open("process_chain_link_check_error.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, indent=2, ensure_ascii=False)
        
    finally:
        if 'conn' in locals():
            await conn.close()
            print("🔌 DB 연결 종료")

if __name__ == "__main__":
    print("🚀 process_chain_link 테이블 확인 시작")
    print("=" * 60)
    
    asyncio.run(check_process_chain_link_table())
