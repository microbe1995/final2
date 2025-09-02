import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Railway PostgreSQL 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def connect_to_database():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("데이터베이스 연결 성공")
        return conn
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        raise

def create_dummy_table(conn):
    """dummy 테이블 생성"""
    try:
        cursor = conn.cursor()
        
        # 기존 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS dummy CASCADE")
        logger.info("기존 dummy 테이블 삭제 완료")
        
        # dummy 테이블 생성 SQL
        create_table_sql = """
        CREATE TABLE dummy (
            id SERIAL PRIMARY KEY,
            로트번호 VARCHAR(255),
            생산품명 VARCHAR(255),
            생산수량 DECIMAL(15,2),
            투입일 DATE,
            종료일 DATE,
            공정 VARCHAR(255),
            투입물명 VARCHAR(255),
            수량 DECIMAL(15,2),
            단위 VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        logger.info("dummy 테이블 생성 완료")
        
    except Exception as e:
        logger.error(f"테이블 생성 실패: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()

def read_excel_data():
    """엑셀 파일 읽기"""
    try:
        # 엑셀 파일 경로
        excel_path = "../masterdb/dummy_db.xlsx"
        
        # 엑셀 파일 읽기
        df = pd.read_excel(excel_path)
        logger.info(f"엑셀 파일 읽기 완료: {len(df)} 행")
        
        # 컬럼명 확인 및 정리
        logger.info(f"컬럼명: {list(df.columns)}")
        
        # 데이터 타입 변환
        df = df.fillna('')  # NaN 값을 빈 문자열로 변환
        
        return df
        
    except Exception as e:
        logger.error(f"엑셀 파일 읽기 실패: {e}")
        raise

def insert_dummy_data(conn, df):
    """dummy 테이블에 데이터 삽입"""
    try:
        cursor = conn.cursor()
        
        # 기존 데이터 삭제는 테이블 재생성 시 이미 처리됨
        logger.info("데이터 삽입 시작")
        
        # 데이터 삽입
        insert_sql = """
        INSERT INTO dummy (
            로트번호, 생산품명, 생산수량, 투입일, 종료일, 
            공정, 투입물명, 수량, 단위
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        inserted_count = 0
        for index, row in df.iterrows():
            try:
                # 날짜 변환
                input_date = None
                end_date = None
                
                if pd.notna(row.get('투입일', '')) and row['투입일'] != '':
                    if isinstance(row['투입일'], str):
                        input_date = datetime.strptime(row['투입일'], '%Y-%m-%d').date()
                    elif isinstance(row['투입일'], datetime):
                        input_date = row['투입일'].date()
                
                if pd.notna(row.get('종료일', '')) and row['종료일'] != '':
                    if isinstance(row['종료일'], str):
                        end_date = datetime.strptime(row['종료일'], '%Y-%m-%d').date()
                    elif isinstance(row['종료일'], datetime):
                        end_date = row['종료일'].date()
                
                # 숫자 데이터 변환
                production_qty = float(row.get('생산수량', 0)) if pd.notna(row.get('생산수량', 0)) else 0
                material_qty = float(row.get('수량', 0)) if pd.notna(row.get('수량', 0)) else 0
                
                cursor.execute(insert_sql, (
                    str(row.get('로트번호', '')),
                    str(row.get('생산품명', '')),
                    production_qty,
                    input_date,
                    end_date,
                    str(row.get('공정', '')),
                    str(row.get(' 투입물명', '')).strip(),  # 앞의 공백 제거
                    material_qty,
                    str(row.get('단위', ''))
                ))
                inserted_count += 1
                
            except Exception as e:
                logger.warning(f"행 {index + 1} 삽입 실패: {e}")
                continue
        
        conn.commit()
        logger.info(f"데이터 삽입 완료: {inserted_count} 행")
        
    except Exception as e:
        logger.error(f"데이터 삽입 실패: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()

def verify_data(conn):
    """데이터 검증"""
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 전체 행 수 확인
        cursor.execute("SELECT COUNT(*) as count FROM dummy")
        total_count = cursor.fetchone()['count']
        logger.info(f"총 데이터 수: {total_count}")
        
        # 샘플 데이터 확인
        cursor.execute("SELECT * FROM dummy LIMIT 5")
        sample_data = cursor.fetchall()
        
        logger.info("샘플 데이터:")
        for row in sample_data:
            logger.info(f"  {row}")
        
        # 컬럼별 데이터 타입 확인
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'dummy'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        logger.info("테이블 스키마:")
        for col in columns:
            logger.info(f"  {col['column_name']}: {col['data_type']}")
        
    except Exception as e:
        logger.error(f"데이터 검증 실패: {e}")
        raise
    finally:
        cursor.close()

def main():
    """메인 실행 함수"""
    conn = None
    try:
        # 1. 데이터베이스 연결
        conn = connect_to_database()
        
        # 2. 엑셀 데이터 읽기
        df = read_excel_data()
        
        # 3. 테이블 생성
        create_dummy_table(conn)
        
        # 4. 데이터 삽입
        insert_dummy_data(conn, df)
        
        # 5. 데이터 검증
        verify_data(conn)
        
        logger.info("모든 작업이 성공적으로 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"작업 실패: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
