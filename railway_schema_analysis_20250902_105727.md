# Railway DB 스키마 분석 보고서

## 📊 데이터베이스 정보
- **데이터베이스명**: railway
- **사용자**: postgres
- **PostgreSQL 버전**: PostgreSQL 16.10 (Debian 16.10-1.pgdg13+1) on x86_64-pc-linux-gnu
- **분석 일시**: 2025-09-02T10:57:18.711448

## 📋 테이블 목록
총 **16**개의 테이블이 발견되었습니다.

## 🗃️ 테이블: `companies`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 0

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('companies_id_seq'::regclass) | - |
| company_name | text | ❌ | - | - |
| country | text | ✅ | - | - |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |

### 🔒 제약조건
- **companies_pkey**: PRIMARY KEY (id)

### 📍 인덱스
- **companies_pkey**: CREATE UNIQUE INDEX companies_pkey ON public.companies USING btree (id)

---

## 🗃️ 테이블: `countries`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 0

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('countries_id_seq'::regclass) | - |
| country_name | text | ❌ | - | - |
| country_code | text | ❌ | - | - |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |

### 🔒 제약조건
- **countries_pkey**: PRIMARY KEY (id)
- **countries_country_code_key**: UNIQUE (country_code)

### 📍 인덱스
- **countries_pkey**: CREATE UNIQUE INDEX countries_pkey ON public.countries USING btree (id)
- **countries_country_code_key**: CREATE UNIQUE INDEX countries_country_code_key ON public.countries USING btree (country_code)

---

## 🗃️ 테이블: `dummy`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 21

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('dummy_id_seq'::regclass) | - |
| 로트번호 | character varying | ✅ | - | - |
| 생산품명 | character varying | ✅ | - | - |
| 생산수량 | numeric | ✅ | - | - |
| 투입일 | date | ✅ | - | - |
| 종료일 | date | ✅ | - | - |
| 공정 | character varying | ✅ | - | - |
| 투입물명 | character varying | ✅ | - | - |
| 수량 | numeric | ✅ | - | - |
| 단위 | character varying | ✅ | - | - |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |

### 🔒 제약조건
- **dummy_pkey**: PRIMARY KEY (id)

### 📍 인덱스
- **dummy_pkey**: CREATE UNIQUE INDEX dummy_pkey ON public.dummy USING btree (id)

---

## 🗃️ 테이블: `edge`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 66

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('edge_id_seq'::regclass) | - |
| source_node_type | USER-DEFINED | ❌ | - | - |
| source_id | integer | ❌ | - | - |
| target_node_type | USER-DEFINED | ❌ | - | - |
| target_id | integer | ❌ | - | - |
| edge_kind | USER-DEFINED | ❌ | - | - |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |

### 🔒 제약조건
- **edge_pkey**: PRIMARY KEY (id)

### 📍 인덱스
- **idx_edge_kind**: CREATE INDEX idx_edge_kind ON public.edge USING btree (edge_kind)
- **idx_edge_source_node_type**: CREATE INDEX idx_edge_source_node_type ON public.edge USING btree (source_node_type)
- **idx_edge_target_node_type**: CREATE INDEX idx_edge_target_node_type ON public.edge USING btree (target_node_type)
- **idx_edge_source_id**: CREATE INDEX idx_edge_source_id ON public.edge USING btree (source_id)
- **idx_edge_target_id**: CREATE INDEX idx_edge_target_id ON public.edge USING btree (target_id)
- **edge_pkey**: CREATE UNIQUE INDEX edge_pkey ON public.edge USING btree (id)

---

## 🗃️ 테이블: `fuel_master`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 40

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('fuel_master_id_seq'::regclass) | - |
| fuel_name | character varying | ❌ | - | - |
| fuel_engname | character varying | ❌ | - | - |
| fuel_factor | numeric | ❌ | - | - |
| net_calory | numeric | ✅ | - | - |
| created_at | timestamp with time zone | ✅ | now() | - |

### 🔒 제약조건
- **fuel_master_pkey**: PRIMARY KEY (id)

