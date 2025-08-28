#!/usr/bin/env python3
"""
엑셀 파일에서 HS-CN 매핑 데이터를 읽어서 Railway PostgreSQL 데이터베이스에 삽입하는 스크립트
"""

import psycopg2
import pandas as pd
import logging
import os
from typing import List, Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Railway PostgreSQL 데이터베이스 URL
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def read_excel_file(file_path: str) -> List[Dict[str, Any]]:
    """엑셀 파일을 읽어서 데이터 추출"""
    try:
        logger.info(f"📖 엑셀 파일 읽는 중: {file_path}")
        
        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)
        
        logger.info(f"📊 엑셀 파일 정보:")
        logger.info(f"   - 행 수: {len(df)}")
        logger.info(f"   - 열 수: {len(df.columns)}")
        logger.info(f"   - 열 이름: {list(df.columns)}")
        
        # 데이터를 딕셔너리 리스트로 변환
        data_list = []
        for index, row in df.iterrows():
            # NaN 값을 None으로 변환
            row_dict = {}
            for col in df.columns:
                value = row[col]
                if pd.isna(value):
                    row_dict[col] = None
                else:
                    row_dict[col] = str(value).strip() if isinstance(value, str) else value
            
            data_list.append(row_dict)
        
        logger.info(f"✅ 엑셀 파일 읽기 완료: {len(data_list)}개 행")
        return data_list
        
    except Exception as e:
        logger.error(f"❌ 엑셀 파일 읽기 실패: {e}")
        raise

def map_excel_columns_to_db(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """엑셀 컬럼을 데이터베이스 컬럼에 매핑"""
    logger.info("🔄 엑셀 컬럼을 DB 컬럼에 매핑 중...")
    
    # 엑셀 컬럼명과 DB 컬럼명 매핑 (필요에 따라 수정)
    column_mapping = {
        # 예시 매핑 (실제 엑셀 파일의 컬럼명에 맞게 수정 필요)
        'HS코드': 'hscode',
        'HS 코드': 'hscode',
        'hscode': 'hscode',
        'CN코드': 'cncode_total',
        'CN 코드': 'cncode_total',
        'cncode_total': 'cncode_total',
        '제품대분류': 'aggregoods_name',
        '제품 대분류': 'aggregoods_name',
        'aggregoods_name': 'aggregoods_name',
        '제품대분류영문': 'aggregoods_engname',
        '제품 대분류 영문': 'aggregoods_engname',
        'aggregoods_engname': 'aggregoods_engname',
        '상세품목명': 'goods_name',
        '상세 품목명': 'goods_name',
        'goods_name': 'goods_name',
        '상세품목명영문': 'goods_engname',
        '상세 품목명 영문': 'goods_engname',
        'goods_engname': 'goods_engname',
    }
    
    mapped_data = []
    for row in data_list:
        mapped_row = {}
        for excel_col, value in row.items():
            if excel_col in column_mapping:
                db_col = column_mapping[excel_col]
                
                # 데이터 타입 처리
                if value is None:
                    mapped_row[db_col] = None
                elif db_col in ['hscode', 'cncode_total']:
                    # HS 코드와 CN 코드는 문자열로 변환하고 특수문자 제거
                    str_value = str(int(value)) if isinstance(value, (int, float)) else str(value)
                    # 특수문자 제거 (*, -, 등)
                    str_value = str_value.replace('*', '').replace('-', '').replace(' ', '')
                    # 8자리로 제한
                    if db_col == 'cncode_total' and len(str_value) > 8:
                        str_value = str_value[:8]
                    mapped_row[db_col] = str_value
                else:
                    # 나머지 필드는 문자열로 변환
                    mapped_row[db_col] = str(value).strip() if isinstance(value, str) else str(value)
        
        # 필수 필드 확인
        if 'hscode' in mapped_row and 'cncode_total' in mapped_row:
            mapped_data.append(mapped_row)
        else:
            logger.warning(f"⚠️ 필수 필드 누락된 행 건너뜀: {row}")
    
    logger.info(f"✅ 컬럼 매핑 완료: {len(mapped_data)}개 유효한 행")
    return mapped_data

def insert_data_to_database(data_list: List[Dict[str, Any]]) -> bool:
    """데이터베이스에 데이터 삽입"""
    try:
        # 데이터베이스 연결
        logger.info("🔗 Railway PostgreSQL 데이터베이스에 연결 중...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 기존 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM hs_cn_mapping;")
        existing_count = cursor.fetchone()[0]
        logger.info(f"📊 기존 데이터 수: {existing_count}개")

        # 데이터 삽입
        logger.info("📝 HS-CN 매핑 데이터를 삽입 중...")
        
        inserted_count = 0
        for data in data_list:
            try:
                cursor.execute("""
                    INSERT INTO hs_cn_mapping (hscode, aggregoods_name, aggregoods_engname, cncode_total, goods_name, goods_engname)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (
                    data.get('hscode'),
                    data.get('aggregoods_name'),
                    data.get('aggregoods_engname'),
                    data.get('cncode_total'),
                    data.get('goods_name'),
                    data.get('goods_engname')
                ))
                inserted_count += 1
            except Exception as e:
                logger.error(f"❌ 행 삽입 실패: {data} - {e}")

        # 변경사항 커밋
        conn.commit()
        
        # 삽입된 데이터 수 확인
        cursor.execute("SELECT COUNT(*) FROM hs_cn_mapping;")
        new_count = cursor.fetchone()[0]
        actual_inserted = new_count - existing_count
        
        logger.info(f"✅ 데이터 삽입 완료!")
        logger.info(f"📈 새로 삽입된 데이터: {actual_inserted}개")
        logger.info(f"📊 전체 데이터 수: {new_count}개")

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
    logger.info("🚀 엑셀 파일에서 HS-CN 매핑 데이터 삽입 스크립트")
    logger.info("=" * 60)
    
    # 엑셀 파일 경로 (사용자가 수정해야 함)
    excel_file_path = input("📁 엑셀 파일 경로를 입력하세요: ").strip()
    
    if not os.path.exists(excel_file_path):
        logger.error(f"❌ 파일을 찾을 수 없습니다: {excel_file_path}")
        return
    
    try:
        # 1. 엑셀 파일 읽기
        excel_data = read_excel_file(excel_file_path)
        
        # 2. 컬럼 매핑
        mapped_data = map_excel_columns_to_db(excel_data)
        
        if not mapped_data:
            logger.error("❌ 매핑된 데이터가 없습니다. 컬럼 매핑을 확인해주세요.")
            return
        
        # 3. 데이터베이스에 삽입
        success = insert_data_to_database(mapped_data)
        
        if success:
            logger.info("\n🎉 엑셀 데이터 삽입이 완료되었습니다!")
            logger.info("\n📝 다음 단계:")
            logger.info("1. 프론트엔드에서 HS 코드 검색 테스트")
            logger.info("2. 모달창에서 실시간 검색 기능 확인")
            logger.info("3. CN 코드 자동 선택 기능 확인")
        else:
            logger.error("\n❌ 엑셀 데이터 삽입에 실패했습니다.")
            
    except Exception as e:
        logger.error(f"❌ 스크립트 실행 중 오류: {e}")

if __name__ == "__main__":
    main()
