이 파일은 backend 및 db 의 사항을 종합하고 커서에게 명령을 내리기 위한 파일임

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

install_name: 사업장 이름, not null, text

reporting_year: 보고기간 (년도), not null, int

create table install (
    id serial primary key,
    install_name text not null,
    reporting_year int not null default extract(year from current_date)
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
- input_name, input_amount는 NOT NULL
- factor, oxy_factor, direm, indirem은 현재는 자동계산 예정이라 nullable float로 선언 (generated 아님)


-- 1. ENUM 타입 정의 (한 번만 실행)
CREATE TYPE input_type_enum AS ENUM ('material', 'fuel', 'electricity');

-- 2. process_input 테이블 생성
CREATE TABLE process_input (
    id                 SERIAL PRIMARY KEY,
    process_id         INT NOT NULL REFERENCES process(id),
    input_type         input_type_enum NOT NULL,
    input_name         TEXT NOT NULL,
    input_amount       FLOAT NOT NULL,
    factor             FLOAT,  -- 나중에 트리거나 뷰로 자동 계산 (nullable)
    oxy_factor         FLOAT,  -- 나중에 트리거나 뷰로 자동 계산 (nullable)
    direm              FLOAT,  -- 나중에 material, fuel용 자동계산
    indirem            FLOAT   -- 나중에 electricity용 자동계산
);


edge 테이블을 만들어줘. 다음 조건을 반영해:

- id는 기본키(PK)
- source_id와 target_id는 각각 process 또는 product 테이블의 id를 참조하는 외래키인데, 실제 FK 제약은 둘 중 하나만 참조하므로 코드에서는 제약 없이 int로 선언
- edge_kind는 enum('consume', 'produce', 'continue')로 선언
- qty는 optional float로 선언


-- 1. ENUM 타입 정의 (한 번만 실행)
CREATE TYPE edge_kind_enum AS ENUM ('consume', 'produce', 'continue');

-- 2. edge 테이블 생성
CREATE TABLE edge (
    id                 SERIAL PRIMARY KEY,
    source_id          INT NOT NULL,
    target_id          INT NOT NULL,
    edge_kind          edge_kind_enum NOT NULL,
    qty                FLOAT
);


맞습니다. 말씀하신 게 정확히 기준정보(마스터 데이터) 레벨에서의 설계 방식이에요.
정리하면 이렇게 이해하시면 돼요:

사업장 기준정보(마스터층)

사업장 단위로 생산하는 제품(Product) 목록을 먼저 등록

각 제품별로 생산에 필요한 **공정(Process)**을 미리 연결해둠

산정경계나 노드 추가 단계

사용자가 특정 사업장에서 노드를 추가할 때는
→ 그 사업장에 등록된 제품노드만 선택 가능
→ 그 사업장에서 정의한 공정노드만 선택 가능

효과

이렇게 하면 다른 사업장에서 쓰지 않는 제품·공정은 선택할 수 없으니 데이터 무결성이 보장됨

각 사업장별로 생산 체계가 다르더라도, 미리 설정된 틀 안에서만 노드/엣지를 추가하게 되어 혼란이 줄어듦

즉, 지금 구상하신 로직은 **"사업장별 제품·공정 마스터를 정의해두고, 실제 노드 생성 시 해당 마스터에만 종속되도록 제한한다"**라는 구조