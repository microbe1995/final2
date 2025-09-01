#!/usr/bin/env python3
"""
matdir 수정사항 테스트 스크립트
- Railway DB의 materials 테이블을 사용하는지 확인
- 원료명 입력 시 배출계수 자동 매핑이 작동하는지 확인
"""

import asyncio
import os
import sys
from decimal import Decimal

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'service', 'cbam-service'))

from app.domain.matdir.matdir_repository import MatDirRepository
from app.domain.matdir.matdir_service import MatDirService
from app.domain.matdir.matdir_schema import MatDirCreateRequest

async def test_material_lookup():
    """원료명으로 배출계수 조회 테스트"""
    print("🔍 원료명으로 배출계수 조회 테스트")
    print("=" * 50)
    
    repository = MatDirRepository()
    service = MatDirService()
    
    # 테스트할 원료명들
    test_materials = [
        "석회석",  # 실제 존재하는 원료
        "선철",    # 실제 존재하는 원료
        "페트콕",  # 실제 존재하는 원료
        "존재하지않는원료"
    ]
    
    for mat_name in test_materials:
        print(f"\n📋 테스트 원료: {mat_name}")
        
        try:
            # Repository 레벨 테스트
            print("  🔧 Repository 레벨 테스트:")
            material = await repository.get_material_by_name(mat_name)
            if material:
                print(f"    ✅ 조회 성공: {material['mat_name']} → 배출계수: {material['mat_factor']}")
            else:
                print(f"    ❌ 조회 실패: {mat_name}을 찾을 수 없음")
            
            # Service 레벨 테스트
            print("  🎯 Service 레벨 테스트:")
            factor_result = await service.get_material_factor_by_name(mat_name)
            if factor_result.get('found'):
                print(f"    ✅ 배출계수 조회 성공: {factor_result['mat_factor']}")
            else:
                print(f"    ❌ 배출계수 조회 실패: {mat_name}")
                
        except Exception as e:
            print(f"    ❌ 오류 발생: {str(e)}")

async def test_auto_factor_mapping():
    """자동 배출계수 매핑 테스트"""
    print("\n\n🚀 자동 배출계수 매핑 테스트")
    print("=" * 50)
    
    service = MatDirService()
    
    # 테스트 데이터 - 실제 존재하는 원료명 사용
    test_data = MatDirCreateRequest(
        process_id=1,
        mat_name="석회석",  # Railway DB에 존재하는 원료명
        mat_factor=Decimal('0'),  # 0으로 설정하여 자동 매핑 테스트
        mat_amount=Decimal('100.0'),
        oxyfactor=Decimal('1.0000')
    )
    
    print(f"📝 테스트 데이터: {test_data.model_dump()}")
    
    try:
        result = await service.create_matdir_with_auto_factor(test_data)
        print(f"✅ 자동 매핑 성공: {result.mat_name} → 배출계수: {result.mat_factor}")
        print(f"   계산된 배출량: {result.matdir_em}")
    except Exception as e:
        print(f"❌ 자동 매핑 실패: {str(e)}")

async def test_materials_table_access():
    """Railway DB의 materials 테이블 접근 테스트"""
    print("\n\n🗄️ Railway DB materials 테이블 접근 테스트")
    print("=" * 50)
    
    repository = MatDirRepository()
    
    try:
        # 모든 원료 조회
        print("📋 모든 원료 조회:")
        all_materials = await repository.get_all_materials()
        print(f"   총 {len(all_materials)}개의 원료가 있습니다.")
        
        if all_materials:
            print("   📝 첫 5개 원료:")
            for i, material in enumerate(all_materials[:5]):
                print(f"     {i+1}. {material['mat_name']} (배출계수: {material['mat_factor']})")
        
        # 검색 테스트
        print("\n🔍 검색 테스트:")
        search_results = await repository.search_materials("석")
        print(f"   '석'으로 검색 결과: {len(search_results)}개")
        for material in search_results[:3]:
            print(f"     - {material['mat_name']} (배출계수: {material['mat_factor']})")
            
    except Exception as e:
        print(f"❌ 테이블 접근 실패: {str(e)}")

async def main():
    """메인 테스트 함수"""
    print("🧪 matdir 수정사항 테스트 시작")
    print("=" * 60)
    
    # 1. Railway DB materials 테이블 접근 테스트
    await test_materials_table_access()
    
    # 2. 원료명으로 배출계수 조회 테스트
    await test_material_lookup()
    
    # 3. 자동 배출계수 매핑 테스트
    await test_auto_factor_mapping()
    
    print("\n\n✅ 모든 테스트 완료!")

if __name__ == "__main__":
    # 환경변수 설정 (필요한 경우)
    if not os.getenv('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway'
    
    asyncio.run(main())
