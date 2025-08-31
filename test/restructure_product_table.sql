-- ============================================================================
-- 🏭 Product 테이블 재구성 스크립트
-- ============================================================================

-- 1단계: 기존 테이블 백업
CREATE TABLE product_backup AS SELECT * FROM product;

-- 2단계: 기존 product 테이블 삭제
DROP TABLE IF EXISTS product;

-- 3단계: product_core 테이블 생성 (사용자 입력 + 자동 생성)
CREATE TABLE product_core (
    id SERIAL PRIMARY KEY,
    install_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL,
    prostart_period DATE NOT NULL,
    proend_period DATE NOT NULL,
    cncode_total TEXT,
    goods_name TEXT,
    goods_engname TEXT,
    aggrgoods_name TEXT,
    aggrgoods_engname TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_install_product UNIQUE(install_id, product_name),
    CONSTRAINT valid_period CHECK(prostart_period <= proend_period)
);

-- 4단계: product_detail 테이블 생성 (나중에 입력받는 정보)
CREATE TABLE product_detail (
    id SERIAL PRIMARY KEY,
    product_core_id INTEGER NOT NULL REFERENCES product_core(id) ON DELETE CASCADE,
    product_amount NUMERIC(15, 6) DEFAULT 0,
    product_sell NUMERIC(15, 6) DEFAULT 0,
    product_eusell NUMERIC(15, 6) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5단계: 기존 데이터 마이그레이션 (핵심 정보만)
INSERT INTO product_core (
    install_id, product_name, product_category, prostart_period, proend_period,
    cncode_total, goods_name, goods_engname, aggrgoods_name, aggrgoods_engname,
    created_at, updated_at
)
SELECT 
    install_id, product_name, product_category, prostart_period, proend_period,
    cncode_total, goods_name, goods_engname, aggrgoods_name, aggrgoods_engname,
    created_at, updated_at
FROM product_backup;

-- 6단계: 기존 데이터 마이그레이션 (상세 정보)
INSERT INTO product_detail (
    product_core_id, product_amount, product_sell, product_eusell, created_at, updated_at
)
SELECT 
    pc.id, pb.product_amount, pb.product_sell, pb.product_eusell, pb.created_at, pb.updated_at
FROM product_backup pb
JOIN product_core pc ON pb.install_id = pc.install_id AND pb.product_name = pc.product_name;

-- 7단계: product_core에 install 테이블 참조 추가
ALTER TABLE product_core 
ADD CONSTRAINT fk_product_core_install 
FOREIGN KEY (install_id) REFERENCES install(id);

-- 8단계: 인덱스 생성 (성능 향상)
CREATE INDEX idx_product_core_install_id ON product_core(install_id);
CREATE INDEX idx_product_core_product_name ON product_core(product_name);
CREATE INDEX idx_product_detail_core_id ON product_detail(product_core_id);

-- 9단계: 확인 쿼리
SELECT 'product_core' as table_name, COUNT(*) as record_count FROM product_core
UNION ALL
SELECT 'product_detail' as table_name, COUNT(*) as record_count FROM product_detail
UNION ALL
SELECT 'product_backup' as table_name, COUNT(*) as record_count FROM product_backup;

-- 10단계: 테이블 구조 확인
\d product_core
\d product_detail
