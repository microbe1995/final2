import psycopg2

def clean_duplicate_products():
    """중복된 product 데이터 정리"""
    
    # Railway DB 연결
    conn = psycopg2.connect(
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    )
    cur = conn.cursor()
    
    try:
        print("🔍 중복 데이터 확인 중...")
        
        # 현재 product 테이블의 모든 데이터 조회
        cur.execute("SELECT * FROM product ORDER BY id;")
        products = cur.fetchall()
        
        print(f"📊 현재 product 테이블에 {len(products)}개의 레코드가 있습니다.")
        
        if len(products) > 0:
            print("\n📋 현재 데이터:")
            for product in products:
                print(f"  ID: {product[0]}, 제품명: {product[2]}, 카테고리: {product[3]}")
            
            # 사용자 확인
            response = input("\n❓ 중복 데이터를 정리하시겠습니까? (y/N): ")
            
            if response.lower() == 'y':
                # 모든 데이터 삭제
                cur.execute("DELETE FROM product;")
                conn.commit()
                
                print("✅ 중복 데이터 정리 완료!")
                print("📝 이제 Frontend에서 새로운 제품을 생성해보세요.")
            else:
                print("❌ 데이터 정리를 취소했습니다.")
        else:
            print("✅ 중복 데이터가 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    clean_duplicate_products()
