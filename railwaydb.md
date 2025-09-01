
📋 1. Railway DB 테이블 목록
============================================================
📊 companies (BASE TABLE)
📊 countries (BASE TABLE)
📊 edge (BASE TABLE)
📊 fuel_master (BASE TABLE)
📊 fueldir (BASE TABLE)
📊 hs_cn_mapping (BASE TABLE)
📊 install (BASE TABLE)
📊 matdir (BASE TABLE)
📊 material_master (BASE TABLE)
📊 process (BASE TABLE)
📊 process_attrdir_emission (BASE TABLE)
📊 process_chain (BASE TABLE)
📊 process_chain_link (BASE TABLE)
📊 product (BASE TABLE)
📊 product_process (BASE TABLE)
📊 users (BASE TABLE)

📊 총 테이블 수: 16

🔍 2. 테이블별 상세 구조 분석
============================================================

📋 테이블: companies
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('companies_id_seq'::regclass)
  company_name              text                 NOT NULL
  country                   text                 NULL
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: countries
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('countries_id_seq'::regclass)
  country_name              text                 NOT NULL
  country_code              text                 NOT NULL
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: edge
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('edge_id_seq'::regclass)
  source_node_type          USER-DEFINED         NOT NULL
  source_id                 integer              NOT NULL
  target_node_type          USER-DEFINED         NOT NULL
  target_id                 integer              NOT NULL
  edge_kind                 USER-DEFINED         NOT NULL
  qty                       double precision     NULL
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: fuel_master
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('fuel_master_id_seq'::regclass)
❌ 오류 발생: 'max_length'
Traceback (most recent call last):
  File "C:\Users\SAMSUNG\Desktop\CBAM\Final\service\cbam-service\analyze_railway_db.py", line 93, in analyze_railway_database
    type_str = f"VARCHAR({col['max_length']})"
                          ~~~^^^^^^^^^^^^^^
KeyError: 'max_length'

❌ 분석 실패! 오류를 확인하고 다시 시도해주세요.
PS C:\Users\SAMSUNG\Desktop\CBAM\Final\service\cbam-service> python analyze_railway_db.py
🚀 Railway DB 직접 연결 스키마 분석 시작
============================================================
📍 rule1.mdc 규칙에 따라 Railway PostgreSQL DB를 먼저 확인합니다.
============================================================
🔗 Railway DB에 직접 연결 중...
📍 연결 주소: shortline.proxy.rlwy.net:46071/railway
✅ Railway DB 연결 성공!

📋 1. Railway DB 테이블 목록
============================================================
📊 companies (BASE TABLE)
📊 countries (BASE TABLE)
📊 edge (BASE TABLE)
📊 fuel_master (BASE TABLE)
📊 fueldir (BASE TABLE)
📊 hs_cn_mapping (BASE TABLE)
📊 install (BASE TABLE)
📊 matdir (BASE TABLE)
📊 material_master (BASE TABLE)
📊 process (BASE TABLE)
📊 process_attrdir_emission (BASE TABLE)
📊 process_chain (BASE TABLE)
📊 process_chain_link (BASE TABLE)
📊 product (BASE TABLE)
📊 product_process (BASE TABLE)
📊 users (BASE TABLE)

📊 총 테이블 수: 16

🔍 2. 테이블별 상세 구조 분석
============================================================

📋 테이블: companies
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('companies_id_seq'::regclass)
  company_name              text                 NOT NULL
  country                   text                 NULL
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: countries
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('countries_id_seq'::regclass)
  country_name              text                 NOT NULL
  country_code              text                 NOT NULL
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: edge
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('edge_id_seq'::regclass)
  source_node_type          USER-DEFINED         NOT NULL
  source_id                 integer              NOT NULL
  target_node_type          USER-DEFINED         NOT NULL
  target_id                 integer              NOT NULL
  edge_kind                 USER-DEFINED         NOT NULL
  qty                       double precision     NULL
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: fuel_master
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('fuel_master_id_seq'::regclass)
  fuel_name                 VARCHAR(255)         NOT NULL
  fuel_engname              VARCHAR(255)         NOT NULL
  fuel_factor               NUMERIC(10,6)        NOT NULL
  net_calory                NUMERIC(10,6)        NULL
  created_at                timestamp with time zone NULL DEFAULT now()

