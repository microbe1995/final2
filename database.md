커서야, product라는 테이블을 만들어줘.
다음 컬럼들이 필요해:

id는 기본키(PK)

install_id는 install 테이블의 id를 참조하는 외래키(FK)

product_name, product_category, prostart_period, proend_period, product_amount는 not null

product_category는 enum처럼 단순제품/복합제품만 입력 가능하게 제한

product_cncode, goods_name, aggrgoods_name은 자동계산 또는 DB매칭용으로 나중에 트리거나 뷰로 처리할 예정이니, 지금은 generated 대신 nullable text로 선언해줘

create table product (
    id serial primary key,
    install_id int not null references install(id),
    product_name text not null,
    product_category text not null check (product_category in ('단순제품', '복합제품')),
    prostart_period date not null,
    proend_period date not null,
    product_cncode text,
    goods_name text,
    aggrgoods_name text,
    product_amount float not null,
    product_sell float,
    product_eusell float
);


커서야, install이라는 테이블을 만들어줘.
두 개의 컬럼이 필요해:

id: 사업장 ID, 기본키(PK), int

name: 사업장 이름, not null, text

create table install (
    id serial primary key,
    name text not null
);


커서야, process라는 테이블을 만들어줘.
총 5개의 컬럼이 필요해:

id: 공정 ID, 기본키(PK), int

product_id: 소속 제품 ID, 외래키(FK)로 product.id 참조, int

process_name: 공정명, not null, text

start_period: 공정 시작일, not null, date

end_period: 공정 종료일, not null, date

create table process (
    id serial primary key,
    product_id int not null references product(id),
    process_name text not null,
    start_period date not null,
    end_period date not null
);


product 테이블을 생성해줘. 다음 조건을 반영해야 해:

- id는 기본키(PK)
- install_id는 install 테이블의 id를 참조하는 외래키(FK)
- product_name, product_category, prostart_period, proend_period, product_amount는 NOT NULL
- product_category는 '단순제품', '복합제품' 값만 입력되도록 ENUM처럼 제한
- product_cncode, goods_name, aggrgoods_name은 추후 계산 또는 매핑용으로 nullable TEXT 컬럼으로 생성 (generated 아님)

이걸 PostgreSQL에 맞춰서 만들어줘.


-- 1. ENUM 타입 정의 (한 번만 실행)
CREATE TYPE product_category_enum AS ENUM ('단순제품', '복합제품');

-- 2. product 테이블 생성
CREATE TABLE product (
    id                SERIAL PRIMARY KEY,
    install_id        INT NOT NULL REFERENCES install(id),
    product_name      TEXT NOT NULL,
    product_category  product_category_enum NOT NULL,
    prostart_period   DATE NOT NULL,
    proend_period     DATE NOT NULL,
    product_amount    FLOAT NOT NULL,
    product_cncode    TEXT,  -- 자동 계산 예정 (nullable)
    goods_name        TEXT,  -- DB 매칭용 (nullable)
    aggrgoods_name    TEXT   -- DB 매칭용 (nullable)
);


process_input 테이블을 만들어줘. 다음 조건을 반영해:

- id는 기본키(PK)
- process_id는 process 테이블의 id를 참조하는 외래키(FK)
- input_type은 ENUM처럼 'material', 'fuel', 'electricity'만 허용되도록 정의하고 NOT NULL
- input_name, amount는 NOT NULL
- factor, oxy_factor, direm_emission, indirem_emission은 현재는 자동계산 예정이라 nullable float로 선언 (generated 아님)


-- 1. ENUM 타입 정의 (한 번만 실행)
CREATE TYPE input_type_enum AS ENUM ('material', 'fuel', 'electricity');

-- 2. process_input 테이블 생성
CREATE TABLE process_input (
    id                 SERIAL PRIMARY KEY,
    process_id         INT NOT NULL REFERENCES process(id),
    input_type         input_type_enum NOT NULL,
    input_name         TEXT NOT NULL,
    amount             FLOAT NOT NULL,
    factor             FLOAT,  -- 나중에 트리거나 뷰로 자동 계산 (nullable)
    oxy_factor         FLOAT,  -- 나중에 트리거나 뷰로 자동 계산 (nullable)
    direm_emission     FLOAT,  -- 나중에 material, fuel용 자동계산
    indirem_emission   FLOAT   -- 나중에 electricity용 자동계산
);


edge 테이블을 만들어줘. 다음 조건을 반영해:

- id는 기본키(PK)
- source_node_type과 target_node_type은 'process' 또는 'product'만 허용되는 enum
- source_node_id와 target_node_id는 각각 process 또는 product 테이블의 id를 참조하는 외래키인데, 실제 FK 제약은 둘 중 하나만 참조하므로 코드에서는 제약 없이 int로 선언
- kind는 enum('consume', 'produce', 'continue')로 선언
- qty는 optional float로 선언


-- 1. ENUM 타입 정의 (한 번만 실행)
CREATE TYPE node_type_enum AS ENUM ('process', 'product');
CREATE TYPE edge_kind_enum AS ENUM ('consume', 'produce', 'continue');

-- 2. edge 테이블 생성
CREATE TABLE edge (
    id                 SERIAL PRIMARY KEY,
    source_node_type   node_type_enum NOT NULL,
    source_node_id     INT NOT NULL,
    target_node_type   node_type_enum NOT NULL,
    target_node_id     INT NOT NULL,
    kind               edge_kind_enum NOT NULL,
    qty                FLOAT
);
