-- ============================================================================
-- 🗑️ Railway DB에서 잘못 만든 dummy_data 테이블 제거
-- ============================================================================

-- 1. 테이블 존재 여부 확인
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'dummy_data'
) AS table_exists;

-- 2. 테이블 구조 확인 (제거 전)
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'dummy_data'
ORDER BY ordinal_position;

-- 3. 테이블 데이터 확인 (제거 전)
SELECT COUNT(*) as total_rows FROM dummy_data;

-- 4. 테이블 제거 (⚠️ 주의: 이 작업은 되돌릴 수 없습니다)
DROP TABLE IF EXISTS dummy_data CASCADE;

-- 5. 제거 확인
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'dummy_data'
) AS table_exists;

-- 6. 정상 dummy 테이블 확인
SELECT 
    table_name,
    table_type,
    (SELECT COUNT(*) FROM dummy) as row_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'dummy';

-- 7. dummy 테이블 구조 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'dummy'
ORDER BY ordinal_position;

-- ============================================================================
-- 📊 정리 결과
-- ============================================================================
-- ✅ dummy_data 테이블 제거 완료
-- ✅ dummy 테이블 유지 (실제 사용할 테이블)
-- ✅ 21개 데이터 보존
-- ============================================================================