📋 테이블: fueldir
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('fueldir_id_seq'::regclass)
  process_id                integer              NOT NULL
  fuel_name                 VARCHAR(255)         NOT NULL
  fuel_factor               NUMERIC(10,6)        NOT NULL
  fuel_amount               NUMERIC(15,6)        NOT NULL
  fuel_oxyfactor            NUMERIC(5,4)         NULL DEFAULT 1.0000
  fueldir_em                NUMERIC(15,6)        NULL DEFAULT 0
  created_at                timestamp with time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp with time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: hs_cn_mapping
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('hs_cn_mapping_id_seq'::regclass)
  hscode                    VARCHAR(6)           NOT NULL
  aggregoods_name           text                 NULL
  aggregoods_engname        text                 NULL
  cncode_total              VARCHAR(8)           NOT NULL
  goods_name                text                 NULL
  goods_engname             text                 NULL

📋 테이블: install
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('install_id_seq'::regclass)
  install_name              text                 NOT NULL
  reporting_year            integer              NOT NULL DEFAULT EXTRACT(year FROM now())
  created_at                timestamp with time zone NULL DEFAULT now()
  updated_at                timestamp with time zone NULL DEFAULT now()

📋 테이블: matdir
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('matdir_id_seq'::regclass)
  process_id                integer              NOT NULL
  mat_name                  VARCHAR(255)         NOT NULL
  mat_factor                NUMERIC(10,6)        NOT NULL
  mat_amount                NUMERIC(15,6)        NOT NULL
  oxyfactor                 NUMERIC(5,4)         NULL DEFAULT 1.0000
  matdir_em                 NUMERIC(15,6)        NULL DEFAULT 0
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: material_master
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('material_master_id_seq'::regclass)
  mat_name                  VARCHAR(255)         NOT NULL
  mat_engname               VARCHAR(255)         NOT NULL
  carbon_content            NUMERIC(10,6)        NULL
  mat_factor                NUMERIC(10,6)        NOT NULL

📋 테이블: process
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('process_id_seq'::regclass)
  process_name              text                 NOT NULL
  start_period              date                 NULL
  end_period                date                 NULL
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: process_attrdir_emission
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('process_attrdir_emission_id_seq'::regclass)
  process_id                integer              NOT NULL
  total_matdir_emission     NUMERIC(15,6)        NULL DEFAULT 0
  total_fueldir_emission    NUMERIC(15,6)        NULL DEFAULT 0
  attrdir_em                NUMERIC(15,6)        NULL DEFAULT 0
  calculation_date          timestamp with time zone NULL DEFAULT now()
  created_at                timestamp with time zone NULL DEFAULT now()
  updated_at                timestamp with time zone NULL DEFAULT now()

📋 테이블: process_chain
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('process_chain_id_seq'::regclass)
  chain_name                text                 NOT NULL
  start_process_id          integer              NOT NULL
  end_process_id            integer              NOT NULL
  chain_length              integer              NOT NULL DEFAULT 1
  is_active                 boolean              NOT NULL DEFAULT true
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: process_chain_link
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('process_chain_link_id_seq'::regclass)
  chain_id                  integer              NOT NULL
  process_id                integer              NOT NULL
  sequence_order            integer              NOT NULL
  is_continue_edge          boolean              NOT NULL DEFAULT true
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

📋 테이블: product
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('product_id_seq'::regclass)
  install_id                integer              NOT NULL
  product_name              text                 NOT NULL
  product_category          text                 NOT NULL
  prostart_period           date                 NOT NULL
  proend_period             date                 NOT NULL
  cncode_total              text                 NULL
  goods_name                text                 NULL
  goods_engname             text                 NULL
  aggrgoods_name            text                 NULL
  aggrgoods_engname         text                 NULL
  product_amount            NUMERIC(15,6)        NULL DEFAULT 0
  product_sell              NUMERIC(15,6)        NULL DEFAULT 0
  product_eusell            NUMERIC(15,6)        NULL DEFAULT 0
  created_at                timestamp with time zone NULL DEFAULT now()
  updated_at                timestamp with time zone NULL DEFAULT now()

📋 테이블: product_process
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('product_process_id_seq1'::regclass)
  product_id                integer              NOT NULL
  process_id                integer              NOT NULL
  created_at                timestamp with time zone NULL DEFAULT now()
  updated_at                timestamp with time zone NULL DEFAULT now()

