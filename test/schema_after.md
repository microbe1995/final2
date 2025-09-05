## 스키마: public
### public.companies (b'r', 16.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('companies_id_seq'::regclass)
  - company_name: text (NOT NULL)
  - country: text (NULL)
  - created_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - updated_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - companies_pkey (UNIQUE) on (id)

### public.countries (b'r', 24.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('countries_id_seq'::regclass)
  - country_name: text (NOT NULL)
  - country_code: text (NOT NULL)
  - created_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - updated_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - countries_country_code_key (UNIQUE) on (country_code)
  - countries_pkey (UNIQUE) on (id)

### public.dummy (b'r', 96.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('dummy_id_seq'::regclass)
  - 로트번호: character varying (NULL)
  - 생산품명: character varying (NULL)
  - 생산수량: numeric (NULL)
  - 투입일: date (NULL)
  - 종료일: date (NULL)
  - 공정: character varying (NULL)
  - 투입물명: character varying (NULL)
  - 수량: numeric (NULL)
  - 단위: character varying (NULL)
  - created_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - updated_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - 주문처명: text (NULL)
  - 오더번호: integer (NULL)
  - 생산수량_단위: text (NULL)
  - 투입물_단위: text (NULL)
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - dummy_pkey (UNIQUE) on (id)
  - idx_dummy_오더번호 (NONUNIQUE) on (오더번호)
  - idx_dummy_주문처명 (NONUNIQUE) on (주문처명)

### public.edge (b'r', 136.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('edge_id_seq'::regclass)
  - source_node_type: USER-DEFINED (NOT NULL)
  - source_id: integer (NOT NULL)
  - target_node_type: USER-DEFINED (NOT NULL)
  - target_id: integer (NOT NULL)
  - edge_kind: USER-DEFINED (NOT NULL)
  - created_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - updated_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - edge_pkey (UNIQUE) on (id)
  - idx_edge_kind (NONUNIQUE) on (edge_kind)
  - idx_edge_source_id (NONUNIQUE) on (source_id)
  - idx_edge_source_node_type (NONUNIQUE) on (source_node_type)
  - idx_edge_target_id (NONUNIQUE) on (target_id)
  - idx_edge_target_node_type (NONUNIQUE) on (target_node_type)

### public.fuel_master (b'r', 64.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('fuel_master_id_seq'::regclass)
  - fuel_name: character varying (NOT NULL)
  - fuel_engname: character varying (NOT NULL)
  - fuel_factor: numeric (NOT NULL)
  - net_calory: numeric (NULL)
  - created_at: timestamp with time zone (NULL) default=now()
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - fuel_master_pkey (UNIQUE) on (id)
  - idx_fuel_master_engname (NONUNIQUE) on (fuel_engname)
  - idx_fuel_master_name (NONUNIQUE) on (fuel_name)

### public.fueldir (b'r', 104.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('fueldir_id_seq'::regclass)
  - process_id: integer (NOT NULL)
  - fuel_name: character varying (NOT NULL)
  - fuel_factor: numeric (NOT NULL)
  - fuel_amount: numeric (NOT NULL)
  - fuel_oxyfactor: numeric (NULL) default=1.0000
  - fueldir_em: numeric (NULL) default=0
  - created_at: timestamp with time zone (NULL) default=CURRENT_TIMESTAMP
  - updated_at: timestamp with time zone (NULL) default=CURRENT_TIMESTAMP
- 기본키: id
- 외래키:
  - fk_fueldir_process: (process_id) -> public.process(id)
- 인덱스:
  - fueldir_pkey (UNIQUE) on (id)
  - idx_fueldir_created_at (NONUNIQUE) on (created_at)
  - idx_fueldir_fuel_name (NONUNIQUE) on (fuel_name)
  - idx_fueldir_process_fuel (NONUNIQUE) on (process_id, fuel_name)
  - idx_fueldir_process_id (NONUNIQUE) on (process_id)
  - unique_fueldir_process_fuel (UNIQUE) on (process_id, fuel_name)

### public.hs_cn_mapping (b'r', 96.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('hs_cn_mapping_id_seq'::regclass)
  - hscode: character varying (NOT NULL)
  - aggregoods_name: text (NULL)
  - aggregoods_engname: text (NULL)
  - cncode_total: character varying (NOT NULL)
  - goods_name: text (NULL)
  - goods_engname: text (NULL)
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - hs_cn_mapping_pkey (UNIQUE) on (id)
  - idx_hs_cn_mapping_cncode (NONUNIQUE) on (cncode_total)
  - idx_hs_cn_mapping_hscode (NONUNIQUE) on (hscode)

### public.install (b'r', 48.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('install_id_seq'::regclass)
  - install_name: text (NOT NULL)
  - reporting_year: integer (NOT NULL) default=EXTRACT(year FROM now())
  - created_at: timestamp with time zone (NULL) default=now()
  - updated_at: timestamp with time zone (NULL) default=now()
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - install_pkey (UNIQUE) on (id)
  - uk_install_name (UNIQUE) on (install_name)

