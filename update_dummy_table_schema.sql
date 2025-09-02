-- ============================================================================
-- 🔧 Dummy 테이블 스키마 업데이트
-- 생산수량, 수량 컬럼을 numeric에서 integer로 변경
-- ============================================================================

-- 1. 기존 데이터 백업 (안전을 위해)
CREATE TABLE dummy_backup AS SELECT * FROM dummy;

-- 2. 생산수량 컬럼을 integer로 변경
ALTER TABLE dummy 
ALTER COLUMN 생산수량 TYPE integer 
USING ROUND(생산수량::numeric);

-- 3. 수량 컬럼을 integer로 변경
ALTER TABLE dummy 
ALTER COLUMN 수량 TYPE integer 
USING ROUND(수량::numeric);

-- 4. 변경 확인
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'dummy' 
AND column_name IN ('생산수량', '수량');

-- 5. 데이터 확인
SELECT id, 생산수량, 수량 FROM dummy LIMIT 5;

-- 6. 백업 테이블 삭제 (변경이 성공적으로 완료된 후)
-- DROP TABLE dummy_backup;
