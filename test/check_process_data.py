import psycopg2

def check_process_data():
    """process 테이블 데이터 확인"""
    
    # Railway DB 연결
    conn = psycopg2.connect(
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    )
    cur = conn.cursor()
    
    try:
        print("🔍 process 테이블 데이터 확인 중...")
        
        # process 테이블 데이터 조회
        cur.execute("""
            SELECT p.id, p.product_id, p.process_name, p.start_period, p.end_period,
                   pr.product_name, pr.product_category
            FROM process p
            LEFT JOIN product pr ON p.product_id = pr.id
            ORDER BY p.id;
        """)
        
        processes = cur.fetchall()
        print(f"📊 현재 process 테이블에 {len(processes)}개의 레코드가 있습니다.")
        
        if len(processes) > 0:
            print("\n📋 현재 데이터:")
            print("-" * 80)
            print(f"{'ID':<4} {'제품ID':<6} {'프로세스명':<20} {'시작일':<12} {'종료일':<12} {'제품명':<15}")
            print("-" * 80)
            
            for process in processes:
                id, product_id, process_name, start_period, end_period, product_name, product_category = process
                product_display = f"{product_name or 'N/A'} ({product_category or 'N/A'})" if product_name else f"제품ID: {product_id}"
                print(f"{id:<4} {product_id:<6} {process_name:<20} {start_period:<12} {end_period:<12} {product_display:<15}")
            
            print("-" * 80)
        else:
            print("✅ process 테이블에 데이터가 없습니다.")
            print("📝 Frontend에서 새로운 프로세스를 생성해보세요.")
        
        # 제품 테이블도 확인
        print("\n🔍 product 테이블 확인...")
        cur.execute("SELECT id, product_name, product_category FROM product ORDER BY id;")
        products = cur.fetchall()
        print(f"📊 product 테이블에 {len(products)}개의 레코드가 있습니다.")
        
        if len(products) > 0:
            print("📋 사용 가능한 제품들:")
            for product in products:
                id, name, category = product
                print(f"  ID: {id}, 제품명: {name}, 카테고리: {category}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_process_data()
