#!/usr/bin/env python3
"""
Railway DB 직접 연결 스키마 분석 스크립트
rule1.mdc 규칙에 따라 Railway PostgreSQL DB를 먼저 확인합니다.
"""

import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, List, Any

# Railway DB 연결 정보 (rule1.mdc에서 가져옴)
RAILWAY_DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def analyze_railway_database():
    """Railway DB 스키마를 직접 분석합니다."""
    
    try:
        # Railway DB 직접 연결
        print("🔗 Railway DB에 직접 연결 중...")
        print(f"📍 연결 주소: {RAILWAY_DATABASE_URL.split('@')[1] if '@' in RAILWAY_DATABASE_URL else '***'}")
        
        conn = await asyncpg.connect(RAILWAY_DATABASE_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 모든 테이블 목록 조회
        print("\n📋 1. Railway DB 테이블 목록")
        print("=" * 60)
        
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
        
        print(f"\n📊 총 테이블 수: {len([t for t in table_info.values() if t['type'] == 'BASE TABLE'])}")
        
        # 2. 각 테이블의 상세 구조 분석
        print("\n🔍 2. 테이블별 상세 구조 분석")
        print("=" * 60)
        
        for table_name in table_info.keys():
            if table_info[table_name]['type'] == 'BASE TABLE':
                print(f"\n📋 테이블: {table_name}")
                print("-" * 40)
                
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
                    
                    # 컬럼 정보 출력 (안전한 방식으로)
                    nullable_str = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default_str = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    
                    if col['data_type'] == 'character varying':
                        max_len = col.get('character_maximum_length', '?')
                        type_str = f"VARCHAR({max_len})" if max_len != '?' else "VARCHAR"
                    elif col['data_type'] == 'numeric':
                        precision = col.get('numeric_precision', '?')
                        scale = col.get('numeric_scale', '?')
                        if precision != '?' and scale != '?':
                            type_str = f"NUMERIC({precision},{scale})"
                        else:
                            type_str = "NUMERIC"
                    else:
                        type_str = col['data_type']
                    
                    print(f"  {col['column_name']:<25} {type_str:<20} {nullable_str}{default_str}")
        
        # 3. 인덱스 정보 분석
        print("\n🔍 3. 테이블별 인덱스 분석")
        print("=" * 60)
        
        for table_name in table_info.keys():
            if table_info[table_name]['type'] == 'BASE TABLE':
                print(f"\n📋 테이블: {table_name}")
                print("-" * 40)
                
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
        print("=" * 60)
        
        for table_name in table_info.keys():
            if table_info[table_name]['type'] == 'BASE TABLE':
                print(f"\n📋 테이블: {table_name}")
                print("-" * 40)
                
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
        
        # 5. 배출량 관련 테이블 상세 분석
        print("\n🔍 5. 배출량 관련 테이블 상세 분석")
        print("=" * 60)
        
        emission_tables = ['process_attrdir_emission', 'matdir', 'fueldir', 'edge', 'process', 'product']
        
        for table_name in emission_tables:
            if table_name in table_info:
                print(f"\n📋 테이블: {table_name}")
                print("-" * 40)
                
                # 테이블 데이터 개수 확인
                try:
                    count_query = f"SELECT COUNT(*) as count FROM {table_name};"
                    count_result = await conn.fetchrow(count_query)
                    row_count = count_result['count'] if count_result else 0
                    print(f"  📊 총 레코드 수: {row_count}")
                    
                    # 샘플 데이터 확인
                    if row_count > 0:
                        sample_query = f"SELECT * FROM {table_name} LIMIT 2;"
                        sample_data = await conn.fetch(sample_query)
                        
                        for i, row in enumerate(sample_data, 1):
                            print(f"  📝 샘플 {i}: {dict(row)}")
                    else:
                        print("  ⚠️ 데이터 없음")
                        
                except Exception as e:
                    print(f"  ❌ 데이터 조회 실패: {e}")
        
        # 6. CBAM 배출량 누적 전달을 위한 현재 상황 분석
        print("\n🎯 6. CBAM 배출량 누적 전달 현황 분석")
        print("=" * 60)
        
        print("\n📊 핵심 테이블 현황:")
        
        # process_attrdir_emission 테이블 확인
        if 'process_attrdir_emission' in table_info:
            print("  ✅ process_attrdir_emission 테이블 존재")
            
            # 누적 배출량 필드 확인
            has_cumulative = any(col['name'] == 'cumulative_emission' 
                               for col in table_info['process_attrdir_emission']['columns'])
            
            if has_cumulative:
                print("  ✅ cumulative_emission 필드 이미 존재")
            else:
                print("  ❌ cumulative_emission 필드 없음 - 추가 필요")
                
            # 기존 필드들 확인
            existing_fields = [col['name'] for col in table_info['process_attrdir_emission']['columns']]
            print(f"  📋 기존 필드들: {', '.join(existing_fields)}")
        else:
            print("  ❌ process_attrdir_emission 테이블 없음 - 생성 필요")
        
        # edge 테이블 확인
        if 'edge' in table_info:
            print("  ✅ edge 테이블 존재")
            
            # edge_kind 필드 확인
            has_edge_kind = any(col['name'] == 'edge_kind' 
                               for col in table_info['edge']['columns'])
            
            if has_edge_kind:
                print("  ✅ edge_kind 필드 존재 (continue/produce/consume)")
                
                # edge_kind 값들 확인
                try:
                    edge_kinds_query = "SELECT DISTINCT edge_kind FROM edge;"
                    edge_kinds = await conn.fetch(edge_kinds_query)
                    kinds = [row['edge_kind'] for row in edge_kinds]
                    print(f"  📋 현재 edge_kind 값들: {', '.join(kinds) if kinds else '없음'}")
                except Exception as e:
                    print(f"  ⚠️ edge_kind 값 조회 실패: {e}")
            else:
                print("  ❌ edge_kind 필드 없음 - 추가 필요")
        else:
            print("  ❌ edge 테이블 없음 - 생성 필요")
        
        # 7. 스키마 확장 권장사항
        print("\n🔧 7. 스키마 확장 권장사항")
        print("=" * 60)
        
        recommendations = []
        
        if 'process_attrdir_emission' in table_info:
            if not any(col['name'] == 'cumulative_emission' for col in table_info['process_attrdir_emission']['columns']):
                recommendations.append("process_attrdir_emission 테이블에 cumulative_emission 필드 추가")
        
        if 'edge' not in table_info:
            recommendations.append("edge 테이블 생성 (공정 간 연결 관리)")
        
        if recommendations:
            print("  📋 권장 스키마 확장:")
            for i, rec in enumerate(recommendations, 1):
                print(f"    {i}. {rec}")
        else:
            print("  ✅ 모든 필요한 테이블과 필드가 이미 존재합니다.")
        
        # 8. 결과를 JSON 파일로 저장
        print("\n💾 8. 분석 결과를 JSON 파일로 저장")
        print("=" * 60)
        
        analysis_result = {
            'analysis_date': datetime.now().isoformat(),
            'database_url': RAILWAY_DATABASE_URL.split('@')[1] if '@' in RAILWAY_DATABASE_URL else '***',
            'total_tables': len([t for t in table_info.values() if t['type'] == 'BASE TABLE']),
            'tables': table_info,
            'cbam_analysis': {
                'has_process_attrdir_emission': 'process_attrdir_emission' in table_info,
                'has_cumulative_emission': any(
                    col['name'] == 'cumulative_emission' 
                    for table in table_info.values() 
                    for col in table.get('columns', [])
                ),
                'has_edge_table': 'edge' in table_info,
                'has_edge_kind': any(
                    col['name'] == 'edge_kind' 
                    for col in table_info.get('edge', {}).get('columns', [])
                )
            },
            'recommendations': recommendations
        }
        
        with open('railway_db_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        print("✅ 분석 결과가 railway_db_analysis.json 파일로 저장되었습니다.")
        
        await conn.close()
        print("\n🔗 Railway DB 연결 종료")
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Railway DB 직접 연결 스키마 분석 시작")
    print("=" * 60)
    print("📍 rule1.mdc 규칙에 따라 Railway PostgreSQL DB를 먼저 확인합니다.")
    print("=" * 60)
    
    result = asyncio.run(analyze_railway_database())
    
    if result:
        print("\n🎯 분석 완료! 다음 단계:")
        print("1. railway_db_analysis.json 파일 확인")
        print("2. 현재 DB 스키마 현황 파악")
        print("3. 필요한 스키마 확장 계획 수립")
        print("4. DB 마이그레이션 스크립트 작성")
    else:
        print("\n❌ 분석 실패! 오류를 확인하고 다시 시도해주세요.")