📋 테이블: users
----------------------------------------
  id                        integer              NOT NULL DEFAULT nextval('users_id_seq'::regclass)
  username                  text                 NOT NULL
  email                     text                 NOT NULL
  password_hash             text                 NOT NULL
  created_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP
  updated_at                timestamp without time zone NULL DEFAULT CURRENT_TIMESTAMP

🔍 3. 테이블별 인덱스 분석
============================================================

📋 테이블: companies
----------------------------------------
  🔗 companies_pkey
     CREATE UNIQUE INDEX companies_pkey ON public.companies USING btree (id)

📋 테이블: countries
----------------------------------------
  🔗 countries_pkey
     CREATE UNIQUE INDEX countries_pkey ON public.countries USING btree (id)
  🔗 countries_country_code_key
     CREATE UNIQUE INDEX countries_country_code_key ON public.countries USING btree (country_code)

📋 테이블: edge
----------------------------------------
  🔗 idx_edge_kind
     CREATE INDEX idx_edge_kind ON public.edge USING btree (edge_kind)
  🔗 idx_edge_source_node_type
     CREATE INDEX idx_edge_source_node_type ON public.edge USING btree (source_node_type)
  🔗 idx_edge_target_node_type
     CREATE INDEX idx_edge_target_node_type ON public.edge USING btree (target_node_type)
  🔗 idx_edge_source_id
     CREATE INDEX idx_edge_source_id ON public.edge USING btree (source_id)
  🔗 idx_edge_target_id
     CREATE INDEX idx_edge_target_id ON public.edge USING btree (target_id)
  🔗 edge_pkey
     CREATE UNIQUE INDEX edge_pkey ON public.edge USING btree (id)

📋 테이블: fuel_master
----------------------------------------
  🔗 fuel_master_pkey
     CREATE UNIQUE INDEX fuel_master_pkey ON public.fuel_master USING btree (id)
  🔗 idx_fuel_master_name
     CREATE INDEX idx_fuel_master_name ON public.fuel_master USING btree (fuel_name)
  🔗 idx_fuel_master_engname
     CREATE INDEX idx_fuel_master_engname ON public.fuel_master USING btree (fuel_engname)

📋 테이블: fueldir
----------------------------------------
  🔗 fueldir_pkey
     CREATE UNIQUE INDEX fueldir_pkey ON public.fueldir USING btree (id)
  🔗 idx_fueldir_process_id
     CREATE INDEX idx_fueldir_process_id ON public.fueldir USING btree (process_id)
  🔗 idx_fueldir_fuel_name
     CREATE INDEX idx_fueldir_fuel_name ON public.fueldir USING btree (fuel_name)
  🔗 idx_fueldir_created_at
     CREATE INDEX idx_fueldir_created_at ON public.fueldir USING btree (created_at)
  🔗 unique_fueldir_process_fuel
     CREATE UNIQUE INDEX unique_fueldir_process_fuel ON public.fueldir USING btree (process_id, fuel_name)
  🔗 idx_fueldir_process_fuel
     CREATE INDEX idx_fueldir_process_fuel ON public.fueldir USING btree (process_id, fuel_name)

📋 테이블: hs_cn_mapping
----------------------------------------
  🔗 hs_cn_mapping_pkey
     CREATE UNIQUE INDEX hs_cn_mapping_pkey ON public.hs_cn_mapping USING btree (id)
  🔗 idx_hs_cn_mapping_hscode
     CREATE INDEX idx_hs_cn_mapping_hscode ON public.hs_cn_mapping USING btree (hscode)
  🔗 idx_hs_cn_mapping_cncode
     CREATE INDEX idx_hs_cn_mapping_cncode ON public.hs_cn_mapping USING btree (cncode_total)

📋 테이블: install
----------------------------------------
  🔗 install_pkey
     CREATE UNIQUE INDEX install_pkey ON public.install USING btree (id)

📋 테이블: matdir
----------------------------------------
  🔗 idx_matdir_process_id
     CREATE INDEX idx_matdir_process_id ON public.matdir USING btree (process_id)
  🔗 matdir_pkey
     CREATE UNIQUE INDEX matdir_pkey ON public.matdir USING btree (id)
  🔗 unique_matdir_process_material
     CREATE UNIQUE INDEX unique_matdir_process_material ON public.matdir USING btree (process_id, mat_name)
  🔗 idx_matdir_process_material
     CREATE INDEX idx_matdir_process_material ON public.matdir USING btree (process_id, mat_name)

