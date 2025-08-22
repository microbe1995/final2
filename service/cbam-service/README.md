# 🚀 CBAM Service (Cal_boundary)

ReactFlow 기반 CBAM 계산 서비스입니다.

## 🏗️ 아키텍처

- **FastAPI**: 현대적인 Python 웹 프레임워크
- **SQLAlchemy 2.x**: ORM 및 데이터베이스 관리
- **PostgreSQL**: 프로덕션 데이터베이스 (SQLite 폴백 지원)
- **ReactFlow**: 다이어그램 기반 프로세스 관리

## 🚨 PostgreSQL Collation 문제 해결

Railway PostgreSQL에서 발생하는 collation 버전 불일치 문제를 자동으로 해결합니다:

```
WARNING: database "railway" has a collation version mismatch
DETAIL: The database was created using collation version 2.36, but the operating system provides version 2.41.
```

### 해결 방법

1. **자동 해결**: 배포 시 `migrate_db.py` 스크립트가 자동으로 실행되어 문제를 해결합니다.
2. **수동 해결**: Railway 대시보드에서 다음 SQL을 실행:

```sql
-- Collation 버전 업데이트
ALTER DATABASE railway REFRESH COLLATION VERSION;

-- 또는 특정 테이블의 collation 재설정
ALTER TABLE your_table_name ALTER COLUMN your_column_name TYPE text COLLATE "default";
```

## 🚀 Railway 배포

### 1. 환경변수 설정

Railway 대시보드에서 다음 환경변수를 설정하세요:

```bash
# 필수 환경변수
DATABASE_URL=postgresql://username:password@host:port/database
PORT=8001

# 선택적 환경변수
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### 2. 배포 과정

1. **GitHub 연동**: Railway에서 GitHub 저장소를 연결
2. **자동 배포**: 코드 변경 시 자동으로 배포됨
3. **마이그레이션**: 배포 시 자동으로 데이터베이스 테이블 생성 및 샘플 데이터 삽입

### 3. 배포 로그 확인

배포 로그에서 다음 메시지들을 확인할 수 있습니다:

```
🚀 CBAM 서비스 시작 중...
🗄️ 데이터베이스 마이그레이션 실행 중...
✅ 데이터베이스 연결 성공
🔧 PostgreSQL collation 문제 해결 중...
✅ Collation 설정 완료
🗄️ 데이터베이스 테이블 생성 중...
✅ fuels 테이블 생성 완료
✅ materials 테이블 생성 완료
✅ precursors 테이블 생성 완료
✅ calculation_results 테이블 생성 완료
✅ 인덱스 생성 완료
📊 샘플 데이터 삽입 중...
✅ 연료 샘플 데이터 삽입 완료
✅ 원료 샘플 데이터 삽입 완료
🎉 데이터베이스 마이그레이션 완료!
🚀 애플리케이션 시작...
```

## 📊 데이터베이스 스키마

### fuels 테이블
```sql
CREATE TABLE fuels (
    id SERIAL PRIMARY KEY,
    fuel_name VARCHAR(255) NOT NULL,
    fuel_eng VARCHAR(255),
    fuel_emfactor DECIMAL(10,2),
    net_calory DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### materials 테이블
```sql
CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    item_eng VARCHAR(255),
    carbon_factor DECIMAL(10,2),
    em_factor DECIMAL(10,2),
    cn_code VARCHAR(50),
    cn_code1 VARCHAR(50),
    cn_code2 VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### precursors 테이블
```sql
CREATE TABLE precursors (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    calculation_type VARCHAR(50) NOT NULL,
    fuel_id INTEGER,
    material_id INTEGER,
    quantity DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fuel_id) REFERENCES fuels(id) ON DELETE SET NULL,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET NULL
);
```

### calculation_results 테이블
```sql
CREATE TABLE calculation_results (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    calculation_type VARCHAR(50) NOT NULL,
    fuel_id INTEGER,
    material_id INTEGER,
    quantity DECIMAL(10,2) NOT NULL,
    result_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fuel_id) REFERENCES fuels(id) ON DELETE SET NULL,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET NULL
);
```

## 🔧 로컬 개발

### 1. 환경 설정

```bash
# .env 파일 생성
cp env.example .env

# 환경변수 설정
DATABASE_URL=postgresql://username:password@localhost:5432/cbam_db
PORT=8001
DEBUG_MODE=true
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션

```bash
python migrate_db.py
```

### 4. 애플리케이션 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📚 API 문서

서비스가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

## 🐳 Docker

### 빌드

```bash
docker build -t cbam-service .
```

### 실행

```bash
docker run -p 8001:8001 --env-file .env cbam-service
```

## 🔍 문제 해결

### 1. 데이터베이스 연결 실패

```bash
# 연결 테스트
python -c "
from app.common.database_base import create_database_engine
engine = create_database_engine()
print('✅ 데이터베이스 연결 성공')
"
```

### 2. Collation 문제

```bash
# 마이그레이션 스크립트 실행
python migrate_db.py
```

### 3. 테이블 생성 실패

```bash
# 수동으로 테이블 생성
python -c "
from app.domain.calculation.calculation_repository import CalculationRepository
repo = CalculationRepository(use_database=True)
print('✅ 테이블 생성 완료')
"
```

## 📞 지원

문제가 발생하면 Railway 배포 로그를 확인하고 GitHub 이슈를 생성해주세요.
