-- ============================================================================
-- 🗑️ 불필요한 source_stream 테이블 제거 스크립트
-- ============================================================================
-- 
-- 이 스크립트는 Railway DB에서 사용되지 않는 source_stream 테이블을 제거합니다.
-- Edge 엔티티가 이미 공정 간 연결을 관리하므로 source_stream은 불필요합니다.
--
-- 실행 전 주의사항:
-- 1. 백업이 있는지 확인
-- 2. 테이블에 중요한 데이터가 없는지 확인
-- 3. 애플리케이션이 실행 중이지 않은지 확인
-- ============================================================================

-- 1. source_stream 테이블 존재 여부 확인
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_name = 'source_stream';

-- 2. source_stream 테이블의 현재 데이터 확인 (있는 경우)
-- SELECT COUNT(*) FROM source_stream;

-- 3. source_stream 테이블 제거
DROP TABLE IF EXISTS source_stream CASCADE;

-- 4. 제거 완료 확인
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_name = 'source_stream';

-- 5. 관련 시퀀스나 인덱스가 남아있는지 확인
SELECT 
    sequence_name
FROM information_schema.sequences 
WHERE sequence_name LIKE '%source_stream%';

-- 6. 관련 제약조건 확인
SELECT 
    constraint_name,
    table_name,
    constraint_type
FROM information_schema.table_constraints 
WHERE table_name LIKE '%source_stream%';

-- ============================================================================
-- ✅ source_stream 테이블 제거 완료!
-- ============================================================================
-- 
-- 이제 Edge 기반의 단순한 공정 연결 관리만 사용됩니다:
-- - edge: 공정 간 기본 연결 정보
-- - process_chain: 통합 공정 그룹
-- - process_chain_link: 그룹 내 공정 연결
-- ============================================================================