📋 테이블: material_master
----------------------------------------
  🔗 idx_material_master_name
     CREATE INDEX idx_material_master_name ON public.material_master USING btree (mat_name)
  🔗 idx_material_master_engname
     CREATE INDEX idx_material_master_engname ON public.material_master USING btree (mat_engname)
  🔗 material_master_pkey
     CREATE UNIQUE INDEX material_master_pkey ON public.material_master USING btree (id)

📋 테이블: process
----------------------------------------
  🔗 process_pkey
     CREATE UNIQUE INDEX process_pkey ON public.process USING btree (id)
  🔗 idx_process_name
     CREATE INDEX idx_process_name ON public.process USING btree (process_name)

📋 테이블: process_attrdir_emission
----------------------------------------
  🔗 idx_process_attrdir_emission_process_id
     CREATE INDEX idx_process_attrdir_emission_process_id ON public.process_attrdir_emission USING btree (process_id)
  🔗 process_attrdir_emission_pkey
     CREATE UNIQUE INDEX process_attrdir_emission_pkey ON public.process_attrdir_emission USING btree (id)
  🔗 process_attrdir_emission_process_id_key
     CREATE UNIQUE INDEX process_attrdir_emission_process_id_key ON public.process_attrdir_emission USING btree (process_id)

📋 테이블: process_chain
----------------------------------------
  🔗 process_chain_pkey
     CREATE UNIQUE INDEX process_chain_pkey ON public.process_chain USING btree (id)
  🔗 idx_process_chain_name
     CREATE INDEX idx_process_chain_name ON public.process_chain USING btree (chain_name)
  🔗 idx_process_chain_start
     CREATE INDEX idx_process_chain_start ON public.process_chain USING btree (start_process_id)
  🔗 idx_process_chain_end
     CREATE INDEX idx_process_chain_end ON public.process_chain USING btree (end_process_id)
  🔗 idx_process_chain_active
     CREATE INDEX idx_process_chain_active ON public.process_chain USING btree (is_active)

📋 테이블: process_chain_link
----------------------------------------
  🔗 process_chain_link_pkey
     CREATE UNIQUE INDEX process_chain_link_pkey ON public.process_chain_link USING btree (id)
  🔗 idx_chain_link_chain_id
     CREATE INDEX idx_chain_link_chain_id ON public.process_chain_link USING btree (chain_id)
  🔗 idx_chain_link_process_id
     CREATE INDEX idx_chain_link_process_id ON public.process_chain_link USING btree (process_id)
  🔗 idx_chain_link_sequence
     CREATE INDEX idx_chain_link_sequence ON public.process_chain_link USING btree (chain_id, sequence_order)

📋 테이블: product
----------------------------------------
  🔗 product_pkey
     CREATE UNIQUE INDEX product_pkey ON public.product USING btree (id)
  🔗 idx_product_install_id
     CREATE INDEX idx_product_install_id ON public.product USING btree (install_id)
  🔗 idx_product_product_name
     CREATE INDEX idx_product_product_name ON public.product USING btree (product_name)
  🔗 unique_install_product_name
     CREATE UNIQUE INDEX unique_install_product_name ON public.product USING btree (install_id, product_name)

📋 테이블: product_process
----------------------------------------
  🔗 product_process_pkey1
     CREATE UNIQUE INDEX product_process_pkey1 ON public.product_process USING btree (id)
  🔗 product_process_product_id_process_id_key
     CREATE UNIQUE INDEX product_process_product_id_process_id_key ON public.product_process USING btree (product_id, process_id)

📋 테이블: users
----------------------------------------
  🔗 users_pkey
     CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id)
  🔗 users_username_key
     CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username)
  🔗 users_email_key
     CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email)

🔍 4. 외래키 관계 분석
============================================================

📋 테이블: companies
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: countries
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: edge
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: fuel_master
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: fueldir
----------------------------------------
  🔗 process_id → process.id

📋 테이블: hs_cn_mapping
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: install
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: matdir
----------------------------------------
  🔗 process_id → process.id

📋 테이블: material_master
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: process
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: process_attrdir_emission
----------------------------------------
  🔗 process_id → process.id