### public.matdir (b'r', 88.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('matdir_id_seq'::regclass)
  - process_id: integer (NOT NULL)
  - mat_name: character varying (NOT NULL)
  - mat_factor: numeric (NOT NULL)
  - mat_amount: numeric (NOT NULL)
  - oxyfactor: numeric (NULL) default=1.0000
  - matdir_em: numeric (NULL) default=0
  - created_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - updated_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
- 기본키: id
- 외래키:
  - matdir_process_id_fkey: (process_id) -> public.process(id)
- 인덱스:
  - idx_matdir_process_id (NONUNIQUE) on (process_id)
  - idx_matdir_process_material (NONUNIQUE) on (process_id, mat_name)
  - matdir_pkey (UNIQUE) on (id)
  - unique_matdir_process_material (UNIQUE) on (process_id, mat_name)

### public.material_master (b'r', 64.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('material_master_id_seq'::regclass)
  - mat_name: character varying (NOT NULL)
  - mat_engname: character varying (NOT NULL)
  - carbon_content: numeric (NULL)
  - mat_factor: numeric (NOT NULL)
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - idx_material_master_engname (NONUNIQUE) on (mat_engname)
  - idx_material_master_name (NONUNIQUE) on (mat_name)
  - material_master_pkey (UNIQUE) on (id)

### public.process (b'r', 80.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('process_id_seq'::regclass)
  - process_name: text (NOT NULL)
  - start_period: date (NULL)
  - end_period: date (NULL)
  - created_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - updated_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - install_id: integer (NOT NULL) default=1
- 기본키: id
- 외래키:
  - fk_process_install: (install_id) -> public.install(id)
- 인덱스:
  - idx_process_name (NONUNIQUE) on (process_name)
  - process_pkey (UNIQUE) on (id)
  - uk_process_name_install (UNIQUE) on (process_name, install_id)

### public.process_attrdir_emission (b'r', 104.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('process_attrdir_emission_id_seq'::regclass)
  - process_id: integer (NOT NULL)
  - total_matdir_emission: numeric (NULL) default=0
  - total_fueldir_emission: numeric (NULL) default=0
  - attrdir_em: numeric (NULL) default=0
  - calculation_date: timestamp with time zone (NULL) default=now()
  - created_at: timestamp with time zone (NULL) default=now()
  - updated_at: timestamp with time zone (NULL) default=now()
  - cumulative_emission: numeric (NULL) default=0
- 기본키: id
- 외래키:
  - process_attrdir_emission_process_id_fkey: (process_id) -> public.process(id)
- 인덱스:
  - idx_process_attrdir_emission_cumulative (NONUNIQUE) on (cumulative_emission)
  - idx_process_attrdir_emission_process_id (NONUNIQUE) on (process_id)
  - process_attrdir_emission_pkey (UNIQUE) on (id)
  - process_attrdir_emission_process_id_key (UNIQUE) on (process_id)

### public.product (b'r', 112.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('product_id_seq'::regclass)
  - install_id: integer (NOT NULL)
  - product_name: text (NOT NULL)
  - product_category: text (NOT NULL)
  - prostart_period: date (NOT NULL)
  - proend_period: date (NOT NULL)
  - cncode_total: text (NULL)
  - goods_name: text (NULL)
  - goods_engname: text (NULL)
  - aggrgoods_name: text (NULL)
  - aggrgoods_engname: text (NULL)
  - product_amount: numeric (NULL) default=0
  - product_sell: numeric (NULL) default=0
  - product_eusell: numeric (NULL) default=0
  - created_at: timestamp with time zone (NULL) default=now()
  - updated_at: timestamp with time zone (NULL) default=now()
  - attr_em: numeric (NULL) default=0.0
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - idx_product_install_id (NONUNIQUE) on (install_id)
  - idx_product_product_name (NONUNIQUE) on (product_name)
  - product_pkey (UNIQUE) on (id)
  - unique_install_product_name (UNIQUE) on (install_id, product_name)

### public.product_process (b'r', 88.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('product_process_id_seq1'::regclass)
  - product_id: integer (NOT NULL)
  - process_id: integer (NOT NULL)
  - created_at: timestamp with time zone (NULL) default=now()
  - updated_at: timestamp with time zone (NULL) default=now()
  - consumption_amount: numeric (NULL) default=0
- 기본키: id
- 외래키:
  - product_process_process_id_fkey1: (process_id) -> public.process(id)
  - product_process_product_id_fkey: (product_id) -> public.product(id)
- 인덱스:
  - idx_product_process_consumption_amount (NONUNIQUE) on (consumption_amount)
  - product_process_pkey1 (UNIQUE) on (id)
  - product_process_product_id_process_id_key (UNIQUE) on (product_id, process_id)

### public.users (b'r', 32.0KB)
- 컬럼:
  - id: integer (NOT NULL) default=nextval('users_id_seq'::regclass)
  - username: text (NOT NULL)
  - email: text (NOT NULL)
  - password_hash: text (NOT NULL)
  - created_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
  - updated_at: timestamp without time zone (NULL) default=CURRENT_TIMESTAMP
- 기본키: id
- 외래키: (없음)
- 인덱스:
  - users_email_key (UNIQUE) on (email)
  - users_pkey (UNIQUE) on (id)
  - users_username_key (UNIQUE) on (username)
