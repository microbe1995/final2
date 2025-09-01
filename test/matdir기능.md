`@matdir/` 폴더의 기능을 분석해서 설명해드리겠습니다. 각 파일을 살펴보겠습니다.


[7 tools called]

## 📦 `@matdir/` 폴더 기능 설명

`@matdir/` 폴더는 **원료직접배출량(Material Direct Emission)** 관리 시스템으로, CBAM 서비스의 핵심 기능 중 하나입니다. DDD(Domain-Driven Design) 패턴을 따라 구성되어 있습니다.

### ��️ **아키텍처 구조**

```
@matdir/
├── __init__.py          # 모듈 초기화 및 외부 노출
├── matdir_entity.py     # 도메인 엔티티 (데이터베이스 모델)
├── matdir_schema.py     # API 요청/응답 스키마
├── matdir_repository.py # 데이터 접근 계층
├── matdir_service.py    # 비즈니스 로직 계층
└── matdir_controller.py # API 엔드포인트 계층
```

### �� **핵심 기능**

#### 1. **원료직접배출량 계산 및 관리**
- **계산 공식**: `matdir_em = mat_amount × mat_factor × oxyfactor`
- **주요 필드**:
  - `process_id`: 공정 ID
  - `mat_name`: 원료명
  - `mat_factor`: 배출계수 (kg CO2/kg 원료)
  - `mat_amount`: 원료 투입량 (kg)
  - `oxyfactor`: 산화계수 (기본값: 1.0000)
  - `matdir_em`: 계산된 배출량 (kg CO2)

#### 2. **CRUD 작업**
- **생성**: `/create` - 새로운 원료직접배출량 데이터 생성
- **조회**: `/list`, `/{id}`, `/process/{process_id}` - 데이터 조회
- **수정**: `/{id}` - 기존 데이터 수정
- **삭제**: `/{id}` - 데이터 삭제

#### 3. **계산 기능**
- **개별 계산**: `/calculate` - 원료직접배출량 계산
- **공정별 총계**: `/process/{process_id}/total` - 특정 공정의 총 배출량

#### 4. **원료 마스터 연동**
- **자동 배출계수**: `/auto-factor` - 원료명으로 배출계수 자동 매핑
- **마스터 조회**: `/material-master` - 원료 마스터 데이터 조회
- **검색 기능**: `/material-master/search/{mat_name}` - 원료명 검색

### �� **데이터 흐름**

```
1. API 요청 → Controller
2. Controller → Service (비즈니스 로직)
3. Service → Repository (데이터 접근)
4. Repository → Database (PostgreSQL)
5. 계산 결과 반환 및 저장
```

### �� **데이터베이스 구조**

```sql
CREATE TABLE matdir (
    id SERIAL PRIMARY KEY,
    process_id INTEGER NOT NULL,
    mat_name VARCHAR(255) NOT NULL,
    mat_factor NUMERIC(10, 6) NOT NULL,
    mat_amount NUMERIC(15, 6) NOT NULL,
    oxyfactor NUMERIC(5, 4) DEFAULT 1.0000,
    matdir_em NUMERIC(15, 6) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### �� **주요 API 엔드포인트**

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/create` | 원료직접배출량 생성 |
| `GET` | `/list` | 전체 목록 조회 |
| `GET` | `/process/{id}` | 공정별 조회 |
| `POST` | `/calculate` | 배출량 계산 |
| `GET` | `/process/{id}/total` | 공정별 총 배출량 |
| `POST` | `/auto-factor` | 자동 배출계수 매핑 |

### �� **특별한 기능**

1. **중복 방지**: `process_id` + `mat_name` 조합으로 중복 데이터 방지
2. **자동 계산**: 원료량, 배출계수, 산화계수로 배출량 자동 계산
3. **마스터 연동**: Railway DB의 `materials` 테이블과 연동하여 배출계수 자동 매핑
4. **공정 연관**: `process` 테이블과 외래키로 연결되어 공정별 관리

이 시스템은 CBAM(Carbon Border Adjustment Mechanism)에서 원료 투입에 따른 탄소 배출량을 정확하게 계산하고 관리하는 핵심 역할을 담당합니다.