### 📍 인덱스
- **fuel_master_pkey**: CREATE UNIQUE INDEX fuel_master_pkey ON public.fuel_master USING btree (id)
- **idx_fuel_master_name**: CREATE INDEX idx_fuel_master_name ON public.fuel_master USING btree (fuel_name)
- **idx_fuel_master_engname**: CREATE INDEX idx_fuel_master_engname ON public.fuel_master USING btree (fuel_engname)

---

## 🗃️ 테이블: `fueldir`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 2

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('fueldir_id_seq'::regclass) | - |
| process_id | integer | ❌ | - | - |
| fuel_name | character varying | ❌ | - | - |
| fuel_factor | numeric | ❌ | - | - |
| fuel_amount | numeric | ❌ | - | - |
| fuel_oxyfactor | numeric | ✅ | 1.0000 | - |
| fueldir_em | numeric | ✅ | 0 | - |
| created_at | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp with time zone | ✅ | CURRENT_TIMESTAMP | - |

### 🔒 제약조건
- **fueldir_pkey**: PRIMARY KEY (id)
- **fk_fueldir_process**: FOREIGN KEY (id)
- **unique_fueldir_process_fuel**: UNIQUE (process_id)
- **unique_fueldir_process_fuel**: UNIQUE (fuel_name)

### 📍 인덱스
- **fueldir_pkey**: CREATE UNIQUE INDEX fueldir_pkey ON public.fueldir USING btree (id)
- **idx_fueldir_process_id**: CREATE INDEX idx_fueldir_process_id ON public.fueldir USING btree (process_id)
- **idx_fueldir_fuel_name**: CREATE INDEX idx_fueldir_fuel_name ON public.fueldir USING btree (fuel_name)
- **idx_fueldir_created_at**: CREATE INDEX idx_fueldir_created_at ON public.fueldir USING btree (created_at)
- **unique_fueldir_process_fuel**: CREATE UNIQUE INDEX unique_fueldir_process_fuel ON public.fueldir USING btree (process_id, fuel_name)
- **idx_fueldir_process_fuel**: CREATE INDEX idx_fueldir_process_fuel ON public.fueldir USING btree (process_id, fuel_name)

---

## 🗃️ 테이블: `hs_cn_mapping`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 84

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('hs_cn_mapping_id_seq'::regclass) | - |
| hscode | character varying | ❌ | - | - |
| aggregoods_name | text | ✅ | - | - |
| aggregoods_engname | text | ✅ | - | - |
| cncode_total | character varying | ❌ | - | - |
| goods_name | text | ✅ | - | - |
| goods_engname | text | ✅ | - | - |

### 🔒 제약조건
- **hs_cn_mapping_pkey**: PRIMARY KEY (id)

### 📍 인덱스
- **hs_cn_mapping_pkey**: CREATE UNIQUE INDEX hs_cn_mapping_pkey ON public.hs_cn_mapping USING btree (id)
- **idx_hs_cn_mapping_hscode**: CREATE INDEX idx_hs_cn_mapping_hscode ON public.hs_cn_mapping USING btree (hscode)
- **idx_hs_cn_mapping_cncode**: CREATE INDEX idx_hs_cn_mapping_cncode ON public.hs_cn_mapping USING btree (cncode_total)

---

## 🗃️ 테이블: `install`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 1

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('install_id_seq'::regclass) | - |
| install_name | text | ❌ | - | - |
| reporting_year | integer | ❌ | EXTRACT(year FROM now()) | - |
| created_at | timestamp with time zone | ✅ | now() | - |
| updated_at | timestamp with time zone | ✅ | now() | - |

### 🔒 제약조건
- **install_pkey**: PRIMARY KEY (id)

### 📍 인덱스
- **install_pkey**: CREATE UNIQUE INDEX install_pkey ON public.install USING btree (id)

---