📋 테이블: process_chain
----------------------------------------
  🔗 start_process_id → process.id
  🔗 end_process_id → process.id

📋 테이블: process_chain_link
----------------------------------------
  🔗 chain_id → process_chain.id
  🔗 process_id → process.id

📋 테이블: product
----------------------------------------
  ⚠️ 외래키 없음

📋 테이블: product_process
----------------------------------------
  🔗 process_id → process.id
  🔗 product_id → product.id

📋 테이블: users
----------------------------------------
  ⚠️ 외래키 없음

🔍 5. 배출량 관련 테이블 상세 분석
============================================================

📋 테이블: process_attrdir_emission
----------------------------------------
  📊 총 레코드 수: 4
  📝 샘플 1: {'id': 25, 'process_id': 156, 'total_matdir_emission': Decimal('321.000000'), 'total_fueldir_emission': Decimal('0.000000'), 'attrdir_em': Decimal('321.000000'), 'calculation_date': datetime.datetime(2025, 8, 29, 11, 31, 12, 318223, tzinfo=datetime.timezone.utc), 'created_at': datetime.datetime(2025, 8, 29, 10, 59, 36, 510515, tzinfo=datetime.timezone.utc), 'updated_at': datetime.datetime(2025, 8, 29, 11, 31, 12, 318223, tzinfo=datetime.timezone.utc)}
  📝 샘플 2: {'id': 21, 'process_id': 157, 'total_matdir_emission': Decimal('304.070000'), 'total_fueldir_emission': Decimal('146.600000'), 'attrdir_em': Decimal('450.670000'), 'calculation_date': datetime.datetime(2025, 8, 29, 11, 31, 59, 531624, tzinfo=datetime.timezone.utc), 'created_at': datetime.datetime(2025, 8, 29, 10, 57, 8, 899884, tzinfo=datetime.timezone.utc), 'updated_at': datetime.datetime(2025, 8, 29, 11, 31, 59, 531624, tzinfo=datetime.timezone.utc)}

📋 테이블: matdir
----------------------------------------
  📊 총 레코드 수: 6
  📝 샘플 1: {'id': 20, 'process_id': 157, 'mat_name': '직접환원철 (DRI)', 'mat_factor': Decimal('0.070000'), 'mat_amount': Decimal('1.000000'), 'oxyfactor': Decimal('1.0000'), 'matdir_em': Decimal('0.070000'), 'created_at': datetime.datetime(2025, 8, 29, 10, 57, 8, 899884), 'updated_at': datetime.datetime(2025, 8, 29, 10, 57, 8, 899884)}
  📝 샘플 2: {'id': 21, 'process_id': 156, 'mat_name': 'EAF 탄소 전극', 'mat_factor': Decimal('3.000000'), 'mat_amount': Decimal('100.000000'), 'oxyfactor': Decimal('1.0000'), 'matdir_em': Decimal('300.000000'), 'created_at': datetime.datetime(2025, 8, 29, 10, 59, 36, 510515), 'updated_at': datetime.datetime(2025, 8, 29, 10, 59, 36, 510515)}

📋 테이블: fueldir
----------------------------------------
  📊 총 레코드 수: 3
  📝 샘플 1: {'id': 8, 'process_id': 157, 'fuel_name': '정유 원료', 'fuel_factor': Decimal('73.300000'), 'fuel_amount': Decimal('1.000000'), 'fuel_oxyfactor': Decimal('1.0000'), 'fueldir_em': Decimal('73.300000'), 'created_at': datetime.datetime(2025, 8, 29, 10, 57, 33, 597997, tzinfo=datetime.timezone.utc), 'updated_at': datetime.datetime(2025, 8, 29, 10, 57, 33, 597997, tzinfo=datetime.timezone.utc)}
  📝 샘플 2: {'id': 10, 'process_id': 165, 'fuel_name': '폐타', 'fuel_factor': Decimal('85.000000'), 'fuel_amount': Decimal('2.000000'), 'fuel_oxyfactor': Decimal('1.0000'), 'fueldir_em': Decimal('170.000000'), 'created_at': datetime.datetime(2025, 9, 1, 8, 58, 2, 5364, tzinfo=datetime.timezone.utc), 'updated_at': datetime.datetime(2025, 9, 1, 8, 58, 2, 5364, tzinfo=datetime.timezone.utc)}

