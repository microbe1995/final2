#!/usr/bin/env python3
"""
Railway DB 마이그레이션 스크립트
process_attrdir_emission 테이블에 cumulative_emission 필드를 추가합니다.
"""

import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, List, Any

# Railway DB 연결 정보 (rule1.mdc에서 가져옴)
RAILWAY_DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def migrate_cumulative_emission():
    """cumulative_emission 필드를 추가하는 마이그레이션을 실행합니다."""
    
    try:
        # Railway DB 직접 연결
        print("🔗 Railway DB에 직접 연결 중...")
        print(f"📍 연결 주소: {RAILWAY_DATABASE_URL.split('@')[1] if '@' in RAILWAY_DATABASE_URL else '***'}")
        
        conn = await asyncpg.connect(RAILWAY_DATABASE_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 현재 테이블 구조 확인
        print("\n🔍 1. 현재 process_attrdir_emission 테이블 구조 확인")
        print("=" * 60)
        
        columns_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'process_attrdir_emission'
        ORDER BY ordinal_position;
        """
        
        columns = await conn.fetch(columns_query)
        
        print("📋 현재 컬럼들:")
        for col in columns:
            nullable_str = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default_str = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']:<25} {col['data_type']:<20} {nullable_str}{default_str}")
        
        # 2. cumulative_emission 필드 존재 여부 확인
        print("\n🔍 2. cumulative_emission 필드 존재 여부 확인")
        print("=" * 60)
        
        has_cumulative = any(col['column_name'] == 'cumulative_emission' for col in columns)
        
        if has_cumulative:
            print("✅ cumulative_emission 필드가 이미 존재합니다.")
            print("🎯 마이그레이션이 필요하지 않습니다.")
            return True
        else:
            print("❌ cumulative_emission 필드가 존재하지 않습니다.")
            print("🔧 마이그레이션을 진행합니다.")
        
        # 3. cumulative_emission 필드 추가
        print("\n🔧 3. cumulative_emission 필드 추가")
        print("=" * 60)
        
        add_column_sql = """
        ALTER TABLE process_attrdir_emission 
        ADD COLUMN cumulative_emission NUMERIC(15, 6) DEFAULT 0;
        """
        
        try:
            await conn.execute(add_column_sql)
            print("✅ cumulative_emission 필드 추가 성공!")
        except Exception as e:
            print(f"❌ 필드 추가 실패: {e}")
            return False
        
        # 4. 필드 추가 후 테이블 구조 재확인
        print("\n🔍 4. 필드 추가 후 테이블 구조 재확인")
        print("=" * 60)
        
        columns_after = await conn.fetch(columns_query)
        
        print("📋 업데이트된 컬럼들:")
        for col in columns_after:
            nullable_str = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default_str = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  {col['column_name']:<25} {col['data_type']:<20} {nullable_str}{default_str}")
        
        # 5. 기존 데이터에 대한 cumulative_emission 초기값 설정
        print("\n🔧 5. 기존 데이터 cumulative_emission 초기값 설정")
        print("=" * 60)
        
        # 기존 데이터 개수 확인
        count_query = "SELECT COUNT(*) as count FROM process_attrdir_emission;"
        count_result = await conn.fetchrow(count_query)
        total_records = count_result['count'] if count_result else 0
        
        print(f"📊 총 레코드 수: {total_records}")
        
        if total_records > 0:
            # 기존 attrdir_em 값을 cumulative_emission에 복사
            update_sql = """
            UPDATE process_attrdir_emission 
            SET cumulative_emission = attrdir_em 
            WHERE cumulative_emission = 0 OR cumulative_emission IS NULL;
            """
            
            try:
                result = await conn.execute(update_sql)
                print("✅ 기존 데이터 cumulative_emission 초기값 설정 완료!")
                print(f"📊 업데이트된 레코드 수: {result.split()[-1] if result else '알 수 없음'}")
            except Exception as e:
                print(f"❌ 초기값 설정 실패: {e}")
                return False
        else:
            print("⚠️ 업데이트할 데이터가 없습니다.")
        
        # 6. 샘플 데이터 확인
        print("\n🔍 6. 마이그레이션 후 샘플 데이터 확인")
        print("=" * 60)
        
        sample_query = """
        SELECT id, process_id, attrdir_em, cumulative_emission, calculation_date
        FROM process_attrdir_emission 
        LIMIT 3;
        """
        
        try:
            sample_data = await conn.fetch(sample_query)
            
            if sample_data:
                print("📝 샘플 데이터:")
                for i, row in enumerate(sample_data, 1):
                    print(f"  📊 샘플 {i}:")
                    print(f"    ID: {row['id']}")
                    print(f"    Process ID: {row['process_id']}")
                    print(f"    attrdir_em: {row['attrdir_em']}")
                    print(f"    cumulative_emission: {row['cumulative_emission']}")
                    print(f"    계산일: {row['calculation_date']}")
                    print()
            else:
                print("⚠️ 샘플 데이터가 없습니다.")
                
        except Exception as e:
            print(f"❌ 샘플 데이터 조회 실패: {e}")
        
        # 7. 인덱스 생성 (성능 최적화)
        print("\n🔧 7. cumulative_emission 필드 인덱스 생성")
        print("=" * 60)
        
        index_sql = """
        CREATE INDEX IF NOT EXISTS idx_process_attrdir_emission_cumulative 
        ON process_attrdir_emission(cumulative_emission);
        """
        
        try:
            await conn.execute(index_sql)
            print("✅ cumulative_emission 필드 인덱스 생성 완료!")
        except Exception as e:
            print(f"⚠️ 인덱스 생성 실패 (이미 존재할 수 있음): {e}")
        
        # 8. 마이그레이션 결과 요약
        print("\n🎯 8. 마이그레이션 결과 요약")
        print("=" * 60)
        
        migration_result = {
            'migration_date': datetime.now().isoformat(),
            'database_url': RAILWAY_DATABASE_URL.split('@')[1] if '@' in RAILWAY_DATABASE_URL else '***',
            'table_name': 'process_attrdir_emission',
            'added_column': 'cumulative_emission',
            'column_type': 'NUMERIC(15, 6)',
            'default_value': 0,
            'total_records': total_records,
            'status': 'SUCCESS'
        }
        
        print("✅ 마이그레이션 완료!")
        print(f"  📋 테이블: {migration_result['table_name']}")
        print(f"  ➕ 추가된 컬럼: {migration_result['added_column']}")
        print(f"  📊 데이터 타입: {migration_result['column_type']}")
        print(f"  🔢 기본값: {migration_result['default_value']}")
        print(f"  📊 총 레코드 수: {migration_result['total_records']}")
        
        # 결과를 JSON 파일로 저장
        with open('migration_result.json', 'w', encoding='utf-8') as f:
            json.dump(migration_result, f, indent=2, ensure_ascii=False, default=str)
        
        print("\n💾 마이그레이션 결과가 migration_result.json 파일로 저장되었습니다.")
        
        await conn.close()
        print("\n🔗 Railway DB 연결 종료")
        
        return True
        
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Railway DB 마이그레이션 시작")
    print("=" * 60)
    print("📍 process_attrdir_emission 테이블에 cumulative_emission 필드 추가")
    print("=" * 60)
    
    success = asyncio.run(migrate_cumulative_emission())
    
    if success:
        print("\n🎯 마이그레이션 완료! 다음 단계:")
        print("1. migration_result.json 파일 확인")
        print("2. 배출량 전파 서비스 구현")
        print("3. 공정 체인 기반 배출량 누적 계산")
    else:
        print("\n❌ 마이그레이션 실패! 오류를 확인하고 다시 시도해주세요.")