## 🗃️ 테이블: `matdir`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 2

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('matdir_id_seq'::regclass) | - |
| process_id | integer | ❌ | - | - |
| mat_name | character varying | ❌ | - | - |
| mat_factor | numeric | ❌ | - | - |
| mat_amount | numeric | ❌ | - | - |
| oxyfactor | numeric | ✅ | 1.0000 | - |
| matdir_em | numeric | ✅ | 0 | - |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |

### 🔒 제약조건
- **matdir_pkey**: PRIMARY KEY (id)
- **matdir_process_id_fkey**: FOREIGN KEY (id)
- **unique_matdir_process_material**: UNIQUE (process_id)
- **unique_matdir_process_material**: UNIQUE (mat_name)

### 📍 인덱스
- **idx_matdir_process_id**: CREATE INDEX idx_matdir_process_id ON public.matdir USING btree (process_id)
- **matdir_pkey**: CREATE UNIQUE INDEX matdir_pkey ON public.matdir USING btree (id)
- **unique_matdir_process_material**: CREATE UNIQUE INDEX unique_matdir_process_material ON public.matdir USING btree (process_id, mat_name)
- **idx_matdir_process_material**: CREATE INDEX idx_matdir_process_material ON public.matdir USING btree (process_id, mat_name)

---

## 🗃️ 테이블: `material_master`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 21

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('material_master_id_seq'::regclass) | - |
| mat_name | character varying | ❌ | - | - |
| mat_engname | character varying | ❌ | - | - |
| carbon_content | numeric | ✅ | - | - |
| mat_factor | numeric | ❌ | - | - |

### 🔒 제약조건
- **material_master_pkey**: PRIMARY KEY (id)

### 📍 인덱스
- **idx_material_master_name**: CREATE INDEX idx_material_master_name ON public.material_master USING btree (mat_name)
- **idx_material_master_engname**: CREATE INDEX idx_material_master_engname ON public.material_master USING btree (mat_engname)
- **material_master_pkey**: CREATE UNIQUE INDEX material_master_pkey ON public.material_master USING btree (id)

---

## 🗃️ 테이블: `process`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 4

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('process_id_seq'::regclass) | - |
| process_name | text | ❌ | - | - |
| start_period | date | ✅ | - | - |
| end_period | date | ✅ | - | - |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |

### 🔒 제약조건
- **process_pkey**: PRIMARY KEY (id)

### 📍 인덱스
- **process_pkey**: CREATE UNIQUE INDEX process_pkey ON public.process USING btree (id)
- **idx_process_name**: CREATE INDEX idx_process_name ON public.process USING btree (process_name)

---

## 🗃️ 테이블: `process_attrdir_emission`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 2

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('process_attrdir_emission_id_seq'::regclass) | - |
| process_id | integer | ❌ | - | - |
| total_matdir_emission | numeric | ✅ | 0 | - |
| total_fueldir_emission | numeric | ✅ | 0 | - |
| attrdir_em | numeric | ✅ | 0 | - |
| calculation_date | timestamp with time zone | ✅ | now() | - |
| created_at | timestamp with time zone | ✅ | now() | - |
| updated_at | timestamp with time zone | ✅ | now() | - |
| cumulative_emission | numeric | ✅ | 0 | - |

### 🔒 제약조건
- **process_attrdir_emission_pkey**: PRIMARY KEY (id)
- **process_attrdir_emission_process_id_key**: UNIQUE (process_id)
- **process_attrdir_emission_process_id_fkey**: FOREIGN KEY (id)

### 📍 인덱스
- **idx_process_attrdir_emission_process_id**: CREATE INDEX idx_process_attrdir_emission_process_id ON public.process_attrdir_emission USING btree (process_id)
- **idx_process_attrdir_emission_cumulative**: CREATE INDEX idx_process_attrdir_emission_cumulative ON public.process_attrdir_emission USING btree (cumulative_emission)
- **process_attrdir_emission_pkey**: CREATE UNIQUE INDEX process_attrdir_emission_pkey ON public.process_attrdir_emission USING btree (id)
- **process_attrdir_emission_process_id_key**: CREATE UNIQUE INDEX process_attrdir_emission_process_id_key ON public.process_attrdir_emission USING btree (process_id)