📋 테이블: edge
----------------------------------------
  📊 총 레코드 수: 48
  📝 샘플 1: {'id': 21, 'source_node_type': 'product', 'source_id': 65512, 'target_node_type': 'product', 'target_id': 445177, 'edge_kind': 'continue', 'qty': None, 'created_at': datetime.datetime(2025, 8, 31, 19, 23, 59, 132397), 'updated_at': datetime.datetime(2025, 8, 31, 19, 23, 59, 132397)}
  📝 샘플 2: {'id': 22, 'source_node_type': 'product', 'source_id': 65512, 'target_node_type': 'product', 'target_id': 445177, 'edge_kind': 'continue', 'qty': None, 'created_at': datetime.datetime(2025, 8, 31, 19, 24, 1, 875215), 'updated_at': datetime.datetime(2025, 8, 31, 19, 24, 1, 875215)}

📋 테이블: process
----------------------------------------
  📊 총 레코드 수: 29
  📝 샘플 1: {'id': 139, 'process_name': '압연1', 'start_period': None, 'end_period': None, 'created_at': datetime.datetime(2025, 8, 29, 6, 33, 0, 990068), 'updated_at': datetime.datetime(2025, 8, 29, 6, 33, 0, 990068)}
  📝 샘플 2: {'id': 140, 'process_name': '압연1', 'start_period': None, 'end_period': None, 'created_at': datetime.datetime(2025, 8, 29, 6, 33, 4, 421073), 'updated_at': datetime.datetime(2025, 8, 29, 6, 33, 4, 421073)}

📋 테이블: product
----------------------------------------
  📊 총 레코드 수: 4
  📝 샘플 1: {'id': 1, 'install_id': 9, 'product_name': '철강1', 'product_category': '단순제품', 'prostart_period': datetime.date(2025, 9, 3), 'proend_period': datetime.date(2025, 10, 2), 'cncode_total': '', 'goods_name': '', 'goods_engname': '', 'aggrgoods_name': '', 'aggrgoods_engname': '', 'product_amount': Decimal('0.000000'), 'product_sell': Decimal('0.000000'), 'product_eusell': Decimal('0.000000'), 'created_at': datetime.datetime(2025, 8, 31, 17, 42, 12, 301952, tzinfo=datetime.timezone.utc), 'updated_at': datetime.datetime(2025, 8, 31, 17, 42, 12, 301952, tzinfo=datetime.timezone.utc)}
  📝 샘플 2: {'id': 7, 'install_id': 9, 'product_name': '철강2', 'product_category': '단순제품', 'prostart_period': datetime.date(2025, 9, 19), 'proend_period': datetime.date(2025, 10, 3), 'cncode_total': '', 'goods_name': '', 'goods_engname': '', 'aggrgoods_name': '', 'aggrgoods_engname': '', 'product_amount': Decimal('0.000000'), 'product_sell': Decimal('0.000000'), 'product_eusell': Decimal('0.000000'), 'created_at': datetime.datetime(2025, 8, 31, 17, 50, 54, 652367, tzinfo=datetime.timezone.utc), 'updated_at': datetime.datetime(2025, 8, 31, 17, 50, 54, 652367, tzinfo=datetime.timezone.utc)}

🎯 6. CBAM 배출량 누적 전달 현황 분석
============================================================

📊 핵심 테이블 현황:
  ✅ process_attrdir_emission 테이블 존재
  ❌ cumulative_emission 필드 없음 - 추가 필요
  📋 기존 필드들: id, process_id, total_matdir_emission, total_fueldir_emission, attrdir_em, calculation_date, created_at, updated_at
  ✅ edge 테이블 존재
  ✅ edge_kind 필드 존재 (continue/produce/consume)
  📋 현재 edge_kind 값들: continue

🔧 7. 스키마 확장 권장사항
============================================================
  📋 권장 스키마 확장:
    1. process_attrdir_emission 테이블에 cumulative_emission 필드 추가

💾 8. 분석 결과를 JSON 파일로 저장
============================================================
✅ 분석 결과가 railway_db_analysis.json 파일로 저장되었습니다.

🔗 Railway DB 연결 종료

🎯 분석 완료! 다음 단계:
1. railway_db_analysis.json 파일 확인
2. 현재 DB 스키마 현황 파악
3. 필요한 스키마 확장 계획 수립
4. DB 마이그레이션 스크립트 작성