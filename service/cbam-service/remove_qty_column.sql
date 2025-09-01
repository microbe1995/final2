-- ============================================================================
-- Railway DB edge 테이블 qty 컬럼 삭제 SQL 스크립트
-- ============================================================================

-- 1. 현재 edge 테이블 구조 확인
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'edge' 
ORDER BY ordinal_position;

-- 2. qty 컬럼 존재 여부 확인
SELECT 
    column_name,
    data_type
FROM information_schema.columns 
WHERE table_name = 'edge' 
AND column_name = 'qty';

-- 3. qty 컬럼 삭제 (존재하는 경우에만)
ALTER TABLE edge DROP COLUMN IF EXISTS qty;

-- 4. 삭제 후 edge 테이블 구조 재확인
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'edge' 
ORDER BY ordinal_position;

-- 5. 삭제 완료 확인
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ qty 컬럼이 성공적으로 삭제되었습니다.'
        ELSE '❌ qty 컬럼이 여전히 존재합니다.'
    END as result
FROM information_schema.columns 
WHERE table_name = 'edge' 
AND column_name = 'qty';
