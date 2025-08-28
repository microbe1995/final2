#!/usr/bin/env python3
"""
HS-CN 매핑 샘플 데이터 삽입 스크립트
Railway PostgreSQL 데이터베이스에 샘플 HS-CN 매핑 데이터를 삽입합니다.
"""

import psycopg2
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Railway PostgreSQL 데이터베이스 URL
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

# 샘플 HS-CN 매핑 데이터
SAMPLE_DATA = [
    # 철강 제품 (HS 코드 72번대)
    {
        'hscode': '720851',
        'aggregoods_name': '철및철강제품',
        'aggregoods_engname': 'IronAndSteelProducts',
        'cncode_total': '72085100',
        'goods_name': '철이나 비합금강의 평판압연제품, 두께 3mm 이상 4.75mm 이하, 폭 600mm 이상',
        'goods_engname': 'Flat-rolled products of iron or non-alloy steel, of a thickness of 3mm or more but not exceeding 4.75mm, of a width of 600mm or more'
    },
    {
        'hscode': '720852',
        'aggregoods_name': '철및철강제품',
        'aggregoods_engname': 'IronAndSteelProducts',
        'cncode_total': '72085200',
        'goods_name': '철이나 비합금강의 평판압연제품, 두께 3mm 미만, 폭 600mm 이상',
        'goods_engname': 'Flat-rolled products of iron or non-alloy steel, of a thickness of less than 3mm, of a width of 600mm or more'
    },
    {
        'hscode': '720853',
        'aggregoods_name': '철및철강제품',
        'aggregoods_engname': 'IronAndSteelProducts',
        'cncode_total': '72085300',
        'goods_name': '철이나 비합금강의 평판압연제품, 두께 3mm 이상, 폭 600mm 미만',
        'goods_engname': 'Flat-rolled products of iron or non-alloy steel, of a thickness of 3mm or more, of a width of less than 600mm'
    },
    
    # 알루미늄 제품 (HS 코드 76번대)
    {
        'hscode': '760429',
        'aggregoods_name': '알루미늄제품',
        'aggregoods_engname': 'AluminumProducts',
        'cncode_total': '76042900',
        'goods_name': '알루미늄의 평판압연제품, 두께 0.2mm 이상 0.3mm 미만',
        'goods_engname': 'Aluminum flat-rolled products, of a thickness of 0.2mm or more but less than 0.3mm'
    },
    {
        'hscode': '760430',
        'aggregoods_name': '알루미늄제품',
        'aggregoods_engname': 'AluminumProducts',
        'cncode_total': '76043000',
        'goods_name': '알루미늄의 평판압연제품, 두께 0.3mm 이상',
        'goods_engname': 'Aluminum flat-rolled products, of a thickness of 0.3mm or more'
    },
    
    # 시멘트 제품 (HS 코드 25번대)
    {
        'hscode': '252329',
        'aggregoods_name': '시멘트제품',
        'aggregoods_engname': 'CementProducts',
        'cncode_total': '25232900',
        'goods_name': '포틀랜드 시멘트, 알루미나 시멘트, 슬래그 시멘트, 초고알루미나 시멘트 및 유사한 수경성 시멘트',
        'goods_engname': 'Portland cement, alumina cement, slag cement, super-sulfated cement and similar hydraulic cements'
    },
    
    # 유리 제품 (HS 코드 70번대)
    {
        'hscode': '700521',
        'aggregoods_name': '유리제품',
        'aggregoods_engname': 'GlassProducts',
        'cncode_total': '70052100',
        'goods_name': '유리의 평판압연제품, 유리판, 유리판지, 유리판지, 유리판지, 유리판지',
        'goods_engname': 'Float glass and surface ground or polished glass, in sheets, whether or not having an absorbent, reflecting or non-reflecting layer'
    },
    
    # 플라스틱 제품 (HS 코드 39번대)
    {
        'hscode': '390410',
        'aggregoods_name': '플라스틱제품',
        'aggregoods_engname': 'PlasticProducts',
        'cncode_total': '39041000',
        'goods_name': '폴리염화비닐, 가소화되지 않은 것',
        'goods_engname': 'Poly(vinyl chloride), not mixed with any other substances'
    },
    {
        'hscode': '390421',
        'aggregoods_name': '플라스틱제품',
        'aggregoods_engname': 'PlasticProducts',
        'cncode_total': '39042100',
        'goods_name': '폴리염화비닐, 가소화된 것',
        'goods_engname': 'Poly(vinyl chloride), plasticized'
    }
]

def insert_sample_data():
    """샘플 HS-CN 매핑 데이터 삽입"""
    try:
        # 데이터베이스 연결
        logger.info("🔗 Railway PostgreSQL 데이터베이스에 연결 중...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 기존 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM hs_cn_mapping;")
        existing_count = cursor.fetchone()[0]
        logger.info(f"📊 기존 데이터 수: {existing_count}개")

        # 샘플 데이터 삽입
        logger.info("📝 샘플 HS-CN 매핑 데이터를 삽입 중...")
        
        for data in SAMPLE_DATA:
            cursor.execute("""
                INSERT INTO hs_cn_mapping (hscode, aggregoods_name, aggregoods_engname, cncode_total, goods_name, goods_engname)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (hscode, cncode_total) DO NOTHING;
            """, (
                data['hscode'],
                data['aggregoods_name'],
                data['aggregoods_engname'],
                data['cncode_total'],
                data['goods_name'],
                data['goods_engname']
            ))

        # 변경사항 커밋
        conn.commit()
        
        # 삽입된 데이터 수 확인
        cursor.execute("SELECT COUNT(*) FROM hs_cn_mapping;")
        new_count = cursor.fetchone()[0]
        inserted_count = new_count - existing_count
        
        logger.info(f"✅ 샘플 데이터 삽입 완료!")
        logger.info(f"📈 새로 삽입된 데이터: {inserted_count}개")
        logger.info(f"📊 전체 데이터 수: {new_count}개")

        # 샘플 조회 테스트
        logger.info("\n🔍 샘플 조회 테스트:")
        logger.info("-" * 50)
        
        # HS 코드 720851로 조회 테스트
        cursor.execute("SELECT * FROM hs_cn_mapping WHERE hscode = '720851';")
        results = cursor.fetchall()
        
        for result in results:
            logger.info(f"HS 코드: {result[1]}")
            logger.info(f"CN 코드: {result[4]}")
            logger.info(f"품목명: {result[5]}")
            logger.info(f"제품 대분류: {result[2]}")
            logger.info("-" * 30)

        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        logger.error(f"❌ 데이터베이스 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        return False

def main():
    """메인 함수"""
    logger.info("🚀 HS-CN 매핑 샘플 데이터 삽입 스크립트")
    logger.info("=" * 50)
    logger.info(f"📡 데이터베이스: Railway PostgreSQL")
    logger.info(f"📝 삽입할 샘플 데이터: {len(SAMPLE_DATA)}개")

    success = insert_sample_data()

    if success:
        logger.info("\n🎉 샘플 데이터 삽입이 완료되었습니다!")
        logger.info("\n📝 다음 단계:")
        logger.info("1. 프론트엔드에서 HS 코드 입력 테스트")
        logger.info("2. CN 코드 자동 조회 기능 확인")
        logger.info("3. 제품 생성 시 CN 코드 정보 자동 입력 확인")
    else:
        logger.error("\n❌ 샘플 데이터 삽입에 실패했습니다.")
        exit(1)

if __name__ == "__main__":
    main()
