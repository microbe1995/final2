#!/usr/bin/env python3
"""
Railway DB 스키마 분석 스크립트
현재 테이블 구조를 파악하여 배출량 누적 전달을 위한 스키마 확장 계획을 수립합니다.
"""

import os
import asyncio
import asyncpg
from typing import Dict, List, Any
import json
from datetime import datetime

# 환경변수에서 DB 연결 정보 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

async def analyze_database_schema():
    """데이터베이스 스키마를 분석합니다."""
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        # DB 연결
        print("🔗 Railway DB에 연결 중...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ DB 연결 성공!")
        
        # 1. 모든 테이블 목록 조회
        print("\n📋 1. 데이터베이스 테이블 목록")
        print("=" * 50)
        
        tables_query = """
        SELECT table_name, table_type
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """
        
        tables = await conn.fetch(tables_query)
        
        table_info = {}
        for table in tables:
            table_name = table['table_name']
            table_type = table['table_type']
            print(f"📊 {table_name} ({table_type})")
            table_info[table_name] = {'type': table_type, 'columns': []}
        
        # 2. 각 테이블의 상세 구조 분석
        print("\n🔍 2. 테이블별 상세 구조 분석")
        print("=" * 50)
        
        for table_name in table_info.keys():
            if table_info[table_name]['type'] == 'BASE TABLE':
                print(f"\n📋 테이블: {table_name}")
                print("-" * 30)
                
                # 컬럼 정보 조회
                columns_query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns 
                WHERE table_name = $1
                ORDER BY ordinal_position;
                """
                
                columns = await conn.fetch(columns_query, table_name)
                
                for col in columns:
                    col_info = {
                        'name': col['column_name'],
                        'type': col['data_type'],
                        'nullable': col['is_nullable'],
                        'default': col['column_default'],
                        'max_length': col['character_maximum_length'],
                        'precision': col['numeric_precision'],
                        'scale': col['numeric_scale']
                    }
                    
                    table_info[table_name]['columns'].append(col_info)
                    
                    # 컬럼 정보 출력
                    nullable_str = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default_str = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    
                    if col['data_type'] == 'character varying':
                        type_str = f"VARCHAR({col['max_length']})"
                    elif col['data_type'] == 'numeric':
                        type_str = f"NUMERIC({col['precision']},{col['scale']})"
                    else:
                        type_str = col['data_type']
                    
                    print(f"  {col['column_name']:<20} {type_str:<15} {nullable_str}{default_str}")
        
        # 3. 인덱스 정보 분석
        print("\n🔍 3. 테이블별 인덱스 분석")
        print("=" * 50)
        
        for table_name in table_info.keys():
            if table_info[table_name]['type'] == 'BASE TABLE':
                print(f"\n📋 테이블: {table_name}")
                print("-" * 30)
                
                indexes_query = """
                SELECT 
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE tablename = $1;
                """
                
                indexes = await conn.fetch(indexes_query, table_name)
                
                if indexes:
                    for idx in indexes:
                        print(f"  🔗 {idx['indexname']}")
                        print(f"     {idx['indexdef']}")
                else:
                    print("  ⚠️ 인덱스 없음")
        
        # 4. 외래키 관계 분석
        print("\n🔍 4. 외래키 관계 분석")
        print("=" * 50)
        
        for table_name in table_info.keys():
            if table_info[table_name]['type'] == 'BASE TABLE':
                print(f"\n📋 테이블: {table_name}")
                print("-" * 30)
                
                foreign_keys_query = """
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = $1;
                """
                
                foreign_keys = await conn.fetch(foreign_keys_query, table_name)
                
                if foreign_keys:
                    for fk in foreign_keys:
                        print(f"  🔗 {fk['column_name']} → {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                else:
                    print("  ⚠️ 외래키 없음")
        
        # 5. 샘플 데이터 확인 (배출량 관련 테이블)
        print("\n🔍 5. 배출량 관련 테이블 샘플 데이터")
        print("=" * 50)
        
        emission_tables = ['process_attrdir_emission', 'matdir', 'fueldir']
        
        for table_name in emission_tables:
            if table_name in table_info:
                print(f"\n📋 테이블: {table_name}")
                print("-" * 30)
                
                try:
                    sample_query = f"SELECT * FROM {table_name} LIMIT 3;"
                    sample_data = await conn.fetch(sample_query)
                    
                    if sample_data:
                        for i, row in enumerate(sample_data, 1):
                            print(f"  📝 샘플 {i}: {dict(row)}")
                    else:
                        print("  ⚠️ 데이터 없음")
                        
                except Exception as e:
                    print(f"  ❌ 샘플 데이터 조회 실패: {e}")
        
        # 6. 스키마 확장 계획 제안
        print("\n🎯 6. 배출량 누적 전달을 위한 스키마 확장 계획")
        print("=" * 50)
        
        print("\n📊 현재 상황:")
        if 'process_attrdir_emission' in table_info:
            print("  ✅ process_attrdir_emission 테이블 존재")
            print("  ✅ attrdir_em 필드 존재 (직접귀속배출량)")
            
            # 누적 배출량 필드 확인
            has_cumulative = any(col['name'] == 'cumulative_emission' 
                               for col in table_info['process_attrdir_emission']['columns'])
            
            if has_cumulative:
                print("  ✅ cumulative_emission 필드 이미 존재")
            else:
                print("  ❌ cumulative_emission 필드 없음 - 추가 필요")
        else:
            print("  ❌ process_attrdir_emission 테이블 없음 - 생성 필요")
        
        if 'edge' in table_info:
            print("  ✅ edge 테이블 존재")
            print("  ✅ edge_kind 필드 존재 (continue/produce/consume)")
        else:
            print("  ❌ edge 테이블 없음 - 생성 필요")
        
        print("\n🔧 권장 스키마 확장:")
        print("  1. process_attrdir_emission 테이블에 cumulative_emission 필드 추가")
        print("  2. 배출량 전파 이력 테이블 생성 (emission_propagation_log)")
        print("  3. 공정 체인 순서 정보 테이블 생성 (process_sequence)")
        
        # 7. 결과를 JSON 파일로 저장
        print("\n💾 7. 분석 결과를 JSON 파일로 저장")
        print("=" * 50)
        
        analysis_result = {
            'analysis_date': datetime.now().isoformat(),
            'database_url': DATABASE_URL.replace(DATABASE_URL.split('@')[0].split(':')[2], '***') if '@' in DATABASE_URL else '***',
            'tables': table_info,
            'recommendations': {
                'add_cumulative_emission': True,
                'create_propagation_log': True,
                'create_process_sequence': True
            }
        }
        
        with open('db_schema_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        print("✅ 분석 결과가 db_schema_analysis.json 파일로 저장되었습니다.")
        
        await conn.close()
        print("\n🔗 DB 연결 종료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Railway DB 스키마 분석 시작")
    print("=" * 50)
    
    asyncio.run(analyze_database_schema())
    
    print("\n🎯 분석 완료! 다음 단계:")
    print("1. db_schema_analysis.json 파일 확인")
    print("2. 스키마 확장 계획 검토")
    print("3. DB 마이그레이션 스크립트 작성")
