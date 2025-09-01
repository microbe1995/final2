-- ============================================================================
-- 🗑️ ProcessChain 관련 테이블 제거 스크립트
-- ============================================================================
-- 이 스크립트는 ProcessChain 도메인 제거에 따라 관련 테이블들을 삭제합니다.
-- Edge 기반 배출량 전파로 통일되었으므로 이 테이블들은 더 이상 필요하지 않습니다.

-- 외래키 제약조건 제거 (순서 중요)
ALTER TABLE process_chain_link DROP CONSTRAINT IF EXISTS process_chain_link_chain_id_fkey;
ALTER TABLE process_chain_link DROP CONSTRAINT IF EXISTS process_chain_link_process_id_fkey;

-- 테이블 삭제
DROP TABLE IF EXISTS process_chain_link;
DROP TABLE IF EXISTS process_chain;

-- 제거 완료 확인
SELECT 'ProcessChain 관련 테이블 제거 완료' as status;

-- 남은 테이블 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name NOT LIKE 'process_chain%'
ORDER BY table_name;