---

## 🗃️ 테이블: `product`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 2

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('product_id_seq'::regclass) | - |
| install_id | integer | ❌ | - | - |
| product_name | text | ❌ | - | - |
| product_category | text | ❌ | - | - |
| prostart_period | date | ❌ | - | - |
| proend_period | date | ❌ | - | - |
| cncode_total | text | ✅ | - | - |
| goods_name | text | ✅ | - | - |
| goods_engname | text | ✅ | - | - |
| aggrgoods_name | text | ✅ | - | - |
| aggrgoods_engname | text | ✅ | - | - |
| product_amount | numeric | ✅ | 0 | - |
| product_sell | numeric | ✅ | 0 | - |
| product_eusell | numeric | ✅ | 0 | - |
| created_at | timestamp with time zone | ✅ | now() | - |
| updated_at | timestamp with time zone | ✅ | now() | - |
| attr_em | numeric | ✅ | 0.0 | - |

### 🔒 제약조건
- **valid_period**: CHECK (proend_period)
- **valid_period**: CHECK (prostart_period)
- **product_pkey**: PRIMARY KEY (id)
- **unique_install_product_name**: UNIQUE (install_id)
- **unique_install_product_name**: UNIQUE (product_name)

### 📍 인덱스
- **product_pkey**: CREATE UNIQUE INDEX product_pkey ON public.product USING btree (id)
- **idx_product_install_id**: CREATE INDEX idx_product_install_id ON public.product USING btree (install_id)
- **idx_product_product_name**: CREATE INDEX idx_product_product_name ON public.product USING btree (product_name)
- **unique_install_product_name**: CREATE UNIQUE INDEX unique_install_product_name ON public.product USING btree (install_id, product_name)

---

## 🗃️ 테이블: `product_process`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 4

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('product_process_id_seq1'::regclass) | - |
| product_id | integer | ❌ | - | - |
| process_id | integer | ❌ | - | - |
| created_at | timestamp with time zone | ✅ | now() | - |
| updated_at | timestamp with time zone | ✅ | now() | - |
| consumption_amount | numeric | ✅ | 0 | - |

### 🔒 제약조건
- **product_process_pkey1**: PRIMARY KEY (id)
- **product_process_product_id_process_id_key**: UNIQUE (product_id)
- **product_process_product_id_process_id_key**: UNIQUE (process_id)
- **product_process_process_id_fkey1**: FOREIGN KEY (id)
- **product_process_product_id_fkey**: FOREIGN KEY (id)

### 📍 인덱스
- **product_process_pkey1**: CREATE UNIQUE INDEX product_process_pkey1 ON public.product_process USING btree (id)
- **product_process_product_id_process_id_key**: CREATE UNIQUE INDEX product_process_product_id_process_id_key ON public.product_process USING btree (product_id, process_id)
- **idx_product_process_consumption_amount**: CREATE INDEX idx_product_process_consumption_amount ON public.product_process USING btree (consumption_amount)

---

## 🗃️ 테이블: `users`

### 📊 기본 정보
- **테이블 타입**: BASE TABLE
- **데이터 개수**: 0

### 📝 컬럼 구조

| 컬럼명 | 데이터 타입 | NULL 허용 | 기본값 | 설명 |
|--------|-------------|-----------|---------|------|
| id | integer | ❌ | nextval('users_id_seq'::regclass) | - |
| username | text | ❌ | - | - |
| email | text | ❌ | - | - |
| password_hash | text | ❌ | - | - |
| created_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |
| updated_at | timestamp without time zone | ✅ | CURRENT_TIMESTAMP | - |

### 🔒 제약조건
- **users_pkey**: PRIMARY KEY (id)
- **users_username_key**: UNIQUE (username)
- **users_email_key**: UNIQUE (email)

### 📍 인덱스
- **users_pkey**: CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id)
- **users_username_key**: CREATE UNIQUE INDEX users_username_key ON public.users USING btree (username)
- **users_email_key**: CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email)

---

